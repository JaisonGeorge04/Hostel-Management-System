from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Room, Booking, Payment, Complaint

admin.site.register(User, UserAdmin)
admin.site.register(Room)
admin.site.register(Booking)
admin.site.register(Payment)
admin.site.register(Complaint)
