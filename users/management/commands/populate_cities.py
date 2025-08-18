from django.core.management.base import BaseCommand
from users.models import City

class Command(BaseCommand):
    help = 'Populates the database with Mumbai, Chennai, Hyderabad, and Gujarat cities'

    def handle(self, *args, **options):
        # List of cities with their descriptions
        cities_data = [
            {
                'name': 'Mumbai',
                'description': 'The financial capital of India, known for its vibrant culture, Bollywood, and historic landmarks.'
            },
            {
                'name': 'Chennai',
                'description': 'The cultural capital of South India, famous for its temples, beaches, and traditional arts.'
            },
            {
                'name': 'Hyderabad',
                'description': 'The City of Pearls, known for its rich history, iconic Charminar, and delicious biryani.'
            },
            {
                'name': 'Gujarat',
                'description': 'A state with rich cultural heritage, known for its diverse landscapes and historical sites.'
            }
        ]

        # Create or update cities
        for city_data in cities_data:
            city, created = City.objects.get_or_create(
                name=city_data['name'],
                defaults={'description': city_data['description']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully created city "{city.name}"'))
            else:
                city.description = city_data['description']
                city.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully updated city "{city.name}"')) 