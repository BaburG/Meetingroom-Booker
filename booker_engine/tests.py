from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from .models import Booking
from .forms import BookingForm
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
import json

class BookingTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        
        # Create a booking
        self.start_time = timezone.now() 
        self.end_time = self.start_time + timedelta(minutes=30)
        self.booking = Booking.objects.create(
            name="Test Booking",
            description="Test Description",
            start=self.start_time,
            end=self.end_time,
            active=True,
            userid=self.user
        )

    def test_1_create_booking_view(self):
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
        

    def test_2_create_booking_overlap(self):
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
        
        url = reverse('create_booking')
        data = {
            'name': 'Overlap Booking',
            'description': 'Overlap Description',
            'date': (timezone.now() + timedelta(days=1)).date(),
            'time': (timezone.now() + timedelta(days=1, hours=1)).time(),
            'duration': 30
        }
        response = self.client.post(url, data)
        self.assertContains(response, "This booking overlaps with an existing booking.")

    def test_3_create_booking_short_duration(self):
        url = reverse('create_booking')
        data = {
            'name': 'Short Booking',
            'description': 'Short Description',
            'date': (timezone.now() + timedelta(days=1)).date(),
            'time': (timezone.now() + timedelta(days=1, hours=1)).time(),
            'duration': 10
        }
        response = self.client.post(url, data)
          # Check that the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check that the form is returned in the context
        self.assertIn('form', response.context)

        # Check for the specific form error
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('duration', form.errors)
        self.assertEqual(form.errors['duration'], ['Ensure this value is greater than or equal to 15.'])
        

    def test_4_edit_booking(self):
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

    def test_5_delete_booking(self):
        url = reverse('delete_booking', args=[self.booking.id])
        response = self.client.post(url)
        self.booking.refresh_from_db()
        self.assertFalse(self.booking.active)

    def test_6_home_view(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.booking.name)

    def test_7_get_bookings(self):
        date = (self.start_time + timedelta(days=1)).date()
        url = reverse('get_bookings') + f'?date={date}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_8_calendar_view(self):
        url = reverse('calendar')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_9_live_view(self):
        url = reverse('live_view')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_10_create_booking_no_duration(self):
        url = reverse('create_booking')
        data = {
            'name': 'Short Booking',
            'description': 'Short Description',
            'date': (timezone.now() + timedelta(days=1)).date(),
            'time': (timezone.now() + timedelta(days=1, hours=1)).time(),
        }
        response = self.client.post(url, data)
          # Check that the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check that the form is returned in the context
        self.assertIn('form', response.context)

        # Check for the specific form error
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('duration', form.errors)
        self.assertEqual(form.errors['duration'], ['This field is required.'])

    def test_11_create_booking_no_name(self):
        url = reverse('create_booking')
        data = {
            'description': 'Short Description',
            'date': (timezone.now() + timedelta(days=1)).date(),
            'time': (timezone.now() + timedelta(days=1, hours=1)).time(),
            'duration': 10
        }
        response = self.client.post(url, data)
          # Check that the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check that the form is returned in the context
        self.assertIn('form', response.context)

        # Check for the specific form error
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('duration', form.errors)
        self.assertEqual(form.errors['name'], ['This field is required.'])


    def test_12_create_booking_no_date(self):
        url = reverse('create_booking')
        data = {
            'name': 'Short Booking',
            'description': 'Short Description',
            'time': (timezone.now() + timedelta(days=1, hours=1)).time(),
            'duration': 10
        }
        response = self.client.post(url, data)
          # Check that the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check that the form is returned in the context
        self.assertIn('form', response.context)

        # Check for the specific form error
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('duration', form.errors)
        self.assertEqual(form.errors['date'], ['This field is required.'])

    def test_13_create_booking_no_time(self):
        url = reverse('create_booking')
        data = {
            'name': 'Short Booking',
            'description': 'Short Description',
            'date': (timezone.now() + timedelta(days=1)).date(),
            'duration': 10
        }
        response = self.client.post(url, data)
          # Check that the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check that the form is returned in the context
        self.assertIn('form', response.context)

        # Check for the specific form error
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('duration', form.errors)
        self.assertEqual(form.errors['time'], ['This field is required.'])


class BookingAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        # Create a booking
        self.start_time = timezone.now()
        self.end_time = self.start_time + timedelta(minutes=30)
        self.booking = Booking.objects.create(
            name="Test Booking",
            description="Test Description",
            start=self.start_time,
            end=self.end_time,
            active=True,
            userid=self.user
        )
    
    def test_1_get_day_bookings(self):
        url = reverse('api_get_day_bookings')
        response = self.client.get(url, {'date': self.start_time.date().isoformat()})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
    
    def test_2_create_booking(self):
        url = reverse('api_create_booking')
        data = {
            'name': 'API Booking',
            'description': 'API Description',
            'start': (timezone.now() + timedelta(days=1)).isoformat(),
            'end': (timezone.now() + timedelta(days=1, hours=1)).isoformat(),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Booking.objects.filter(name='API Booking').exists())
    
    def test_3_create_booking_overlap(self):
        url = reverse('api_create_booking')
        data = {
            'name': 'API Booking',
            'description': 'API Description',
            'start': self.start_time.isoformat(),
            'end': (self.start_time + timedelta(minutes=30)).isoformat(),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Booking.objects.filter(name='API Booking').exists())

        url = reverse('api_create_booking')
        data = {
            'name': 'Overlap API Booking',
            'description': 'Overlap API Description',
            'start': self.start_time.isoformat(),
            'end': (self.start_time + timedelta(minutes=30)).isoformat(),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        
        # Check for '__all__' key in response data
        self.assertIn('__all__', response.data)

        # Assert the specific error message
        self.assertIn("This booking overlaps with an existing booking.", response.data['__all__'])

    def test_4_get_booking(self):
        url = reverse('api_get_booking')
        response = self.client.get(url, {'id': self.booking.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], self.booking.name)
    
    def test_5_update_booking(self):
        url = reverse('api_update_booking') + f"?id={self.booking.id}"
        data = {
            'name': 'Updated API Booking',
            'description': 'Updated API Description',
            'start': self.start_time.isoformat(),
            'end': (self.start_time + timedelta(hours=1)).isoformat(),
        }
        response = self.client.put(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.name, 'Updated API Booking')

    def test_6_delete_booking(self):
        url = reverse('api_delete_booking') + f"?id={self.booking.id}"
        response = self.client.delete(url, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.booking.refresh_from_db()
        self.assertFalse(self.booking.active)

    def test_7_create_booking_short_duration(self):
        url = reverse('api_create_booking')
        data = {
            'name': 'API Booking',
            'description': 'API Description',
            'start': (timezone.now() + timedelta(days=1)).isoformat(),
            'end': (timezone.now() + timedelta(days=1, minutes=10)).isoformat(),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    def test_8_create_booking_no_end(self):
        url = reverse('api_create_booking')
        data = {
            'name': 'API Booking',
            'description': 'API Description',
            'start': (timezone.now() + timedelta(days=1)).isoformat(),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    def test_9_create_booking_no_start(self):
        url = reverse('api_create_booking')
        data = {
            'name': 'API Booking',
            'description': 'API Description',
            'end': (timezone.now() + timedelta(days=1, hours=1)).isoformat(),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    def test_10_create_booking_no_name(self):
        url = reverse('api_create_booking')
        data = {
            'description': 'API Description',
            'start': (timezone.now() + timedelta(days=1)).isoformat(),
            'end': (timezone.now() + timedelta(days=1, hours=1)).isoformat(),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)

    def test_11_create_booking_zero_duration(self):
        url = reverse('api_create_booking')
        data = {
            'name': 'API Booking',
            'description': 'API Description',
            'start': (timezone.now() + timedelta(days=1)).isoformat(),
            'end': (timezone.now() + timedelta(days=1)).isoformat(),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Booking.objects.filter(name='API Booking').exists())