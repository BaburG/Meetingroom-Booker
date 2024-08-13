from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from datetime import datetime, timedelta
from .models import Booking

class BookingForm(forms.ModelForm):
    date = forms.DateField(widget=forms.NumberInput(attrs={"type": "date"}))
    time = forms.TimeField(widget=forms.TimeInput(format="%H:%M", attrs={"type": "time"}))
    duration = forms.IntegerField(help_text="Enter duration in minutes", min_value=15, max_value=300)

    class Meta:
        model = Booking
        fields = ['name', 'description', 'date', 'time', 'duration']

    def __init__(self, *args, **kwargs):
        super(BookingForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        time = cleaned_data.get("time")
        duration = int(cleaned_data.get("duration"))

        if date and time and duration:
            
            start_datetime = datetime.combine(date, time, timezone.get_current_timezone())
            end_datetime = start_datetime + timedelta(minutes=duration)
            

            # Check for overlapping bookings
            overlapping_bookings = Booking.objects.filter(
                start__lt=end_datetime, end__gt=start_datetime, active=True
            ).exclude(id=self.instance.id)  # Exclude the current instance from the check
            if overlapping_bookings.exists():
                raise forms.ValidationError(
                    "This booking overlaps with an existing booking."
                )

            cleaned_data["start"] = start_datetime
            cleaned_data["end"] = end_datetime

        return cleaned_data

    def save(self, commit=True):
        instance = super(BookingForm, self).save(commit=False)
        instance.start = self.cleaned_data['start']
        instance.end = self.cleaned_data['end']
        
        if commit:
            instance.save()
        return instance
    
class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'User Name'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    keep_signed_in = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))


class DateForm(forms.Form):
    date = forms.DateField(input_formats=['%Y-%m-%d'], error_messages={
        'invalid': 'Enter a valid date in YYYY-MM-DD format.'
    })


class BookingAPIForm(forms.ModelForm):
    start = forms.DateTimeField()
    end = forms.DateTimeField()

    class Meta:
        model = Booking
        fields = ['name', 'description', 'start', 'end']

    def __init__(self, *args, **kwargs):
        super(BookingAPIForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start")
        end = cleaned_data.get("end")

        if start and end:

            # Check for overlapping bookings
            overlapping_bookings = Booking.objects.filter(
                start__lt=end, end__gt=start, active=True
            ).exclude(id=self.instance.id)  # Exclude the current instance from the check
            if overlapping_bookings.exists():
                raise forms.ValidationError(
                    "This booking overlaps with an existing booking."
                )

        return cleaned_data