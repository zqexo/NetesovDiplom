from rest_framework import serializers

from users.models import User


class PhoneSerializer(serializers.Serializer):
    phone = serializers.IntegerField(min_value=79111111111, max_value=79999999999)


class VerifyCodeSerializer(serializers.Serializer):
    phone = serializers.CharField()
    code = serializers.CharField()


class ReferralActivationSerializer(serializers.Serializer):
    phone = serializers.CharField()
    invite_code = serializers.CharField()


class PhoneVerificationSerializer(serializers.Serializer):
    phone = serializers.CharField()

    @staticmethod
    def validate_phone(value):
        if not value.isdigit():
            raise serializers.ValidationError("Invalid phone number")
        return value

    def save(self, **kwargs):
        # Логика отправки SMS (замените на реальную)
        phone = self.validated_data["phone"]
        # Пример: send_sms(phone, code)
        return phone


class CodeVerificationSerializer(serializers.Serializer):
    phone = serializers.CharField()
    code = serializers.CharField()

    def validate(self, data):
        phone = data.get("phone")
        code = data.get("code")
        # Пример проверки кода (замените на реальную логику)
        if code != "1234":  # Предполагаемый тестовый код
            raise serializers.ValidationError("Invalid verification code")
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
        data["user"] = user
        return data
