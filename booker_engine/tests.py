from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from .models import Booking
from .forms import BookingForm

class BookingTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        
        # Create a booking from a month ago
        self.start_time = timezone.now() - timedelta(days=30, minutes=30)
        self.end_time = self.start_time + timedelta(minutes=30)
        self.booking = Booking.objects.create(
            name="Test Booking",
            description="Test Description",
            start=self.start_time,
            end=self.end_time,
            active=True,
            userid=self.user
        )

    def test_create_booking_view(self):
        url = reverse('create_booking')
        data = {
            'name': 'New Booking',
            'description': 'New Description',
            'date': (timezone.now() + timedelta(days=1)).date(),
            'time': (timezone.now() + timedelta(days=1, hours=1)).time(),
            'duration': 30
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Booking.objects.filter(name='New Booking').exists())

    def test_create_booking_overlap(self):
        url = reverse('create_booking')
        data = {
            'name': 'Overlap Booking',
            'description': 'Overlap Description',
            'date': self.start_time.date(),
            'time': self.start_time.time(),
            'duration': 30
        }
        response = self.client.post(url, data)
        self.assertFormError(response, 'form', None, 'This booking overlaps with an existing booking.')

    def test_create_booking_short_duration(self):
        url = reverse('create_booking')
        data = {
            'name': 'Short Booking',
            'description': 'Short Description',
            'date': (timezone.now() + timedelta(days=1)).date(),
            'time': (timezone.now() + timedelta(days=1, hours=1)).time(),
            'duration': 10
        }
        response = self.client.post(url, data)
        self.assertFormError(response, 'form', 'duration', 'Ensure this value is greater than or equal to 15.')

    def test_edit_booking(self):
        url = reverse('edit_booking', args=[self.booking.id])
        data = {
            'name': 'Updated Booking',
            'description': 'Updated Description',
            'date': self.booking.start.date(),
            'time': (self.booking.start + timedelta(minutes=30)).time(),
            'duration': 30
        }
        response = self.client.post(url, data)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.name, 'Updated Booking')

    def test_delete_booking(self):
        url = reverse('delete_booking', args=[self.booking.id])
        response = self.client.post(url)
        self.booking.refresh_from_db()
        self.assertFalse(self.booking.active)

    def test_view_booking(self):
        url = reverse('view_booking', args=[self.booking.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.booking.name)

    def test_home_view(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.booking.name)

    def test_get_bookings(self):
        date = (self.start_time + timedelta(days=1)).date()
        url = reverse('get_bookings') + f'?date={date}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_calendar_view(self):
        url = reverse('calendar')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_live_view(self):
        url = reverse('live_view')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
