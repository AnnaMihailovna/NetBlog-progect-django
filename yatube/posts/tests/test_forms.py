import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

import constants as c

from ..models import Comment, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=c.USERNAME_AUTHOR)
        cls.group = Group.objects.create(title=c.GROUP_TITLE,
                                         slug=c.GROUP_SLUG,
                                         description=c.GROUP_DESCRIPTION)
        cls.group_new = Group.objects.create(
            title=c.GROUP_TITLE_NEW,
            slug=c.GROUP_SLUG_NEW,
            description=c.GROUP_DESCRIPTION_NEW
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=c.POST_TEXT,
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        """Валидная форма создает запись в Post
        и редирект на страницу пользователя."""
        count_posts = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=c.SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': c.POST_TEXT_NEW,
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), count_posts + 1)
        self.assertTrue(Post.objects.filter(text=c.POST_TEXT_NEW,
                                            author=self.user,
                                            group=self.group.id,
                                            image='posts/small.gif').exists())
        redirect_url = (
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        self.assertRedirects(response, redirect_url)

    def test_post_edit(self):
        """Валидная форма редактирует запись в Post."""
        form_data = {
            'text': c.POST_TEXT_NEW,
            'group': self.group_new.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.post.refresh_from_db()
        post = Post.objects.get(id=self.post.id)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(post.text, c.POST_TEXT_NEW)
        self.assertEqual(post.group.slug, c.GROUP_SLUG_NEW)
        redirect_url = (
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertRedirects(response, redirect_url)

    def test_not_create_post_anonymous_(self):
        """Неавторизованный пользователь не может отправлять форму."""
        count_posts = Post.objects.count()
        form_data = {
            'text': c.POST_TEXT_NEW,
            'group': self.group.id
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), count_posts)
        self.assertRedirects(response, reverse('users:login') + '?next='
                             + reverse('posts:post_create'))

    def test_add_comment_auth_user(self):
        """Комментарий создается авторизированным пользователем
        и редирект."""
        form_data = {
            'text': c.COMMENT_TEXT,
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertTrue(Comment.objects.filter(
            text=c.COMMENT_TEXT))
        redirect_url = (
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertRedirects(response, redirect_url)

    def test_not_add_comment_anonymous_user(self):
        """Комментарий не создается неавторизированным пользователем
        и редирект."""
        count_comments = Comment.objects.count()
        form_data = {
            'text': c.COMMENT_TEXT,
        }
        response = self.client.post(reverse('posts:add_comment',
                                            kwargs={'post_id': self.post.id}),
                                    data=form_data,
                                    follow=True)
        self.assertFalse(Comment.objects.filter(
            text=c.COMMENT_TEXT))
        self.assertEqual(Comment.objects.count(), count_comments)
        redirect_url = (reverse('users:login') + '?next='
                        + reverse('posts:add_comment',
                        kwargs={'post_id': self.post.id}))
        self.assertRedirects(response, redirect_url)

    def test_create_comment_post_detail(self):
        """После успешной отправки комментарий появляется
        на странице поста."""
        comments_post_detail_count = Comment.objects.filter(
            post=self.post.id).count()
        form_data = {
            'text': c.COMMENT_TEXT,
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(Comment.objects.filter(post=self.post.id).count(),
                         comments_post_detail_count + 1)
        self.assertTrue(Comment.objects.filter(
                        text=c.COMMENT_TEXT, post=self.post.id))
