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

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS("Superuser already exists"))
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        self.stdout.write(self.style.SUCCESS("Superuser created"))
