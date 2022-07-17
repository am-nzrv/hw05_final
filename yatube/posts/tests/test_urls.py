from collections import namedtuple
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        cls.author = User.objects.create_user(username='author')
        cls.authorized_author = Client()
        cls.authorized_author.force_login(cls.author)
        cls.guest_user = Client()
        cls.group = Group.objects.create(slug='test_slug')
        cls.post = Post.objects.create(author=cls.author)
        Urls = namedtuple('Urls', ['code', 'template'])
        cls.urls_list = {
            reverse('posts:index'): Urls(HTTPStatus.OK, 'posts/index.html'),
            reverse('posts:group_list',
                    args=(PostURLTests.group.slug,)
                    ): Urls(HTTPStatus.OK, 'posts/group_list.html'),
            reverse('posts:profile',
                    args=(PostURLTests.user.username,)
                    ): Urls(HTTPStatus.OK, 'posts/profile.html'),
            reverse('posts:post_detail',
                    args=(PostURLTests.post.id,)
                    ): Urls(HTTPStatus.OK, 'posts/post_detail.html'),
            reverse('posts:post_create'): Urls(HTTPStatus.FOUND,
                                               'posts/create_post.html'),
            reverse('posts:post_edit',
                    args=(PostURLTests.post.id,)
                    ): Urls(HTTPStatus.FOUND, 'posts/create_post.html')
        }

    def test_urls_for_guest_user(self):
        """Проверка доступа для неавторизированного пользователя."""
        for reversed_name, code in PostURLTests.urls_list.items():
            with self.subTest(reversed_name=reversed_name):
                response = PostURLTests.guest_user.get(reversed_name)
                self.assertEqual(response.status_code, code[0])

        response = PostURLTests.guest_user.get('/abracadabra/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_url_for_authorized_user(self):
        response = PostURLTests.authorized_user.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_add_comment_for_authorized_user(self):
        response = PostURLTests.guest_user.get(
            reverse('posts:add_comment',
                    args=(PostURLTests.post.id,)))
        self.assertEqual(response.status_code, 302)

    def test_post_edit_for_author(self):
        """
        Тест доступа к редактированию поста только для автора.
        """
        user_response_list = {
            PostURLTests.authorized_user: 302,
            PostURLTests.authorized_author: 200,
            PostURLTests.guest_user: 302
        }
        for user, code in user_response_list.items():
            with self.subTest(user=user):
                response = user.get(reverse('posts:post_edit',
                                            args=(PostURLTests.post.id,)))
                self.assertEqual(response.status_code, code)

    def test_urls_uses_correct_template(self):
        cache.clear()
        for reversed_name, template in PostURLTests.urls_list.items():
            with self.subTest(reversed_name=reversed_name):
                response = PostURLTests.authorized_author.get(reversed_name)
                self.assertTemplateUsed(response, template[1])
