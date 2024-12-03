import random

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from smsaero import SmsAeroException

from frontend.forms import ReferralActivationForm, VerifyCodeForm
from users.models import User
from users.utils import send_sms


class SendCodeView(View):
    template_name = "frontend/send_code.html"
    success_url = "/verify_code/"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        phone = request.POST.get("phone")

        if not phone:
            return render(request, self.template_name, {"error": "Телефон неверный"})

        try:
            phone_number = int(phone)  # Преобразуем в число
        except ValueError:
            return render(
                request,
                self.template_name,
                {"error": "Неверный формат номера телефона"},
            )

        code = str(random.randint(1000, 9999))
        cache.set(phone_number, code, timeout=300)  # 5 минут

        try:
            send_sms(phone_number, f"Ваш код подтверждения: {code}")
            return render(
                request, self.template_name, {"message": "Код отправлен на ваш телефон"}
            )
        except SmsAeroException as e:
            return render(request, self.template_name, {"error": str(e)})


class VerifyCodeView(View):
    template_name = "frontend/verify_code.html"
    form_class = VerifyCodeForm
    success_url = "/user-profile/"  # URL для редиректа на установку пароля

    def get_success_url(self, phone):
        # Генерация URL для установки пароля
        return f"{self.success_url}?phone={phone}"

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            phone = form.cleaned_data["phone"]
            code = form.cleaned_data["code"]

            cached_code = cache.get(phone)
            if cached_code and cached_code == code:
                user, created = User.objects.get_or_create(phone=phone)
                # Сохранить номер телефона в сессии для следующего шага
                request.session["phone"] = phone
                login(request, user)
                return redirect(self.get_success_url(phone))

            return render(
                request, self.template_name, {"error": "Неправильный код", "form": form}
            )

        return render(request, self.template_name, {"form": form})


class CustomLoginView(LoginView):
    template_name = "frontend/login.html"  # Шаблон для страницы логина
    redirect_authenticated_user = True  # Перенаправить авторизованного пользователя

    def get_success_url(self):
        return self.request.GET.get("next", "/profile/")  # Перенаправление после входа


@method_decorator(login_required(login_url="/send_code/"), name="dispatch")
class UserProfileView(View):
    template_name = "frontend/user_profile.html"

    def get(self, request):
        user = request.user  # Получаем текущего авторизованного пользователя
        invited_users = User.objects.filter(referred_by=user)
        invited_phones = [u.phone for u in invited_users]

        context = {
            "phone": user.phone,
            "invite_code": user.invite_code,
            "invited_users": invited_phones,
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name="dispatch")
class ReferralActivationView(View):
    template_name = "frontend/referral_activation.html"

    def get(self, request):
        # Форма отображается только для текущего пользователя
        form = ReferralActivationForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = ReferralActivationForm(request.POST)

        if form.is_valid():
            invite_code = form.cleaned_data["invite_code"]
            current_user = request.user

            try:
                # Найти пользователя, чей код введён
                referred_user = User.objects.get(invite_code=invite_code)

                # Проверить, не пытается ли пользователь стать своим же рефералом
                if current_user == referred_user:
                    return render(
                        request,
                        self.template_name,
                        {
                            "form": form,
                            "error": "Вы не можете быть рефералом самому себе.",
                        },
                    )

                # Установить текущего пользователя как реферала
                current_user.referred_by = referred_user
                current_user.save()

                # Успешный редирект на профиль текущего пользователя
                success_url = reverse("user_profile")  # Переходим на свой профиль
                return redirect(success_url)

            except User.DoesNotExist:
                # Если пользователь с таким реферальным кодом не найден
                return render(
                    request,
                    self.template_name,
                    {"form": form, "error": "Неправильный реферальный код."},
                )

        # При ошибке валидации формы возвращаем форму с ошибками
        return render(request, self.template_name, {"form": form})


class CustomLogoutView(LogoutView):
    """Выход пользователя из системы."""

    next_page = reverse_lazy("frontend:home")
    http_method_names = ["post", "options", "get"]

    def get(self, request, *arg, **kwargs):
        return self.post(request, *arg, **kwargs)


def home_view(request):
    """Главная страница."""
    return render(request, "frontend/home.html")
