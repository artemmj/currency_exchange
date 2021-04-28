import json
import requests

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from project.settings import exchange_rates_api_app_id
from .models import User, USDRelation, HistoryExchange


def transate(sender_id, target_id, amount):
    '''
    Отдельная инкаспулированная функция перевода денег - на вход получает лишь
    id отправителя и получателя и сумму перевода. Внутри происходит логирование
    всех отправлений, а так же работа с самим переводом - переписывание
    значений и конвертация сумм в случае расхождения валют.
    '''
    transaction_amount = amount

    sender = User.objects.get(pk=sender_id)
    recipient = User.objects.get(pk=target_id)

    # Сохранить историю
    history = HistoryExchange.objects.create(
        sender=sender,
        recipient=recipient,
        transfer_currency=sender.currency,
        transfer_amount=transaction_amount,
        target_currency=sender.currency,
        success=False,  # пока транза не прошла, флаг в False
    )
    history.save()

    # Если валюты не сходятся
    if sender.currency != recipient.currency:

        sender.balance -= transaction_amount

        # TODO
        # 1. Несколько источников - для более точных значений
        # 2. Автоматическая периодическая актуализация - САМЫЙ свежий курс :)
        # Пока что просто делаем запрос и получаем самый актуальный курс
        url = 'https://openexchangerates.org/api/latest.json?app_id='
        url += exchange_rates_api_app_id

        # Два варианта: либо делаем запрос и получаем свежайшие данные, пишем
        # в БД, и довольно вычисляем перевод. Либо, стянуть свежие даннные не
        # получится - тогда смотри except
        # WARN: Понятное дело, что в случае, когда посещаемость и пользование
        # переводами возрастет до 1 000 в день :) то придется немного
        # модифицировать систему: отделить сервис транзакции от сервиса
        # обновления и актуализации данных.
        try:
            resp = requests.get(url)
            result = json.loads(resp.content)
            eur = result['rates']['EUR']
            gbp = result['rates']['GBP']
            rub = result['rates']['RUB']
            btc = result['rates']['BTC']
            USDRelation.objects.create(
                EUR=eur,  # Мы сохраняем отношение доллара ко всем актуальным
                GBP=gbp,  # валютам, так как через доллар проще всего провести
                RUB=rub,  # несколько арифметич. операц. и посчитать правильные
                BTC=btc   # коэффициенты для всех комбинаций переводимых валют.
            )                             # (и еще легко стащить свежие данные)
        # В случае проблем с подключением - просто лезем в БД и берем самую
        # возможно свежую запись с курсами, присваиваем результаты
        except requests.exceptions.ConnectionError:
            result = USDRelation.objects.latest('created_at')
            eur = result.EUR
            gbp = result.GBP
            rub = result.RUB
            btc = result.BTC

        # Математика здесь, конечно, 'супер': берем переводящего, и переводим
        # его сумму перевода в доллары => фиксируем
        if sender.currency == 'USD':
            summ_dollar = transaction_amount
        if sender.currency == 'EUR':
            summ_dollar = transaction_amount / eur
        elif sender.currency == 'GBP':
            summ_dollar = transaction_amount / gbp
        elif sender.currency == 'RUB':
            summ_dollar = transaction_amount / rub
        elif sender.currency == 'BTC':
            summ_dollar = transaction_amount / btc

        # Далее, в зависимости от того, какая валюта у принимающей стороны,
        # переводим переводимую сумму в эту валюту (или просто += если $ :) )
        if recipient.currency == 'USD':
            recipient.balance += summ_dollar

        elif recipient.currency == 'EUR':
            # Например, если переводим в ЕВРО, то берем наш скачанный (или
            # вытащенный с БД, все выше) коэффициент к евро и умножаем:
            # получаем сумму перевода в валюте получающего
            summ_target = summ_dollar * eur
            # Суммируем)
            recipient.balance += summ_target

        elif recipient.currency == 'GBP':
            # Везде аналогично
            summ_target = summ_dollar * gbp
            recipient.balance += summ_target

        elif recipient.currency == 'RUB':
            summ_target = summ_dollar * rub
            recipient.balance += summ_target

        elif recipient.currency == 'BTC':
            summ_target = summ_dollar * btc
            recipient.balance += summ_target

            history.target_amount = summ_target
    # Иначе все просто
    else:
        sender.balance -= transaction_amount
        recipient.balance += transaction_amount
        history.target_amount = transaction_amount

    sender.save()
    recipient.save()

    # Транзакция прошла успешно: проставить флаг в журнале, сохранить
    history.success = True
    history.save()


class TransferAPIView(APIView):
    ''' Эндпоинт перевода денег '''
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        '''
        Эндпоинт используется при переводе денежной суммы.
        В теле запроса ожидаются два поля: target_id (id юзера-получателя)
        и sum_transaction (сумма перевода в валюте переводящего)
        '''
        data = request.data.copy()
        try:
            target_id = data['target_id']
            sum_transaction = data['sum_transaction']
        except Exception:
            return Response({
                'error': 'check request args'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Необходимо убедиться, что получатель существует - иначе вернуть 400
        try:
            recipient = User.objects.get(pk=target_id)
        except User.DoesNotExist:
            return Response({
                'error': 'User with this target_id not found. Please check ID.'
            }, status=status.HTTP_400_BAD_REQUEST)

        transate(request.user.id, recipient.id, sum_transaction)

        return Response('transfer complete!', status=status.HTTP_200_OK)


class HistoryTransactionsAPIView(ListAPIView):
    ''' Эндпоинт получения истории переводов '''
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        # Отобрать из БД переводы пользователя, который делает запрос
        qs = HistoryExchange.objects.filter(sender=request.user)
        # Объект для возврата
        values = []
        for item in qs:
            # Набираем нужные данные: при расширении HistoryExchanges
            # легко добавить новые необходимые поля
            values.append({
                'sender': str(item.sender),
                'recipient': str(item.recipient),
                'sender currency': str(item.transfer_currency),
                'sender amount': str(item.transfer_amount),
                'recipient currency': str(item.target_currency),
                'recipient amount': str(item.target_amount),
                'date': item.created_at.strftime('%Y-%m-%d - %H:%M:%S'),
            })
        return Response(values, status=status.HTTP_200_OK)
