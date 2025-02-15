from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from constants.user_constants import (EMAIL_MAX_LENGTH, NAME_MAX_LENGTH,
                                      PASSWORD_MAX_LENGTH)


from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from constants.user_constants import (
    EMAIL_MAX_LENGTH, NAME_MAX_LENGTH, PASSWORD_MAX_LENGTH)


class FoodgramUser(AbstractUser):
    email = models.EmailField(
        "Электронная почта", max_length=EMAIL_MAX_LENGTH, unique=True
    )

    username = models.CharField(
        "Имя пользователя",
        max_length=NAME_MAX_LENGTH,
        unique=True,
        validators=[UnicodeUsernameValidator()],
    )

    first_name = models.CharField("Имя", max_length=NAME_MAX_LENGTH)

    last_name = models.CharField("Фамилия", max_length=NAME_MAX_LENGTH)

    password = models.CharField("Пароль", max_length=PASSWORD_MAX_LENGTH)

    avatar = models.ImageField(
        upload_to="users/",
        null=True,
        blank=True,
        default="",
        verbose_name="Аватар"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.email}: {self.first_name} {self.last_name}"


class Subscription(models.Model):
    user = models.ForeignKey(
        FoodgramUser,
        related_name="subscriptions",
        on_delete=models.CASCADE,
        verbose_name="Подписчик",
    )

    subscribed_to = models.ForeignKey(
        FoodgramUser,
        related_name="subscribers",
        on_delete=models.CASCADE,
        verbose_name="Подписан на",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "subscribed_to"], name="unique_subscription"
            )
        ]

    def clean(self):
        """Запрещаем подписку на самого себя."""
        if self.user == self.subscribed_to:
            raise ValidationError("Нельзя подписаться на самого себя!")

    def save(self, *args, **kwargs):
        """Перед сохранением вызываем `clean()` для валидации."""
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} подписан на {self.subscribed_to}"
