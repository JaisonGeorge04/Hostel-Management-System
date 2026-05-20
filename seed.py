import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hostel_core.settings")
django.setup()

from hostel_app.models import User, Room

print("Seeding database...")
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@hostel.com', 'admin123')
    admin.role = 'ADMIN'
    admin.save()

    warden = User.objects.create_user('warden1', 'warden@hostel.com', 'warden123')
    warden.role = 'WARDEN'
    warden.save()

    student = User.objects.create_user('student1', 'student@hostel.com', 'student123')
    student.role = 'STUDENT'
    student.save()

    Room.objects.create(room_number='A101', capacity=2, price_per_month=5000.00, room_type='AC')
    Room.objects.create(room_number='A102', capacity=2, price_per_month=5000.00, room_type='AC')
    Room.objects.create(room_number='B201', capacity=3, price_per_month=3000.00, room_type='NON_AC')
    print("Database seeded successfully with users (admin, warden1, student1) and dummy rooms.")
else:
    print("Skipping seed: Database already has admin user.")
