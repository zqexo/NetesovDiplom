from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils.crypto import get_random_string


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None):
        if not phone:
            raise ValueError("Users must have a phone number")

        user = self.model(phone=phone)
        user.set_password(password)
        user.save(using=self._db)
        return user


def get_invite_code():
    return get_random_string(6, allowed_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890")


class User(AbstractBaseUser):
    phone = models.CharField(max_length=15, unique=True)
    invite_code = models.CharField(
        max_length=6, unique=True, blank=True, null=True, default=get_invite_code
    )
    referred_by = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )

    USERNAME_FIELD = "phone"
    objects = UserManager()

    def __str__(self):
        return self.phone
