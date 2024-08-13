from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import F, Func, Value
from booker_engine.forms import DateForm
from booker_engine.models import Booking
from collections import defaultdict
from rest_framework import status
from django.db.models.functions import Cast


from .forms import BookingAPIForm
from .models import Booking

@csrf_exempt
@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
    return Response({'error': 'Invalid Credentials'}, status=400)



@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request):
    request.user.auth_token.delete()
    logout(request)
    return Response({'message': 'Logged out successfully'})




@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_day(request):
    date_str = request.query_params.get('date')
    if date_str:
        try:
            fetched_date = timezone.make_aware(datetime.strptime(date_str, "%Y-%m-%d"))
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
    else:
        return Response({"error": "No Date input"}, status=400)
    start_of_day = timezone.make_aware(datetime.combine(fetched_date, datetime.min.time()))
    end_of_day = timezone.make_aware(datetime.combine(fetched_date + timedelta(days=1), datetime.min.time()) - timedelta(seconds=1))
    bookings = Booking.objects.filter(start__gt=start_of_day, start__lt=end_of_day, active=True).select_related('userid').order_by("start")
    bookings_list = list(bookings.values('id','name', 'description', 'start', 'end', username=F('userid__username')))
    
    return Response(bookings_list)




@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_week(request):
    date_str = request.query_params.get('date')
    if date_str:
        try:
            fetched_date = timezone.make_aware(datetime.strptime(date_str, "%Y-%m-%d"))
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
    else:
        return Response({"error": "No Date input"}, status=400)
    start_of_day = timezone.make_aware(datetime.combine(fetched_date, datetime.min.time()))
    end_of_day = timezone.make_aware(datetime.combine(fetched_date + timedelta(days=1), datetime.min.time()) - timedelta(seconds=1))
    weekBookings = list(Booking.objects.filter(active=True, start__gt=start_of_day, start__lt=(end_of_day + timedelta(days=7)))
               .select_related('userid')
               .order_by("start")
               .values('id','name', 'description', 'start', 'end', username=F('userid__username')))

    bookingByDay = dict()

    for booking in weekBookings:
        bookingDay = str(booking['start'].date())
        if bookingDay in bookingByDay:
            bookingByDay[bookingDay].append(booking)
        else:
            bookingByDay[bookingDay] = [booking]

    return Response(bookingByDay)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_booking(request):
    # Extract the token from the request
    try:
        token = request.auth
        # Reverse search the token to find the user
        user = Token.objects.get(key=token).user
    except Token.DoesNotExist:
        return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

    # Add the user ID to the request data
    data = request.data.copy()
    data['userid'] = user.id

    data['start'] = datetime.fromisoformat(data['start']).replace(tzinfo=timezone.get_current_timezone())
    data['end'] = datetime.fromisoformat(data['end']).replace(tzinfo=timezone.get_current_timezone())
    
    # Validate the form
    form = BookingAPIForm(data=data)

    if form.is_valid():
        # Save the booking with the correct user
        booking = form.save(commit=False)
        booking.userid = user  # Ensure the user is correctly set
        booking.save()
        return Response({"message": "Booking created successfully"}, status=status.HTTP_201_CREATED)
    else:
        # Return validation errors
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def my_bookings(request):
    # Extract the token from the request
    try:
        token = request.auth
        # Reverse search the token to find the user
        user = Token.objects.get(key=token).user_id
    except Token.DoesNotExist:
        return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

    now = timezone.now()

    bookings = list(Booking.objects.filter(start__gt=now, userid=user, active=True)
            .select_related('userid')
            .order_by("start")
            .values('id','name', 'description', 'start', 'end', username=F('userid__username')))

    return Response(bookings)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_booking(request):
    booking_id = request.query_params.get('id')

    try:
        token = request.auth
        # Reverse search the token to find the user
        user = Token.objects.get(key=token.key).user
    except Token.DoesNotExist:
        return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

    booking = Booking.objects.filter(id=booking_id, userid=user, active=True).select_related('userid').values(
        'id', 'name', 'description', 'start', 'end', username=F('userid__username')
    ).first()

    if not booking:
        return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)

    
    return Response(booking, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_booking(request):
    booking_id = request.query_params.get('id')

    if not booking_id:
        return Response({"error": "Booking ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = request.user  # Get the user directly from the request
    except Token.DoesNotExist:
        return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        # Find the booking belonging to the user
        booking = Booking.objects.get(id=booking_id, userid=user)
    except Booking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)

    # If you have an `active` field, otherwise delete the booking or set it to inactive
    booking.active = False
    booking.save()

    return Response(status=status.HTTP_200_OK)

@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_booking(request):
    booking_id = request.query_params.get('id')
    if not booking_id:
        return Response({"error": "Booking ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Extract the token from the request
    try:
        token = request.auth
        # Reverse search the token to find the user
        user = Token.objects.get(key=token).user
    except Token.DoesNotExist:
        return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

    # Check if the booking exists and belongs to the user
    try:
        booking = Booking.objects.get(id=booking_id, userid=user)
    except Booking.DoesNotExist:
        return Response({"error": "Booking not found or you do not have permission to edit this booking."},
                        status=status.HTTP_404_NOT_FOUND)

    # Add the user ID to the request data
    data = request.data.copy()
    data['userid'] = user.id

    data['start'] = datetime.fromisoformat(data['start']).replace(tzinfo=timezone.get_current_timezone())
    data['end'] = datetime.fromisoformat(data['end']).replace(tzinfo=timezone.get_current_timezone())
    
    # Validate the form with existing instance
    form = BookingAPIForm(data=data, instance=booking)

    if form.is_valid():
        # Save the updated booking
        updated_booking = form.save()
        return Response({"message": "Booking updated successfully"}, status=status.HTTP_200_OK)
    else:
        # Return validation errors
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)