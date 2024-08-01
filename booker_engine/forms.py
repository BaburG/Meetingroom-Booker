from django import forms
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
            start_datetime = datetime.combine(date, time)
            end_datetime = start_datetime + timedelta(minutes=duration)

            # Check for overlapping bookings
            overlapping_bookings = Booking.objects.filter(
                start__lt=end_datetime, end__gt=start_datetime
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