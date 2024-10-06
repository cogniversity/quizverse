# quiz/decorators.py

from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from .models import Profile

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.profile.is_admin:
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied  # You could also redirect to a different page if you prefer.
    return _wrapped_view
