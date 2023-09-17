"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path, include

urlpatterns = [
    # 기존의 pybo 앱 URL 매핑
    path('pybo/', include('pybo.urls')),
    # 추가적으로 루트 URL('/')로 접속시 pybo 앱의 URL 매핑을 처리하도록 설정
    path('', include('pybo.urls')),
    path('admin/', admin.site.urls),
]
