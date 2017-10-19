"""admin_python URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from summer_admin.apps import views
from summer_admin.apps import playerViews

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    #登录
    url(r'^user/login$', views.login),
    url(r'^user/info$', views.get_info),


    #代理
    url(r'^agent/list$', views.agent_list),
    url(r'^agent$', views.agent),
    url(r'^agent/charge$', views.agent_charge),
    url(r'^agent/chargelist$', playerViews.agent_charge_list),
    #搜索代理充值列表
    url(r'^agent/fetchlist$', playerViews.search_agent_charge),

    url(r'^player/charge$', playerViews.charge),
    url(r'^player/list$', playerViews.user_list),

    #搜索用户列表
    url(r'^player/fetchlist$', playerViews.search_player),


    url(r'^player/chargelist$', playerViews.charge_list),

    url(r'^constant$', views.constant),

    url(r'^user/logout$', playerViews.logout)

]
