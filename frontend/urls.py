from django.contrib.auth.views import LoginView
from django.urls import path

from frontend import views
from frontend.apps import FrontendConfig

app_name = FrontendConfig.name

urlpatterns = [
    path("", views.home_view, name="home"),
    path(
        "login/", LoginView.as_view(template_name="frontend/login.html"), name="login"
    ),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("send_code/", views.SendCodeView.as_view(), name="send_code"),
    path("verify-code/", views.VerifyCodeView.as_view(), name="verify_code"),
    path("user-profile/", views.UserProfileView.as_view(), name="user_profile"),
    path(
        "referral-activation/",
        views.ReferralActivationView.as_view(),
        name="referral_activation",
    ),
]
