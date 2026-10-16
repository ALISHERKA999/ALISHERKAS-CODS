
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, Product


@override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
class ModeratorPermissionTests(APITestCase):

    def setUp(self):
        User = get_user_model()

        self.moderator = User.objects.create_user(
            email='moderator_test@example.com',
            phone_number='996700111222',
            password='TestPassword123!',
            is_staff=True
        )

        self.regular_user = User.objects.create_user(
            email='regular_test@example.com',
            phone_number='996700111333',
            password='TestPassword123!',
            is_staff=False
        )

        self.category = Category.objects.create(name='Электроника')

        self.product = Product.objects.create(
            title='Тестовый телефон',
            description='Описание телефона',
            price='1000.00',
            category=self.category
        )

        self.list_url = '/api/v1/products/'
        self.detail_url = f'/api/v1/products/{self.product.id}/'

    def test_moderator_can_view_products(self):
        self.client.force_authenticate(user=self.moderator)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_moderator_cannot_create_product(self):
        self.client.force_authenticate(user=self.moderator)

        response = self.client.post(
            self.list_url,
            {
                'title': 'Новый телефон',
                'description': 'Описание',
                'price': '2000.00',
                'category': self.category.id
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product.objects.count(), 1)

    def test_moderator_can_update_product(self):
        self.client.force_authenticate(user=self.moderator)

        response = self.client.patch(
            self.detail_url,
            {'title': 'Изменённый телефон'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.product.refresh_from_db()
        self.assertEqual(self.product.title, 'Изменённый телефон')

    def test_moderator_can_delete_product(self):
        self.client.force_authenticate(user=self.moderator)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    def test_regular_user_cannot_update_product(self):
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.patch(
            self.detail_url,
            {'title': 'Чужое изменение'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_cannot_delete_product(self):
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

