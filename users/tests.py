import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from users.models import Attraction, AttractionType, Booking, City, Itinerary, ItineraryDay, Profile


class BookingModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass12345")
        self.city = City.objects.create(name="Mumbai")
        self.attraction = Attraction.objects.create(
            name="Gateway",
            city=self.city,
            type=AttractionType.MONUMENT,
            info="Historic place",
            address="Mumbai",
            duration_minutes=90,
            interest_tags="culture,history",
        )

    def test_slot_availability_reduces_after_confirmed_booking(self):
        Booking.objects.create(
            user=self.user,
            attraction=self.attraction,
            date=timezone.now().date() + datetime.timedelta(days=1),
            time_slot="morning",
            number_of_people=5,
            status="confirmed",
        )
        availability = Booking.get_slot_availability(
            self.attraction,
            timezone.now().date() + datetime.timedelta(days=1),
            "morning",
        )
        self.assertEqual(availability["booked"], 5)
        self.assertEqual(availability["available"], 45)


class ItineraryFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="itinerary", password="pass12345")
        self.client.login(username="itinerary", password="pass12345")
        self.city = City.objects.create(name="Mumbai")
        for i in range(4):
            Attraction.objects.create(
                name=f"Attraction {i}",
                city=self.city,
                type=AttractionType.MONUMENT,
                info="Great cultural attraction",
                address="Mumbai",
                duration_minutes=60,
                interest_tags="culture,history",
                rating=4.5,
            )

    def test_itinerary_generation_creates_days_with_city_mapping(self):
        response = self.client.post(
            reverse("itinerary_create"),
            data={
                "name": "Test Plan",
                "cities": [str(self.city.id)],
                "start_date": (timezone.now().date() + datetime.timedelta(days=1)).isoformat(),
                "end_date": (timezone.now().date() + datetime.timedelta(days=2)).isoformat(),
                "interests": ["culture"],
                "transportation_type": "mixed",
                "total_budget": "1000",
            },
        )
        self.assertEqual(response.status_code, 302)
        itinerary = Itinerary.objects.latest("id")
        days = ItineraryDay.objects.filter(itinerary=itinerary)
        self.assertTrue(days.exists())
        self.assertTrue(all(day.city_id == self.city.id for day in days))


class ProfileUpdateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="profileuser",
            email="old@example.com",
            password="pass12345",
        )
        Profile.objects.create(user=self.user)
        self.client.login(username="profileuser", password="pass12345")

    def test_profile_update_endpoint_updates_user_email(self):
        response = self.client.post(
            reverse("update_profile"),
            data={
                "first_name": "Krish",
                "last_name": "Mistry",
                "email": "new@example.com",
                "phone_number": "9999999999",
                "birth_date": "2000-01-01",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "new@example.com")
