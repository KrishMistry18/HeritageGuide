from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import City, Attraction, Booking
from datetime import datetime, timedelta
import pytz

class Command(BaseCommand):
    help = 'Populates the database with attractions and sample booking data'

    def handle(self, *args, **options):
        # Create cities if they don't exist
        mumbai, _ = City.objects.get_or_create(name="Mumbai")
        delhi, _ = City.objects.get_or_create(name="Delhi")
        
        # List of attractions
        attractions_data = [
            # Mumbai Monuments
            {
                'name': 'Gateway of India',
                'city': mumbai,
                'type': 'monument',
                'info': 'An arch monument built in the 20th century, symbolizing the grandeur of Mumbai.',
                'address': 'Apollo Bandar, Colaba, Mumbai',
                'opening_time': '00:00',
                'closing_time': '23:59',
                'duration_minutes': 120,
                'rating': 4.8,
                'interest_tags': 'history,architecture,culture'
            },
            {
                'name': 'Bandra Fort',
                'city': mumbai,
                'type': 'monument',
                'info': 'Historic fort offering panoramic views of the sea and Bandra-Worli Sea Link.',
                'address': 'Bandra West, Mumbai',
                'opening_time': '09:00',
                'closing_time': '17:30',
                'duration_minutes': 90,
                'rating': 4.5,
                'interest_tags': 'history,architecture,views'
            },
            
            # Mumbai Museums
            {
                'name': 'Chhatrapati Shivaji Maharaj Vastu Sangrahalaya',
                'city': mumbai,
                'type': 'museum',
                'info': 'Former Prince of Wales Museum showcasing Indian history and culture.',
                'address': 'Mahatma Gandhi Road, Fort, Mumbai',
                'opening_time': '10:00',
                'closing_time': '18:00',
                'duration_minutes': 180,
                'rating': 4.7,
                'interest_tags': 'history,art,culture'
            },
            {
                'name': 'Dr. Bhau Daji Lad Museum',
                'city': mumbai,
                'type': 'museum',
                'info': "Mumbai's oldest museum featuring city history and decorative arts.",
                'address': 'Byculla East, Mumbai',
                'opening_time': '10:00',
                'closing_time': '18:00',
                'duration_minutes': 120,
                'rating': 4.4,
                'interest_tags': 'history,art,culture'
            },
            
            # Delhi Monuments
            {
                'name': 'Red Fort',
                'city': delhi,
                'type': 'monument',
                'info': 'Historic fort complex built in the 17th century.',
                'address': 'Netaji Subhash Marg, Chandni Chowk, Delhi',
                'opening_time': '09:30',
                'closing_time': '16:30',
                'duration_minutes': 180,
                'rating': 4.8,
                'interest_tags': 'history,architecture,culture'
            },
            {
                'name': 'Qutub Minar',
                'city': delhi,
                'type': 'monument',
                'info': 'UNESCO World Heritage site featuring a 73-meter tall minaret.',
                'address': 'Mehrauli, New Delhi',
                'opening_time': '07:00',
                'closing_time': '17:00',
                'duration_minutes': 120,
                'rating': 4.7,
                'interest_tags': 'history,architecture,culture'
            },
            
            # Delhi Museums
            {
                'name': 'National Museum',
                'city': delhi,
                'type': 'museum',
                'info': 'Premier cultural institution housing diverse collections.',
                'address': 'Janpath Road, New Delhi',
                'opening_time': '10:00',
                'closing_time': '18:00',
                'duration_minutes': 240,
                'rating': 4.6,
                'interest_tags': 'history,art,culture'
            },
            {
                'name': 'National Gallery of Modern Art',
                'city': delhi,
                'type': 'museum',
                'info': 'Houses and showcases modern and contemporary Indian art.',
                'address': 'Jaipur House, India Gate, New Delhi',
                'opening_time': '11:00',
                'closing_time': '18:00',
                'duration_minutes': 180,
                'rating': 4.5,
                'interest_tags': 'art,culture,modern'
            },
            
            # Events in Mumbai
            {
                'name': 'Kala Ghoda Arts Festival',
                'city': mumbai,
                'type': 'event',
                'info': 'Annual arts and cultural festival in February.',
                'address': 'Kala Ghoda, Fort, Mumbai',
                'opening_time': '10:00',
                'closing_time': '22:00',
                'duration_minutes': 720,
                'rating': 4.9,
                'interest_tags': 'art,culture,festival'
            },
            {
                'name': 'Mumbai Film Festival',
                'city': mumbai,
                'type': 'event',
                'info': 'International film festival showcasing world cinema.',
                'address': 'Various locations in Mumbai',
                'opening_time': '09:00',
                'closing_time': '23:00',
                'duration_minutes': 840,
                'rating': 4.8,
                'interest_tags': 'film,culture,entertainment'
            }
        ]

        # Create attractions
        created_attractions = []
        for data in attractions_data:
            attraction, created = Attraction.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            created_attractions.append(attraction)
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f"{status}: {attraction.name}")

        # Create sample bookings
        # First, ensure we have a test user
        test_user, created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@example.com',
                'is_active': True
            }
        )
        if created:
            test_user.set_password('test123')
            test_user.save()

        # Create some sample bookings
        today = datetime.now(pytz.UTC).date()
        time_slots = ['morning', 'afternoon', 'evening']
        
        for attraction in created_attractions[:3]:  # Create bookings for first 3 attractions
            for days_ahead in range(7):  # Create bookings for next 7 days
                booking_date = today + timedelta(days=days_ahead)
                for slot in time_slots:
                    # Create a booking with random number of people
                    Booking.objects.get_or_create(
                        user=test_user,
                        attraction=attraction,
                        date=booking_date,
                        time_slot=slot,
                        defaults={
                            'number_of_people': 2,
                            'status': 'confirmed'
                        }
                    )

        self.stdout.write(self.style.SUCCESS('Successfully populated database with attractions and bookings')) 