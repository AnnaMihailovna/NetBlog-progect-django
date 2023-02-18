from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

import constants as c

User = get_user_model()


class UserURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username=c.USERNAME_AUTHOR)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_user_urls_exists_at_desired_location(self):
        """Страница с этими url доступны любому пользователю."""
        url_names = (
            reverse('users:logout'),
            reverse('users:signup'),
            reverse('users:login'),
            reverse('users:password_reset_form'),
            reverse(
                'users:password_reset_confirm', args=['<uidb64>', '<token>']),
            reverse('users:password_reset_done'),
            reverse('users:password_reset_complete'),
        )
        for url in url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_url_exists_authorized_only(self):
        """Страницы доступна авторизованному пользователю."""
        url_names = (
            reverse('users:password_change_form'),
            reverse('users:password_change_done'),
        )
        for url in url_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверяем редиректы для неавторизованного пользователя
    def test_url_password_change_redirect_anonymous_on_login(self):
        """Страницы /auth/password_change/ и /auth/password_change/done/
        перенаправят анонимного пользователя на страницу логина.
        """
        url_names = (
            reverse('users:password_change_form'),
            reverse('users:password_change_done'),
        )
        for url in url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
        self.assertRedirects(
            response, f'/auth/login/?next={url}')

    # Проверяем,что запрос к несуществующей странице вернёт ошибку 404
    def test_user_url_unexisting_page(self):
        """Страница /auth/unexisting_page/ возвращает ошибку 404."""
        response = self.guest_client.get('/auth/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    # Проверяем вызываемые HTML-шаблоны
    def test_user_urls_template_name(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('users:logout'): c.LOGOUT_TEMPLATE,
            reverse('users:signup'): c.SIGNUP_TEMPLATE,
            reverse('users:login'): c.LOGIN_TEMPLATE,
            reverse('users:password_reset_form'): c.PASS_RESET_FORM_TEMPLATE,
            reverse('users:password_reset_done'): c.PASS_RESET_DONE_TEMPLATE,
            reverse(
                'users:password_reset_confirm', args=['<uidb64>', '<token>']
            ): c.PASS_RESET_CONFIRM_TEMPLATE,
            reverse(
                'users:password_reset_complete'
            ): c.PASS_RESET_COMPLETE_TEMPLATE,
            reverse('users:password_change_form'): c.LOGIN_TEMPLATE,
            reverse('users:password_change_done'): c.LOGIN_TEMPLATE,
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url, follow=True)
                self.assertTemplateUsed(response, template)
