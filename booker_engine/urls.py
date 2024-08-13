from django.urls import path
from django.contrib.auth import views as auth_views
from . import views, api
from rest_framework.authtoken.views import obtain_auth_token

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
    path("",views.index, name="index" ),
    path("api/login", api.login, name="api_login"),
    path("api/logout", api.logout, name="api_logout"),
    path('api/token', obtain_auth_token, name='api_token_auth'),
    path('api/get_day_bookings', api.get_day, name='api_get_day_bookings'),
    path('api/get_week_bookings', api.get_week, name='api_get_week_bookings'),
    path('api/create_booking',api.create_booking, name='api_create_booking'),
    path('api/my_bookings', api.my_bookings, name='api_my_bookings'),
    path('api/get_booking', api.get_booking, name='api_get_booking'),
    path('api/delete_booking', api.delete_booking, name='api_delete_booking'),
    path('api/update_booking',api.update_booking, name='api_update_booking'),

]