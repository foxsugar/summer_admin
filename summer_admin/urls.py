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
from summer_admin.apps import robotViews
from summer_admin.apps import officailWebViews





urlpatterns = [
    url(r'^admin/', admin.site.urls),
    #登录
    url(r'^user/login$', views.login),
    url(r'^user/info$', views.get_info),
    url(r'^user/changepwd$', playerViews.change_password),
    #代理
    url(r'^agent/list$', views.agent_list),
    url(r'^agent$', views.agent),
    url(r'^agent/charge$', views.agent_charge),
    url(r'^agent/chargeGold$', views.agent_charge_gold),
    url(r'^agent/chargelist$', playerViews.agent_charge_list),
    url(r'^agent/delagent$', playerViews.delete_agent),
    url(r'^agent/fetchself$', playerViews.agent_fetch_slf),
    url(r'^agent/fetchdelegates$', playerViews.fetch_delegates),
    url(r'^agent/upGoal$', playerViews.agent_upGoal),
    url(r'^agent/downGoal$', playerViews.agent_downGoal),
    url(r'^agent/goldCashList$', playerViews.gold_cash_list),
    url(r'^agent/changeState$', playerViews.agent_change_state),


    #搜索代理充值列表
    url(r'^agent/fetchlist$', playerViews.search_agent_charge),
    url(r'^agent/fetchgoldlist$', playerViews.search_agent_record),
    url(r'^player/charge$', playerViews.charge),
    url(r'^player/chargeGold$', playerViews.charge_gold),
    url(r'^player/changeUserDelegate$', playerViews.change_user_delegate),
    url(r'^player/list$', playerViews.user_list),
    url(r'^player/memberlist$', playerViews.user_member_list),
    url(r'^player/listvip$', playerViews.user_list_vip),
    #搜索用户列表
    url(r'^player/fetchlist$', playerViews.search_player),
    url(r'^player/fetchplayer$', playerViews.fetchplayer),
    url(r'^player/fetchplayers$', playerViews.serarch_player_list),
    url(r'^player/fetchPlayersRef$', playerViews.serarch_player_list_with_referee),

    url(r'^player/fetchplayersvip$', playerViews.serarch_player_list_vip),
    url(r'^player/chargelist$', playerViews.charge_list),
    url(r'^upload$', playerViews.upload),

    url(r'^user/logout$', playerViews.logout),
    url(r'^user/deldelegate$', playerViews.delete_delegate),
    url(r'^user/cashGold$', playerViews.cash_gold),
    url(r'^user/upload$', playerViews.goto_upload),
    url(r'^user/showimg$', playerViews.show_img),
    # 服务器信息
    url(r'^constant$', views.constant),
    url(r'^constant/update$', views.constant_update),
    #机器人
    url(r'^robot/createroom$', robotViews.create_room),
    url(r'^robot/getRoomInfo$', robotViews.get_room_info),
    url(r'^robot/sendMessage', robotViews.send_message),

    # 官网
    url(r'^game$', officailWebViews.officail_web),

    # url(r'^startWx$', wxRo.start),
]
