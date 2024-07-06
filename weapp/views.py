from django.shortcuts import render
from django.db.models import Max, Min

import requests
import json
import os


# Create your views here.
from rest_framework import viewsets, mixins
from rest_framework import status
from rest_framework.decorators import action
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token

from core.models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
# cos
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'current_page': self.page.number,  # 添加当前页码
            'total_pages': self.page.paginator.num_pages,  # 总页数
            'results': data
        })

class UnitViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Unit.objects.filter(isShow=True)
    serializer_class = UnitSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.all()
        serializer = self.serializer_class(queryset, many=True)
        custom_data = {
            "code": 0,
            "data": serializer.data
        }
        return Response(custom_data, status=status.HTTP_200_OK)

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination

    secret_id = os.getenv('SECRET_ID')
    secret_key = os.getenv('SECRET_KEY')
    region = os.getenv('REGION')
    bucket = os.getenv('BUCKET')

    token = None
    scheme = 'https'
    config = CosConfig(Region=region, SecretId=secret_id,
                       SecretKey=secret_key, Token=token, Scheme=scheme)
    client = CosS3Client(config)


    def list(self, request, *args, **kwargs):
        print('ProductViewSet list')
        category_id = int(request.query_params.get('id'))
        print('category_id:', category_id)
        if category_id is None:
            return Response({"error": "categoryId is required"}, status=status.HTTP_400_BAD_REQUEST)
        if category_id == 0:
            print('product_id == 0')
            queryset = self.queryset.all()
        else:
            queryset = self.queryset.filter(categoryId=category_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            print('page is not None')
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
            for item in data:
                item['imgurl'] = self.client.get_presigned_url(
                    Method='GET',
                    Bucket=self.bucket, 
                    Key=item['imgurl'], 
                    Expired=300)
                
            custom_data = {
                "code": 0,
                "data": data
            }
            return self.get_paginated_response(custom_data)
        # serializer = self.serializer_class(queryset, many=True)
        data = serializer.data
        custom_data = {
            "code": 0,
            "data": data
        }
        return Response(custom_data, status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ItemofProductViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = ItemofProduct.objects.all()
    serializer_item = ItemofProductSerializer

    queryset_product = Product.objects.all()
    serializer_product = ProductSerializer

    queryset_gallery = Gallery.objects.all()
    serializer_gallery = GallerySerializer


    secret_id = os.getenv('SECRET_ID')
    secret_key = os.getenv('SECRET_KEY')
    region = os.getenv('REGION')
    bucket = os.getenv('BUCKET')
    token = None
    scheme = 'https'
    config = CosConfig(Region=region, SecretId=secret_id,
                       SecretKey=secret_key, Token=token, Scheme=scheme)
    client = CosS3Client(config)

    def list(self, request, *args, **kwargs):
        print('ItemofProductViewSet list')
        product_id = int(request.query_params.get('id'))
        print('product_id:', product_id)
        if product_id is None:
            return Response({"error": "productId is required"}, status=status.HTTP_400_BAD_REQUEST)
        queryset = self.queryset.filter(productId=product_id)
        price_extremes = queryset.aggregate(Max('price'), Min('price'))
        


        product = self.queryset_product.get(id=product_id)
        product_serializer = self.serializer_product(product)
        product_data = product_serializer.data
        if price_extremes['price__min'] == price_extremes['price__max']:
            product_data['retail_price'] = f"{price_extremes['price__min']}"
        else:
            product_data['retail_price'] = f"{price_extremes['price__min']}~{price_extremes['price__max']}"

        gallery = self.queryset_gallery.filter(productId=product_id)
        gallery_serializer = self.serializer_gallery(gallery, many=True)

        for item in gallery_serializer.data:
            item['imgurl'] = self.client.get_presigned_url(
                Method='GET',
                Bucket=self.bucket, 
                Key=item['imgurl'], 
                Expired=300)
        
        serializer = self.serializer_item(queryset, many=True)
        data = serializer.data
        custom_data = {
            "code": 0,
            "data": data,
            "product": product_data,
            "gallery": gallery_serializer.data
        }
        return Response(custom_data, status=status.HTTP_200_OK)
    

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    queryset_product = Product.objects.all()
    serializer_product = ProductSerializer

    queryset_item = ItemofProduct.objects.all()
    serializer_item = ItemofProductSerializer

    secret_id = os.getenv('SECRET_ID')
    secret_key = os.getenv('SECRET_KEY')
    region = os.getenv('REGION')
    bucket = os.getenv('BUCKET')
    token = None
    scheme = 'https'
    config = CosConfig(Region=region, SecretId=secret_id,
                       SecretKey=secret_key, Token=token, Scheme=scheme)
    client = CosS3Client(config)

    # def perform_create(self, serializer):
    #     print('CartViewSet perform_create')
    #     serializer.save()
    #     return Response({"code": 0, "data": "success"}, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        print('CartViewSet create')
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({"code": 0, "data": "success"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        data = self.get_serializer(queryset, many=True).data
        # print('data:', data)
        for item in data:
            print('item:', item)
            productid = item['productId']
            itemid = item['itemId']
            if productid not in self.queryset_product.values_list('id', flat=True):
                continue
            product = self.queryset_product.get(id=productid)
            itemofproduct = self.queryset_item.get(id=itemid)
            item['product_name'] = product.name
            item['item_name'] = itemofproduct.name
            item['price'] = itemofproduct.price
            item['isShow'] = product.isShow
            item['imgurl'] = self.client.get_presigned_url(
                Method='GET',
                Bucket=self.bucket, 
                Key=product.imgurl, 
                Expired=300)
        


        serializer = self.get_serializer(queryset, many=True)
        cartTotal = self.cartTotal(serializer.data)
        custom_response_data = {
            'code': 0, 
            'data': data,
            'cartTotal': cartTotal,
        }
        return Response(custom_response_data, status=status.HTTP_200_OK)

    def cartTotal(self, data):
        count = 0
        sumprice = 0
        cartTotal = {}
        for item in data:
            if item['selected']:
                itemid = item['itemId']
                itemofproduct = self.queryset_item.get(id=itemid)
                price = itemofproduct.price
                sumprice += price * item['quantity']
                count += 1
        
        cartTotal['sumprice'] = sumprice
        cartTotal['count'] = count
        return cartTotal

    
    def update(self, request, *args, **kwargs):
        # Check if it's a partial update (PATCH)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        print(instance)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            self.perform_update(serializer)
            queryset = self.filter_queryset(self.get_queryset())
            cartTotal = self.cartTotal(
                self.get_serializer(queryset, many=True).data)

            custom_response_data = {
                'code': 0, 
                'data': serializer.data,
                'cartTotal': cartTotal
            }
            return Response(custom_response_data, status=status.HTTP_200_OK)
        else:
            # Return error details if the data is not valid
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        print("CartViewSet delete")
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
        except Exception as e:
            return Response({'code': 1}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'code': 0}, status=status.HTTP_200_OK)



class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        print('OrderViewSet perform_create')
        serializer.save()
        return Response({"code": 0, "data": "success"}, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response({"code": 0, "data": "success"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AuthViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = AuthSerializer
    access_token = ''
    wechat_api = "https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token="

    appid = os.getenv('APPID')
    secret = os.getenv('SECRET')

    def get_weapp_token(self):
        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.appid,
            "secret": self.secret,
        }
        try:
            response = requests.get(url, params=params, verify=True)
            response_data = response.json()  # 假设返回的是JSON格式的数据
            self.access_token = response_data['access_token']
            return Response(status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            # 处理请求异常
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(methods=['post'], detail=False, url_path='check')
    def auth_phone_number(self, request, *args, **kwargs):
        self.get_weapp_token()

        print('AuthViewSet auth_phone_number')
        url = "https://api.weixin.qq.com/wxa/business/getuserphonenumber"
        print("code:", request.data['code'])
        params = {
            "access_token": self.access_token
        }
        data = {
            "code": request.data['code'],
        }
        print("access_token:", self.access_token)
        try:
            response = requests.post(url, data=json.dumps(data), params=params, verify=True)

            response_data = response.json()
            print("response_data:", response_data)
            watermark_appid = response_data['phone_info']['watermark']['appid']
            print("watermark_appid:", watermark_appid)
            if watermark_appid != self.appid:
                return Response({'error': 'error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                phone_number = response_data['phone_info']['phoneNumber']
                print("phone_number:", phone_number)
                try:
                    customer = Customer.objects.get(phone_number=phone_number)
                except Customer.DoesNotExist:
                    # 不存在用户则创建
                    user = User.objects.create_user(username=phone_number)
                    customer = Customer(user=user, phone_number=phone_number)
                    # serializer = self.get_serializer(data={"phone_number": phone_number, "user": user})
                    customer.save()
                    token = Token.objects.create(user=user)
                    return Response({
                            'code': 0,
                            'token': token.key,
                            'user': self.obscure_phone_number(phone_number)
                        }, status=status.HTTP_200_OK)
        
                user = User.objects.get(username=phone_number)
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    'code': 0,
                    'token': token.key,
                    'user': self.obscure_phone_number(phone_number)
                }, status=status.HTTP_200_OK)


        except requests.exceptions.RequestException as e:
            return Response(e, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def obscure_phone_number(self, phone_number):
        if not isinstance(phone_number, str) or len(phone_number) < 10:
            raise ValueError("Invalid phone number")

        prefix = phone_number[:3]
        suffix = phone_number[-4:]
        obscured_middle = '*' * (len(phone_number) - 7)  # 中间部分的长度

        return prefix + obscured_middle + suffix
    