from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Post, Group

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста', )

        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )

    def setUp(self):
        self.author = User.objects.create_user(username='Linnaip')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:posts'): 'posts/index.html',
            reverse('posts:group_posts', kwargs={'slug': 'test-slug'}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': f'{self.user}'}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': f'{self.post.pk}'}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.pk}'}): 'posts/create_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:posts'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        self.assertEqual(post_text_0, 'Тестовый текст поста')
        self.assertEqual(post_author_0, f'{self.user}')

    def test_group_pages_show_correct_context(self):
        """Шаблон group_list сформирован с правильны контекстом."""
        response = self.authorized_client.get(reverse
                                              ('posts:group_posts',
                                               kwargs={'slug': 'test-slug'}))
        first_object = response.context["group"]
        group_title_0 = first_object.title
        group_slug_0 = first_object.slug
        group_description_0 = first_object.description
        self.assertEqual(group_title_0, 'Тестовый заголовок')
        self.assertEqual(group_slug_0, 'test-slug')
        self.assertEqual(group_description_0, 'Тестовое описание')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильны контекстом."""
        response = self.authorized_client.get(reverse
                                              ('posts:profile',
                                               kwargs={'username': f'{self.user}'}))
        ctx = response.context
        first_object = ctx['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(ctx['author'].username, 'auth')
        self.assertEqual(post_text_0, 'Тестовый текст поста')

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильны контекстом."""
        response = self.authorized_client.get(reverse
                                              ('posts:post_detail',
                                               kwargs={'post_id': f'{self.post.pk}'}))
        ctx = response.context
        self.assertEqual(ctx['author'].pk, self.user.pk)
        self.assertEqual(ctx['post'].pk, self.post.pk)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильны контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_create_edit_page_correct_context(self):
        """Шаблон post_edit сформирован с правильны контекстом."""
        response = self.authorized_client.get(reverse
                                              ('posts:post_edit',
                                               kwargs={'post_id': f'{self.post.pk}'}))
        ctx = response.context
        self.assertEqual(ctx['post'].pk, self.post.pk)
        form_fields = {
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
    #доделать 3 задание 'Если не выбирать группу'

class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        for i in range(15):
            Post.objects.create(
            author=cls.user,
            text=f'Тестовый текст поста {i}',
            group=cls.group
            )

    def test_first_page_contains_ten_records(self):
        url_names = {
            reverse('posts:posts'): 'posts/index.html',
            reverse('posts:group_posts', kwargs={'slug': 'test-slug'}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': f'{self.user}'}): 'posts/profile.html',
        }
        for url in url_names.keys():
            response = self.client.get(url)
            self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_five_records(self):
        url_names = {
            reverse('posts:posts') + '?page=2':
                'posts/index.html',
            reverse('posts:group_posts', kwargs={'slug': 'test-slug'}) + '?page=2':
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': f'{self.user}'}) + '?page=2':
                'posts/profile.html',
        }
        for url in url_names.keys():
            response = self.client.get(url)
            self.assertEqual(len(response.context['page_obj']), 5)
