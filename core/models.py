from django.db import models

from project.settings import CURRENCIES_CHOICES
from authentication.models import User


class USDRelation(models.Model):
    '''
    Храним курс доллара к требуемым валютам. Вынес в отдельную таблицу
    с целью, например, дальнейшего хранения и анализа истории курса валют.
    Так же, имеем локальные независимые коэффициенты.
    '''
    EUR = models.FloatField(default=0.0)
    GBP = models.FloatField(default=0.0)
    RUB = models.FloatField(default=0.0)
    BTC = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        res = self.created_at.strftime('%Y-%m-%d -- %H:%M:%S')
        return str(res)


class HistoryExchange(models.Model):
    '''
    Храним историю транзакций - отправитель и получатель, валюта и сумма.
    Можно расширить до сколь угодно больших масштабов - коэффициенты на момент
    трансфера, длительность транзакции и т.д. и т.п.
    '''
    # Отправитель
    sender = models.ForeignKey(
                    User, on_delete=models.CASCADE, related_name='sender')
    # Получатель
    recipient = models.ForeignKey(
                    User, on_delete=models.CASCADE, related_name='recipient')
    # Валюта перевода
    transfer_currency = models.CharField(
        max_length=3,
        choices=CURRENCIES_CHOICES
    )
    # Сумма перевода - в валюте отправителя
    transfer_amount = models.FloatField()
    # Сумма которую получил получатель (и валюта)
    target_amount = models.FloatField(default=0.0)
    target_currency = models.CharField(
        max_length=3,
        choices=CURRENCIES_CHOICES,
        null=True, blank=True,
    )
    # Дата перевода
    created_at = models.DateTimeField(auto_now_add=True)

    # Успешна ли операция
    success = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return self.sender.email + ' > ' + self.recipient.email
