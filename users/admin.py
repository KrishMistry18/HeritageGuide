from django.contrib import admin
from .models import Museum, Monuments, Events, Booking, Attraction, City

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'attraction', 'date', 'time_slot', 'number_of_people', 'status')
    list_filter = ('status', 'time_slot', 'date')
    search_fields = ('user__username', 'attraction__name')
    date_hierarchy = 'date'

@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'type', 'rating', 'opening_time', 'closing_time')
    list_filter = ('type', 'city')
    search_fields = ('name', 'info', 'address')

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Register your models here.
admin.site.register(Museum)
admin.site.register(Monuments)
admin.site.register(Events)
