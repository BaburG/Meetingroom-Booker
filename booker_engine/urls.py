from django.urls import path

from . import views

urlpatterns = [
    path('booking/<int:id>/', views.edit_booking, name="edit_booking"),
    path('all_bookings/', views.all_bookings, name="all_bookings"),
    path('liveview/', views.live_view, name="live_view"),
    path('get-bookings', views.get_bookings, name='get_bookings'),
    path("calendar/", views.calendar, name="calendar"),
    path("create_booking/", views.create_booking, name="create_booking"),
    path("", views.index, name="index"),
]