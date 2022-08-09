from django.contrib.auth.models import AbstractUser
from django.db import models

USER = 'user'
ADMIN = 'admin'
CHOICES = (
    (USER, 'user'),
    (ADMIN, 'admin'),
)


class User(AbstractUser):
    """Модель пользователя"""
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        unique=True,
        help_text='Поле бязательно к заполнению. Не более 150 символов.',
    )
    email = models.EmailField(
        max_length=254,
        verbose_name='Адрес электронной почты',
        unique=True,
        help_text='Это поле обязательно к заполнению и должно быть уникальным'
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        help_text='Это поле обязательно к заполнению'
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        help_text='Это поле обязательно к заполнению'
    )
    role = models.CharField(
        max_length=20,
        choices=CHOICES,
        default=USER,
        verbose_name='Роль пользователя'
    )

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    REQUIRED_FIELD = ['username', 'email', 'first_name', 'last_name']

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_staff or self.is_superuser

    @property
    def is_user(self):
        return self.role == USER

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['email', 'username'],
                                    name='unique_user')
        ]
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписки на пользователя"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_follow')
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
