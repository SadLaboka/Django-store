from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from products.models import Product, ProductCategory


class IndexViewTestCase(TestCase):

    def test_view(self):
        path = reverse('index')
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], 'Store')
        self.assertTemplateUsed(response, 'products/index.html')


class ProductsListViewTestCase(TestCase):
    fixtures = ['categories.json', 'goods.json']

    def setUp(self):
        self.products = Product.objects.all()
        self.category = ProductCategory.objects.first()

    def test_list(self):
        path = reverse('products:index')
        response = self.client.get(path)
        self._common_tests(response)

        self.assertEqual(list(response.context_data['object_list']), list(self.products[:1]))

    def test_list_with_category(self):
        path = reverse('products:category', kwargs={'category_id': self.category.id})
        response = self.client.get(path)
        self._common_tests(response)

        self.assertEqual(
            list(response.context_data['object_list']),
            list(self.products.filter(category_id=self.category.id)[:1])
        )

    def test_list_with_page(self):
        path = reverse('products:paginator', kwargs={'page': 2})
        response = self.client.get(path)
        self._common_tests(response)

        self.assertEqual(list(response.context_data['object_list']), list(self.products[1:2]))

    def test_list_with_category_and_page(self):
        path = reverse(
            'products:category_paginator',
            kwargs={'category_id': self.category.id, 'page': 2}
        )
        response = self.client.get(path)
        self._common_tests(response)

        self.assertEqual(
            list(response.context_data['object_list']),
            list(self.products.filter(category_id=self.category.id)[1:2])
        )

    def _common_tests(self, response):
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], 'Store - Каталог')
        self.assertTemplateUsed(response, 'products/products.html')
