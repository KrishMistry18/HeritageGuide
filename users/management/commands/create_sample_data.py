from django.core.management.base import BaseCommand
from users.models import City, Attraction
from django.utils import timezone

class Command(BaseCommand):
    help = 'Creates sample attractions and cities'

    def handle(self, *args, **kwargs):
        # Create cities
        mumbai, _ = City.objects.get_or_create(
            name='Mumbai',
            defaults={
                'description': 'The financial capital of India, known for its vibrant culture and entertainment.'
            }
        )
        
        hyderabad, _ = City.objects.get_or_create(
            name='Hyderabad',
            defaults={
                'description': 'The City of Pearls, known for its rich history and iconic monuments.'
            }
        )
        
        chennai, _ = City.objects.get_or_create(
            name='Chennai',
            defaults={
                'description': 'The cultural capital of South India, known for its temples and beaches.'
            }
        )
        
        gujarat, _ = City.objects.get_or_create(
            name='Gujarat',
            defaults={
                'description': 'Known for its vibrant culture, festivals, and historical monuments.'
            }
        )
        
        # Create sample attractions
        attractions = [
            {
                'name': 'Bandra Fort',
                'type': 'monument',
                'info': 'Bandra Fort, also known as Castella de Aguada, is a historic Portuguese fort in Mumbai.',
                'address': 'Bandra West, Mumbai',
                'opening_time': timezone.now().replace(hour=6, minute=0),
                'closing_time': timezone.now().replace(hour=18, minute=0),
                'duration_minutes': 60,
                'rating': 4.2,
                'interest_tags': 'culture,history,architecture',
                'city': mumbai
            },
            {
                'name': 'Birla Planetarium',
                'type': 'museum',
                'info': 'Birla Planetarium is a renowned space and astronomy center in India, offering interactive exhibits and immersive sky shows.',
                'address': 'Hyderabad',
                'opening_time': timezone.now().replace(hour=10, minute=30),
                'closing_time': timezone.now().replace(hour=20, minute=0),
                'duration_minutes': 120,
                'rating': 4.5,
                'interest_tags': 'science,education,entertainment',
                'city': hyderabad
            },
            {
                'name': 'Salar Jung Museum',
                'type': 'museum',
                'info': 'The Salar Jung Museum in Hyderabad is renowned for housing one of the world\'s largest collections of antiques.',
                'address': 'Hyderabad',
                'opening_time': timezone.now().replace(hour=10, minute=0),
                'closing_time': timezone.now().replace(hour=17, minute=0),
                'duration_minutes': 180,
                'rating': 4.7,
                'interest_tags': 'culture,history,art',
                'city': hyderabad
            },
            {
                'name': 'Chowmahalla Palace',
                'type': 'monument',
                'info': 'A grand 18th-century palace in Hyderabad showcasing exquisite Persian, Indo-Saracenic, and European architectural styles.',
                'address': 'Hyderabad',
                'opening_time': timezone.now().replace(hour=9, minute=0),
                'closing_time': timezone.now().replace(hour=17, minute=0),
                'duration_minutes': 120,
                'rating': 4.6,
                'interest_tags': 'culture,history,architecture',
                'city': hyderabad
            },
            {
                'name': 'Valluvar Kottam',
                'type': 'monument',
                'info': 'A monument in Chennai dedicated to the Tamil poet and philosopher Thiruvalluvar.',
                'address': 'Chennai',
                'opening_time': timezone.now().replace(hour=8, minute=0),
                'closing_time': timezone.now().replace(hour=18, minute=0),
                'duration_minutes': 90,
                'rating': 4.3,
                'interest_tags': 'culture,history,architecture',
                'city': chennai
            },
            {
                'name': 'Fort St George',
                'type': 'monument',
                'info': 'The first British fortress in India, established in 1644.',
                'address': 'Chennai',
                'opening_time': timezone.now().replace(hour=9, minute=0),
                'closing_time': timezone.now().replace(hour=17, minute=0),
                'duration_minutes': 150,
                'rating': 4.4,
                'interest_tags': 'history,culture,architecture',
                'city': chennai
            },
            {
                'name': 'Rani Ki Vav',
                'type': 'monument',
                'info': 'An intricately carved stepwell in Gujarat, built in the 11th century.',
                'address': 'Patan, Gujarat',
                'opening_time': timezone.now().replace(hour=8, minute=0),
                'closing_time': timezone.now().replace(hour=18, minute=0),
                'duration_minutes': 120,
                'rating': 4.8,
                'interest_tags': 'culture,history,architecture',
                'city': gujarat
            },
            {
                'name': 'Vijay Vilas Palace',
                'type': 'monument',
                'info': 'An exquisite summer palace built in the 1920s by Maharao Vijayrajji of Kutch.',
                'address': 'Mandvi, Gujarat',
                'opening_time': timezone.now().replace(hour=9, minute=0),
                'closing_time': timezone.now().replace(hour=17, minute=0),
                'duration_minutes': 90,
                'rating': 4.5,
                'interest_tags': 'culture,history,architecture',
                'city': gujarat
            }
        ]

        for attraction_data in attractions:
            city = attraction_data.pop('city')
            Attraction.objects.get_or_create(
                name=attraction_data['name'],
                defaults={
                    **attraction_data,
                    'city': city
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully created sample data')) 