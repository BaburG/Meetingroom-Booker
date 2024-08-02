from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.shortcuts import redirect, get_object_or_404, render
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import F

from .models import Booking
from .forms import BookingForm, SignUpForm, LoginForm, DateForm

def last_midnight():
    return timezone.make_aware(datetime.combine(timezone.now().date(), datetime.min.time()))

def today_midnight():
    return last_midnight() + timedelta(days=1)

def tomorrow_midnight():
    return today_midnight() + timedelta(days=1)

def after_tomorrow_midnight():
    return today_midnight() + timedelta(days=2)

@login_required()
def home(request):
    today_list = Booking.objects.filter(
        start__gte=last_midnight(), start__lt=today_midnight(), active=True
    ).select_related('userid').order_by("start")
    tomorrow_list = Booking.objects.filter(
        start__gte=today_midnight(), start__lt=tomorrow_midnight(), active=True
    ).select_related('userid').order_by("start")
    after_tomorrow_list = Booking.objects.filter(
        start__gte=tomorrow_midnight(), start__lt=after_tomorrow_midnight(), active=True
    ).select_related('userid').order_by("start")

    template = loader.get_template("booker/home.html")
    context = {
        "today_list": today_list,
        "tomorrow_list": tomorrow_list,
        "after_tomorrow_list": after_tomorrow_list,
    }
    return HttpResponse(template.render(context, request))

@login_required()
def create_booking(request):
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = Booking(
                name=form.cleaned_data["name"],
                description=form.cleaned_data["description"],
                start=form.cleaned_data["start"],
                end=form.cleaned_data["end"],
                userid=request.user  # Use request.user instead of request.user.id
            )
            booking.save()
            return redirect("home")
    else:
        form = BookingForm()
    return render(request, "booker/create_booking.html", {"form": form})

@login_required()
def calendar(request):
    return render(request, "booker/calendar.html")

@login_required()
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

@login_required()
def get_bookings(request):
    form = DateForm(request.GET)
    if form.is_valid():
        fetched_date = form.cleaned_data['date']
        start_of_day = timezone.make_aware(datetime.combine(fetched_date, datetime.min.time()))
        end_of_day = timezone.make_aware(datetime.combine(fetched_date + timedelta(days=1), datetime.min.time()) - timedelta(seconds=1))
        
        bookings = Booking.objects.filter(start__gt=start_of_day, start__lt=end_of_day, active=True).select_related('userid').order_by("start")
        bookings_list = list(bookings.values('name', 'description', 'start', 'end', username=F('userid__username')))
        return JsonResponse(bookings_list, safe=False)
    
    return JsonResponse({'errors': form.errors}, status=400)

@login_required()
def live_view(request):
    return render(request, "booker/live_view.html")

@login_required()
def view_booking(request, id):
    booking = get_object_or_404(Booking, id=id)
    return render(request, "booker/view_booking.html", {'booking': booking})

@login_required()
def edit_booking(request, id):
    booking = get_object_or_404(Booking, id=id)
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            return redirect("home")
    elif request.method == 'GET':
        date = booking.start.date()
        time = booking.start.astimezone(timezone.get_current_timezone()).time()
        duration = booking.end - booking.start
        duration_in_min = int(duration.total_seconds() / 60)

        form = BookingForm(initial={
            'name': booking.name,
            'description': booking.description,
            'date': date,
            'time': time,
            'duration': duration_in_min,
        })
    return render(request, "booker/edit.html", {'id': booking.id, 'form': form, 'booking': booking})

@login_required()
def delete_booking(request, id):
    booking = get_object_or_404(Booking, id=id)
    if request.method == 'POST':
        booking.active = False
        booking.save()
        return redirect("home")
    return redirect("home")

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'auth/signup.html', {'form': form})

def index(request):
    return redirect('login')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            keep_signed_in = form.cleaned_data['keep_signed_in']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if keep_signed_in:
                    request.session.set_expiry(1209600)
                else:
                    request.session.set_expiry(0)
                return redirect('home')
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        if request.user.id:
            return redirect('home')
        form = LoginForm()
    
    return render(request, 'auth/login.html', {'form': form})
