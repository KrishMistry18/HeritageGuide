import os
import json
import logging
import traceback
import datetime
import random
from collections import defaultdict
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponseNotFound, FileResponse
from django.views.decorators.csrf import csrf_exempt
from anthropic import Anthropic
from django.conf import settings
from .forms import ItineraryForm, BookingForm, SignUpForm, ProfileUpdateForm
from django.views.generic import FormView

import firebase_admin
from firebase_admin import firestore, auth as firebase_auth

logger = logging.getLogger(__name__)
_anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
anthropic_client = Anthropic(api_key=_anthropic_key) if _anthropic_key else None

def get_db():
    return firestore.client()

def firebase_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not getattr(request.user, 'is_authenticated', False):
            messages.error(request, "Please log in to access this page.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

# --- Chatbot ---
@csrf_exempt
def get_response(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            if not user_message: return JsonResponse({'error': 'Message cannot be empty'}, status=400)
            # Local Keyword-Based AI Fallback using Firestore Database
            db = get_db()
            
            # Fetch cities
            cities_ref = db.collection('cities').stream()
            cities = {doc.id: doc.to_dict().get('name', '').lower() for doc in cities_ref}
            
            # Fetch attractions
            attractions_ref = db.collection('attractions').stream()
            attractions = []
            for doc in attractions_ref:
                a = doc.to_dict()
                a['id'] = doc.id
                a['city_name'] = cities.get(a.get('city_id'), '').lower()
                attractions.append(a)
                
            user_msg_lower = user_message.lower()
            
            # 1. Greetings
            if user_msg_lower in ['hi', 'hello', 'hey', 'greetings']:
                return JsonResponse({'response': "Hello there! I'm Roamly. Which city are you planning to visit, or what kind of heritage sites are you looking for?"})
                
            # 2. Match Cities
            mentioned_cities = [name for cid, name in cities.items() if name in user_msg_lower]
            if mentioned_cities:
                city = mentioned_cities[0]
                city_attrs = [a for a in attractions if a['city_name'] == city]
                if city_attrs:
                    names = [a.get('name') for a in city_attrs[:4]]
                    return JsonResponse({'response': f"If you're visiting {city.title()}, I highly recommend checking out: {', '.join(names)}. You can search for them or view them on our map to book a slot!"})
                else:
                    return JsonResponse({'response': f"I see you're interested in {city.title()}, but we don't have any specific attractions listed there yet. Try asking about Mumbai, Delhi, or Jaipur!"})
                    
            # 3. Match Specific Attractions
            for a in attractions:
                if a.get('name', '').lower() in user_msg_lower:
                    return JsonResponse({'response': f"Ah, {a.get('name')}! It is a wonderful {a.get('type', 'place')}. It's located in {a['city_name'].title()}. You can book a slot to visit it directly through our platform!"})
                    
            # 4. Match Categories
            if 'museum' in user_msg_lower:
                museums = [a.get('name') for a in attractions if a.get('type') == 'museum'][:4]
                if museums: return JsonResponse({'response': f"We have some great museums! You should check out {', '.join(museums)}."})
            if 'monument' in user_msg_lower or 'fort' in user_msg_lower or 'palace' in user_msg_lower:
                monuments = [a.get('name') for a in attractions if a.get('type') == 'monument'][:4]
                if monuments: return JsonResponse({'response': f"If you love historical monuments, don't miss {', '.join(monuments)}!"})
                
            # 5. Fallback
            return JsonResponse({'response': "I can help you find historical monuments, museums, and cultural events. Try asking me about a specific city like 'Mumbai', 'Delhi', or 'Agra'!"})
        except Exception as e:
            return JsonResponse({'response': f"Sorry, I encountered an internal error. But as a travel bot, I'd say: Pack your bags and explore!"})
    return JsonResponse({'error': 'Invalid request'}, status=405)

def chatbot(request): return render(request, "chatbot.html")

# --- Static Pages ---
def home(request): return render(request, 'index.html')
def index(request): return render(request, 'index.html')
def info(request): return render(request, 'info.html')
def about(request): return render(request, "about.html")
def contact(request): return render(request, "contact.html")
def search(request): return render(request, 'search.html')
def map_view(request): return render(request, "map.html", {'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', '')})

from django.contrib.auth.hashers import make_password, check_password

# --- Auth ---
@csrf_exempt
def loginUser(request):
    if request.method == "POST":
        # Handle Firebase ID Token
        id_token = request.POST.get('idToken')
        email = request.POST.get('email')
        
        if id_token and email:
            try:
                firebase_auth.verify_id_token(id_token)
                db = get_db()
                user_doc = db.collection('users').document(email).get()
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    request.session['user_email'] = email
                    request.session['user_username'] = user_data.get('username', email.split('@')[0])
                    request.session['user_first_name'] = user_data.get('first_name', '')
                    request.session['user_last_name'] = user_data.get('last_name', '')
                    return JsonResponse({"status": "success"})
            except Exception as e:
                return JsonResponse({"status": "error", "message": str(e)}, status=401)
                
        # Traditional local login logic fallback (optional but good for testing)
        loginusername = request.POST.get("loginusername", "").strip()
        loginpassword = request.POST.get("loginpassword", "").strip()
        if loginusername and loginpassword:
            db = get_db()
            user_doc = db.collection('users').document(loginusername).get()
            if not user_doc.exists:
                messages.error(request, "Invalid credentials.")
                return redirect("login")
            
            user_data = user_doc.to_dict()
            if check_password(loginpassword, user_data.get('password', '')):
                request.session['user_email'] = loginusername
                request.session['user_username'] = user_data.get('username', loginusername.split('@')[0])
                messages.success(request, "Login successful!")
                return redirect("home")
            else:
                messages.error(request, "Invalid credentials.")
                return redirect("login")
            
    return render(request, "login2.html", {"google_configured": False})

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        id_token = request.POST.get('idToken')
        email = request.POST.get('email')
        if id_token and email:
            try:
                firebase_auth.verify_id_token(id_token)
                request.session['user_email'] = email
                request.session['user_username'] = email.split('@')[0]
                
                # Save to Firestore users collection
                db = get_db()
                db.collection('users').document(email).set({
                    'email': email,
                    'username': email.split('@')[0]
                })
                return JsonResponse({"status": "success"})
            except Exception as e:
                return JsonResponse({"status": "error", "message": str(e)}, status=401)
                
        form = SignUpForm(request.POST)
        if form.is_valid():
            db = get_db()
            email = form.cleaned_data['email']
            db.collection('users').document(email).set({
                'email': email,
                'username': form.cleaned_data['username'],
                'password': make_password(form.cleaned_data['password1']),
                'phone_number': form.cleaned_data.get('phone_number', ''),
                'birth_date': form.cleaned_data.get('birth_date', '').strftime('%Y-%m-%d') if form.cleaned_data.get('birth_date') else ''
            })
            messages.success(request, "Account created successfully. Please log in.")
            return redirect("login")
    else:
        form = SignUpForm()
    return render(request, 'signup3.html', {'form': form, 'google_configured': False})

def logoutUser(request):
    request.session.flush()
    messages.success(request, "You logged out successfully")
    return redirect("home")

# --- Account ---
@firebase_login_required
def account_view(request):
    db = get_db()
    email = request.user.email
    import datetime
    user_doc = db.collection('users').document(email).get().to_dict() or {}
    
    if user_doc.get('birth_date'):
        try:
            user_doc['birth_date_obj'] = datetime.datetime.strptime(user_doc['birth_date'], '%Y-%m-%d').date()
        except ValueError:
            user_doc['birth_date_obj'] = None
            
    initial_data = {
        'first_name': user_doc.get('first_name', ''),
        'last_name': user_doc.get('last_name', ''),
        'email': email,
        'phone_number': user_doc.get('phone_number', ''),
        'birth_date': user_doc.get('birth_date', '')
    }
    profile_form = ProfileUpdateForm(initial=initial_data)
    
    # Recent bookings
    bookings = []
    for b in db.collection('bookings').where('user_email', '==', email).limit(5).stream():
        b_dict = b.to_dict()
        attr_doc = db.collection('attractions').document(b_dict['attraction_id']).get()
        b_dict['attraction'] = attr_doc.to_dict() if attr_doc.exists else {'name': 'Unknown'}
        b_dict['id'] = b.id
        bookings.append(b_dict)
        
    itineraries = []
    for i in db.collection('itineraries').where('user_email', '==', email).limit(5).stream():
        i_dict = i.to_dict()
        i_dict['id'] = i.id
        itineraries.append(i_dict)
        
    return render(request, 'account.html', {
        'user': request.user,
        'profile': user_doc,
        'profile_form': profile_form,
        'recent_bookings': bookings,
        'recent_itineraries': itineraries
    })

@firebase_login_required
def update_profile(request):
    if request.method == 'POST':
        db = get_db()
        email = request.user.email
        form = ProfileUpdateForm(request.POST)
        if form.is_valid():
            db.collection('users').document(email).update({
                'first_name': form.cleaned_data.get('first_name', ''),
                'last_name': form.cleaned_data.get('last_name', ''),
                'phone_number': form.cleaned_data.get('phone_number', ''),
                'birth_date': form.cleaned_data.get('birth_date', '').strftime('%Y-%m-%d') if form.cleaned_data.get('birth_date') else ''
            })
            request.session['user_first_name'] = form.cleaned_data.get('first_name', '')
            request.session['user_last_name'] = form.cleaned_data.get('last_name', '')
            messages.success(request, "Profile updated successfully!")
        else:
            messages.error(request, "Failed to update profile. Please check your inputs.")
    return redirect("account")

# --- Attractions ---
def _attractions_view(request, attr_type, title):
    city_name = request.GET.get('city', '').strip()
    db = get_db()
    
    query = db.collection('attractions').where('type', '==', attr_type)
    attractions = [doc.to_dict() for doc in query.stream()]
    for doc, a in zip(query.stream(), attractions):
        a['id'] = doc.id
        
    cities = [{'id': doc.id, **doc.to_dict()} for doc in db.collection('cities').stream()]
    
    if city_name:
        city_id = next((c['id'] for c in cities if c['name'].lower() == city_name.lower()), None)
        if city_id:
            attractions = [a for a in attractions if a.get('city_id') == city_id]
            
    for a in attractions:
        c = next((c for c in cities if c['id'] == a.get('city_id')), None)
        a['city'] = c

    return render(request, "attractions/list.html", {
        "attractions": attractions, "title": title,
        "cities": cities, "active_city": city_name,
    })

def monuments_view(request): return _attractions_view(request, "monument", "Monuments")
def museums_view(request): return _attractions_view(request, "museum", "Museums")
def events_view(request): return _attractions_view(request, "event", "Events")

def attraction_detail(request, type, id):
    db = get_db()
    doc = db.collection('attractions').document(str(id)).get()
    if not doc.exists:
        messages.error(request, "Attraction not found.")
        return redirect('home')
    
    attraction = doc.to_dict()
    attraction['id'] = doc.id
    
    city_doc = db.collection('cities').document(attraction.get('city_id', '')).get()
    attraction['city'] = city_doc.to_dict() if city_doc.exists else None
    
    # Get related
    related = []
    if attraction.get('city_id'):
        for d in db.collection('attractions').where('city_id', '==', attraction['city_id']).limit(4).stream():
            if d.id != str(id):
                r = d.to_dict()
                r['id'] = d.id
                related.append(r)
                
    return render(request, "attractions/detail.html", {
        "attraction": attraction,
        "related_attractions": related,
    })

@firebase_login_required
def book_slot(request, attraction_id):
    db = get_db()
    doc = db.collection('attractions').document(str(attraction_id)).get()
    if not doc.exists:
        messages.error(request, "Attraction not found.")
        return redirect('home')
        
    attraction = doc.to_dict()
    attraction['id'] = doc.id
    

    
    # Fetch city
    if 'city_id' in attraction:
        city_doc = db.collection('cities').document(attraction['city_id']).get()
        attraction['city'] = city_doc.to_dict() if city_doc.exists else None

    selected_date_str = request.GET.get("date", datetime.datetime.now().strftime('%Y-%m-%d'))
    try:
        selected_date_obj = datetime.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date_obj = datetime.datetime.now().date()
        selected_date_str = selected_date_obj.strftime('%Y-%m-%d')
        
    # Convert opening and closing times to time objects if they exist
    for time_key in ['opening_time', 'closing_time']:
        if attraction.get(time_key) and isinstance(attraction[time_key], str):
            try:
                attraction[time_key] = datetime.datetime.strptime(attraction[time_key], '%H:%M:%S').time()
            except ValueError:
                pass

    # Fetch bookings for this attraction to filter in memory (avoids Firestore composite index error)
    bookings = [b.to_dict() for b in db.collection('bookings').where('attraction_id', '==', str(attraction_id)).stream()]

    def get_avail(ts):
        booked = 0
        for b in bookings:
            if b.get('date') == selected_date_str and b.get('time_slot') == ts:
                booked += b.get('number_of_people', 0)
        return {'available': max(0, 50 - booked), 'booked': booked, 'total_capacity': 50}

    availabilities = {
        "morning": get_avail("morning"),
        "afternoon": get_avail("afternoon"),
        "evening": get_avail("evening"),
    }
    
    if request.method == "POST":
        date = request.POST.get('date')
        time_slot = request.POST.get('time_slot')
        number_of_people = int(request.POST.get('number_of_people', 1))
        
        avail = get_avail(time_slot)
        if number_of_people > avail['available']:
            messages.error(request, f"Sorry, only {avail['available']} slots are available.")
            return redirect(f"{request.path}?date={date}")
            
        b_ref = db.collection('bookings').document()
        b_ref.set({
            'user_email': request.user.email,
            'attraction_id': str(attraction_id),
            'date': date,
            'time_slot': time_slot,
            'number_of_people': number_of_people,
            'status': 'confirmed'
        })
        messages.success(request, "Your booking is confirmed.")
        return redirect("booking_confirmation", booking_id=b_ref.id)
        
    form = BookingForm()
    return render(request, 'booking/book_slot.html', {
        'form': form, 'attraction': attraction, 'availabilities': availabilities, 
        "selected_date": selected_date_obj, "selected_date_str": selected_date_str
    })

@firebase_login_required
def booking_confirmation(request, booking_id):
    db = get_db()
    b_doc = db.collection('bookings').document(str(booking_id)).get()
    if not b_doc.exists:
        messages.error(request, "Booking not found.")
        return redirect('home')
        
    booking = b_doc.to_dict()
    booking['id'] = b_doc.id
    
    attr_doc = db.collection('attractions').document(booking.get('attraction_id', '')).get()
    if attr_doc.exists:
        attraction = attr_doc.to_dict()
        attraction['id'] = attr_doc.id
        if 'city_id' in attraction:
            city_doc = db.collection('cities').document(attraction['city_id']).get()
            attraction['city'] = city_doc.to_dict() if city_doc.exists else None
        booking['attraction'] = attraction
    else:
        booking['attraction'] = {'name': 'Unknown', 'id': 0, 'type': 'monument'}
        
    if 'date' in booking and isinstance(booking['date'], str):
        try:
            booking['date'] = datetime.datetime.strptime(booking['date'], '%Y-%m-%d').date()
        except ValueError:
            pass
            
    class MockBooking:
        def __init__(self, d):
            for k,v in d.items(): setattr(self, k, v)
    
    return render(request, 'booking/booking_confirmation.html', {'booking': MockBooking(booking)})

# --- API ---
def search_suggestions(request):
    query = request.GET.get('q', '').strip().lower()
    if not query: return JsonResponse([], safe=False)
    db = get_db()
    sugs = []
    for d in db.collection('attractions').stream():
        a = d.to_dict()
        if query in a.get('name', '').lower():
            sugs.append({'id': d.id, 'name': a.get('name'), 'type': a.get('type')})
    return JsonResponse(sorted(sugs, key=lambda x: x['name'])[:8], safe=False)

def all_names(request):
    db = get_db()
    sugs = [{'id': d.id, 'name': d.to_dict().get('name'), 'type': d.to_dict().get('type')} for d in db.collection('attractions').stream()]
    return JsonResponse(sorted(sugs, key=lambda x: x['name']), safe=False)

# --- Itineraries ---
class ItineraryCreateView(FormView):
    template_name = 'itinerary/create_itinerary.html'
    form_class = ItineraryForm
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        db = get_db()
        class MockCity:
            def __init__(self, id, name): self.id = id; self.name = name
        ctx['cities'] = [MockCity(d.id, d.to_dict().get('name')) for d in db.collection('cities').stream()]
        ctx['interest_choices'] = [
            ('culture', 'Culture & History'),
            ('adventure', 'Adventure'),
            ('relaxation', 'Relaxation'),
            ('food', 'Food & Cuisine'),
            ('nature', 'Nature & Wildlife'),
            ('shopping', 'Shopping'),
            ('entertainment', 'Entertainment')
        ]
        ctx['transportation_choices'] = [('car', 'Rental Car'), ('public', 'Public Transportation'), ('tour', 'Guided Tours'), ('walk', 'Walking')]
        return ctx

    def form_valid(self, form):
        if getattr(self.request.user, 'is_authenticated', False) == False:
            messages.error(self.request, "Log in first.")
            return redirect('login')
        
        db = get_db()
        i_ref = db.collection('itineraries').document()
        i_ref.set({
            'user_email': self.request.user.email,
            'name': form.cleaned_data['name'],
            'start_date': form.cleaned_data['start_date'].strftime('%Y-%m-%d'),
            'end_date': form.cleaned_data['end_date'].strftime('%Y-%m-%d'),
            'transportation_type': form.cleaned_data['transportation_type'],
            'total_budget': float(form.cleaned_data['total_budget']) if form.cleaned_data['total_budget'] else 0.0,
            'interests': form.cleaned_data['interests'],
            'created_at': datetime.datetime.now().isoformat()
        })
        return redirect('itinerary_detail', itinerary_id=i_ref.id)

def itinerary_preview(request): return redirect('home')

@firebase_login_required
def itinerary_detail(request, itinerary_id):
    db = get_db()
    i_doc = db.collection('itineraries').document(str(itinerary_id)).get()
    if not i_doc.exists: return redirect('home')
    
    itin = i_doc.to_dict()
    class MockItin:
        def __init__(self, d):
            for k,v in d.items(): setattr(self, k, v)
    
    return render(request, 'itinerary/itinerary_detail.html', {
        'itinerary': MockItin(itin),
        'days_by_city': {},
        'total_activities': 0,
        'cities_count': 1,
    })

# Info redirects
for i in range(1, 17):
    exec(f"def info{i}(request): return redirect('home')")

def view_file(request):
    file_path = request.GET.get('path')
    if '..' in file_path: return HttpResponseNotFound()
    absolute_path = os.path.join(settings.STATIC_ROOT, file_path)
    if os.path.exists(absolute_path) and os.path.isfile(absolute_path):
        return FileResponse(open(absolute_path, 'rb'))
    return HttpResponseNotFound()

@firebase_login_required
def products_view(request):
    return render(request, 'products.html', {'products': []})
