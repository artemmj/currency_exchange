import jwt

from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)

from project.settings import CURRENCIES_CHOICES


class UserManager(BaseUserManager):
    """
    Django требует, чтобы кастомные пользователи определяли свой собственный
    класс Manager. Наследуя 'BaseUserManager' мы получаем контроль над кодом,
    который используется Django для создания класса 'User'.
    """

    def create_user(self, email, balance, currency, password=None):  # username
        """ Создать и вернуть 'User' с почтой и паролем. """

        # if username is None:
        #     raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        if balance is None:
            raise TypeError('Users must have an balance value.')

        if currency is None:
            raise TypeError('Users must have an currency type.')

        user = self.model(
            # username=username,
            email=self.normalize_email(email),
            currency=currency,
            balance=balance
        )
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password):  # username,
        """ Создать и вернуть 'User' с правами админа. """
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(email, 999, 'RUB', password)  # username,
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):

    # Нам так же нужен способ связаться с пользователем и способ идентификации
    # пользователя при входе его в систему. Мы также будем использовать
    # электронную почту для входа в систему, потому что это сегодня стандарт.
    email = models.EmailField(db_index=True, unique=True)

    # Когда пользователь захочит удалиться, это санет небольшой проблемой,
    # потому что данные, которые мы собираем, ценны. Вариант - это предложить
    # пользователю деактивировать свою учетную запись вместо полного удаления.
    # Таким образом, он больше не будет появляться на сайте, а мы так же
    # сможем анализировать данные.
    is_active = models.BooleanField(default=True)

    # Флаг отображает возможность пользователя залогиниться в admin-панели.
    # Большинству пользователей установить в False.
    is_staff = models.BooleanField(default=False)

    # Когда запись была создана.
    created_at = models.DateTimeField(auto_now_add=True)

    # Когда запись была изменена.
    updated_at = models.DateTimeField(auto_now=True)

    # Поле баланса
    balance = models.FloatField(default=0.0)
    # Поле для варианта валюты
    currency = models.CharField(
        max_length=3,
        choices=CURRENCIES_CHOICES,
        default='BTC'
    )

    # Доп. поля, обязательный для Django при определении кастомной модели User.

    # 'USERNAME_FIELD' указывает какое поле использовать при логине - 'email'.
    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['username']

    # Поля добавил для веса и наглядности
    # (все необязательные, так что проблем с ними нет)
    first_name = models.CharField(max_length=128, null=True, blank=True)
    last_name = models.CharField(max_length=128, null=True, blank=True)
    born_city = models.CharField(max_length=128, null=True, blank=True)
    born_date = models.DateField(null=True, blank=True)

    # Сказать Django использовать определенный UserManager как менеджер.
    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def token(self):
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        """
        Генерирует JSON Web Token, в котором хранится ID пользователя и срок
        его действия. Дата установлена на 60 дней.
        """
        dt = datetime.now() + timedelta(days=60)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')
