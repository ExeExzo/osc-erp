from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from django.utils.translation import gettext_lazy as _

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Роль", {"fields": ("role",)}),
    )
    list_display = ("username", "email", "role", "is_staff", "is_superuser")
    list_filter = ("role",)
