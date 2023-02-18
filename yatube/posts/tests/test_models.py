from django.contrib.auth import get_user_model
from django.test import TestCase

import constants as c

from ..models import Group, Post

User = get_user_model()


class PostsModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=c.USERNAME_AUTHOR)
        cls.group = Group.objects.create(
            title=c.GROUP_TITLE,
            slug=c.GROUP_SLUG,
            description=c.GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=c.POST_TEXT,
        )

    def test_models_post_and_group_correct_object_names(self):
        """Проверяем, что у моделей post и group корректно работает __str__."""
        post = PostsModelsTest.post
        group = PostsModelsTest.group
        data = {post: (str(post), post.text[:c.LEN_OF_STR_METHOD_IN_POST]),
                group: (str(group), group.title)}
        for key, value in data.items():
            actual_value, expected = value
            with self.subTest(
                model=key, expected=expected, actual_value=actual_value
            ):
                self.assertEqual(expected, actual_value)

    def test_verbose_name_post_and_group(self):
        """verbose_name в полях модели Post и Group совпадает с ожидаемым."""
        post = PostsModelsTest.post
        group = PostsModelsTest.group
        field_verboses = {
            ('text', 'Текст поста'): post,
            ('pub_date', 'Дата и время публикации'): post,
            ('author', 'Автор поста'): post,
            ('group', 'Группа'): post,
            ('title', 'Заголовок'): group,
            ('description', 'Описание группы'): group
        }
        for value, model in field_verboses.items():
            field, expected_value = value
            with self.subTest(
                model=model, field=field, expected_value=expected_value
            ):
                self.assertEqual(
                    model._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_text_post_and_group(self):
        """help_text в полях модели Post и Group совпадает с ожидаемым."""
        post = PostsModelsTest.post
        group = PostsModelsTest.group
        fields_help_text = {
            ('text', 'Введите текст поста'): post,
            ('group', 'Группа, к которой будет относиться пост'): post,
            ('description', 'Краткое описание группы'): group,
        }
        for value, model in fields_help_text.items():
            field, expected_value = value
            with self.subTest(
                model=model, field=field, expected_value=expected_value
            ):
                self.assertEqual(
                    model._meta.get_field(field).help_text, expected_value
                )
