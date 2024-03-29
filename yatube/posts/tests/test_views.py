from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Follow, Group, Post
User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.author_client = Client()
        cls.authorized_client_2 = Client()
        cls.user = User.objects.create_user(username='NoName1')
        cls.authorized_client.force_login(cls.user)
        cls.user_2 = User.objects.create_user(username='NoName2')
        cls.authorized_client_2.force_login(cls.user_2)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            image='posts/image.png'
        )
        cls.post_2 = Post.objects.create(
            author=cls.user,
            text='Тестовый пост'
        )
        cls.follows = Follow.objects.create(
            user=cls.user,
            author=cls.post.author
        )
        cls.unfollows = Follow.objects.create(
            user=cls.user,
            author=cls.post.author
        ).delete()
        cls.author_client.force_login(cls.post.author)
        cls.templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{cls.group.slug}'}): (
                'posts/group_list.html'
            ),
            reverse(
                'posts:post_detail', kwargs={'post_id': f'{cls.post.id}'}): (
                'posts/post_detail.html'
            ),
            reverse(
                'posts:profile',
                kwargs={'username': f'{cls.post.author}'}):
                    'posts/profile.html',
            reverse('posts:post_create'): 'posts/create_post.html'
        }
        cls.correct_context_names = {
            'index': reverse('posts:index'),
            'post_detail': reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{cls.post.id}'}),
            'profile': reverse(
                'posts:profile',
                kwargs={'username': f'{cls.post.author}'})
        }

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates_pages_names.items():
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
        group = response.context['group']
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.slug, self.group.slug)
        self.assertEqual(group.description, self.group.description)

    def test_views_show_correct_context(self):
        """Шаблоны index, post_detail, profile с правильным контекстом."""
        for name, reverse_name in self.correct_context_names.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    response.context['post'].author,
                    self.post.author
                )
                self.assertEqual(
                    response.context['post'].text, self.post.text)


    def test_caches(self):
        """Проверка кеширования на странице index """
        response = self.client.get(reverse('posts:index'))
        self.assertContains(response, self.post_2.text)
        self.assertContains(response, self.post_2.author)
        self.post_2.delete()
        cache.clear()
        self.assertContains(response, self.post_2.text)
        self.assertContains(response, self.post_2.author)


    def test_follows_correct_context(self):
        """Авторизованный пользователь может подписываться
        на других пользователей и удалять их из подписок.
        Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан.
        """
        follows_count = Follow.objects.count()
        response = self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': f'{self.user_2}'}),
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': f'{self.user_2}'})
        )
        self.assertEqual(Follow.objects.count(), follows_count + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.user_2
            ).exists()
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(
            response.context['page_obj'][0].text,
            self.post.text
        )
        self.assertEqual(response.context['page_obj'][0].author, self.post.author)
        self.assertEqual(response.context['page_obj'][0].text, self.post.text)
        response = self.authorized_client_2.get(reverse('posts:follow_index'))
        self.assertNotContains(response, self.post.text)
        self.assertNotContains(response, self.post.author)
        response = self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': f'{self.user_2}'}),
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': f'{self.user_2}'})
        )
        self.assertEqual(Follow.objects.count(), follows_count)
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.user_2
            )
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName1')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.posts_count = 13
        cls.posts = Post.objects.bulk_create([Post(
            id=id,
            author=cls.user,
            text=f'Тестовый пост {id}',
            group=cls.group) for id in range(cls.posts_count)
        ])
        cls.paginator_context_names = {
            'index': '/',
            'group_list': f'/group/{cls.group.slug}/',
            'profile': f'/profile/{cls.user}/'
        }

    def test_paginator_correct_context(self):
        """index, group_list, profile содержат 10 постов на первой странице"""
        for name, url in self.paginator_context_names.items():
            with self.subTest(name=name):
                response = self.client.get(url)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_paginator_correct_context_2(self):
        """index, group_list, profile содержат 3 поста на второй странице"""
        for name, url in self.paginator_context_names.items():
            with self.subTest(name=name):
                response = self.client.get(url + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)
