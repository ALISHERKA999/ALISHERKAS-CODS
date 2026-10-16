from rest_framework import serializers
from django.db.models import Avg

from .models import Category, Product, Review


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'products_count']

    def get_products_count(self, obj):
        return obj.products.count()

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                'Название категории не может быть пустым.'
            )

        if len(value) < 2:
            raise serializers.ValidationError(
                'Название категории должно содержать минимум 2 символа.'
            )

        return value


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                'Название товара не может быть пустым.'
            )

        if len(value) < 2:
            raise serializers.ValidationError(
                'Название товара должно содержать минимум 2 символа.'
            )

        return value

    def validate_description(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                'Описание товара не может быть пустым.'
            )

        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Цена должна быть больше 0.'
            )

        return value


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

    def validate_text(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                'Текст отзыва не может быть пустым.'
            )

        if len(value) < 3:
            raise serializers.ValidationError(
                'Отзыв должен содержать минимум 3 символа.'
            )

        return value

    def validate_stars(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                'Оценка должна быть от 1 до 5.'
            )

        return value


class ProductReviewsSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'description',
            'price',
            'category',
            'reviews',
            'rating'
        ]

    def get_rating(self, obj):
        return obj.reviews.aggregate(
            Avg('stars')
        )['stars__avg']
