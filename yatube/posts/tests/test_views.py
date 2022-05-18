import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Post, Group, Comment

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста',
            image=cls.uploaded,
        )

        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:posts'): 'posts/index.html',
            reverse('posts:group_posts',
                    kwargs={
                        'slug':
                            f'{self.group.slug}'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={
                        'username':
                            f'{self.user}'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={
                        'post_id':
                            f'{self.post.pk}'}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={
                        'post_id':
                            f'{self.post.pk}'}): 'posts/create_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:posts'))
        self.first_object(response)

    def test_group_pages_show_correct_context(self):
        """Шаблон group_list сформирован с правильны контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_posts',
                    kwargs={'slug': f'{self.group.slug}'}))
        first_object = response.context['group']
        group_id_0 = first_object.id
        group_title_0 = first_object.title
        group_slug_0 = first_object.slug
        group_description_0 = first_object.description
        post_image_0 = Post.objects.first().image
        self.assertEqual(group_id_0, self.group.pk)
        self.assertEqual(group_title_0, self.group.title)
        self.assertEqual(group_slug_0, self.group.slug)
        self.assertEqual(group_description_0, self.group.description)
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильны контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': f'{self.user}'})
        )
        self.first_object(response)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильны контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': f'{self.post.pk}'})
        )
        ctx = response.context
        self.assertEqual(ctx['post'].image, 'posts/small.gif')
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
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{self.post.pk}'})
        )
        ctx = response.context
        self.assertEqual(ctx['post'].pk, self.post.pk)
        form_fields = {
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_additional_verification_create_post(self):
        """Дополнительная проверка при создании поста."""
        ctx = [
            reverse('posts:posts'),
            reverse('posts:group_posts',
                    kwargs={'slug': f'{self.group.slug}'}),
            reverse('posts:profile',
                    kwargs={'username': f'{self.user}'})
        ]
        post_2 = Post.objects.create(
            author=self.user,
            text='Данные 2 текста',
            group=self.group,
        )
        for reverse_name in ctx:
            with self.subTest(reverse_name=ctx):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(post_2, response.context['page_obj'][0])

    def first_object(self, response):
        """Шаблоны profile/index сформированы с правильным контекстом."""
        first_object = response.context['page_obj'][0]
        post_id_0 = first_object.id
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, f'{self.user}')
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_id_0, self.post.pk)
        self.assertEqual(post_image_0, 'posts/small.gif')


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
        cls.pages = 15
        cls.first_page = settings.CONSTANT
        for i in range(cls.pages):
            Post.objects.create(
                author=cls.user,
                text=f'Тестовый текст поста {i}',
                group=cls.group
            )

    def test_first_page_contains_ten_records(self):
        url_names = {
            reverse('posts:posts'): 'posts/index.html',
            reverse('posts:group_posts',
                    kwargs={
                        'slug':
                            f'{self.group.slug}'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={
                        'username':
                            f'{self.user}'}): 'posts/profile.html',
        }
        for url in url_names.keys():
            response = self.client.get(url)
            self.assertEqual(len(
                response.context['page_obj']), self.first_page)

    def test_second_page_contains_five_records(self):
        second_page = self.pages - self.first_page
        url_names = {
            reverse('posts:posts') + '?page=2':
                'posts/index.html',
            reverse('posts:group_posts',
                    kwargs={'slug': f'{self.group.slug}'}) + '?page=2':
                'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': f'{self.user}'}) + '?page=2':
                'posts/profile.html',
        }
        for url in url_names.keys():
            response = self.client.get(url)
            self.assertEqual(len(
                response.context['page_obj']), second_page)


class CommentsViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста'
        )

        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.user = User.objects.create_user(username='Linnaip')
        self.authorized_client.force_login(self.user)

    def test_add_comment(self):
        comment_count = Comment.objects.filter(post=self.post.pk).count()
        form_data = {
            'text': 'test comment'
        }
        response = self.authorized_client.post(reverse('posts:add_comment',
                                                       kwargs={'post_id': f'{self.post.pk}'}),
                                               data=form_data,
                                               follow=True)
        #??????
        selection = Comment.objects.filter(post=self.post.pk)
        self.assertEqual(Comment.objects.filter(post=self.post.pk).count(), comment_count)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={
                        'post_id': f'{self.post.pk}'}))
        #self.assertEqual(selection, 'test comment')
