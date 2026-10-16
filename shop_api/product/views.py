
from rest_framework import generics
from rest_framework.permissions import BasePermission, IsAuthenticated
from common.validators import validate_product_birthdate
from .models import Category, Product, Review
from .permissions import IsModerator
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ReviewSerializer,
    ProductReviewsSerializer
)


class ProductAccessPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        if not request.user.is_authenticated:
            return False

        if request.user.is_staff:
            return IsModerator().has_permission(request, view)

        return request.method == 'POST'

    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        if request.user.is_staff:
            return IsModerator().has_permission(request, view)

        return False


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'id'


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [ProductAccessPermission]
    def create(self, request, *args, **kwargs):
        validate_product_birthdate(request)
        return super().create(request, *args, **kwargs)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [ProductAccessPermission]
    lookup_field = 'id'


class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    lookup_field = 'id'


class ProductReviewsView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductReviewsSerializer
