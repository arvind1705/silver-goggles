"""fampay URL Configuration

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

from fampay.search.views import get_youtube_videos, search_youtube_videos, insert_mock_data

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/video/', get_youtube_videos),
    path('api/video/search/', search_youtube_videos),
    path('api/mock_data', insert_mock_data)
]
