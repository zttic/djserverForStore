from rest_framework import serializers, status
from core.models import *
from rest_framework.response import Response

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'imgurl', 'unit']

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['name', 'id']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'id']

class ItemofProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemofProduct
        fields = ['id', 'name', 'price', 'imgurl', 'description', 'available', 'sortOrder']

class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ['id', 'imgurl']

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'userId', 'productId', 'itemId', 'quantity', 'date', 'selected']
        read_only_fields = ['total_price', 'price']

    def create(self, validated_data):
        print('CartSerializer create')
        id = validated_data.get('itemId')
        quantity = validated_data.get('quantity')
        price = validated_data.get('price')
        item = ItemofProduct.objects.get(id=id)
        price = item.price
        
        total = quantity * price
        validated_data['price'] = price
        validated_data['total_price'] = total  # 计算总价
        cart = Cart.objects.create(**validated_data)
        return cart


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'productId',
                  'itemId', 'quantity', 'price', 'product_name', 'item_name']
        
class OrderSerializer(serializers.ModelSerializer):
    orderItem = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = ['id', 'userId', 'date', 'total_price', 'total_quantity', 'status', 'payMethod', 'orderItem']

    def create(self, validated_data):
        # 实现创建订单以及订单项的逻辑
        total_price = 0
        total_quantity = 0
        order_items_data = validated_data.pop('orderItem')
        order = Order.objects.create(**validated_data)

        for item_data in order_items_data:
            OrderItem.objects.create(orderId=order, **item_data)
            total_price += item_data['price'] * item_data['quantity']
            total_quantity += 1

        order.total_price = total_price
        order.total_quantity = total_quantity
        order.status = 1
        order.data = timezone.now()
        order.save()
        return order
    
class AuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['phone_number']
    
    def create(self, validated_data):
        return super().create(validated_data)

