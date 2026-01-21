from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import PurchaseRequest, Customer, Supplier
from .serializers import PurchaseRequestSerializer, CustomerSerializer, SupplierSerializer
from .permissions import IsEmployeeOrReadOnly, IsManagerOrAccountant
from user.decorators import admin_or_accountant_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Case, When, IntegerField


@login_required(login_url="/accounts/login/")
def home(request):
    return redirect("/user/profile/")


class PurchaseRequestViewSet(viewsets.ModelViewSet):
    queryset = PurchaseRequest.objects.all().order_by('-created_at')
    serializer_class = PurchaseRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create']:
            self.permission_classes = [IsAuthenticated, IsEmployeeOrReadOnly]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsManagerOrAccountant]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

@login_required
@admin_or_accountant_required
def requests_list_view(request):
    # статусы, которые доступны для фильтрации
    filter_values = [
        PurchaseRequest.Status.WAITING,
        PurchaseRequest.Status.APPROVED,
        PurchaseRequest.Status.REJECTED,
        PurchaseRequest.Status.PAID,
        PurchaseRequest.Status.CANCELLED,
    ]

    # базовый queryset с сортировкой (оставляем аннотацию сортировки)
    requests_qs = PurchaseRequest.objects.annotate(
        sort_order=Case(
            When(status=PurchaseRequest.Status.WAITING, then=1),
            When(status=PurchaseRequest.Status.APPROVED, then=2),
            When(status=PurchaseRequest.Status.PAID, then=3),
            When(status=PurchaseRequest.Status.REJECTED, then=4),
            When(status=PurchaseRequest.Status.CANCELLED, then=5),
            default=99,
            output_field=IntegerField()
        )
    ).order_by("sort_order", "-created_at")

    # применить фильтр по GET-параметру ?status=...
    selected_status = request.GET.get("status", "")
    if selected_status in filter_values:
        requests_qs = requests_qs.filter(status=selected_status)

    # передать в шаблон варианты фильтра (значение, метка)
    # используем только те варианты, которые входят в filter_values
    status_choices = [c for c in PurchaseRequest.Status.choices if c[0] in filter_values]

    return render(request, "request/requests_list.html", {
        "requests": requests_qs,
        "statuses": status_choices,
        "selected_status": selected_status,
    })


@admin_or_accountant_required
def change_request_status(request, pk, status):
    pr = get_object_or_404(PurchaseRequest, pk=pk)

    allowed_statuses = [
        PurchaseRequest.Status.APPROVED,
        PurchaseRequest.Status.REJECTED,
        PurchaseRequest.Status.PAID,
        PurchaseRequest.Status.CANCELLED,
    ]

    if status not in allowed_statuses:
        return redirect("requests_list")

    pr.status = status
    pr.manager = request.user
    pr.save()

    return redirect("requests_list")


class SupplierViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    pagination_class = None
    permission_classes = [AllowAny]

class CustomerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    pagination_class = None
    permission_classes = [AllowAny]


@login_required
def purchase_request(request):
    return render(request, "request/request.html")


@login_required
def my_requests_view(request):
    my_requests = (
        PurchaseRequest.objects
        .filter(creator=request.user)
        .select_related("supplier", "customer")
        .prefetch_related("items")
        .order_by("-created_at")
    )

    return render(request, "request/my_requests.html", {
        "requests": my_requests
    })