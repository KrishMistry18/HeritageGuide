from django.core.management.base import BaseCommand
from users.models import Attraction, City, AttractionType
from datetime import time

class Command(BaseCommand):
    help = 'Populates the database with all attractions'

    def handle(self, *args, **options):
        # Create or get cities
        mumbai, _ = City.objects.get_or_create(
            name='Mumbai',
            defaults={'description': 'The financial capital of India and home to Bollywood'}
        )
        delhi, _ = City.objects.get_or_create(
            name='Delhi',
            defaults={'description': 'The capital city of India with rich historical heritage'}
        )

        # Mumbai Monuments
        mumbai_monuments = [
            {
                'name': 'Bandra Fort',
                'info': 'Castella de Aguada, commonly known as Bandra Fort, is a historic Portuguese fort located at Land\'s End in Bandra, Mumbai. Built in 1640, this strategic watchtower was designed to overlook Mahim Bay, the Arabian Sea, and the southern island of Mahim.',
                'address': 'Byramji Jeejeebhoy Road, Bandra West, Mumbai, Maharashtra 400050',
                'opening_time': time(6, 0),
                'closing_time': time(18, 30),
                'reviews': 'Historic fort with beautiful sea views. Perfect for sunset watching and photography.',
                'type': AttractionType.MONUMENT,
                'city': mumbai
            },
            {
                'name': 'Gateway of India',
                'info': 'The Gateway of India is an arch-monument built in the early 20th century in the city of Mumbai. It was erected to commemorate the landing of King-Emperor George V and Queen-Empress Mary at Apollo Bunder when they visited India in 1911.',
                'address': 'Apollo Bandar, Colaba, Mumbai, Maharashtra 400001',
                'opening_time': time(0, 0),
                'closing_time': time(23, 59),
                'reviews': 'Must-visit landmark of Mumbai. Beautiful architecture and historical significance. Perfect for photos and experiencing the city\'s heritage.',
                'type': AttractionType.MONUMENT,
                'city': mumbai
            },
            {
                'name': 'Chhatrapati Shivaji Terminus',
                'info': 'A historic railway station and UNESCO World Heritage site that serves as the headquarters of the Central Railways. Built in 1888, it is a perfect example of Victorian Gothic architecture in India.',
                'address': 'Chhatrapati Shivaji Terminus Area, Fort, Mumbai, Maharashtra 400001',
                'opening_time': time(0, 0),
                'closing_time': time(23, 59),
                'reviews': 'Magnificent architecture, bustling with life 24/7. One of Mumbai\'s most iconic landmarks.',
                'type': AttractionType.MONUMENT,
                'city': mumbai
            },
            {
                'name': 'Elephanta Caves',
                'info': 'The Elephanta Caves are a UNESCO World Heritage Site and a collection of cave temples predominantly dedicated to the Hindu god Shiva. Located on Elephanta Island in Mumbai Harbour.',
                'address': 'Elephanta Island, Mumbai Harbour',
                'opening_time': time(9, 30),
                'closing_time': time(16, 0),
                'reviews': 'Ancient cave temples with remarkable sculptures. A must-visit for history and art enthusiasts.',
                'type': AttractionType.MONUMENT,
                'city': mumbai
            },
            {
                'name': 'Haji Ali Dargah',
                'info': 'Haji Ali Dargah is one of the most popular religious places in Mumbai. This monument was constructed in 1431 and is dedicated to Sayyed Peer Haji Ali Shah Bukhari.',
                'address': 'Dargah Road, Haji Ali, Mumbai, Maharashtra 400026',
                'opening_time': time(5, 30),
                'closing_time': time(18, 0),
                'reviews': 'Beautiful mosque in the middle of the sea. Amazing architecture and peaceful atmosphere.',
                'type': AttractionType.MONUMENT,
                'city': mumbai
            },
            {
                'name': 'Siddhivinayak Temple',
                'info': 'The Shree Siddhivinayak Ganapati Mandir is a Hindu temple dedicated to Lord Ganesha. It was built in 1801 and is one of the richest temples in Mumbai.',
                'address': 'SK Bole Marg, Prabhadevi, Mumbai, Maharashtra 400028',
                'opening_time': time(5, 30),
                'closing_time': time(18, 0),
                'reviews': 'One of the most famous Ganesh temples. Beautiful architecture and divine atmosphere.',
                'type': AttractionType.MONUMENT,
                'city': mumbai
            }
        ]

        # Create Delhi monuments
        delhi_monuments = [
            {
                'name': 'Red Fort',
                'info': 'The Red Fort is a historic fortress built in the 17th century by Mughal Emperor Shah Jahan. It served as the main residence of Mughal Emperors and is now a UNESCO World Heritage Site.',
                'address': 'Netaji Subhash Marg, Lal Qila, Chandni Chowk, New Delhi, Delhi 110006',
                'opening_time': time(9, 30),
                'closing_time': time(17, 0),
                'reviews': 'Magnificent Mughal architecture. The light and sound show in the evening is spectacular.',
                'type': AttractionType.MONUMENT,
                'city': delhi
            },
            {
                'name': 'Qutub Minar',
                'info': 'A UNESCO World Heritage Site, Qutub Minar is a 73-meter tall minaret built in the 12th century. It is surrounded by several historically significant monuments.',
                'address': 'Mehrauli, New Delhi, Delhi 110030',
                'opening_time': time(7, 0),
                'closing_time': time(17, 0),
                'reviews': 'Incredible piece of history with beautiful architecture. The complex is well-maintained and informative.',
                'type': AttractionType.MONUMENT,
                'city': delhi
            },
            {
                'name': 'India Gate',
                'info': 'India Gate is a war memorial dedicated to the soldiers of the British Indian Army who died in the First World War. Built in 1931, it\'s one of Delhi\'s most iconic landmarks.',
                'address': 'Rajpath, India Gate, New Delhi, Delhi 110001',
                'opening_time': time(0, 0),
                'closing_time': time(23, 59),
                'reviews': 'Beautiful memorial, especially stunning at night. Popular spot for evening visits.',
                'type': AttractionType.MONUMENT,
                'city': delhi
            },
            {
                'name': 'Humayun\'s Tomb',
                'info': 'Humayun\'s Tomb is a UNESCO World Heritage Site. Built in 1570, this tomb is of particular cultural significance as it was the first garden-tomb on the Indian subcontinent.',
                'address': 'Mathura Road, Nizamuddin, New Delhi, Delhi 110013',
                'opening_time': time(6, 0),
                'closing_time': time(18, 0),
                'reviews': 'Beautiful Mughal architecture with well-maintained gardens. A must-visit historical site.',
                'type': AttractionType.MONUMENT,
                'city': delhi
            },
            {
                'name': 'Lotus Temple',
                'info': 'The Lotus Temple is a Bahai House of Worship, notable for its flower-like shape. It was completed in 1986 and serves as the Mother Temple of the Indian subcontinent.',
                'address': 'Lotus Temple Road, Bahapur, New Delhi, Delhi 110019',
                'opening_time': time(9, 0),
                'closing_time': time(17, 0),
                'reviews': 'Stunning architecture and peaceful atmosphere. Beautiful both during day and when lit up at night.',
                'type': AttractionType.MONUMENT,
                'city': delhi
            }
        ]

        # Create Mumbai Museums
        mumbai_museums = [
            {
                'name': 'Chhatrapati Shivaji Maharaj Vastu Sangrahalaya',
                'info': 'Formerly known as the Prince of Wales Museum, this museum is one of the largest and most important in India. It houses over 50,000 artifacts.',
                'address': 'Mahatma Gandhi Road, Fort, Mumbai, Maharashtra 400001',
                'opening_time': time(10, 15),
                'closing_time': time(18, 0),
                'reviews': 'Excellent collection of Indian history and art. The building itself is an architectural marvel.',
                'type': AttractionType.MUSEUM,
                'city': mumbai
            },
            {
                'name': 'Dr. Bhau Daji Lad Museum',
                'info': 'Mumbai\'s oldest museum showcasing the city\'s cultural heritage. Features decorative and industrial arts, as well as artifacts about Mumbai\'s history.',
                'address': 'Veer Mata Jijabai Bhosale Udyan, Dr Baba Saheb Ambedkar Road, Byculla East',
                'opening_time': time(10, 0),
                'closing_time': time(18, 0),
                'reviews': 'Beautiful Victorian building with fascinating exhibits about Mumbai\'s history.',
                'type': AttractionType.MUSEUM,
                'city': mumbai
            },
            {
                'name': 'Nehru Science Centre',
                'info': 'India\'s largest interactive science center with over 500 hands-on exhibits. Features regular science shows and exhibitions.',
                'address': 'Dr E Moses Road, Worli, Mumbai, Maharashtra 400018',
                'opening_time': time(9, 30),
                'closing_time': time(18, 0),
                'reviews': 'Excellent place for children to learn about science through interactive exhibits.',
                'type': AttractionType.MUSEUM,
                'city': mumbai
            },
            {
                'name': 'Mani Bhavan Gandhi Museum',
                'info': 'Historic building and museum dedicated to Mahatma Gandhi, showcasing his life and India\'s independence movement.',
                'address': '19, Laburnum Road, Gamdevi, Mumbai, Maharashtra 400007',
                'opening_time': time(9, 30),
                'closing_time': time(18, 0),
                'reviews': 'Important historical site with well-preserved memorabilia of Gandhi\'s life.',
                'type': AttractionType.MUSEUM,
                'city': mumbai
            }
        ]

        # Create Delhi Museums
        delhi_museums = [
            {
                'name': 'Salar Jung Museum',
                'info': 'The Salar Jung Museum is one of India\'s largest museums, housing an extraordinary collection of over 43,000 artifacts gathered by Mir Yousuf Ali Khan, also known as Salar Jung III. The museum features antiques from India, Europe, the Middle East, and Japan.',
                'address': 'Salar Jung Museum, Hyderabad 500002, Telangana State',
                'opening_time': time(10, 30),
                'closing_time': time(19, 30),
                'reviews': 'Incredible collection of artifacts from around the world. Must-see attractions include the Veiled Rebecca and the Musical Clock.',
                'type': AttractionType.MUSEUM,
                'city': delhi
            },
            {
                'name': 'National Museum',
                'info': 'The National Museum is one of the largest museums in India, housing collections of artifacts from prehistoric era to modern works of art.',
                'address': 'Janpath Road, Central Secretariat, New Delhi',
                'opening_time': time(10, 0),
                'closing_time': time(18, 0),
                'reviews': 'Extensive collection spanning Indian history. Must-visit for history enthusiasts.',
                'type': AttractionType.MUSEUM,
                'city': delhi
            },
            {
                'name': 'National Gallery of Modern Art',
                'info': 'India\'s premier art gallery showcasing modern and contemporary Indian art from the 1850s onwards.',
                'address': 'Jaipur House, India Gate, New Delhi',
                'opening_time': time(11, 0),
                'closing_time': time(18, 0),
                'reviews': 'Excellent collection of modern Indian art in a beautiful building.',
                'type': AttractionType.MUSEUM,
                'city': delhi
            },
            {
                'name': 'Indira Gandhi Memorial Museum',
                'info': 'Former residence of Prime Minister Indira Gandhi, now a museum dedicated to her life and legacy.',
                'address': '1 Safdarjung Road, New Delhi, Delhi 110011',
                'opening_time': time(9, 30),
                'closing_time': time(17, 30),
                'reviews': 'Moving tribute to Indira Gandhi with well-preserved personal effects and historical documents.',
                'type': AttractionType.MUSEUM,
                'city': delhi
            },
            {
                'name': 'National Science Centre',
                'info': 'Interactive science museum with exhibits on various scientific principles and technological developments.',
                'address': 'Near Gate No.1, Pragati Maidan, New Delhi, Delhi 110001',
                'opening_time': time(10, 0),
                'closing_time': time(17, 30),
                'reviews': 'Engaging exhibits for all ages. Great place to learn about science and technology.',
                'type': AttractionType.MUSEUM,
                'city': delhi
            }
        ]

        # Create Mumbai Events
        mumbai_events = [
            {
                'name': 'Kala Ghoda Arts Festival',
                'info': 'Annual nine-day long arts festival featuring visual arts, dance, music, cinema, literature, and more. Held in February.',
                'address': 'Kala Ghoda, Fort, Mumbai',
                'opening_time': time(10, 0),
                'closing_time': time(22, 0),
                'reviews': 'Mumbai\'s largest cultural festival. Great atmosphere and diverse artistic performances.',
                'type': AttractionType.EVENT,
                'city': mumbai
            },
            {
                'name': 'Mumbai Film Festival',
                'info': 'Annual international film festival showcasing the best of world cinema. Features workshops, masterclasses, and film screenings.',
                'address': 'Various locations across Mumbai',
                'opening_time': time(9, 0),
                'closing_time': time(23, 0),
                'reviews': 'Premier film festival with excellent curation of international cinema.',
                'type': AttractionType.EVENT,
                'city': mumbai
            },
            {
                'name': 'Mumbai Marathon',
                'info': 'Asia\'s largest marathon and a major annual sporting event that brings together runners from around the world.',
                'address': 'Starts at CST, Mumbai',
                'opening_time': time(5, 40),
                'closing_time': time(14, 0),
                'reviews': 'Well-organized international marathon with great city views and enthusiastic crowd support.',
                'type': AttractionType.EVENT,
                'city': mumbai
            },
            {
                'name': 'Elephanta Festival',
                'info': 'Annual cultural festival held at the Elephanta Caves featuring classical music and dance performances.',
                'address': 'Elephanta Caves, Mumbai Harbour',
                'opening_time': time(16, 0),
                'closing_time': time(22, 0),
                'reviews': 'Unique festival combining heritage site with classical performances.',
                'type': AttractionType.EVENT,
                'city': mumbai
            }
        ]

        # Create Delhi Events
        delhi_events = [
            {
                'name': 'India Art Fair',
                'info': 'South Asia\'s leading platform for modern and contemporary art, featuring galleries from India and around the world.',
                'address': 'NSIC Exhibition Grounds, Okhla Industrial Estate, New Delhi',
                'opening_time': time(11, 0),
                'closing_time': time(19, 0),
                'reviews': 'Premier art event showcasing diverse contemporary artworks.',
                'type': AttractionType.EVENT,
                'city': delhi
            },
            {
                'name': 'Delhi Literature Festival',
                'info': 'Annual literary festival featuring book launches, author interactions, and panel discussions.',
                'address': 'Various venues across Delhi',
                'opening_time': time(10, 0),
                'closing_time': time(20, 0),
                'reviews': 'Engaging literary discussions and great opportunity to meet authors.',
                'type': AttractionType.EVENT,
                'city': delhi
            },
            {
                'name': 'International Mango Festival',
                'info': 'Annual festival celebrating different varieties of mangoes from across India.',
                'address': 'Talkatora Stadium, New Delhi',
                'opening_time': time(11, 0),
                'closing_time': time(20, 0),
                'reviews': 'Unique festival showcasing India\'s mango diversity with fun activities.',
                'type': AttractionType.EVENT,
                'city': delhi
            },
            {
                'name': 'Delhi International Arts Festival',
                'info': 'Multi-venue festival showcasing performing arts, visual arts, and cultural events.',
                'address': 'Various venues across Delhi',
                'opening_time': time(10, 0),
                'closing_time': time(22, 0),
                'reviews': 'Rich cultural experience with diverse artistic performances.',
                'type': AttractionType.EVENT,
                'city': delhi
            }
        ]

        # Create all attractions
        all_attractions = (
            mumbai_monuments + delhi_monuments +
            mumbai_museums + delhi_museums +
            mumbai_events + delhi_events
        )

        for attraction_data in all_attractions:
            Attraction.objects.get_or_create(
                name=attraction_data['name'],
                defaults={
                    'info': attraction_data['info'],
                    'address': attraction_data['address'],
                    'opening_time': attraction_data['opening_time'],
                    'closing_time': attraction_data['closing_time'],
                    'reviews': attraction_data['reviews'],
                    'type': attraction_data['type'],
                    'city': attraction_data['city']
                }
            )
            self.stdout.write(f"Added/Updated attraction: {attraction_data['name']}")

        self.stdout.write(self.style.SUCCESS('Successfully populated all attractions')) 