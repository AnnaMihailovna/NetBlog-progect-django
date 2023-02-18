from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

import constants as c


class AboutURLTests(TestCase):

    def setUp(self):
        # Создаем неавторизованый клиент
        self.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адреса /about/author/ и /about/tech/."""
        urls_about = (
            reverse('about:author'),
            reverse('about:tech'),
        )
        for url in urls_about:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_url_uses_correct_template(self):
        """Проверка шаблона для адресов /about/author/ и /about/tech/."""
        urls_template_names = {
            reverse('about:author'): c.AUTHOR_TEMPLATE,
            reverse('about:tech'): c.TECH_TEMPLATE,
        }
        for url, template_name in urls_template_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template_name)
