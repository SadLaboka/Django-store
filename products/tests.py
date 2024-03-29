from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from products.models import Product, ProductCategory
from products.views import ProductsListView
from users.models import User


class IndexViewTestCase(TestCase):

    def test_view(self):
        path = reverse('index')
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], 'UltraStore')
        self.assertTemplateUsed(response, 'products/index.html')


class ProductsListViewTestCase(TestCase):
    fixtures = ['categories.json', 'goods.json']

    def setUp(self):
        self.products = Product.objects.all().order_by('-quantity')
        self.category = ProductCategory.objects.first()
        self.paginator = ProductsListView.paginate_by

        self.user = {
            'first_name': 'test_fn',
            'last_name': 'test_ln',
            'username': 'testusername',
            'email': 'test@mail.ru'
        }
        user = User.objects.create(**self.user)
        user.set_password('TestPassword1')
        user.save()
        self.data = {
            'username': self.user['username'],
            'password': 'TestPassword1',
        }
        self.client.post(reverse('users:login'), {'username': 'testusername', 'password': 'TestPassword1'})

    def test_list(self):
        path = reverse('products:index')
        response = self.client.get(path)
        self._common_tests(response)

        self.assertEqual(list(response.context_data['object_list']), list(self.products[:self.paginator]))

    def test_list_with_category(self):
        path = reverse('products:category', kwargs={'category_id': self.category.id})
        response = self.client.get(path)
        self._common_tests(response)

        self.assertEqual(
            list(response.context_data['object_list']),
            list(self.products.filter(category_id=self.category.id)[:self.paginator])
        )

    def test_list_with_page(self):
        path = reverse('products:paginator', kwargs={'page': 2})
        response = self.client.get(path)
        self._common_tests(response)

        self.assertEqual(list(response.context_data['object_list']),
                         list(self.products[self.paginator:self.paginator*2]))

    def test_list_with_category_and_page(self):
        path = reverse(
            'products:category_paginator',
            kwargs={'category_id': self.category.id, 'page': 2}
        )
        response = self.client.get(path)
        self._common_tests(response)

        self.assertEqual(
            list(response.context_data['object_list']),
            list(self.products.filter(category_id=self.category.id)[self.paginator:self.paginator*2])
        )

    def _common_tests(self, response):
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], 'UltraStore - Каталог')
        self.assertTemplateUsed(response, 'products/products.html')
