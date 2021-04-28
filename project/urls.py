"""
project URL Configuration
"""
from django.contrib import admin
from django.urls import include, path
# from django.shortcuts import redirect

from core.views import IndexView

urlpatterns = [
    path('auth/', include('authentication.urls', namespace='authentication')),
    path('api/', include('core.urls', namespace='core')),
    path('admin/', admin.site.urls),

    path('', IndexView.as_view()),
]
