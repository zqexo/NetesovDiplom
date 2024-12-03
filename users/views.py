import random

from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from smsaero import SmsAeroException

from users.models import User
from users.serializers import (PhoneSerializer, ReferralActivationSerializer,
                               VerifyCodeSerializer)
from users.utils import send_sms


class SendCodeAPIView(APIView):
    @staticmethod
    def post(request):

        phone_ser = PhoneSerializer(data=request.data)
        if not phone_ser.is_valid():
            return Response(
                {"error": "Invalid phone number format"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        phone_number = phone_ser.validated_data["phone"]

        code = str(random.randint(1000, 9999))
        cache.set(phone_number, code, timeout=300)  # 5 минут

        try:
            send_sms(phone_number, f"Ваш код подтверждения: {code}")
            return Response({"message": "Code sent successfully"})
        except SmsAeroException as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyCodeAPIView(APIView):
    @staticmethod
    def post(request):
        serializer = VerifyCodeSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data["phone"]
            code = serializer.validated_data["code"]

            cached_code = cache.get(phone)
            if cached_code and cached_code == code:
                user, created = User.objects.get_or_create(phone=phone)
                if created:
                    return Response(
                        {"message": "User created", "invite_code": user.invite_code}
                    )
                return Response(
                    {"message": "User logged in", "invite_code": user.invite_code}
                )

            return Response(
                {"error": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPIView(APIView):
    @staticmethod
    def get(request):
        phone = request.query_params.get("phone")
        try:
            user = User.objects.get(phone=phone)
            invited_users = User.objects.filter(referred_by=user)
            invited_phones = [u.phone for u in invited_users]
            return Response(
                {
                    "phone": user.phone,
                    "invite_code": user.invite_code,
                    "invited_users": invited_phones,
                }
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @staticmethod
    def post(request):
        serializer = ReferralActivationSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data["phone"]
            invite_code = serializer.validated_data["invite_code"]
            user = User.objects.get(phone=phone)
            if user.invite_code == invite_code:
                return Response(
                    {"error": "You cannot refer yourself"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                referred_user = User.objects.get(invite_code=invite_code)
                user.referred_by = referred_user
                user.save()
                return Response({"message": "Referral activated"})
            except User.DoesNotExist:
                return Response(
                    {"error": "Invalid phone or invite code"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
