from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()

class Command(BaseCommand):
    help = "Create default superuser if not exists"

    def handle(self, *args, **kwargs):
        username = os.getenv("DJANGO_SU_NAME")
        email = os.getenv("DJANGO_SU_EMAIL")
        password = os.getenv("DJANGO_SU_PASSWORD")

        if not username or not password:
            self.stdout.write(self.style.WARNING("Superuser env vars not set"))
            return

        existing = User.objects.filter(username=username).first()
        if existing:
            # ensure existing user is an admin (update role and flags)
            existing.role = User.Role.ADMIN
            existing.is_staff = True
            existing.is_superuser = True
            if email:
                existing.email = email
            existing.save()
            self.stdout.write(self.style.SUCCESS("Existing user updated to superuser"))
            return

        # ensure role is ADMIN so User.save() will keep is_staff/is_superuser True
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            role=User.Role.ADMIN,
        )

        self.stdout.write(self.style.SUCCESS("Superuser created"))
