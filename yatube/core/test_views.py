from django.test import TestCase


class ViewTestClass(TestCase):
    def test_error_page(self):
        response = self.client.get('/sfafat/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_server_error(self):
        response = self.client.get('/check_500/')
        self.assertEqual(response.status_code, 500)
        self.assertTemplateUsed(response, 'core/500.html')
