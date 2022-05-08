from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='noname')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.author_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client.force_login(self.user)
        self.author_client.force_login(self.post.author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': f'{self.group.slug}'}): (
                'posts/group_list.html'
            ),
            reverse(
                'posts:post_detail', kwargs={'post_id': f'{self.post.id}'}): (
                'posts/post_detail.html'
            ),
            reverse(
                'posts:profile',
                kwargs={'username': f'{self.post.author}'}):
                    'posts/profile.html',
            reverse('posts:post_create'): 'posts/create_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

        response = self.author_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': f'{self.post.id}'}))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_create_show_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.author_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': f'{self.post.id}'}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': f'{self.group.slug}'})
        )
        self.assertEqual(response.context['group'].title, 'Тестовая группа')
        self.assertEqual(response.context['group'].slug, 'test_slug')
        self.assertEqual(
            response.context.get('group').description,
            'Тестовое описание')

    def test_show_correct_context(self):
        """Шаблоны index, post_detail, profile с правильным контекстом."""
        templates_pages_names = {
            'index': reverse('posts:index'),
            'post_detail': reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{self.post.id}'}),
            'profile': reverse(
                'posts:profile',
                kwargs={'username': f'{self.post.author}'})
        }
        for name, reverse_name in templates_pages_names.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    response.context['post'].author,
                    self.post.author
                )
                self.assertEqual(
                    response.context['post'].text, 'Тестовый пост')


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='noname')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        for index in range(13):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост {index}',
                group=cls.group
            )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.author_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client.force_login(self.user)
        self.author_client.force_login(self.post.author)

    def test_paginator_correct_context(self):
        """index, group_list, profile содержат 10 постов на первой странице"""
        templates_pages_names = {
            'index': reverse('posts:index'),
            'group_list': reverse(
                'posts:group_list',
                kwargs={'slug': f'{self.group.slug}'}),
            'profile': reverse(
                'posts:profile',
                kwargs={'username': f'{self.post.author}'})
        }
        for name, reverse_name in templates_pages_names.items():
            with self.subTest(name=name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_paginator_correct_context_2(self):
        """index, group_list, profile содержат 3 поста на второй странице"""
        templates_pages_names = {
            'index': reverse('posts:index') + '?page=2',
            'group_list': reverse(
                'posts:group_list',
                kwargs={'slug': f'{self.group.slug}'}) + '?page=2',
            'profile': reverse(
                'posts:profile',
                kwargs={'username': f'{self.post.author}'}) + '?page=2'
        }
        for name, reverse_name in templates_pages_names.items():
            with self.subTest(name=name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 3)
