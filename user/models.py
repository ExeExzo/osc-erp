from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _

# Create your models here.

class User(AbstractUser):

    class Role(models.TextChoices):
        EMPLOYEE = 'EMPLOYEE', 'Сотрудник'
        MANAGER = 'MANAGER', 'Менеджер'
        ACCOUNTANT = 'ACCOUNTANT', 'Бухгалтер'
        ADMIN = 'ADMIN', 'Администратор'

    role = models.CharField(_("Role"),
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE,
    )

    # Важно: меняем related_name для групп и прав
    groups = models.ManyToManyField(
        Group,
        verbose_name=_("groups"),
        blank=True,
        related_name="custom_user_set"
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("user permissions"),
        blank=True,
        related_name="custom_user_permissions_set"
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
    
    def save(self, *args, **kwargs):
        if self.role == self.Role.ADMIN:
            self.is_staff = True
            self.is_superuser = True
        elif self.role == self.Role.ACCOUNTANT:
            self.is_staff = True
            self.is_superuser = False
        else:
            self.is_staff = False
            self.is_superuser = False
        super().save(*args, **kwargs)