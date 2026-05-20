from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def admin_required(function=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.role == 'ADMIN',
        login_url='login'
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def warden_required(function=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.role == 'WARDEN',
        login_url='login'
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def student_required(function=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.role == 'STUDENT',
        login_url='login'
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
