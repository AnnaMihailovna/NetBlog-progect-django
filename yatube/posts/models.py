from django.contrib.auth import get_user_model
from django.db import models

import constants as c
from core.models import CreatedModel

User = get_user_model()


class Post(CreatedModel):
    text = models.TextField(verbose_name='Текст поста',
                            help_text='Введите текст поста',)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор поста',)
    group = models.ForeignKey('Group', blank=True,
                              null=True, on_delete=models.SET_NULL,
                              verbose_name='Группа',
                              help_text='Группа, к которой '
                              'будет относиться пост',)
    image = models.ImageField('Картинка',
                              upload_to='posts/', blank=True,)

    class Meta:
        ordering = ('-pub_date',)
        default_related_name = 'posts'
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        return self.text[:c.LEN_OF_STR_METHOD_IN_POST]


class Group(models.Model):
    title = models.CharField(verbose_name='Заголовок',
                             max_length=200,)
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name='Описание группы',
                                   help_text='Краткое описание группы',)

    def __str__(self) -> str:
        return self.title


class Comment(CreatedModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             verbose_name='Комментарий поста',
                             related_name='comments',)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор поста',
                               related_name='comments',)
    text = models.TextField(verbose_name='Текст поста',)


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="following")
