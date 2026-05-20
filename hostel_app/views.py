from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .forms import StudentSignUpForm
from .models import User, Room, Booking, Payment, Complaint
from .decorators import admin_required, warden_required, student_required

def home(request):
    if request.user.is_authenticated:
        if request.user.role == 'ADMIN':
            return redirect('admin_dashboard')
        elif request.user.role == 'WARDEN':
            return redirect('warden_dashboard')
        else:
            return redirect('student_dashboard')
    return render(request, 'home.html')

def register_view(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. Welcome!')
            return redirect('student_dashboard')
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = StudentSignUpForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                if user.role == 'ADMIN':
                    return redirect('admin_dashboard')
                elif user.role == 'WARDEN':
                    return redirect('warden_dashboard')
                else:
                    return redirect('student_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have successfully logged out.')
    return redirect('home')

# --- Warden Views ---
@login_required
@warden_required
def warden_dashboard(request):
    pending_bookings = Booking.objects.filter(status='PENDING')
    active_complaints = Complaint.objects.filter(status='ACTIVE')
    return render(request, 'warden/dashboard.html', {
        'pending_bookings': pending_bookings,
        'active_complaints': active_complaints
    })

@login_required
@warden_required
def manage_booking(request, booking_id, action):
    booking = Booking.objects.get(id=booking_id)
    if action == 'approve':
        booking.status = 'APPROVED'
        booking.room.current_occupancy += 1
        if booking.room.current_occupancy >= booking.room.capacity:
            booking.room.is_available = False
        booking.room.save()
        booking.save()
        messages.success(request, f'Booking approved.')
    elif action == 'reject':
        booking.status = 'REJECTED'
        booking.save()
        messages.info(request, f'Booking rejected.')
    return redirect('warden_dashboard')

@login_required
@warden_required
def resolve_complaint(request, complaint_id):
    complaint = Complaint.objects.get(id=complaint_id)
    complaint.status = 'RESOLVED'
    complaint.save()
    messages.success(request, 'Complaint resolved.')
    return redirect('warden_dashboard')

# --- Admin Views ---
@login_required
@admin_required
def admin_dashboard(request):
    users_count = User.objects.count()
    rooms_count = Room.objects.count()
    bookings_count = Booking.objects.count()
    payments_count = Payment.objects.count()
    return render(request, 'admin/dashboard.html', {
        'users_count': users_count,
        'rooms_count': rooms_count,
        'bookings_count': bookings_count,
        'payments_count': payments_count
    })

@login_required
@admin_required
def admin_users(request):
    users = User.objects.exclude(is_superuser=True)
    return render(request, 'admin/users.html', {'users': users})

@login_required
@admin_required
def admin_rooms(request):
    if request.method == 'POST':
        room_number = request.POST.get('room_number')
        capacity = request.POST.get('capacity')
        price = request.POST.get('price_per_month')
        room_type = request.POST.get('room_type')
        try:
            Room.objects.create(room_number=room_number, capacity=capacity, price_per_month=price, room_type=room_type)
            messages.success(request, 'Room added successfully.')
        except IntegrityError:
            messages.error(request, 'Error: Room with this number already exists.')
        except Exception as e:
            messages.error(request, f'Error adding room: {str(e)}')
        return redirect('admin_rooms')
    rooms = Room.objects.all()
    return render(request, 'admin/rooms.html', {'rooms': rooms})

@login_required
@student_required
def student_dashboard(request):
    return render(request, 'student/dashboard.html')

# --- Student Views ---

@login_required
@student_required
def room_list(request):
    rooms = Room.objects.filter(is_available=True)
    return render(request, 'student/room_list.html', {'rooms': rooms})

@login_required
@student_required
def book_room(request, room_id):
    room = Room.objects.get(id=room_id)
    if request.method == 'POST':
        # Check if user already has an active booking
        existing = Booking.objects.filter(student=request.user, status__in=['PENDING', 'APPROVED']).exists()
        if existing:
            messages.error(request, 'You already have an active or pending booking.')
        elif room.is_available:
            Booking.objects.create(student=request.user, room=room)
            messages.success(request, 'Booking request submitted successfully! Waiting for approval.')
        else:
            messages.error(request, 'Room is no longer available.')
            return redirect('room_list')
        return redirect('student_dashboard')
    
    return render(request, 'student/book_room.html', {'room': room})

@login_required
@student_required
def my_bookings(request):
    bookings = Booking.objects.filter(student=request.user).order_by('-created_at')
    return render(request, 'student/my_bookings.html', {'bookings': bookings})

@login_required
@student_required
def make_payment(request, booking_id):
    booking = Booking.objects.get(id=booking_id, student=request.user)
    if request.method == 'POST':
        # Dummy transaction
        transaction_id = "TXN" + str(booking.id) + request.user.username[:3].upper()
        Payment.objects.create(booking=booking, amount=booking.room.price_per_month, status='PAID', transaction_id=transaction_id)
        messages.success(request, 'Payment simulated successfully!')
        return redirect('student_dashboard')
    return render(request, 'student/make_payment.html', {'booking': booking})

@login_required
@student_required
def student_complaints(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        description = request.POST.get('description')
        if subject and description:
            Complaint.objects.create(student=request.user, subject=subject, description=description)
            messages.success(request, 'Complaint raised successfully.')
            return redirect('student_complaints')
    complaints = Complaint.objects.filter(student=request.user).order_by('-created_at')
    return render(request, 'student/complaints.html', {'complaints': complaints})
