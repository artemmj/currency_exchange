from django.urls import path

from .views import RegistrationAPIView, LoginAPIView


app_name = 'authentication'
urlpatterns = [
    path('create/', RegistrationAPIView.as_view()),
    path('login/', LoginAPIView.as_view())
]
