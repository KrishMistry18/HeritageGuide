from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User 
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.views.generic import FormView, ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Sum
from django.db.models import Q
from .forms import ItineraryForm, SlotBookingForm, BookingForm, SignUpForm, ProfileUpdateForm
from .models import City, Attraction, Itinerary, ItineraryDay, ItineraryActivity, SlotBooking, AttractionType, Booking, Profile
import random
import datetime
from django.utils import timezone
from collections import defaultdict

import os
import openai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import ChatMessage
import logging
from anthropic import Anthropic
import traceback
from .supabase_client import get_supabase_anon_client

logger = logging.getLogger(__name__)

# Configure Claude API — optional, chatbot disabled if key not set
_anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
anthropic_client = Anthropic(api_key=_anthropic_key) if _anthropic_key else None

@csrf_exempt
def get_response(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            
            logger.debug(f"Received message: {user_message}")
            logger.debug(f"API Key present: {bool(os.getenv('ANTHROPIC_API_KEY'))}")

            if not user_message:
                return JsonResponse({'error': 'Message cannot be empty'}, status=400)

            if not anthropic_client:
                return JsonResponse({'error': 'AI chatbot is not configured. Please add ANTHROPIC_API_KEY.'}, status=503)

            try:
                # Generate response using Claude
                logger.debug("Attempting to create Claude message...")
                response = anthropic_client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=150,
                    messages=[
                        {
                            "role": "user", 
                            "content": f"You are a helpful travel assistant. Respond to this message: {user_message}"
                        }
                    ]
                )
                logger.debug("Claude message created successfully")

                bot_response = response.content[0].text.strip()
                logger.debug(f"Bot response: {bot_response}")

                return JsonResponse({
                    'response': bot_response
                })

            except Exception as e:
                logger.error(f"Claude API Error: {str(e)}")
                logger.error(traceback.format_exc())
                return JsonResponse({
                    'error': f'Claude API Error: {str(e)}. Please try again later.'
                }, status=500)

        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
            return JsonResponse({'error': 'Invalid request format'}, status=400)
        
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            logger.error(traceback.format_exc())
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

