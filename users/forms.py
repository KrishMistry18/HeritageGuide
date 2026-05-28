from django import forms
from django.core.exceptions import ValidationError
import datetime
from django.utils import timezone
from datetime import date

def MinDateValidator(value):
    today = timezone.now().date()
    if value < today:
        raise ValidationError("The date cannot be in the past.")
    return value

class ItineraryForm(forms.Form):
    INTEREST_CHOICES = [
        ('culture', 'Culture'),
        ('adventure', 'Adventure'),
        ('relaxation', 'Relaxation'),
        ('food', 'Food'),
        ('nature', 'Nature'),
        ('shopping', 'Shopping'),
        ('entertainment', 'Entertainment')
    ]

    TRANSPORTATION_CHOICES = [
        ('mixed', 'Mixed (Recommended)'),
        ('car', 'Rental Car'),
        ('public', 'Public Transportation'),
        ('tour', 'Guided Tours'),
        ('walk', 'Walking'),
        ('bike', 'Biking')
    ]

    name = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter a name for your itinerary',
            'class': 'form-control'
        })
    )
    
    cities = forms.MultipleChoiceField(
        choices=[],  # Will be populated in view
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        validators=[MinDateValidator],
        required=True
    )
    
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        validators=[MinDateValidator],
        required=True
    )
    
    interests = forms.MultipleChoiceField(
        choices=INTEREST_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    
    transportation_type = forms.ChoiceField(
        choices=TRANSPORTATION_CHOICES,
        initial='mixed',
        required=True
    )
    
    total_budget = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Enter your budget amount',
            'class': 'form-control'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        cities = cleaned_data.get('cities', [])
        interests = cleaned_data.get('interests', [])

        if start_date and end_date:
            if end_date < start_date:
                raise ValidationError("End date must be after start date")
            
            trip_duration = (end_date - start_date).days + 1
            if trip_duration < len(cities):
                raise ValidationError(f"Trip duration ({trip_duration} days) must be at least the number of selected cities ({len(cities)})")
        
        if not cities:
            raise ValidationError("Please select at least one city")
            
        if not interests:
            raise ValidationError("Please select at least one interest")
        
        return cleaned_data

class SlotBookingForm(forms.Form):
    booking_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    booking_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    number_of_people = forms.IntegerField(widget=forms.NumberInput(attrs={'min': 1, 'max': 10}))

class BookingForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'min': date.today().isoformat()}))
    time_slot = forms.ChoiceField(choices=[('morning', 'Morning'), ('afternoon', 'Afternoon'), ('evening', 'Evening')], widget=forms.Select(attrs={'class': 'form-control'}))
    number_of_people = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '10'}))

    def clean_date(self):
        booking_date = self.cleaned_data.get('date')
        if booking_date < date.today():
            raise forms.ValidationError("Booking date cannot be in the past")
        return booking_date

    def clean_number_of_people(self):
        num_people = self.cleaned_data.get('number_of_people')
        if num_people < 1:
            raise forms.ValidationError("Number of people must be at least 1")
        if num_people > 10:
            raise forms.ValidationError("Maximum 10 people allowed per booking")
        return num_people

class SignUpForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, required=True)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    phone_number = forms.CharField(max_length=15, required=True)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

class ProfileUpdateForm(forms.Form):
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "+91XXXXXXXXXX"}), required=False)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), required=False)
