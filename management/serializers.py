from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from core.models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'id']


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['name', 'id']




# 分别添加商品主条目，类别条目，商品图片条目到三个表当中
class ItemofProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemofProduct
        fields = ['name', 'price']

class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ['imgurl']

class ProductSerializer(serializers.ModelSerializer):
    item = ItemofProductSerializer(many=True)
    gallery = GallerySerializer(many=True)
    class Meta:
        model = Product
        fields = ['name', 'imgurl', 'isShow', 'categoryId', 'unit', 'item', 'gallery', 'id']
    
    def __init__(self, *args, **kwargs):
        super(ProductSerializer, self).__init__(*args, **kwargs)
        if 'context' in kwargs and 'request' in kwargs['context']:
            request = kwargs['context']['request']
            if request.method in ['POST']:  # 如果是创建操作
                self.fields.pop('id', None)  # 创建时移除 id 字段

    def create(self, validated_data):
        item_data = validated_data.pop('item')
        gallery = validated_data.pop('gallery')
        product = Product.objects.create(**validated_data)
        for item in item_data:
            ItemofProduct.objects.create(productId=product, **item)
        for img in gallery:
            Gallery.objects.create(productId=product, **img)

        return product
    
    # def validate_price(self, value):
    #     if value < 0:
    #         raise serializers.ValidationError("价格必须大于0")
    #     return value

