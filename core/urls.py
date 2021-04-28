from django.urls import path

from .api import TransferAPIView, HistoryTransactionsAPIView


app_name = 'core'
urlpatterns = [
    path('transfer/', TransferAPIView.as_view()),
    path('history/', HistoryTransactionsAPIView.as_view())
]
