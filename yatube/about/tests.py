from http import HTTPStatus

from django.test import Client, TestCase


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_user = Client()

    def test_urls_for_guest_user(self):
        urls_list = {
            '/about/author/': HTTPStatus.OK,
            '/about/tech/': HTTPStatus.OK
        }
        for address, code in urls_list.items():
            with self.subTest(adress=address):
                response = AboutURLTests.guest_user.get(address)
                self.assertEqual(response.status_code, code)

    def test_urls_uses_correct_tempalte(self):
        urls_template_list = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for address, template in urls_template_list.items():
            with self.subTest(address=address):
                response = AboutURLTests.guest_user.get(address)
                self.assertTemplateUsed(response, template)
