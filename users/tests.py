from django.test import TestCase

from users.models import User


class UserTestCase(TestCase):
    def test_create_user(self):
        user = User.objects.create(phone="1234567890", invite_code="ABC123")
        self.assertEqual(user.phone, "1234567890")
        self.assertEqual(user.invite_code, "ABC123")
