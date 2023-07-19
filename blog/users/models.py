from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UnicodeUsernameValidator
from django.contrib.auth.models import UserManager as DefaultUserManager
from django.db import models


class UserManager(DefaultUserManager):
    # Patch to allow nullable emails
    @classmethod
    def normalize_email(cls, email):
        return super().normalize_email(email) or None


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        max_length=150,
        unique=True,
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
        validators=[username_validator],
        error_messages={
            "unique": "A user with that username already exists.",
        },
    )
    email = models.EmailField(
        unique=True, default=None, null=True, error_messages={"unique": "A user with that email already exists."}
    )
    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        text = self.username

        if self.email:
            text += f": {self.email}"

        return text
