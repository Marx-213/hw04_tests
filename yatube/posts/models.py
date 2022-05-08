from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField('заголовок', max_length=200)
    slug = models.SlugField('слаг', unique=True)
    description = models.TextField('описание')

    def _str_(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField('текст', help_text='Введите текст поста')
    pub_date = models.DateTimeField('дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='группа',
        help_text='Группа, к которой будет относиться пост'
    )

    class Meta:
        ordering = ('-pub_date',)

    def _str_(self) -> str:
        return self.text[:15]