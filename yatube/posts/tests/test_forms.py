from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client_2 = Client()
        cls.author_client = Client()
        cls.user = User.objects.create_user(username='NoName')
        cls.user_2 = User.objects.create_user(username='NoName_2')
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_2.force_login(cls.user_2)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост'
        )
        cls.author_client.force_login(cls.post.author)
        cls.form = PostForm()
        cls.form_data = {
            'text': f'{cls.post.text}',
            'group': f'{cls.group.id}',
        }

    def test_guest_can_not_create_post(self):
        """Гость не может создавать посты
        и перенаправляется на страницу логина"""
        posts_count = Post.objects.count()
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=self.form_data,
            follow=True
        )
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_guest_can_not_edit_post(self):
        """Гость не может редактировать посты
        и перенаправляется на страницу логина"""
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'}),
            data=self.form_data,
            follow=True
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/edit/'
        )

    def test_users_can_not_edit_post(self):
        """Пользователи не могут изменять чужие посты."""
        response = self.authorized_client_2.post(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'}),
            data=self.form_data,
            follow=True
        )
        self.assertRedirects(
            response, f'/profile/{self.user}/'
        )

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=self.form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': f'{self.user}'})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=self.post.text,
                author=self.user,
                group=self.group.id
            ).exists()
        )

    def test_edit_post(self):
        posts_count = Post.objects.count()
        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'}),
            data=self.form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                text=self.post.text,
            ).exists()
        )
