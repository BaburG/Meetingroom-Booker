from django import forms
from datetime import datetime, timedelta
from .models import Booking


class BookingForm(forms.Form):
    name = forms.CharField(max_length=255)
    description = forms.CharField(widget=forms.Textarea, required=False)
    date = forms.DateField(widget=forms.NumberInput(attrs={"type": "date"}))
    time = forms.TimeField(
        widget=forms.TimeInput(format="%H:%M", attrs={"type": "time"})
    )
    duration = forms.DecimalField(help_text="Enter duration in minutes")

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
            )
            if overlapping_bookings.exists():
                raise forms.ValidationError(
                    "This booking overlaps with an existing booking."
                )

            cleaned_data["start"] = start_datetime
            cleaned_data["end"] = end_datetime

        return cleaned_data
