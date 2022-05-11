from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )

    def test_models_have_correct_object_names(self):
        post = PostModelTest.post
        result = post.text[:15]
        self.assertEqual(str(post), result, 'Проверь работу models постов')

    def test_models_group_have_correct_names(self):
        group = PostModelTest.group
        result = group.title
        self.assertEqual(str(group), result, 'Проверь работу group models')
