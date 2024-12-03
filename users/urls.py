from django.urls import path

from users.apps import UsersConfig
from users.views import SendCodeAPIView, UserProfileAPIView, VerifyCodeAPIView

app_name = UsersConfig.name

urlpatterns = [
    path("auth/phone/", SendCodeAPIView.as_view(), name="send_phone"),
    path("auth/code/", VerifyCodeAPIView.as_view(), name="verify_code"),
    path("profile/", UserProfileAPIView.as_view(), name="user_profile"),
]