class ItineraryCreateView(LoginRequiredMixin, FormView):
    template_name = 'itinerary/create_itinerary.html'
    form_class = ItineraryForm
    
    interest_descriptions = {
        'culture': "Historical sites, museums, local traditions, and cultural experiences",
        'adventure': "Thrilling activities, outdoor sports, and exciting experiences",
        'relaxation': "Peaceful activities, wellness centers, and stress-free environments",
        'food': "Local cuisine, food tours, cooking classes, and culinary experiences",
        'nature': "Parks, gardens, wildlife, and outdoor natural attractions",
        'shopping': "Markets, malls, boutiques, and shopping districts",
        'entertainment': "Shows, concerts, nightlife, and entertainment venues"
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all cities from the database
        context['cities'] = City.objects.all()
        
        # Add interest choices based on the interest_descriptions
        context['interest_choices'] = [
            (key, value.split(',')[0]) for key, value in self.interest_descriptions.items()
        ]
        
        # Add transportation choices
        context['transportation_choices'] = [
            ('car', 'Rental Car'),
            ('public', 'Public Transportation'),
            ('tour', 'Guided Tours'),
            ('walk', 'Walking'),
            ('bike', 'Biking'),
            ('mixed', 'Mixed')
        ]
        
        return context

    def get_attractions_by_interest(self, city, interests):
        """Get city attractions using robust interest keyword matching."""
        interest_map = {
            "culture": ["culture", "history", "heritage", "art", "architecture"],
            "adventure": ["adventure", "trek", "hike", "outdoor"],
            "relaxation": ["relaxation", "wellness", "spa", "calm"],
            "food": ["food", "cuisine", "restaurant", "street food"],
            "nature": ["nature", "park", "wildlife", "garden", "beach"],
            "shopping": ["shopping", "market", "mall", "bazaar"],
            "entertainment": ["entertainment", "show", "event", "music", "nightlife"],
        }
        query = Q()
        for interest in interests:
            for keyword in interest_map.get(interest, [interest]):
                query |= Q(interest_tags__icontains=keyword) | Q(type__icontains=keyword)

        matched = Attraction.objects.filter(city=city).filter(query).order_by("-rating")
        if not matched.exists():
            matched = Attraction.objects.filter(city=city).order_by("-rating")
        return list(matched)

    def form_valid(self, form):
        try:
            selected_city_ids = [int(city_id) for city_id in form.cleaned_data["cities"]]
            city_map = {city.id: city for city in City.objects.filter(id__in=selected_city_ids)}
            cities = [city_map[city_id] for city_id in selected_city_ids if city_id in city_map]
            if not cities:
                messages.error(self.request, "No valid cities selected.")
                return self.form_invalid(form)
            
            # Create the itinerary
            itinerary = Itinerary.objects.create(
                user=self.request.user,
                name=form.cleaned_data['name'],
                start_date=form.cleaned_data['start_date'],
                end_date=form.cleaned_data['end_date'],
                transportation_type=form.cleaned_data['transportation_type'],
                total_budget=form.cleaned_data['total_budget'],
                interests=','.join(form.cleaned_data['interests'])
            )
            
            itinerary.cities.set(cities)
            
            # Calculate number of days for the trip
            total_days = (form.cleaned_data['end_date'] - form.cleaned_data['start_date']).days + 1
            
            # Distribute days among cities
            days_per_city = total_days // len(cities)
            remaining_days = total_days % len(cities)
            
            current_date = form.cleaned_data['start_date']
            for i, city in enumerate(cities):
                city_days = days_per_city + (1 if i < remaining_days else 0)
                all_city_attractions = self.get_attractions_by_interest(city, form.cleaned_data["interests"])
                used_attraction_ids = set()

                for day_idx in range(city_days):
                    itinerary_day = ItineraryDay.objects.create(
                        itinerary=itinerary,
                        city=city,
                        date=current_date,
                        notes=f"Explore cultural highlights and local experiences in {city.name}."
                    )
                    fresh_attractions = [a for a in all_city_attractions if a.id not in used_attraction_ids]
                    day_attractions = fresh_attractions[:3]
                    if len(day_attractions) < 3:
                        fallback = [a for a in all_city_attractions if a.id not in {d.id for d in day_attractions}]
                        day_attractions.extend(fallback[: 3 - len(day_attractions)])

                    if not day_attractions:
                        ItineraryActivity.objects.create(
                            day=itinerary_day,
                            custom_activity=f"Self-guided cultural walk in {city.name}",
                            start_time=datetime.time(10, 0),
                            end_time=datetime.time(12, 0),
                            notes="Explore local neighborhoods, cafes, and heritage streets.",
                            order=0,
                        )
                        current_date += datetime.timedelta(days=1)
                        continue

                    for idx, attraction in enumerate(day_attractions):
                        used_attraction_ids.add(attraction.id)
                        start_hour = 9 + (idx * 3)
                        if start_hour > 17:
                            continue
                        start_time = datetime.time(start_hour, 0)
                        end_time = datetime.time(min(start_hour + 2, 18), 0)
                        activity_notes = f"Visit {attraction.name} - {attraction.get_type_display()}. "
                        if attraction.rating:
                            activity_notes += f"Rated {attraction.rating}/5. "
                        if attraction.info:
                            activity_notes += attraction.info
                        ItineraryActivity.objects.create(
                            day=itinerary_day,
                            attraction=attraction,
                            start_time=start_time,
                            end_time=end_time,
                            notes=activity_notes,
                            order=idx
                        )
                    current_date += datetime.timedelta(days=1)
            return redirect('itinerary_detail', itinerary_id=itinerary.id)
        except Exception as e:
            print(f"Error creating itinerary: {str(e)}")
            messages.error(self.request, "Failed to create itinerary. Please try again.")
            return self.form_invalid(form)

def itinerary_preview(request):
    # Get the itinerary ID from session
    itinerary_id = request.session.get('itinerary_id')
    
    if not itinerary_id:
        messages.error(request, "No itinerary found. Please create a new one.")
        return redirect('create_itinerary')
    
    # Get the itinerary object with all related data
    itinerary = get_object_or_404(Itinerary, id=itinerary_id)
    
    # Group days by city for better presentation
    days_by_city = defaultdict(list)
    
    for day in itinerary.days.all().order_by('date'):
        # Try to determine which city this day belongs to
        day_activities = day.activities.all()
        
        if day_activities.exists() and day_activities.first().attraction:
            city = day_activities.first().attraction.city
        else:
            # If no attraction or custom activity, use the first city
            city = itinerary.cities.first()
        
        days_by_city[city].append({
            'day_obj': day,
            'date': day.date,
            'activities': day.activities.all().order_by('order', 'start_time')
        })
    
    # Convert interests string to list
    interests = [interest.strip() for interest in itinerary.interests.split(',') if interest.strip()]
    
    context = {
        'itinerary': itinerary,
        'days_by_city': dict(days_by_city),
        'interests': interests
    }
    
    return render(request, 'itinerary/itinerary_detail.html', context)

# Create your views here.
def home(request):
    return render(request, 'index.html')

# # Keep other existing view functions...

# def create_itinerary(request):
#     # Create a new form instance
#     form = ItineraryForm()
    
#     # Get all destinations from the database
#     destinations = Destination.objects.all()
    
#     # Define interest choices
#     interest_choices = [
#         ('culture', 'Culture & History'),
#         ('adventure', 'Adventure'),
#         ('relaxation', 'Relaxation'),
#         ('food', 'Food & Cuisine'),
#         ('nature', 'Nature & Wildlife')
#     ]
    
#     # Define transportation choices
#     transportation_choices = [
#         ('car', 'Rental Car'),
#         ('public', 'Public Transportation'),
#         ('tour', 'Guided Tours'),
#         ('walk', 'Walking'),
#         ('bike', 'Biking'),
#         ('mixed', 'Mixed')
#     ]
    
#     # Check if destinations exist, if not create some sample ones
#     if not destinations.exists():
#         sample_destinations = [
#             "Paris", "Tokyo", "New York", "Rome", "Barcelona", 
#             "Sydney", "London", "Dubai", "Bangkok", "Istanbul"
#         ]
#         for dest_name in sample_destinations:
#             Destination.objects.create(name=dest_name)
#         destinations = Destination.objects.all()
    
#     context = {
#         'form': form,
#         'destinations': destinations,
#         'interest_choices': interest_choices,
#         'transportation_choices': transportation_choices
#     }
    
#     return render(request, "itinerary/create_itinerary.html", context)

# def itinerary_detail(request, itinerary_id=None):
#     if itinerary_id:
#         # Get the specific itinerary
#         itinerary = get_object_or_404(Itinerary, id=itinerary_id)
#     else:
#         # Get the itinerary ID from session
#         itinerary_id = request.session.get('itinerary_id')
#         if not itinerary_id:
#             messages.error(request, "No itinerary found. Please create a new one.")
#             return redirect('create_itinerary')
#         itinerary = get_object_or_404(Itinerary, id=itinerary_id)
    
#     # Group days by city for better presentation
#     days_by_city = defaultdict(list)
    
#     for day in itinerary.days.all().order_by('date'):
#         # Try to determine which city this day belongs to
#         day_activities = day.activities.all()
        
#         if day_activities.exists() and day_activities.first().attraction:
#             city = day_activities.first().attraction.city
#         else:
#             # If no attraction or custom activity, use the first city
#             city = itinerary.cities.first()
        
#         days_by_city[city].append({
#             'day_obj': day,
#             'date': day.date,
#             'activities': day.activities.all().order_by('order', 'start_time')
#         })
    
#     # Convert interests string to list
#     interests = [interest.strip() for interest in itinerary.interests.split(',') if interest.strip()]
    
#     context = {
#         'itinerary': itinerary,
#         'days_by_city': dict(days_by_city),
#         'interests': interests
#     }
    
#     return render(request, "itinerary/itinerary_detail.html", context)


def _unique_username_from_email(email: str) -> str:
    base = (email.split("@")[0] or "traveler").replace(" ", "").lower()
    candidate = base
    suffix = 1
    while User.objects.filter(username=candidate).exists():
        candidate = f"{base}{suffix}"
        suffix += 1
    return candidate


def _supabase_signup(email: str, password: str):
    client = get_supabase_anon_client()
    if not client:
        return None, "Supabase is not configured. Contact admin."
    try:
        response = client.auth.sign_up(
            {
                "email": email,
                "password": password,
            }
        )
        return response, None
    except Exception as exc:
        return None, str(exc)


def _supabase_signin(email: str, password: str):
    client = get_supabase_anon_client()
    if not client:
        return None, "Supabase is not configured. Contact admin."
    try:
        response = client.auth.sign_in_with_password(
            {
                "email": email,
                "password": password,
            }
        )
        return response, None
    except Exception as exc:
        return None, str(exc)


def loginUser(request):
    if request.method == "POST":
        loginusername = request.POST.get("loginusername", "").strip()
        loginpassword = request.POST.get("loginpassword", "").strip()
        if not loginusername or not loginpassword:
            messages.error(request, "Please enter both username/email and password.")
            return redirect("login")

        user = authenticate(request, username=loginusername, password=loginpassword)
        if user is None and "@" in loginusername:
            linked_user = User.objects.filter(email__iexact=loginusername).first()
            if linked_user:
                user = authenticate(request, username=linked_user.username, password=loginpassword)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("home")

        # If local auth fails, try Supabase and sync local account.
        if "@" in loginusername:
            supa_session, supa_error = _supabase_signin(loginusername, loginpassword)
            if supa_session and getattr(supa_session, "user", None):
                local_user = User.objects.filter(email__iexact=loginusername).first()
                if not local_user:
                    local_user = User.objects.create_user(
                        username=_unique_username_from_email(loginusername),
                        email=loginusername.lower(),
                        password=loginpassword,
                    )
                    Profile.objects.get_or_create(user=local_user)
                else:
                    local_user.set_password(loginpassword)
                    local_user.save(update_fields=["password"])
                login(request, local_user)
                messages.success(request, "Login successful!")
                return redirect("home")
            if supa_error:
                logger.error("Supabase signin failed: %s", supa_error)

        messages.error(request, "Invalid username/email or password.")
        return redirect("login")
    google_configured = bool(os.getenv("GOOGLE_CLIENT_ID", "").strip())
    return render(request, "login2.html", {"google_configured": google_configured})
def search(request):
    return render(request,'search.html')

  
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    supa_response, supa_error = _supabase_signup(
                        user.email,
                        form.cleaned_data["password1"],
                    )
                    if supa_error:
                        logger.error("Supabase signup failed for %s: %s", user.email, supa_error)
                        # Don't show Supabase errors to users — account still works locally
                    else:
                        pass  # Supabase sync succeeded
                    messages.success(request, "Account created successfully. Please log in.")
                return redirect("login")
            except Exception as e:
                messages.error(request, f'An error occurred during signup: {str(e)}')
                google_configured = bool(os.getenv("GOOGLE_CLIENT_ID", "").strip())
                return render(request, 'signup3.html', {'form': form, 'google_configured': google_configured})
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = SignUpForm()
    google_configured = bool(os.getenv("GOOGLE_CLIENT_ID", "").strip())
    return render(request, 'signup3.html', {'form': form, 'google_configured': google_configured})

def logoutUser(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You logged out successfully")
        return redirect("home")
    return redirect("account")

from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def info(request):
    return render(request, 'info.html')

@login_required
def account_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileUpdateForm(instance=profile, user=request.user)
    context = {
        'user': request.user,
        'profile': profile,
        'profile_form': form,
        'recent_bookings': Booking.objects.filter(user=request.user).select_related("attraction")[:5],
        'recent_itineraries': Itinerary.objects.filter(user=request.user).order_by("-created_at")[:5],
    }
    return render(request, 'account.html', context)

def map_view(request):
    from django.conf import settings
    return render(request, "map.html", {
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    })

def create_itinerary(request):
    form = ItineraryForm()
    return render(request, "itinerary/create_itinerary.html", {'form': form})

@login_required
def itinerary_detail(request, itinerary_id):
    # Get the specific itinerary
    itinerary = get_object_or_404(Itinerary, id=itinerary_id, user=request.user)
    
    # Get all days for this itinerary, ordered by date
    days = ItineraryDay.objects.filter(itinerary=itinerary).order_by('date')
    
    # For each day, prefetch related activities and their attractions to optimize queries
    days = days.prefetch_related(
        'activities',
        'activities__attraction'
    )
    
    # Calculate some useful statistics
    total_activities = sum(day.activities.count() for day in days)
    cities_count = itinerary.cities.count()
    
    # Group days by city for better organization
    days_by_city = defaultdict(list)
    for day in days:
        city = day.city or itinerary.cities.first()
        
        days_by_city[city].append(day)
    
    context = {
        'itinerary': itinerary,
        'days': days,
        'days_by_city': dict(days_by_city),
        'total_activities': total_activities,
        'cities_count': cities_count,
    }
    
    return render(request, 'itinerary/itinerary_detail.html', context)

def chatbot(request):
    return render(request, "chatbot.html")

def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")

from django.shortcuts import render
from .models import Museum, Monuments, Events


def search_suggestions(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse([], safe=False)
    
    try:
        # Search in the Attraction model
        attractions = Attraction.objects.filter(name__icontains=query).values('id', 'name', 'type')[:8]
        
        # Format the results
        suggestions = []
        
        for attraction in attractions:
            suggestions.append({
                'id': attraction['id'],
                'name': attraction['name'],
                'type': attraction['type']
            })
        
        # Sort alphabetically
        suggestions.sort(key=lambda x: x['name'])
        
        return JsonResponse(suggestions, safe=False)
        
    except Exception as e:
        logger.error(f"Error in search_suggestions: {str(e)}")
        return JsonResponse([], safe=False)

def attraction_detail(request, type, id):
    try:
        attraction = Attraction.objects.get(id=id, type=type)
        related_attractions = Attraction.objects.filter(city=attraction.city).exclude(id=attraction.id)[:4]
        return render(
            request,
            "attractions/detail.html",
            {
                "attraction": attraction,
                "related_attractions": related_attractions,
            },
        )
    except Attraction.DoesNotExist:
        messages.error(request, "Attraction not found.")
        return redirect('home')

def all_names(request):
    """API endpoint that returns all attraction names."""
    all_items = list(
        Attraction.objects.values("id", "name", "type").order_by("name")
    )
    return JsonResponse(all_items, safe=False)

def info1(request):
    return redirect("home")

def info2(request):
    return redirect("home")

def info3(request):
    return redirect("home")

def info4(request):
    return redirect("home")

def info5(request):
    return redirect("home")

def info6(request):
    return redirect("home")

def info7(request):
    return redirect("home")

def info8(request):
    # Get the Mumbai city object
    city = get_object_or_404(City, name="Mumbai")
    
    # Get or create the Bandra Fort attraction
    attraction, created = Attraction.objects.get_or_create(
        id=8,
        defaults={
            'name': 'Bandra Fort',
            'city': city,
            'type': AttractionType.MONUMENT,
            'info': 'Bandra Fort, also known as Castella de Aguada, is a historic fort located in Bandra, Mumbai. Built by the Portuguese in 1640, it offers stunning views of the Bandra-Worli Sea Link and the Arabian Sea.',
            'address': 'Bandra West, Mumbai, Maharashtra 400050',
            'opening_time': datetime.time(9, 0),  # 9:00 AM
            'closing_time': datetime.time(17, 30),  # 5:30 PM
            'duration_minutes': 180,
            'rating': 4.5,
            'interest_tags': 'culture,history,architecture'
        }
    )
    
    return redirect("attraction_detail", type=attraction.type, id=attraction.id)

def info9(request):
    return redirect("home")

def info10(request):
    return redirect("home")

def info11(request):
    return redirect("home")

def info12(request):
    return redirect("home")

def info13(request):
    return redirect("home")

# def info14(request):
#     return render(request, "newinfo/info14.html")

def info15(request):
    return redirect("home")

def info16(request):
    return redirect("home")

# In your views.py
from django.http import FileResponse, HttpResponseNotFound
from django.conf import settings
import os

def view_file(request):
    file_path = request.GET.get('path')
    
    # Security check to prevent directory traversal
    if '..' in file_path:
        return HttpResponseNotFound()
    
    # Construct the absolute path
    absolute_path = os.path.join(settings.STATIC_ROOT, file_path)
    
    if os.path.exists(absolute_path) and os.path.isfile(absolute_path):
        return FileResponse(open(absolute_path, 'rb'))
    else:
        return HttpResponseNotFound()

@login_required
def book_slot(request, attraction_id):
    try:
        attraction = Attraction.objects.get(id=attraction_id)
    except Attraction.DoesNotExist:
        messages.error(request, "Sorry, this attraction is not available for booking.")
        return redirect('home')
    
    selected_date = request.GET.get("date")
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            time_slot = form.cleaned_data['time_slot']
            number_of_people = form.cleaned_data['number_of_people']
            try:
                with transaction.atomic():
                    current_booked = (
                        Booking.objects.select_for_update()
                        .filter(
                            attraction=attraction,
                            date=date,
                            time_slot=time_slot,
                            status="confirmed",
                        )
                        .aggregate(total=Sum("number_of_people"))["total"]
                        or 0
                    )
                    remaining = max(0, 50 - current_booked)
                    if number_of_people > remaining:
                        messages.error(
                            request,
                            f"Sorry, only {remaining} slots are available for the selected time slot.",
                        )
                        return redirect(f"{request.path}?date={date}")

                    booking = form.save(commit=False)
                    booking.user = request.user
                    booking.attraction = attraction
                    booking.status = "confirmed"
                    booking.save()

                updated_availability = Booking.get_slot_availability(attraction, date, time_slot)
                messages.success(
                    request,
                    f"Your booking is confirmed. {updated_availability['available']} slots remain in this time slot.",
                )
                return redirect("booking_confirmation", booking_id=booking.id)
                
            except Exception as e:
                messages.error(request, f"An error occurred while creating your booking: {str(e)}")
                return redirect('book_slot', attraction_id=attraction_id)
    else:
        form = BookingForm()
        selected_date = request.GET.get("date")

    if not selected_date:
        selected_date = timezone.now().date()
    availabilities = {
        "morning": Booking.get_slot_availability(attraction, selected_date, "morning"),
        "afternoon": Booking.get_slot_availability(attraction, selected_date, "afternoon"),
        "evening": Booking.get_slot_availability(attraction, selected_date, "evening"),
    }
    
    return render(request, 'booking/book_slot.html', {
        'form': form,
        'attraction': attraction,
        'availabilities': availabilities,
        "selected_date": selected_date,
    })

@login_required
def booking_confirmation(request, booking_id):
    try:
        # Get the booking with related attraction data
        booking = get_object_or_404(
            Booking.objects.select_related('attraction', 'user'),
            id=booking_id,
            user=request.user
        )
        
        return render(request, 'booking/booking_confirmation.html', {
            'booking': booking
        })
        
    except Exception as e:
        messages.error(request, f"An error occurred while retrieving your booking: {str(e)}")
        return redirect('home')

def monuments_view(request):
    city_name = request.GET.get('city', '').strip()
    attractions = Attraction.objects.filter(type=AttractionType.MONUMENT).select_related("city")
    if city_name:
        attractions = attractions.filter(city__name__iexact=city_name)
    cities = City.objects.all()
    return render(request, "attractions/list.html", {
        "attractions": attractions, "title": "Monuments",
        "cities": cities, "active_city": city_name,
    })

def museums_view(request):
    city_name = request.GET.get('city', '').strip()
    attractions = Attraction.objects.filter(type=AttractionType.MUSEUM).select_related("city")
    if city_name:
        attractions = attractions.filter(city__name__iexact=city_name)
    cities = City.objects.all()
    return render(request, "attractions/list.html", {
        "attractions": attractions, "title": "Museums",
        "cities": cities, "active_city": city_name,
    })

def events_view(request):
    city_name = request.GET.get('city', '').strip()
    attractions = Attraction.objects.filter(type=AttractionType.EVENT).select_related("city")
    if city_name:
        attractions = attractions.filter(city__name__iexact=city_name)
    cities = City.objects.all()
    return render(request, "attractions/list.html", {
        "attractions": attractions, "title": "Events",
        "cities": cities, "active_city": city_name,
    })

@login_required
def products_view(request):
    # For now, we'll use a placeholder list of products
    # In a real application, you would have a Product model
    products = [
        {
            'id': 1,
            'name': 'Museum Guide Book',
            'price': 19.99,
            'description': 'Comprehensive guide to the museum\'s collections',
            'image': 'products/guidebook.jpg'
        },
        {
            'id': 2,
            'name': 'Historical Replica',
            'price': 49.99,
            'description': 'Handcrafted replica of a famous artifact',
            'image': 'products/replica.jpg'
        },
        # Add more products as needed
    ]
    return render(request, 'products.html', {'products': products})

@login_required
def book_slot_view(request, attraction_id):
    # This view will handle the booking process
    # You'll need to implement the actual booking logic
    return render(request, 'book_slot.html', {'attraction_id': attraction_id})

@login_required
def update_profile(request):
    if request.method == 'POST':
        profile, _ = Profile.objects.get_or_create(user=request.user)
        form = ProfileUpdateForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
        else:
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)
        return redirect("account")
    
    return redirect('account')