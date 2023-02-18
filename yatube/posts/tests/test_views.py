import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

import constants as c
from posts.models import Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=c.SMALL_GIF,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username=c.USERNAME_AUTHOR,
                                            email=c.EMAIL_USER,
                                            password=c.PASSWORD,)
        cls.user_new = User.objects.create_user(username=c.USERNAME_NEW,
                                                email=c.EMAIL_USER_NEW,
                                                password=c.PASSWORD,)
        cls.post1 = Post.objects.create(
            author=cls.user,
            text=c.POST_TEXT,
            group=Group.objects.create(title=c.GROUP_TITLE,
                                       slug=c.GROUP_SLUG),
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            c.INDEX_TEMPLATE: reverse('posts:index'),
            c.CREATE_POST_TEMPLATE: reverse('posts:post_create'),
            c.GROUP_LIST_TEMPLATE: (
                reverse('posts:group_list',
                        kwargs={'slug': self.post1.group.slug})
            ),
            c.PROFILE_TEMPLATE: reverse(
                'posts:profile', kwargs={'username': self.post1.author}
            ),
            c.POST_DETAIL_TEMPLATE: (
                reverse('posts:post_detail', kwargs={'post_id': self.post1.id})
            ),
            c.UPDATE_POST_TEMPLATE: (reverse('posts:post_edit',
                                     kwargs={'post_id': self.post1.id}))
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_show_correct_context(self):
        """Шаблоны сформированы с правильным контекстом."""
        url_names = (
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': self.post1.group.slug}),
            reverse('posts:profile', kwargs={'username': self.post1.author}),
        )
        for url in url_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                first_object = response.context['page_obj'][0]
                post_text_0 = first_object.text
                post_image_0 = first_object.image
                post_author_0 = first_object.author.username
                post_group_title_0 = first_object.group.title
                post_group_slug_0 = first_object.group.slug
                self.assertEqual(post_text_0, c.POST_TEXT)
                self.assertEqual(post_image_0, self.post1.image)
                self.assertEqual(post_author_0, c.USERNAME_AUTHOR)
                self.assertEqual(post_group_title_0, c.GROUP_TITLE)
                self.assertEqual(post_group_slug_0, c.GROUP_SLUG)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post1.id}))
        post_object = response.context['post']
        post_text = post_object.text
        post_image = post_object.image
        post_author = post_object.author.username
        post_group_title = post_object.group.title
        post_group_slug = post_object.group.slug
        self.assertEqual(post_text, c.POST_TEXT)
        self.assertEqual(post_image, self.post1.image)
        self.assertEqual(post_author, c.USERNAME_AUTHOR)
        self.assertEqual(post_group_title, c.GROUP_TITLE)
        self.assertEqual(post_group_slug, c.GROUP_SLUG)

    def test_post_edit_show_correct_context(self):
        """Шаблон create_post для post_edit сформирован
        с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post1.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_another_group(self):
        """Пост не попал в другую группу."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={'slug': self.post1.group.slug}))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertTrue(post_text_0, 'Пост попал в чужую группу')

    def test_new_post_on_the_right_pages(self):
        """Созданный пост отобразился на нужных страницах."""

        desired_pages = (
            reverse('posts:index'),
            reverse(
                'posts:group_list', kwargs={'slug': self.post1.group.slug}),
            reverse('posts:profile', kwargs={'username': self.post1.author}),
        )
        for page in desired_pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertIn(self.post1.text, response.content.decode())

    def test_new_post_not_on_the_another_pages(self):
        """Созданный пост не отобразился на чужих страницах."""

        post2 = Post.objects.create(
            author=self.user_new,
            text=c.POST_TEXT_NEW,
            group=Group.objects.create(title=c.GROUP_TITLE_NEW,
                                       slug=c.GROUP_SLUG_NEW)
        )
        desired_pages = (
            reverse(
                'posts:group_list', kwargs={'slug': self.post1.group.slug}),
            reverse('posts:profile', kwargs={'username': self.post1.author}),
        )
        for page in desired_pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertNotIn(post2.text, response.content.decode())


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=c.USERNAME_AUTHOR,
                                              email=c.EMAIL_USER,
                                              password=c.PASSWORD,)
        cls.group = Group.objects.create(
            title=(c.GROUP_TITLE),
            slug=c.GROUP_SLUG,)
        Post.objects.bulk_create([
            Post(
                text=f'{c.POST_TEXT} {i}', author=cls.author, group=cls.group
            ) for i in range(c.POSTS_PER_PAGE + 3)
        ])

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_first_page_contains_ten_posts(self):
        """Проверка количества постов на первой странице."""
        list_urls = (
            reverse('posts:index'),
            reverse("posts:group_list", kwargs={"slug": self.group.slug}),
            reverse("posts:profile", kwargs={"username": self.author}),
        )
        for tested_url in list_urls:
            response = self.client.get(tested_url)
            self.assertEqual(
                len(response.context.get('page_obj').object_list),
                c.POSTS_PER_PAGE
            )

    def test_second_page_contains_three_posts(self):
        """Проверка количества постов на второй странице."""
        list_urls = (
            reverse('posts:index') + "?page=2",
            reverse(
                "posts:group_list", kwargs={"slug": self.group.slug}
            ) + "?page=2",
            reverse(
                "posts:profile", kwargs={"username": self.author}
            ) + "?page=2",
        )
        for tested_url in list_urls:
            response = self.client.get(tested_url)
            self.assertEqual(
                len(response.context.get('page_obj').object_list), 3)


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(username=c.USERNAME_AUTHOR,
                                            email=c.EMAIL_USER,
                                            password=c.PASSWORD,),
            text=c.POST_TEXT)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username=c.USERNAME_NEW)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_index(self):
        """Тест кэширования страницы index.html"""
        first_response = self.authorized_client.get(reverse('posts:index'))
        post_object = Post.objects.get(id=self.post.id)
        post_object.text = c.POST_TEXT_NEW
        post_object.save()
        second_response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(first_response.content, second_response.content)
        cache.clear()
        third_response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(first_response.content, third_response.content)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_follower = (
            User.objects.create_user(username=c.USERNAME_NOT_AUTHOR,
                                     email=c.EMAIL_USER_NEW,
                                     password=c.PASSWORD))
        cls.user_following = (
            User.objects.create_user(username=c.USERNAME_AUTHOR,
                                     email=c.EMAIL_USER,
                                     password=c.PASSWORD))
        cls.post = Post.objects.create(
            author=cls.user_following,
            text=c.POST_TEXT
        )

    def setUp(self):
        self.auth_client_follower = Client()
        self.auth_client_following = Client()
        self.auth_client_follower.force_login(self.user_follower)
        self.auth_client_following.force_login(self.user_following)

    def test_follow(self):
        """Авторизованный пользователь может
        подписываться на других пользователей."""
        follow_count = Follow.objects.all().count()
        self.auth_client_follower.get(
            reverse('posts:profile_follow', kwargs={'username':
                    self.user_following.username}))
        self.assertEqual(Follow.objects.all().count(), follow_count + 1)

    def test_unfollow(self):
        """Авторизованный пользователь может
        удалять пользователей из подписок."""
        follow_count = Follow.objects.all().count()
        self.auth_client_follower.get(
            reverse('posts:profile_follow', kwargs={'username':
                    self.user_following.username}))
        self.auth_client_follower.get(
            reverse('posts:profile_unfollow', kwargs={'username':
                    self.user_following.username}))
        self.assertEqual(Follow.objects.all().count(), follow_count)

    def test_subscription_feed(self):
        """Новая запись пользователя появляется в ленте подписчиков,
        и не появляется в ленте тех, кто не подписан."""
        Follow.objects.create(user=self.user_follower,
                              author=self.user_following)
        response = self.auth_client_follower.get(
            reverse('posts:follow_index'))
        post_object = response.context["page_obj"][0]
        post_text_0 = post_object.text
        self.assertEqual(post_text_0, c.POST_TEXT)
        response_not_follow = self.auth_client_following.get(
            reverse('posts:follow_index'))
        self.assertNotContains(response_not_follow, c.POST_TEXT)
