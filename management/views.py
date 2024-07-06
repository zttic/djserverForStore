from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

# Create your views here.
# Create your views here.
from rest_framework import viewsets
from core.models import *
from .serializers import *




class CheckSessionViewSet(APIView):
    print('CheckSessionViewSet')
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        print('CheckSessionViewSet get')
        print(request)
        if request.user.is_authenticated:
            return Response({'isAuthenticated': True}, status=status.HTTP_200_OK)
        else:
            return Response({'isAuthenticated': False}, status=status.HTTP_401_UNAUTHORIZED)
        
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import requests
import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def UploadImageToCOSViewSet(request):
    # permission_classes = [IsAuthenticated]
    secret_id = os.getenv('SECRET_ID')
    secret_key = os.getenv('SECRET_KEY')
    region = os.getenv('REGION')
    bucket = os.getenv('BUCKET')
    token = None
    scheme = 'https'
    config = CosConfig(Region=region, SecretId=secret_id,
                       SecretKey=secret_key, Token=token, Scheme=scheme)
    client = CosS3Client(config)
    
    if request.method == 'POST':
        print('UploadImageToOSSViewSet post')
        data = json.loads(request.body)
        print(data)
        url = client.get_presigned_url(
            Method='PUT',
            Bucket=bucket,
            Key=data['key'],
            Expired=120  # 120秒后过期，过期时间请根据自身场景定义
        )
        if url is None:
            return JsonResponse({'detail': 'Failed to upload image.'}, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse({'url': url}, status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        print('UploadImageToOSSViewSet delete')
        print(request.data)
        data = json.loads(request.body)
        response = client.delete_object(
            Bucket=bucket,
            Key=data['key'],
        )
        return Response({'detail': 'Successfully deleted image.'}, status=status.HTTP_200_OK)



class DeleteImageFromCOSViewSet(APIView):
    # permission_classes = [IsAuthenticated]

    secret_id = os.getenv('SECRET_ID')
    secret_key = os.getenv('SECRET_KEY')
    region = os.getenv('REGION')
    bucket = os.getenv('BUCKET')
    token = None
    scheme = 'https'
    config = CosConfig(Region=region, SecretId=secret_id,
                       SecretKey=secret_key, Token=token, Scheme=scheme)
    client = CosS3Client(config)

    def post(self, request, *args, **kwargs):
        print('DeleteImageFromCOSViewSet post')
        print(request.data)
        response = self.client.delete_object(
            Bucket=self.bucket,
            Key=request.data.get('key'),
        )
        return Response({'detail': 'Successfully deleted image.'}, status=status.HTTP_200_OK)


class LogoutViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print('LogoutViewSet post')
        logout(request)
        return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)

class RegisterViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save()


class LoginViewSet(APIView):
    permission_classes = [AllowAny] # 根据需要调整

    def post(self, request, *args, **kwargs):
        print('LoginViewSet post')
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({'detail': 'Successfully logged in.'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


# 添加条目
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer

class ProductViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = Product.objects.filter(isShow=True)
    serializer_class = ProductSerializer
    secret_id = os.getenv('SECRET_ID')
    secret_key = os.getenv('SECRET_KEY')
    region = os.getenv('REGION')
    bucket = os.getenv('BUCKET')
    token = None
    scheme = 'https'
    config = CosConfig(Region=region, SecretId=secret_id,
                       SecretKey=secret_key, Token=token, Scheme=scheme)
    client = CosS3Client(config)


    def perform_create(self, serializer):
        serializer.save()

    def retrieve(self, request, *args, **pk):
        print('ProductViewSet retrieve')
        try:
            product = self.get_object()
            # 添加图片的预签名链接
            signed_url = []
            presigned_imgurl = self.client.get_presigned_url(
                Method='GET',
                Bucket=self.bucket,
                Key=product.imgurl,
                Expired=120
            )
            signed_url.append({
                'original_url': product.imgurl,
                'presigned_url': presigned_imgurl
            })
            # product.imgurl = signed_url

            gallery_with_presigned_urls = []
            for img in product.gallery.all():
                presigned_url = self.client.get_presigned_url(
                    Method='GET',
                    Bucket=self.bucket,
                    Key=img.imgurl,
                    Expired=120
                )
                gallery_with_presigned_urls.append({
                    'original_url': img.imgurl,
                    'presigned_url': presigned_url
                })

            serializer = self.get_serializer(product)
            data = serializer.data
            data['gallery'] = gallery_with_presigned_urls
            data['imgurl'] = signed_url

            return Response(data)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request, *args, **pk):
        print('ProductViewSet list')
        queryset = self.filter_queryset(self.get_queryset())
        for product in queryset:
            product.imgurl = self.client.get_presigned_url(
                Method='GET',
                Bucket=self.bucket,
                Key=product.imgurl,
                Expired=120  # 120秒后过期，过期时间请根据自身场景定义
            )

        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    



