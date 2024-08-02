from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('booking/<int:id>/', views.edit_booking, name="edit_booking"),
    path('booking/<int:id>/delete/', views.delete_booking, name="delete_booking"),
    path('all_bookings/', views.all_bookings, name="all_bookings"),
    path('liveview/', views.live_view, name="live_view"),
    path('get-bookings', views.get_bookings, name='get_bookings'),
    path("calendar/", views.calendar, name="calendar"),
    path("create_booking/", views.create_booking, name="create_booking"),
    path("home/", views.home, name="home"),
    path("",views.index, name="index" )
]