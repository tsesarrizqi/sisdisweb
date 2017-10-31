"""sisdisweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from sisdis1 import views

handler404 = 'sisdis1.views.page_not_found'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/hello', views.hello),
    url(r'^api/plus_one/(?P<val>\d+)', views.plus_one),
    url(r'^api/spesifikasi.yaml', views.spesifikasi),
    url(r'^ewallet/ping', views.ping),
    url(r'^ewallet/register', views.register),
    url(r'^ewallet/getSaldo', views.get_saldo),
    url(r'^ewallet/getTotalSaldo', views.get_total_saldo),
    url(r'^ewallet/transfer', views.transfer),
    url(r'^ewallet/transferKe', views.transfer_ke),
]

handler404 = 'sisdis1.views.page_not_found'
