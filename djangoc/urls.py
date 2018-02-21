"""djangoc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path

from djangoc import settings
from web.views import game, index, game_create, lobby, logout, clone

from django.conf.urls.static import static

urlpatterns = [
    path('game/<str:game_name>', game, name='game'),
    path('game/', game_create, name='game_create'),
    path('lobby/<str:game_name>', lobby, name='lobby'),
    path('clone/<str:game_name>', clone, name='clone'),
    path('logout/', logout, name='logout'),
    path('', index, name='index'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)