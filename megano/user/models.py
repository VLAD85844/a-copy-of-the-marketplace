from django.db import models
from django.contrib.auth.models import User


class Avatar(models.Model):
    """Модель для хранения аватара пользователя"""
    src = models.ImageField(
        upload_to="app_users/avatars/user_avatars/",
        default="app_users/avatars/default.png",
        verbose_name="link"
    )
    alt = models.CharField(max_length=128, verbose_name="Description")

    class Meta:
        verbose_name = "Avatar"
        verbose_name_plural = "Avatar"


class Profile(models.Model):
    """Модель профиля пользователя"""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile'
    )
    fullName = models.CharField(max_length=128, verbose_name="Полное имя")
    phone = models.PositiveIntegerField(
        blank=True, null=True, unique=True, verbose_name="Номер телефона"
    )
    avatar = models.ForeignKey(
        Avatar,
        on_delete=models.SET_NULL,
        related_name="profile",
        verbose_name="Avatar",
        null=True,
        blank=True,
    )
    email = models.EmailField(
        blank=True, null=True, unique=True, verbose_name="Email"
    )

    def __str__(self):
        return self.fullName
