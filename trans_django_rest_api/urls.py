"""trans_django_rest_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
import trans_api.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('slack_events/', trans_api.views.slack_events, name='slack_events'),
    path('arxiv_check/', trans_api.views.arxiv_check, name='arxiv_check'),
    path('debug_cat/', trans_api.views.debug_cat, name='debug_cat'),
    path('debug_ls/', trans_api.views.debug_ls, name='debug_ls'),
    path('debug_cmd/', trans_api.views.debug_cmd, name='debug_cmd'),
]
