from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class CreationFormTests(TestCase):

    def test_new_user(self):
        """При регистрации создается новый пользователь."""
        count_users = User.objects.count()
        form_data = {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'username': 'IVAN',
            'email': 'i.ivan@gmail.com',
            'password1': 'test_pass',
            'password2': 'test_pass'
        }
        response = self.client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(User.objects.count(), count_users + 1)
