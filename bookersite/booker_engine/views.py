from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.shortcuts import redirect
from datetime import datetime, timedelta, timezone

from .models import Booking
from .forms import BookingForm


def index(request):
    now = datetime.now()
    last_midnight = datetime.combine(now.date(), datetime.min.time())
    today_midnight = last_midnight + timedelta(days=1)
    tomorrow_midnight = today_midnight + timedelta(days=1)
    after_tomorrow_midnight = today_midnight + timedelta(days=2)

    today_list = Booking.objects.filter(
        start__gte=last_midnight, start__lt=today_midnight
    ).order_by("start")
    tomorrow_list = Booking.objects.filter(
        start__gte=today_midnight, start__lt=tomorrow_midnight
    ).order_by("start")
    after_tomorrow_list = Booking.objects.filter(
        start__gte=tomorrow_midnight, start__lt=after_tomorrow_midnight
    ).order_by("start")

    template = loader.get_template("booker/index.html")
    context = {
        "today_list": today_list,
        "tomorrow_list": tomorrow_list,
        "after_tomorrow_list": after_tomorrow_list,
    }
    return HttpResponse(template.render(context, request))


def create_booking(request):
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = Booking(
                name=form.cleaned_data["name"],
                description=form.cleaned_data["description"],
                start=form.cleaned_data["start"],
                end=form.cleaned_data["end"],
            )
            booking.save()
            return redirect("index")  # Replace with your success URL
    else:
        form = BookingForm()
    return render(request, "booker/create_booking.html", {"form": form})


def calendar(request):
    return render(request, "booker/calendar.html")

def all_bookings(request):
    all_bookings = Booking.objects.all()
    out = []
    for booking in all_bookings:
        out.append({
            'name' : booking.name,
            'start' : booking.start.isoformat(),
            'end' : booking.end.isoformat(),
        })
    return JsonResponse(out, safe=False)



def get_bookings(request):
    fetched_date = request.GET.get('date')
    date = datetime.strptime(fetched_date, "%Y-%m-%d")
    
    # Start of the day (midnight)
    start_of_day = datetime.combine(date, datetime.min.time())
    
    # End of the day (last second of the day)
    end_of_day = datetime.combine(date + timedelta(days=1), datetime.min.time()) - timedelta(seconds=1)
    if date:
        bookings = Booking.objects.filter(start__gt=start_of_day, start__lt=end_of_day).order_by("start")
        bookings_list = list(bookings.values('name', 'description', 'start', 'end'))
        return JsonResponse(bookings_list, safe=False)
    return JsonResponse([], safe=False)

def live_view(request):
    return render(request, "booker/live_view.html")