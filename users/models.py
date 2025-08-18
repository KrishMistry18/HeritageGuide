# In your app's models.py (e.g., travels/models.py)
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# class Destination(models.Model):
#     name = models.CharField(max_length=200)
#     description = models.TextField()
#     interest = models.CharField(max_length=50)
#     min_budget = models.DecimalField(max_digits=10, decimal_places=2)
#     max_budget = models.DecimalField(max_digits=10, decimal_places=2)
    
#     def __str__(self):
#         return self.name

# class Itinerary(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     destinations = models.ManyToManyField(Destination)
#     trip_date = models.DateField()
#     duration = models.IntegerField()
#     created_at = models.DateTimeField(auto_now_add=True)
    
    # def __str__(self):
    #     return f"Itinerary for {self.user.username} on {self.trip_date}"
    

    
class ChatMessage(models.Model):
    user_message = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User: {self.user_message[:50]} | Bot: {self.bot_response[:50]}"
    
# # class Device(models.Model):
# #     """Smart home device model"""
# #     NAME_CHOICES = [
# #         ('smart_plug', 'Smart Plug'),
# #         ('air_conditioner', 'Air Conditioner'),
# #         ('smart_lamp', 'Smart Lamp'),
# #         ('smart_lock', 'Smart Lock'),
# #         ('robot_vacuum', 'Robot Vacuum'),
# #     ]
    
# #     ICON_CHOICES = [
# #         ('📱', 'Phone'),
# #         ('❄️', 'AC'),
# #         ('💡', 'Light'),
# #         ('🔒', 'Lock'),
# #         ('🤖', 'Robot'),
# #     ]
    
# #     name = models.CharField(max_length=50, choices=NAME_CHOICES)
# #     icon = models.CharField(max_length=5, choices=ICON_CHOICES)
    
# #     def __str__(self):
# #         return self.get_name_display()


class Museum(models.Model):
    name = models.CharField(max_length=100)
    info=models.TextField()
    GmapAddress=models.CharField(max_length=100)
    time = models.TimeField(max_length=255)
    reviews=models.TextField()
    images= models.ImageField(upload_to='users/images/',default=" ")

class Monuments(models.Model):
    name = models.CharField(max_length=100)
    info=models.TextField()
    GmapAddress=models.CharField(max_length=100)
    time = models.TimeField(max_length=255)
    reviews=models.TextField()
    images= models.ImageField(upload_to='users/images/',default=" ")

class Events(models.Model):
    name = models.CharField(max_length=100)
    info=models.TextField()
    GmapAddress=models.CharField(max_length=100)
    time = models.TimeField(max_length=255)
    reviews=models.TextField()
    images= models.ImageField(upload_to='users/images/',default=" ")
    
def __str__(self):
    return f"{self.room} - {self.get_sensor_type_display()}: {self.value}{self.unit}"


from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class City(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='cities/', blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Cities"

class AttractionType(models.TextChoices):
    MUSEUM = 'museum', 'Museum'
    MONUMENT = 'monument', 'Monument'
    EVENT = 'event', 'Event'
    RESTAURANT = 'restaurant', 'Restaurant'
    SHOPPING = 'shopping', 'Shopping'
    NATURE = 'nature', 'Nature Spot'
    OTHER = 'other', 'Other'

class Attraction(models.Model):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='attractions')
    type = models.CharField(max_length=20, choices=AttractionType.choices)
    info = models.TextField()
    address = models.CharField(max_length=200)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=60, help_text="Estimated time to spend here (minutes)")
    reviews = models.TextField(blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.0)
    image = models.ImageField(upload_to='attractions/', blank=True, null=True)
    interest_tags = models.CharField(max_length=100, blank=True, help_text="Comma-separated tags like 'culture,food,history'")
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()}) - {self.city.name}"
    
    def get_interest_tags_list(self):
        return [tag.strip() for tag in self.interest_tags.split(',') if tag.strip()]

class Itinerary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="My Itinerary")
    cities = models.ManyToManyField(City)
    start_date = models.DateField()
    end_date = models.DateField()
    transportation_type = models.CharField(max_length=50, blank=True)
    total_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    interests = models.CharField(max_length=200, blank=True, default="adventure")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} for {self.user.username} ({self.start_date} to {self.end_date})"
    
    class Meta:
        verbose_name_plural = "Itineraries"

class ItineraryDay(models.Model):
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, related_name='days')
    date = models.DateField()
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Day for {self.itinerary.name} on {self.date}"
    
    class Meta:
        ordering = ['date']

class ItineraryActivity(models.Model):
    day = models.ForeignKey(ItineraryDay, on_delete=models.CASCADE, related_name='activities')
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE, null=True, blank=True)
    custom_activity = models.CharField(max_length=200, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        activity_name = self.attraction.name if self.attraction else self.custom_activity
        return f"{activity_name} on {self.day.date}"
    
    class Meta:
        ordering = ['order', 'start_time']
        verbose_name_plural = "Itinerary activities"

class SlotBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE)
    booking_date = models.DateField()
    booking_time = models.TimeField()
    number_of_people = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ])
    
    def __str__(self):
        return f"{self.user.username}'s booking for {self.attraction.name} on {self.booking_date} at {self.booking_time}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Slot Bookings"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE)
    date = models.DateField()
    time_slot = models.CharField(max_length=20, choices=[
        ('morning', '9:00 AM - 12:00 PM'),
        ('afternoon', '12:00 PM - 3:00 PM'),
        ('evening', '3:00 PM - 6:00 PM'),
    ])
    number_of_people = models.PositiveIntegerField()
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    
    def __str__(self):
        return f"{self.user.username}'s booking for {self.attraction.name} on {self.date}"

    class Meta:
        ordering = ['-booking_date']
        unique_together = ['attraction', 'date', 'time_slot', 'user']  # One booking per user per slot

    @classmethod
    def get_slot_availability(cls, attraction, date, time_slot):
        # Default capacity per slot
        SLOT_CAPACITY = 50
        
        # Get total booked for this slot (only count confirmed bookings)
        total_booked = cls.objects.filter(
            attraction=attraction,
            date=date,
            time_slot=time_slot,
            status='confirmed'
        ).aggregate(
            total=models.Sum('number_of_people')
        )['total'] or 0
        
        available_slots = max(0, SLOT_CAPACITY - total_booked)
        return {
            'total_capacity': SLOT_CAPACITY,
            'booked': total_booked,
            'available': available_slots
        }

# Keep existing models
# class ChatMessage(models.Model):
#     user_message = models.TextField()
#     bot_response = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"User: {self.user_message[:50]} | Bot: {self.bot_response[:50]}"

# class Museum(models.Model):
#     name = models.CharField(max_length=100)
#     info = models.TextField()
#     GmapAddress = models.CharField(max_length=100)
#     time = models.TimeField(max_length=255)
#     reviews = models.TextField()
#     images = models.ImageField(upload_to='users/images/', default=" ")

# class Monuments(models.Model):
#     name = models.CharField(max_length=100)
#     info = models.TextField()
#     GmapAddress = models.CharField(max_length=100)
#     time = models.TimeField(max_length=255)
#     reviews = models.TextField()
#     images = models.ImageField(upload_to='users/images/', default=" ")

# class Events(models.Model):
#     name = models.CharField(max_length=100)
#     info = models.TextField()
#     GmapAddress = models.CharField(max_length=100)
#     time = models.TimeField(max_length=255)
#     reviews = models.TextField()
#     images = models.ImageField(upload_to='users/images/', default=" ")

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"



