from http import HTTPStatus

from django.test import TestCase, Client


class UsersPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_users_url_exists_at_desired_location(self):
        """Проверка доступности staticpages."""
        url_names = (
            '/auth/signup/',
            '/auth/logout/',
            '/auth/login/'
        )
        for url in url_names:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_users_url_uses_correct_template(self):
        """Проверка шаблонов staticpages ."""
        templates_url_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/login/': 'users/login.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(address=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
