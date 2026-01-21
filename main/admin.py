from django.contrib import admin
from .models import (
    Supplier,
    Customer,
    PurchaseRequest,
    PurchaseItem,
    RequestDocument
)
from django.utils.translation import gettext_lazy as _


# --------------------
# SUPPLIER
# --------------------
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "bin_iin", "phone", "email")
    search_fields = ("name", "bin_iin")
    list_filter = ("name",)


# --------------------
# CUSTOMER / DEPARTMENT
# --------------------
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


# --------------------
# INLINE ITEMS
# --------------------
class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1
    fields = ("name", "description", "quantity", "price", "total")
    readonly_fields = ("total",)


# --------------------
# INLINE DOCUMENTS
# --------------------
class RequestDocumentInline(admin.TabularInline):
    model = RequestDocument
    extra = 1
    fields = ("file", "type", "uploaded_by", "uploaded_at")
    readonly_fields = ("uploaded_at",)


# --------------------
# PURCHASE REQUEST
# --------------------
@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):

    list_display = (
        "ro_number",
        "supplier",
        "customer",
        "creator",
        "manager",
        "amount_with_vat",
        "status",
        "payment_date",
        "created_at",
    )

    list_filter = (
        "status",
        "supplier",
        "customer",
        "created_at",
        "payment_date",
    )

    search_fields = (
        "ro_number",
        "supplier__name",
        "creator__email",
        "manager__email",
    )

    ordering = ("-created_at",)

    inlines = [PurchaseItemInline, RequestDocumentInline]

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Основная информация", {
            "fields": ("ro_number", "status", "creator", "manager")
        }),
        ("Контрагенты", {
            "fields": ("supplier", "customer")
        }),
        ("Финансы", {
            "fields": ("amount_without_vat", "vat_percent", "amount_with_vat", "payment_date")
        }),
        ("Сроки и комментарии", {
            "fields": ("ddl", "comment", "accountant_comment")
        }),
        ("Системные поля", {
            "fields": ("created_at", "updated_at")
        }),
    )

    actions = ["mark_as_approved", "mark_as_rejected", "mark_as_paid"]

    # --------------------
    # ADMIN ACTIONS
    # --------------------
    @admin.action(description="✅ Одобрить")
    def mark_as_approved(self, request, queryset):
        queryset.update(status=PurchaseRequest.Status.APPROVED)

    @admin.action(description="❌ Отклонить")
    def mark_as_rejected(self, request, queryset):
        queryset.update(status=PurchaseRequest.Status.REJECTED)

    @admin.action(description="💰 Отметить как оплачено")
    def mark_as_paid(self, request, queryset):
        queryset.update(status=PurchaseRequest.Status.PAID)
