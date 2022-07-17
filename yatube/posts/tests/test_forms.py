from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Post, Group, Comment

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='username')
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Новая группа',
            slug='test_slug'
        )
        cls.edit_group = Group.objects.create(
            title='Другая группа',
            slug='test_another_grp'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст'
        )
        cls.comment = Comment.objects.create(
            text='Comment',
            author=cls.user,
            post_id=PostCreateFormTests.post.id
        )
        cls.form = PostForm()

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый пост',
            'group': PostCreateFormTests.group.id,
            'image': 'image'
        }
        response = PostCreateFormTests.auth_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile',
                    args=(PostCreateFormTests.user.username,)))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertContains(response, PostCreateFormTests.post.text)
        self.assertContains(response, PostCreateFormTests.group.id)
        self.assertContains(response, PostCreateFormTests.post.image)

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Редактированный пост',
            'group': PostCreateFormTests.edit_group.id
        }
        response = PostCreateFormTests.auth_user.post(
            reverse('posts:post_edit',
                    args=(PostCreateFormTests.post.id,)),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     args=(PostCreateFormTests.post.id,)))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertContains(response, 'Редактированный пост')
        self.assertContains(response, PostCreateFormTests.edit_group.id)

    def test_add_comment(self):
        posts_count = Comment.objects.count()
        form_data = {
            'text': 'Комментарий'
        }
        response = PostCreateFormTests.auth_user.post(
            reverse('posts:add_comment',
                    args=(PostCreateFormTests.post.id,)),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail',
                    args=(PostCreateFormTests.post.id,)))
        self.assertEqual(Comment.objects.count(), posts_count + 1)
        self.assertContains(response, PostCreateFormTests.comment.text)

