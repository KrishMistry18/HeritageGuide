from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User 
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.views.generic import FormView, ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ItineraryForm, SlotBookingForm, BookingForm, SignUpForm
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


logger = logging.getLogger(__name__)

# Configure Claude API
anthropic_client = Anthropic(
    api_key=os.getenv('ANTHROPIC_API_KEY')
)

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
        """Get attractions in a city filtered by user interests"""
        attractions = []
        for interest in interests:
            # Filter attractions with matching interest tags
            matching_attractions = Attraction.objects.filter(
                city=city, 
                interest_tags__icontains=interest
            ).order_by('-rating')[:5]  # Get top 5 rated attractions per interest
            attractions.extend(list(matching_attractions))
        
        # Remove duplicates while preserving order
        unique_attractions = []
        seen = set()
        for attraction in attractions:
            if attraction.id not in seen:
                unique_attractions.append(attraction)
                seen.add(attraction.id)
        
        return unique_attractions

    def form_valid(self, form):
        try:
            # Create cities list from selected city values
            selected_city_names = form.cleaned_data['cities']
            cities = []
            for city_name in selected_city_names:
                city, created = City.objects.get_or_create(name=city_name.title())
                cities.append(city)
            
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
            
            # Add selected cities to the itinerary
            for city in cities:
                itinerary.cities.add(city)
            
            # Calculate number of days for the trip
            total_days = (form.cleaned_data['end_date'] - form.cleaned_data['start_date']).days + 1
            
            # Distribute days among cities
            days_per_city = total_days // len(cities)
            remaining_days = total_days % len(cities)
            
            current_date = form.cleaned_data['start_date']
            for i, city in enumerate(cities):
                # Allocate days for this city
                city_days = days_per_city + (1 if i < remaining_days else 0)
                
                # Get all attractions for this city
                all_city_attractions = []
                for interest in form.cleaned_data['interests']:
                    matching_attractions = Attraction.objects.filter(
                        city=city,
                        interest_tags__icontains=interest
                    ).order_by('-rating')
                    all_city_attractions.extend(list(matching_attractions))
                
                # Remove duplicates by name (not just ID) while preserving order
                unique_attractions = []
                seen_names = set()
                for attraction in all_city_attractions:
                    if attraction.name.lower() not in seen_names:
                        unique_attractions.append(attraction)
                        seen_names.add(attraction.name.lower())
                
                # Create days for this city
                for day_idx in range(city_days):
                    itinerary_day = ItineraryDay.objects.create(
                        itinerary=itinerary,
                        date=current_date,
                        notes=f"Exploring {city.name}'s highlights and experiencing local culture"
                    )
                    attractions_per_day = min(4, max(3, len(unique_attractions) // city_days))
                    total_needed = attractions_per_day
                    day_attractions = []
                    start_idx = (day_idx * attractions_per_day) % len(unique_attractions) if unique_attractions else 0
                    for j in range(total_needed):
                        if unique_attractions:
                            idx = (start_idx + j) % len(unique_attractions)
                            day_attractions.append(unique_attractions[idx])
                    for idx, attraction in enumerate(day_attractions):
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


def loginUser(request):
        if request.method == "POST":
             loginusername = request.POST.get('loginusername', '').strip()
             loginpassword = request.POST.get('loginpassword', '').strip()

             print(f"Received Username: {loginusername}, Password: {loginpassword}")  # Debugging

             user = authenticate(request, username=loginusername, password=loginpassword)

             if user is not None:
                  login(request, user)
                  messages.success(request, "Login successful!")
                  return redirect('home')  # Redirect to home page
                
             else:
                 messages.error(request, "Invalid username or password.")
                 return redirect('login')
        return render(request,'login2.html')
def search(request):
    return render(request,'search.html')

  
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, 'Account created successfully! Please log in.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'An error occurred during signup: {str(e)}')
                return render(request, 'signup3.html', {'form': form})
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = SignUpForm()
    
    return render(request, 'signup3.html', {'form': form})

def logoutUser(request):
    logout(request)
    messages.success(request,"You logged out successfully")
    return redirect('home')

from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def info(request):
    return render(request, 'info.html')

@login_required
def account_view(request):
    # Get the user's profile data
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = None
    
    context = {
        'user': request.user,
        'profile': profile
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
        # Try to determine which city this day belongs to
        day_activities = day.activities.all()
        
        if day_activities.exists() and day_activities.first().attraction:
            city = day_activities.first().attraction.city
        else:
            # If no attraction or custom activity, use the first city
            city = itinerary.cities.first()
        
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
        # Get the corresponding template based on the attraction type
        template_name = f'newinfo/info{id}.html'
        return render(request, template_name, {'attraction': attraction})
    except Attraction.DoesNotExist:
        messages.error(request, "Attraction not found.")
        return redirect('home')

def all_names(request):
    """API endpoint that returns all names from all models (for smaller datasets)"""
    # Get all names from each model
    museums = Museum.objects.all().values('id', 'name')
    monuments = Monuments.objects.all().values('id', 'name')
    events = Events.objects.all().values('id', 'name')
    
    # Format the results
    all_items = []
    
    for museum in museums:
        all_items.append({
            'id': museum['id'],
            'name': museum['name'],
            'type': 'museum'
        })
    
    for monument in monuments:
        all_items.append({
            'id': monument['id'],
            'name': monument['name'],
            'type': 'monument'
        })
    
    for event in events:
        all_items.append({
            'id': event['id'],
            'name': event['name'],
            'type': 'event'
        })
    
    # Sort alphabetically
    all_items.sort(key=lambda x: x['name'])
    
    return JsonResponse(all_items, safe=False)

def info1(request):
    return render(request, "newinfo/info1.html")

def info2(request):
    return render(request, "newinfo/info2.html")

def info3(request):
    return render(request, "newinfo/info3.html")

def info4(request):
    return render(request, "newinfo/info4.html")

def info5(request):
    return render(request, "newinfo/info5.html")

def info6(request):
    return render(request, "newinfo/info6.html")

def info7(request):
    return render(request, "newinfo/info7.html")

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
    
    context = {
        'attraction': attraction
    }
    return render(request, "newinfo/info8.html", context)

def info9(request):
    return render(request, "newinfo/info9.html")

def info10(request):
    return render(request, "newinfo/info10.html")

def info11(request):
    return render(request, "newinfo/info11.html")

def info12(request):
    return render(request, "newinfo/info12.html")

def info13(request):
    return render(request, "newinfo/info13.html")

# def info14(request):
#     return render(request, "newinfo/info14.html")

def info15(request):
    return render(request, "newinfo/info15.html")

def info16(request):
    return render(request, "newinfo/info16.html")

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
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            time_slot = form.cleaned_data['time_slot']
            number_of_people = form.cleaned_data['number_of_people']
            
            # Check slot availability
            availability = Booking.get_slot_availability(attraction, date, time_slot)
            if number_of_people > availability['available']:
                messages.error(request, f"Sorry, only {availability['available']} slots available for this time slot.")
                return render(request, 'booking/book_slot.html', {
                    'form': form,
                    'attraction': attraction,
                    'availability': availability
                })
            
            try:
                # Create the booking
                booking = form.save(commit=False)
                booking.user = request.user
                booking.attraction = attraction
                booking.status = 'confirmed'
                booking.save()
                
                # Get updated availability for the selected date and time slot
                updated_availability = Booking.get_slot_availability(attraction, date, time_slot)
                
                messages.success(request, f'Your booking has been confirmed! {number_of_people} slots booked. {updated_availability["available"]} slots remaining.')
                return redirect('booking_confirmation', booking_id=booking.id)
                
            except Exception as e:
                messages.error(request, f"An error occurred while creating your booking: {str(e)}")
                return redirect('book_slot', attraction_id=attraction_id)
    else:
        form = BookingForm()
        # Get availability for each time slot for the current date
        selected_date = request.GET.get('date', timezone.now().date())
        availabilities = {
            'morning': Booking.get_slot_availability(attraction, selected_date, 'morning'),
            'afternoon': Booking.get_slot_availability(attraction, selected_date, 'afternoon'),
            'evening': Booking.get_slot_availability(attraction, selected_date, 'evening')
        }
    
    return render(request, 'booking/book_slot.html', {
        'form': form,
        'attraction': attraction,
        'availabilities': availabilities
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
    monuments = Monuments.objects.all()
    return render(request, 'monument.html', {'monuments': monuments})

def museums_view(request):
    museums = Museum.objects.all()
    return render(request, 'museums.html', {'museums': museums})

def events_view(request):
    events = Events.objects.all()
    return render(request, 'events.html', {'events': events})

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
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            profile = Profile(user=request.user)
        
        profile.phone_number = request.POST.get('phone_number')
        birth_date = request.POST.get('birth_date')
        if birth_date:
            profile.birth_date = birth_date
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('account')
    
    return redirect('account')