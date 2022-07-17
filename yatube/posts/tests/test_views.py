from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.core.cache import cache

from ..models import Post, Group, Comment

User = get_user_model()


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cache.clear()
        cls.user = User.objects.create_user(username='test_user')
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        cls.guest_user = Client()
        cls.group = Group.objects.create(title='test_group',
                                         slug='test_slug',
                                         description='test_description')
        cls.second_group = Group.objects.create(title='second_test_group',
                                                slug='second_grp')
        cls.post = Post.objects.create(author=cls.user,
                                       text='test_text',
                                       pub_date='10.10.2000',
                                       group=cls.group,
                                       image='')
        cls.reverse_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    args=('test_slug',)): 'posts/group_list.html',
            reverse('posts:profile',
                    args=('test_user',)): 'posts/profile.html',
            reverse('posts:post_detail',
                    args=(PostViewsTest.post.id,)): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    args=(PostViewsTest.post.id,)): 'posts/create_post.html'
        }
        # Перенес все словари, но т.к начинало ругаться на то,
        # что не определены переменные post_object, index_object и тд,
        # тоже засунул их сюда, может можно и лучше, но кажется работает
        response_post = PostViewsTest.authorized_user.get(
            reverse('posts:post_detail',
                    args=(PostViewsTest.post.id,)))
        post_object = response_post.context['post']
        cls.post_detail_obj_list = {
            post_object.id: PostViewsTest.post.id,
            post_object.text: PostViewsTest.post.text,
            post_object.author: PostViewsTest.post.author,
            post_object.pub_date: PostViewsTest.post.pub_date,
            post_object.group: PostViewsTest.post.group,
            post_object.image: PostViewsTest.post.image
        }
        response_index = PostViewsTest.authorized_user.get(
            reverse('posts:index'))
        index_object = response_index.context['page_obj'][0]
        cls.index_obj_list = {
            index_object.text: PostViewsTest.post.text,
            index_object.author: PostViewsTest.post.author,
            index_object.pub_date: PostViewsTest.post.pub_date,
            index_object.image: PostViewsTest.post.image
        }
        response_group = PostViewsTest.authorized_user.get(
            reverse('posts:group_list',
                    args=(PostViewsTest.group.slug,)))
        group_object = response_group.context['page_obj'][0]
        cls.group_obj_list = {
            group_object.group: PostViewsTest.post.group,
            group_object.text: PostViewsTest.post.text,
            group_object.image: PostViewsTest.post.image
        }
        response = PostViewsTest.authorized_user.get(
            reverse(
                'posts:profile',
                args=(PostViewsTest.user.username,)))
        profile_object = response.context['page_obj'][0]
        cls.profile_obj_list = {
            profile_object.author: PostViewsTest.post.author,
            profile_object.text: PostViewsTest.post.text,
            profile_object.pub_date: PostViewsTest.post.pub_date,
            profile_object.group: PostViewsTest.post.group,
            profile_object.image: PostViewsTest.post.image
        }

    def test_pages_uses_correct_templates(self):
        for reverse_name, template in PostViewsTest.reverse_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = PostViewsTest.authorized_user.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_create_and_edit_context(self):
        form_fields = {
            reverse('posts:post_create'): {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField
            },
            reverse('posts:post_edit',
                    args=(PostViewsTest.post.id,)): {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField
            }
        }
        for reversed_name in form_fields.keys():
            response = PostViewsTest.authorized_user.get(reversed_name)
            for value, expected in form_fields[reversed_name].items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_post_page_uses_correct_context(self):
        for obj, post_obj in PostViewsTest.post_detail_obj_list.items():
            with self.subTest(obj=obj):
                self.assertEqual(obj, post_obj)

    def test_index_page_uses_correct_context(self):
        cache.clear()
        for obj, post_obj in PostViewsTest.index_obj_list.items():
            with self.subTest(obj=obj):
                self.assertEqual(obj, post_obj)

    def test_group_page_uses_correct_context(self):
        for obj, post_obj in PostViewsTest.group_obj_list.items():
            with self.subTest(obj=obj):
                self.assertEqual(obj, post_obj)

    def test_profile_page_uses_correct_context(self):
        for obj, post_obj in PostViewsTest.profile_obj_list.items():
            with self.subTest(obj=obj):
                self.assertEqual(obj, post_obj)

    def test_post_not_exist_in_other_group_page(self):
        response = PostViewsTest.authorized_user.get(
            reverse('posts:group_list',
                    args=(PostViewsTest.second_group.slug,)))
        group_object = response.context['group']
        objects_list = {
            group_object.id: PostViewsTest.post.group.id
        }
        for obj, post_obj in objects_list.items():
            with self.subTest(obj=obj):
                self.assertNotEquals(obj, post_obj)

    def test_index_cache(self):
        response_1 = (
            PostViewsTest.authorized_user.get(reverse('posts:index')))
        old_content = response_1.content
        Post.objects.create(
            text='test cache index page',
            author=self.user,
            group=self.group
        )
        response_2 = (
            PostViewsTest.authorized_user.get(reverse('posts:index')))
        self.assertEqual(response_2.content, old_content)
        cache.clear()
        response_3 = (
            PostViewsTest.authorized_user.get(reverse('posts:index')))
        self.assertNotEqual(response_3.content, old_content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='pagination_user')
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.user)
        cls.group = Group.objects.create(title='test_group',
                                         slug='test_slug')
        objs = [
            Post(
                text=123,
                author=cls.user,
                group=cls.group
            )
            for _ in range(15)
        ]
        cls.post_list = Post.objects.bulk_create(objs)

    def test_pagination_pagination_page_one(self):
        cache.clear()
        reversed_names_list = {
            reverse('posts:index'): 10,
            reverse('posts:group_list',
                    args=('test_slug',)): 10,
            reverse('posts:profile',
                    args=('pagination_user',)): 10
        }
        for reversed_names, posts in reversed_names_list.items():
            with self.subTest(reversed_names=reversed_names):
                response = PaginatorViewsTest.auth_user.get(reversed_names)
                self.assertEqual(len(response.context['page_obj']), posts)

    def test_pagination_page_two(self):
        cache.clear()
        reversed_names_list = {
            reverse('posts:index'): 5,
            reverse('posts:group_list',
                    args=('test_slug',)): 5,
            reverse('posts:profile',
                    args=('pagination_user',)): 5
        }
        for reversed_names, posts in reversed_names_list.items():
            with self.subTest(reversed_names=reversed_names):
                response = (PaginatorViewsTest.auth_user.
                            get(reversed_names + '?page=2'))
                self.assertEqual(len(response.context['page_obj']), posts)
