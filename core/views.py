import json
import requests

from django.views import generic
from django.shortcuts import render

from project.settings import exchange_rates_api_app_id
from .models import USDRelation


class IndexView(generic.View):
    '''
    index.html, начальная домашная страница приложения: 127.0.0.1:8000/
    '''
    template_name = 'core/index.html'

    def get(self, request):
        '''
        По запросу просто отобразить текущие курсы к доллару.
        Для красоты и наглядности добавил отображение, чего сколько в 100$
        '''
        # Для отображения на homepage берем свежайшее из БД
        try:
            result = USDRelation.objects.latest('created_at')
            eur = result.EUR
            gbp = result.GBP
            rub = result.RUB
            btc = result.BTC
        # Если в БД нет ( о_О wyat ) : лезем в сеть и тащим свежие данные
        except USDRelation.DoesNotExist:
            try:
                url = 'https://openexchangerates.org/api/latest.json?app_id='
                url += exchange_rates_api_app_id

                resp = requests.get(url)
                result = json.loads(resp.content)
                eur = result['rates']['EUR']
                gbp = result['rates']['GBP']
                rub = result['rates']['RUB']
                btc = result['rates']['BTC']

                USDRelation.objects.create(
                    EUR=eur,
                    GBP=gbp,
                    RUB=rub,
                    BTC=btc,
                )
                # На край проставить нули
            except requests.exceptions.ConnectionError:
                eur = 0
                gbp = 0
                rub = 0
                btc = 0

        # Просто для красоты и наглядности, + чего сколько в ста долларах
        obj = {
            'eur': eur,
            'gbp': gbp,
            'rub': rub,
            'btc': btc,
            # :)
            '100dollarseur': eur * 100,
            '100dollaersgbp': gbp * 100,
            '100dollarsrub': rub * 100,
            '100dollarsbtc': btc * 100,
        }
        return render(request, 'core/index.html', context=obj)
