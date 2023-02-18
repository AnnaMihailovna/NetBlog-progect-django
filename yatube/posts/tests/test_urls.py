from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

import constants as c

from ..models import Group, Post

User = get_user_model()


# smoke test
class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username=c.USERNAME_AUTHOR)
        cls.user_not_author = User.objects.create_user(
            username=c.USERNAME_NOT_AUTHOR)
        cls.group = Group.objects.create(
            title=c.GROUP_TITLE,
            slug=c.GROUP_SLUG,
            description=c.GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text=c.POST_TEXT,
            group=cls.group,
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_not_author = Client()
        self.authorized_client_author.force_login(self.user_author)
        self.authorized_client_not_author.force_login(self.user_not_author)

    def test_urls_exists_at_desired_location(self):
        """Страница с этими url доступны любому пользователю."""
        urls_names = (
            f'/group/{self.group.slug}/',
            f'/profile/{self.user_author.username}/',
            f'/posts/{self.post.id}/',
        )
        for url in urls_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_exists_authorized_only(self):
        """Страница /create/ доступна любому авторизованному пользователю"""
        response = self.authorized_client_not_author.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_exists_authorized_author_only(self):
        """Страница /post/post_id/edit/ доступна
        авторизованному пользователю - автору поста.
        """
        response_author = self.authorized_client_author.get(
            f'/posts/{self.post.id}/edit/')
        self.assertEqual(response_author.status_code, HTTPStatus.OK)
        response_not_author = self.authorized_client_not_author.get(
            f'/posts/{self.post.id}/edit/')
        self.assertRedirects(response_not_author,
                             f'/posts/{self.post.id}/')

    def test_create_post_url_redirect_anonymous_on_login(self):
        """Страницы /create/ и /posts/<post_id>/edit/ перенаправят
        анонимного пользователя на страницу логина.
        """

        url_names = (
            '/create/',
            f'/posts/{self.post.id}/edit/',
        )
        for url in url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
        self.assertRedirects(
            response, f'/auth/login/?next={url}')

    def test_url_unexisting_page(self):
        """Страница /unexisting_page/ возвращает ошибку 404."""

        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_urls_template_name(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.post.group.slug}
                    ): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.user_author.username}
                    ): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}
                    ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}
                    ): 'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client_author.get(url)
                self.assertTemplateUsed(response, template)
