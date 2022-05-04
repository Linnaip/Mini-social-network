from http import HTTPStatus

from django.test import TestCase, Client


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности staticpages."""
        url_names = (
            '/about/author/',
            '/about/tech/'
        )
        for url in url_names:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_url_uses_correct_template(self):
        """Проверка шаблонов staticpages ."""
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(address=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
