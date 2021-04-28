from django.test import Client, TestCase

from .models import User


class UserModelTests(TestCase):

    def setUp(self):
        ''' Начальные настройки '''

        self.client = Client()

        # Первый пользователь
        self.password = 'qweasdzxc'
        self.email = 'admin@admin.admin'
        self.balance = 20
        self.currency = 'BTC'

        self.data = {
            'email': self.email,
            'password': self.password,
            'balance': self.balance,
            'currency': self.currency
        }

        # Второй пользователь
        self.password2 = 'qweasdzxc'
        self.email2 = 'user@user.user'
        self.balance2 = 200
        self.currency2 = 'RUB'

        self.data2 = {
            'email': self.email2,
            'password': self.password2,
            'balance': self.balance2,
            'currency': self.currency2
        }

    def test_create_user(self):
        '''
        Тестирование кейса: создание пользователя.
        '''

        resp = self.client.post("/auth/create/", data=self.data)
        # Статус должен быть 201
        self.assertEqual(resp.status_code, 201)
        # Наличие пользователя в БД
        self.assertTrue(User.objects.filter(email=self.email).exists())
        # Корректность конкретных полей
        user = User.objects.get(email=self.email)
        self.assertEqual(user.email, self.email)
        self.assertEqual(user.balance, self.balance)
        self.assertEqual(user.currency, self.currency)

    def test_login(self):
        '''
        Тестирование кейса: аутентификация пользователя.
        В рамках метода выполнить так же и создание пользователя.
        Успехом считаем получение токена и его корректное использование.
        '''

        # Создадим пользователя
        self.client.post("/auth/create/", data=self.data)

        # Модифицируем data - для аутентификации нужны email и password
        self.data = {
            'email': self.email,
            'password': self.password
        }

        resp = self.client.post("/auth/login/", data=self.data)
        # Статус должен быть 200
        self.assertEqual(resp.status_code, 200)
        # Ответ должен содержать token - тогда считать тест успешно пройденным
        self.assertContains(resp, 'token')
