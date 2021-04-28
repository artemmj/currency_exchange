from django.test import Client, TestCase

from .models import User, HistoryExchange
from .api import transate


class CoreApiTests(TestCase):

    def setUp(self):
        ''' Начальные настройки '''

        self.client = Client()

        # Первый пользователь
        self.password = 'qweasdzxc'
        self.email = 'admin@admin.admin'
        self.balance = 500
        self.currency = 'RUB'

        self.data = {
            'email': self.email,
            'password': self.password,
            'balance': self.balance,
            'currency': self.currency
        }

        # Второй пользователь
        self.password2 = 'qweasdzxc'
        self.email2 = 'user@user.user'
        self.balance2 = 500
        self.currency2 = 'RUB'

        self.data2 = {
            'email': self.email2,
            'password': self.password2,
            'balance': self.balance2,
            'currency': self.currency2
        }

    def test_transfer(self):
        ''' Тестирование кейса: перевод денег '''

        # Создать пользователей для обмена
        self.client.post("/auth/create/", data=self.data)
        self.client.post("/auth/create/", data=self.data2)
        user1 = User.objects.get(email=self.email)
        user2 = User.objects.get(email=self.email2)

        # Инкапсулированная функция перевода/рассчета,
        # которая требует только три параметра:
        # айди отправителя и получателя и сумма в валюте отправителя
        transate(user1.id, user2.id, 123)

        # Если в журнале этой операции флаг success поствлен в True,то перевод
        # выполнен успешно (см. в конце метода transate)
        history = HistoryExchange.objects.get(sender=user1)
        self.assertTrue(history.success)
