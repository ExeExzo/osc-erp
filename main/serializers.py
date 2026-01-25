from rest_framework import serializers
from .models import PurchaseRequest, PurchaseItem, Supplier, Customer
from django.conf import settings

User = settings.AUTH_USER_MODEL


class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItem
        fields = ["id", "name", "description", "quantity", "price", "total"]
        read_only_fields = ["total"]

    def create(self, validated_data):
        # автоматически считаем total
        validated_data['total'] = validated_data['quantity'] * validated_data['price']
        return super().create(validated_data)


class PurchaseRequestSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True)
    
    amount_without_vat = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    amount_with_vat = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = PurchaseRequest
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        # calculate totals
        total_without_vat = sum([item['quantity'] * item['price'] for item in items_data])
        vat_percent = validated_data.get('vat_percent', 12)
        total_with_vat = total_without_vat * (1 + vat_percent / 100)

        validated_data['amount_without_vat'] = total_without_vat
        validated_data['amount_with_vat'] = total_with_vat

        request = PurchaseRequest.objects.create(**validated_data)

        for item_data in items_data:
            PurchaseItem.objects.create(request=request, **item_data)

        return request


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'