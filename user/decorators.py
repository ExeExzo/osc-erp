from django.core.exceptions import PermissionDenied

def admin_or_accountant_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied

        if request.user.role not in ["ADMIN", "ACCOUNTANT"]:
            raise PermissionDenied

        return view_func(request, *args, **kwargs)
    return wrapper
