from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# Create your models here.

# (Поставщик)
class Supplier(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    bin_iin = models.CharField(_("BIN/IIN"), max_length=20, blank=True, null=True)
    phone = models.CharField(_("Phone"), max_length=30, blank=True, null=True)
    email = models.EmailField(_("Email"), blank=True, null=True)
    bank_details = models.TextField(_("Bank details"), blank=True, null=True)

    def __str__(self):
        return self.name
    

# (Отдел)
class Customer(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True, null=True)

    def __str__(self):
        return self.name
    

# (Заказ)
class PurchaseRequest(models.Model):

    class Status(models.TextChoices):
        WAITING = 'WAITING', _('Waiting for review')
        PAID = 'PAID', _('Paid')
        CANCELLED = 'CANCELLED', _('Cancelled')

    ro_number = models.CharField(_("R.O number"), max_length=100, unique=True)

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='created_requests', verbose_name=_("Creator")
    )

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='managed_requests', verbose_name=_("Manager")
    )

    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True,
        related_name='requests', verbose_name=_("Supplier")
    )

    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True,
        related_name='requests', verbose_name=_("Department")
    )

    amount_without_vat = models.DecimalField(_("Amount without VAT"), max_digits=12, decimal_places=2)
    amount_with_vat = models.DecimalField(_("Amount with VAT"), max_digits=12, decimal_places=2)
    vat_percent = models.DecimalField(_("VAT percent"), max_digits=5, decimal_places=2, default=12)

    payment_date = models.DateField(_("Payment date"), blank=True, null=True)
    ddl = models.DateField(_("Deadline"), blank=True, null=True)

    comment = models.TextField(_("Comment"), blank=True, null=True)
    accountant_comment = models.TextField(_("Accountant comment"), blank=True, null=True)

    status = models.CharField(
        _("Status"), max_length=20, choices=Status.choices, default=Status.WAITING
    )

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    def __str__(self):
        return f"{self.ro_number} - {self.supplier}"
    

# (Несколько заказов)
class PurchaseItem(models.Model):
    request = models.ForeignKey(
        PurchaseRequest, on_delete=models.CASCADE, related_name='items'
    )

    name = models.CharField(_("Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True, null=True)

    quantity = models.PositiveIntegerField(_("Quantity"), default=1)
    price = models.DecimalField(_("Price"), max_digits=12, decimal_places=2)
    total = models.DecimalField(_("Total"), max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.quantity})"
    

# (Документы)
class RequestDocument(models.Model):

    class DocType(models.TextChoices):
        INVOICE = 'INVOICE', _('Invoice')
        CONTRACT = 'CONTRACT', _('Contract')
        ACT = 'ACT', _('Act')
        OTHER = 'OTHER', _('Other')

    request = models.ForeignKey(
        PurchaseRequest, on_delete=models.CASCADE, related_name='documents'
    )

    file = models.FileField(_("File"), upload_to='purchase_requests/documents/')
    type = models.CharField(_("Type"), max_length=20, choices=DocType.choices, default=DocType.OTHER)

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )

    uploaded_at = models.DateTimeField(_("Uploaded at"), auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.request.ro_number}"