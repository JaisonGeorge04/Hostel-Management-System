from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('panel/users/', views.admin_users, name='admin_users'),
    path('panel/rooms/', views.admin_rooms, name='admin_rooms'),
    path('warden_dashboard/', views.warden_dashboard, name='warden_dashboard'),
    path('warden/booking/<int:booking_id>/<str:action>/', views.manage_booking, name='manage_booking'),
    path('warden/complaint/<int:complaint_id>/resolve/', views.resolve_complaint, name='resolve_complaint'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/rooms/', views.room_list, name='room_list'),
    path('student/book_room/<int:room_id>/', views.book_room, name='book_room'),
    path('student/my_bookings/', views.my_bookings, name='my_bookings'),
    path('student/make_payment/<int:booking_id>/', views.make_payment, name='make_payment'),
    path('student/complaints/', views.student_complaints, name='student_complaints'),
]
