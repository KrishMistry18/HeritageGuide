"""
Management command: setup_4cities
- Removes Delhi and Ahmedabad cities (and their attractions)
- Adds full attraction data for Chennai, Hyderabad, Gujarat
- Assigns existing media images to attractions
"""
from django.core.management.base import BaseCommand
from users.models import City, Attraction, AttractionType
from datetime import time
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# Images are in static/heritage-images/ (committed to git, works on Vercel)
STATIC_IMG = os.path.join(BASE_DIR, 'static', 'heritage-images')
# Fallback to old media path for local dev
MEDIA_IMG = os.path.join(BASE_DIR, 'media', 'users', 'images')


def img(filename):
    """Return full path to an image file — checks static first, then media."""
    static_path = os.path.join(STATIC_IMG, filename)
    if os.path.exists(static_path):
        return static_path
    return os.path.join(MEDIA_IMG, filename)


class Command(BaseCommand):
    help = 'Set up the 4 target cities: Mumbai, Chennai, Hyderabad, Gujarat'

    def handle(self, *args, **options):
        # ── 1. Remove unwanted cities ──────────────────────────────────────
        for name in ['Delhi', 'Ahmedabad']:
            deleted, _ = City.objects.filter(name=name).delete()
            if deleted:
                self.stdout.write(f'Removed city: {name}')

        # ── 2. Ensure the 4 target cities exist ───────────────────────────
        mumbai, _    = City.objects.get_or_create(name='Mumbai',    defaults={'description': 'The financial capital of India and home to Bollywood'})
        chennai, _   = City.objects.get_or_create(name='Chennai',   defaults={'description': 'The cultural capital of South India, known as the Gateway to South India'})
        hyderabad, _ = City.objects.get_or_create(name='Hyderabad', defaults={'description': 'The City of Pearls, blending Mughal heritage with modern tech'})
        gujarat, _   = City.objects.get_or_create(name='Gujarat',   defaults={'description': 'Land of legends, vibrant culture, and ancient stepwells'})

        # ── 3. Chennai attractions ─────────────────────────────────────────
        chennai_data = [
            dict(name='Fort St. George', type=AttractionType.MONUMENT,
                 info='Fort St. George is a historic British East India Company fortress built in 1644 in Chennai (formerly Madras). It was the first English fortress in India and now houses the Tamil Nadu Legislative Assembly.',
                 address='Rajaji Salai, Chennai, Tamil Nadu 600009',
                 opening_time=time(9,0), closing_time=time(17,0),
                 rating=4.3, duration_minutes=120,
                 interest_tags='history,architecture,colonial',
                 reviews='Fascinating piece of colonial history. The museum inside is excellent.',
                 image_file='Fort_St._George_.jpeg'),
            dict(name='Kapaleeshwarar Temple', type=AttractionType.MONUMENT,
                 info='Kapaleeshwarar Temple is a Hindu temple dedicated to Lord Shiva, located in Mylapore, Chennai. Built in the Dravidian style of architecture, it is one of the most famous temples in Tamil Nadu.',
                 address='Mylapore, Chennai, Tamil Nadu 600004',
                 opening_time=time(5,45), closing_time=time(21,0),
                 rating=4.6, duration_minutes=90,
                 interest_tags='culture,religion,architecture',
                 reviews='Stunning Dravidian architecture. A must-visit for anyone in Chennai.',
                 image_file='Kapaleeshwarar_Temple_.jpeg'),
            dict(name='San Thome Basilica', type=AttractionType.MONUMENT,
                 info='San Thome Basilica is a Roman Catholic minor basilica built over the tomb of St. Thomas the Apostle. Originally built by Portuguese explorers in the 16th century, the current neo-Gothic structure was built in 1896.',
                 address='San Thome High Road, Mylapore, Chennai, Tamil Nadu 600004',
                 opening_time=time(6,0), closing_time=time(20,0),
                 rating=4.5, duration_minutes=60,
                 interest_tags='religion,history,architecture',
                 reviews='Beautiful Gothic church with deep historical significance.',
                 image_file='San_Thome_Basilica_.jpeg'),
            dict(name='Valluvar Kottam', type=AttractionType.MONUMENT,
                 info='Valluvar Kottam is a monument in Chennai dedicated to the classical Tamil poet Thiruvalluvar. Built in 1976, it features a chariot-shaped structure and an auditorium that can seat 4,000 people.',
                 address='Village Road, Nungambakkam, Chennai, Tamil Nadu 600034',
                 opening_time=time(8,30), closing_time=time(20,30),
                 rating=4.1, duration_minutes=60,
                 interest_tags='culture,history,literature',
                 reviews='Impressive monument celebrating Tamil literary heritage.',
                 image_file='Valluvar_Kottam.jpeg'),
            dict(name='DakshinaChitra', type=AttractionType.MUSEUM,
                 info='DakshinaChitra is a living-history museum that showcases the art, architecture, crafts, and performing arts of South India. It features authentic houses from Tamil Nadu, Kerala, Karnataka, and Andhra Pradesh.',
                 address='East Coast Road, Muttukadu, Chennai, Tamil Nadu 603112',
                 opening_time=time(10,0), closing_time=time(18,0),
                 rating=4.4, duration_minutes=180,
                 interest_tags='culture,art,architecture',
                 reviews='Wonderful museum showcasing South Indian heritage. Very well maintained.',
                 image_file='DakshinaChitra.jpeg'),
            dict(name='Chennai Rail Museum', type=AttractionType.MUSEUM,
                 info='The Chennai Rail Museum preserves the glory of Indian Railways with a collection of vintage locomotives, royal saloons, and railway memorabilia dating back to the 19th century.',
                 address='Near ICF Colony, Ayanavaram, Chennai, Tamil Nadu 600023',
                 opening_time=time(9,30), closing_time=time(17,0),
                 rating=4.2, duration_minutes=120,
                 interest_tags='history,technology,family',
                 reviews='Great place for railway enthusiasts and families. Vintage engines are impressive.',
                 image_file='Chennai_Rail_Museum__Preserving_the_Glory_of_Indian_Railways.JPG'),
            dict(name='Government Museum Chennai', type=AttractionType.MUSEUM,
                 info='The Government Museum in Chennai is one of the oldest museums in India, established in 1851. It houses an extensive collection of archaeological, numismatic, and natural history exhibits.',
                 address='Pantheon Road, Egmore, Chennai, Tamil Nadu 600008',
                 opening_time=time(9,30), closing_time=time(17,0),
                 rating=4.0, duration_minutes=150,
                 interest_tags='history,archaeology,art',
                 reviews='Excellent collection of South Indian bronzes and archaeological finds.',
                 image_file='State_government_museum.jpeg'),
        ]

        # ── 4. Hyderabad attractions ───────────────────────────────────────
        hyderabad_data = [
            dict(name='Charminar', type=AttractionType.MONUMENT,
                 info='The Charminar is a monument and mosque built in 1591 by Muhammad Quli Qutb Shah. It is the most recognised structure in Hyderabad and a symbol of the city, featuring four grand arches and minarets.',
                 address='Charminar Road, Char Kaman, Hyderabad, Telangana 500002',
                 opening_time=time(9,30), closing_time=time(17,30),
                 rating=4.5, duration_minutes=90,
                 interest_tags='history,architecture,mughal',
                 reviews='Iconic landmark of Hyderabad. The surrounding bazaar is equally fascinating.',
                 image_file='Charminar.jpg'),
            dict(name='Golconda Fort', type=AttractionType.MONUMENT,
                 info='Golconda Fort is a magnificent ruined fort and former capital of the medieval Sultanate of Golconda. Built in the 16th century, it is famous for its acoustic system, palaces, and the famous Fateh Darwaza.',
                 address='Ibrahim Bagh, Hyderabad, Telangana 500008',
                 opening_time=time(8,0), closing_time=time(17,30),
                 rating=4.6, duration_minutes=180,
                 interest_tags='history,architecture,fort',
                 reviews='Spectacular fort with amazing acoustics. The sound and light show is a must-see.',
                 image_file='Golkonda_fort.jpeg'),
            dict(name='Chowmahalla Palace', type=AttractionType.MONUMENT,
                 info='Chowmahalla Palace was the official residence of the Nizams of Hyderabad. Built in the 18th and 19th centuries, it showcases a blend of Persian, Indo-Saracenic, and European architectural styles.',
                 address='20-4-236, Motigalli, Khilwat, Hyderabad, Telangana 500002',
                 opening_time=time(10,0), closing_time=time(17,0),
                 rating=4.4, duration_minutes=120,
                 interest_tags='history,architecture,nizam',
                 reviews='Stunning palace with beautiful architecture and well-preserved interiors.',
                 image_file='Chowmahalla_Palace.jpeg'),
            dict(name='Qutb Shahi Tombs', type=AttractionType.MONUMENT,
                 info='The Qutb Shahi Tombs are a group of monuments containing the tombs of the seven Qutb Shahi rulers of Golconda. Built between the 16th and 17th centuries, they represent a unique blend of Persian, Pathan, and Hindu architectural styles.',
                 address='Ibrahim Bagh, Hyderabad, Telangana 500008',
                 opening_time=time(9,30), closing_time=time(17,30),
                 rating=4.3, duration_minutes=90,
                 interest_tags='history,architecture,mughal',
                 reviews='Beautifully restored tombs with impressive domes and intricate carvings.',
                 image_file='Qutub_Shahi_tombs.jpeg'),
            dict(name='Salar Jung Museum', type=AttractionType.MUSEUM,
                 info='The Salar Jung Museum is one of the largest museums in India, housing an extraordinary collection of over 43,000 artifacts gathered by Mir Yousuf Ali Khan (Salar Jung III). It features antiques from India, Europe, the Middle East, and Japan.',
                 address='Salar Jung Museum Road, Darulshifa, Hyderabad, Telangana 500002',
                 opening_time=time(10,0), closing_time=time(17,0),
                 rating=4.5, duration_minutes=180,
                 interest_tags='art,history,culture',
                 reviews='Incredible collection of artifacts from around the world. The Veiled Rebecca is breathtaking.',
                 image_file='Salar_Jung_Museum_.jpeg'),
            dict(name="Nizam's Museum", type=AttractionType.MUSEUM,
                 info="The Nizam's Museum is housed in the Purani Haveli palace and showcases the personal collection of the last Nizam of Hyderabad. It features a remarkable collection of gifts, jewellery, and personal effects.",
                 address='Purani Haveli, Hyderabad, Telangana 500002',
                 opening_time=time(10,0), closing_time=time(17,0),
                 rating=4.2, duration_minutes=90,
                 interest_tags='history,royalty,culture',
                 reviews='Fascinating glimpse into the opulent lifestyle of the Nizams.',
                 image_file='Nizams_Museum_.jpeg'),
            dict(name='Taramati Baradari', type=AttractionType.MONUMENT,
                 info='Taramati Baradari is a 17th-century cultural pavilion built by Abdullah Qutb Shah for his court dancer Taramati. It is a beautiful example of Qutb Shahi architecture and now serves as a cultural venue.',
                 address='Ibrahim Bagh, Hyderabad, Telangana 500008',
                 opening_time=time(9,0), closing_time=time(18,0),
                 rating=4.1, duration_minutes=60,
                 interest_tags='history,architecture,culture',
                 reviews='Beautiful heritage structure with a romantic history. Great for evening visits.',
                 image_file='Taramati_Baradari__The_Cultural_Pavilion.jpeg'),
        ]

        # ── 5. Gujarat attractions ─────────────────────────────────────────
        gujarat_data = [
            dict(name='Rani Ki Vav', type=AttractionType.MONUMENT,
                 info='Rani Ki Vav (The Queen\'s Stepwell) is an intricately carved stepwell located in Patan, Gujarat. Built in the 11th century by Queen Udayamati in memory of her husband, it is a UNESCO World Heritage Site.',
                 address='Patan, Gujarat 384265',
                 opening_time=time(8,0), closing_time=time(18,0),
                 rating=4.8, duration_minutes=120,
                 interest_tags='history,architecture,UNESCO',
                 reviews='Absolutely stunning UNESCO World Heritage Site. The carvings are incredibly detailed.',
                 image_file='Rani_Ki_Vav__The_Queens_Stepwell_Patan.jpeg'),
            dict(name='Modhera Sun Temple', type=AttractionType.MONUMENT,
                 info='The Modhera Sun Temple is a Hindu temple dedicated to the sun god Surya, built in 1026 CE by King Bhimdev I of the Solanki dynasty. It is one of the finest examples of Solanki-style architecture.',
                 address='Modhera, Mehsana, Gujarat 384212',
                 opening_time=time(7,0), closing_time=time(18,0),
                 rating=4.7, duration_minutes=120,
                 interest_tags='history,architecture,religion',
                 reviews='Magnificent temple with exquisite carvings. The dance festival held here is spectacular.',
                 image_file='Modhera_Sun_Temple__A_Shrine_Dedicated_to_Surya.jpeg'),
            dict(name='Vijay Vilas Palace', type=AttractionType.MONUMENT,
                 info='Vijay Vilas Palace is an exquisite summer residence built in the 1920s by Maharao Vijayraiji of Kutch. The palace blends Rajput and European architectural styles and is surrounded by beautiful gardens.',
                 address='Mandvi, Kutch, Gujarat 370465',
                 opening_time=time(9,0), closing_time=time(18,0),
                 rating=4.3, duration_minutes=90,
                 interest_tags='history,architecture,royalty',
                 reviews='Beautiful palace with stunning architecture and a private beach nearby.',
                 image_file='Vijay_vilas_palace.jpeg'),
            dict(name='Dwarkadhish Temple', type=AttractionType.MONUMENT,
                 info='The Dwarkadhish Temple, also known as Jagat Mandir, is a Hindu temple dedicated to Lord Krishna. It is one of the Char Dham pilgrimage sites and is believed to have been built over 2,500 years ago.',
                 address='Dwarka, Gujarat 361335',
                 opening_time=time(6,0), closing_time=time(21,0),
                 rating=4.6, duration_minutes=90,
                 interest_tags='religion,history,culture',
                 reviews='Sacred and beautiful temple. The architecture is magnificent and the atmosphere divine.',
                 image_file='Dwarkadhish_Temple_.jpeg'),
            dict(name='Kutch Museum', type=AttractionType.MUSEUM,
                 info='The Kutch Museum in Bhuj is the oldest museum in Gujarat, established in 1877. It houses an extensive collection of Kutchi textiles, jewellery, weapons, and archaeological finds.',
                 address='Museum Road, Bhuj, Kutch, Gujarat 370001',
                 opening_time=time(10,0), closing_time=time(17,30),
                 rating=4.1, duration_minutes=90,
                 interest_tags='culture,art,history',
                 reviews='Excellent collection of Kutchi crafts and artefacts. A must-visit in Bhuj.',
                 image_file='Kutch_Museum_.jpeg'),
            dict(name='Gujarat Science City', type=AttractionType.MUSEUM,
                 info='Gujarat Science City is one of the largest science centres in Asia, located in Ahmedabad. It features interactive exhibits, an IMAX theatre, a robotics gallery, and an energy park.',
                 address='Science City Road, Sola, Ahmedabad, Gujarat 380060',
                 opening_time=time(10,0), closing_time=time(19,0),
                 rating=4.4, duration_minutes=240,
                 interest_tags='science,technology,family',
                 reviews='Fantastic science museum with interactive exhibits. Great for families and students.',
                 image_file='Gujarat_Science_City_.jpeg'),
            dict(name='Sardar Vallabhbhai Patel National Museum', type=AttractionType.MUSEUM,
                 info='The Sardar Vallabhbhai Patel National Museum in Vadodara is dedicated to the Iron Man of India. It houses personal memorabilia, photographs, and documents related to Sardar Patel\'s life and the Indian independence movement.',
                 address='Sayajigunj, Vadodara, Gujarat 390005',
                 opening_time=time(10,0), closing_time=time(17,0),
                 rating=4.0, duration_minutes=90,
                 interest_tags='history,independence,culture',
                 reviews='Informative museum about a great Indian leader. Well-curated exhibits.',
                 image_file='Sardar_Vallabhbhai_Patel_National_Museum_.jpeg'),
        ]

        # ── 6. Mumbai — assign images to existing attractions ─────────────
        mumbai_images = {
            'Bandra Fort':                              'Castella_del_aguada.jpg',
            'Gateway of India':                         'Gateway_of_India.jpg',
            'Elephanta Caves':                          'elephantalcaves.jpg',
            'Haji Ali Dargah':                          'Haji_Ali_Dargah.jpg',
            'Chhatrapati Shivaji Maharaj Vastu Sangrahalaya': 'Shivaji_maharaj_sanghralaye.jpg',
            'Dr. Bhau Daji Lad Museum':                 'Dr.Bhau_Daji_Lad_Museum.jpeg',
            'Nehru Science Centre':                     'Nehru_Science_centre.jpeg',
            'Mani Bhavan Gandhi Museum':                'Mani_Bhavan_Gandhi_Museum.jpeg',
        }
        for name, fname in mumbai_images.items():
            qs = Attraction.objects.filter(name=name, city=mumbai)
            if qs.exists():
                a = qs.first()
                if not a.image:
                    a.image = f'heritage-images/{fname}'
                    a.save(update_fields=['image'])
                    self.stdout.write(f'  Image set for Mumbai: {name}')

        # ── 7. Create/update Chennai, Hyderabad, Gujarat attractions ──────
        for city, data_list in [(chennai, chennai_data), (hyderabad, hyderabad_data), (gujarat, gujarat_data)]:
            for d in data_list:
                fname = d.pop('image_file')
                d['city'] = city
                a, created = Attraction.objects.get_or_create(
                    name=d['name'],
                    defaults={k: v for k, v in d.items() if k != 'name'}
                )
                if not created:
                    for k, v in d.items():
                        if k != 'name':
                            setattr(a, k, v)
                    a.save()

                # Set image path directly (images are in static/heritage-images/)
                if not a.image:
                    a.image = f'heritage-images/{fname}'
                    a.save(update_fields=['image'])

                action = 'Created' if created else 'Updated'
                self.stdout.write(f'  {action}: {city.name} — {a.name}')

        self.stdout.write(self.style.SUCCESS('\nDone! 4 cities set up with attractions and images.'))

