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
        cls.author_client = Client()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client.force_login(cls.user)
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

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()

        form_data = {
            'text': f'{self.post.text}',
            'group': f'{self.post.id}',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
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
        form_data = {
            'text': f'{self.post.text}',
            'group': f'{self.post.id}',
        }
        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                text=self.post.text,
            ).exists()
        )
