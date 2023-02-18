from django import forms
from django.test import TestCase
from django.urls import reverse


class SignupTests(TestCase):

    def test_signup_correct_form_context(self):
        """На страницу регистрации передается форма
        с правильным контекстом.
        """
        response = self.client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
