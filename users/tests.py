from datetime import timedelta
from http import HTTPStatus

from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.utils.timezone import now

from users.models import EmailVerification, User


class UserRegistrationViewTestCase(TestCase):

    def setUp(self) -> None:
        self.path = reverse('users:registration')
        self.data = {
            'first_name': 'test_fn',
            'last_name': 'test_ln',
            'username': 'testusername',
            'email': 'test@mail.ru',
            'password1': 'testPassword1',
            'password2': 'testPassword1'
        }

    def test_user_registration_get(self):
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], 'Store - Регистрация')
        self.assertTemplateUsed(response, 'users/register.html')

    @override_settings(CELERY_TASK_EAGER_PROPAGATES=True,
                       CELERY_TASK_ALWAYS_EAGER=True,
                       BROKER_BACKEND='memory',
                       EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend')
    def test_user_registration_post_success(self):
        username = self.data['username']
        self.assertFalse(User.objects.filter(username=username).exists())
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('users:login'))
        self.assertTrue(User.objects.filter(username=username).exists())

        email_verification = EmailVerification.objects.filter(user__username=username)
        self.assertTrue(email_verification.exists())
        self.assertEqual(
            email_verification.first().expiration.date(),
            (now() + timedelta(hours=48)).date()
        )
        self.assertTrue(User.objects.filter(username=username).exists())

    def test_user_registration_post_error(self):
        username = self.data['username']
        User.objects.create(username=username)
        response = self.client.post(self.path, self.data)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Пользователь с таким именем уже существует.', html=True)


class UserLoginViewTestCase(TestCase):

    def setUp(self) -> None:
        self.path = reverse('users:login')
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

    def test_user_login_get(self):
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context_data['title'], 'Store - Авторизация')
        self.assertTemplateUsed(response, 'users/login.html')

    def test_user_login_post_success(self):
        response_before = self.client.get(reverse('index'))
        self.assertFalse(response_before.context['user'].is_authenticated)
        response = self.client.post(self.path, {'username': 'testusername', 'password': 'TestPassword1'})

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('index'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_user_login_post_error(self):
        response_before = self.client.get(reverse('index'))
        self.assertFalse(response_before.context['user'].is_authenticated)
        response = self.client.post(self.path, {'username': 'testusername', 'password': 'WrongPass'})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/login.html')
        self.assertFalse(response.context['user'].is_authenticated)
