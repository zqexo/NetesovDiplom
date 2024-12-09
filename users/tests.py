from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User
from unittest.mock import patch
from smsaero import SmsAeroException


class SendCodeAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("users:send_phone")

    def test_send_code_invalid_phone(self):
        """Test sending code with invalid phone number"""
        data = {"phone": "invalid_phone"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid phone number format")

    @patch("users.views.send_sms")
    def test_send_code_sms_failure(self, mock_send_sms):
        """Test failure when sending SMS"""
        mock_send_sms.side_effect = SmsAeroException("SMS sending failed")
        data = {"phone": "79111111111"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["error"], "SMS sending failed")


class VerifyCodeAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("users:verify_code")
        self.phone = "79111111111"
        self.code = "1234"
        self.user = User.objects.create(phone=self.phone)
        # Set the code in cache (simulate SMS sending)
        cache.set(self.phone, self.code, timeout=300)

    def test_verify_code_success(self):
        """Test successful verification of the code"""
        data = {"phone": self.phone, "code": self.code}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "User logged in")
        self.assertIn("invite_code", response.data)

    def test_verify_code_invalid_code(self):
        """Test invalid verification code"""
        data = {"phone": self.phone, "code": "0000"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid code")


class UserProfileAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(phone="79111111111")
        self.url = reverse("users:user_profile")

    def test_user_profile_success(self):
        """Test retrieving the user profile"""
        data = {"phone": self.user.phone}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["phone"], self.user.phone)
        self.assertEqual(response.data["invite_code"], self.user.invite_code)

    def test_user_profile_user_not_found(self):
        """Test retrieving user profile for a non-existing user"""
        data = {"phone": "79998887766"}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "User not found")

    def test_referral_activation_invalid_invite_code(self):
        """Test invalid invite code"""
        data = {"phone": self.user.phone, "invite_code": "invalid_code"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid phone or invite code")
