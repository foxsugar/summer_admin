import imghdr
import json
import random

import os
from django.http import JsonResponse
from django.core.cache import cache
from django.shortcuts import render

from summer_admin.apps.models import Users, Charge, Agent_charge
from summer_admin.rpc.rpc import *
from summer_admin.apps.views import *
import datetime
from django.db.models import Q
# import urllib.request
# import urllib.parse
from urllib import request, parse, error
import collections

#更新rebeat
@check_login
def save_or_update_constant_rebate(request):
    param = json.loads(str(request.GET['constantFrom']))
    # 具体更新哪个字段 比如 rebate100  rebate4 explain pay_aa
    kk = param["key"]
    vv = param["value"]

    if vv < 0 or vv > 100:
        raise RuntimeError('返利比例不正确')
    constant = Constant.objects.get(id=1)
    other = json.loads(constant.other)
    rebate_data = other["rebateData"]
    rebate_data[kk] = vv
    r = json.dumps(other)
    constant.other = r
    constant.save()
    return JsonResponse({'code': 1000, 'data': '更新成功'})
@check_login
def fetch_constant_text_list(request):
    param = json.loads(str(request.GET['constantFrom']))
    kk = param["key"]
    constant = Constant.objects.get(id=1)
    other = json.loads(constant.other)
    data = other[kk]
    li = []
    for k,v in data:
        d = dict()
        d["key"] = k
        d["v"] = v
        li.append(d)

    data = {'tableData': li, 'totalPage': len(li)}
    return JsonResponse({'code': 20000, 'data': data})
@check_login
def fetch_constant_rebate_list(request):
    param = json.loads(str(request.GET['constantFrom']))
    kk = param["key"]
    constant = Constant.objects.get(id=1)
    other = json.loads(constant.other)
    data = other["rebateData"]
    data = {'data': data}
    return JsonResponse({'code': 20000, 'data': data})

#更新非rebeat
@check_login
def save_or_update_constant_text(request):
    param = json.loads(str(request.GET['constantFrom']))
    #具体更新哪个字段 比如 notice  promo explain

    kk = param["key"]
    skk =param["subKey"]
    vv = param["value"]
    #更新
    if skk is not None:
        constant = Constant.objects.get(id=1)
        other = json.loads(constant.other)
        data = other[kk]
        data[skk] = vv
        r = json.dumps(other)
        constant.other = r
        constant.save()
        return JsonResponse({'code': 1000, 'data': '更新成功'})
    else:
        constant = Constant.objects.get(id=1)
        other = json.loads(constant.other)
        data = other[kk]
        size = len(data)
        sub_key = "key" + (size + 1)
        data[sub_key] = vv
        r = json.dumps(other)
        constant.other = r
        constant.save()
        return JsonResponse({'code': 1000, 'data': '插入成功'})

@check_login
def change_user_delegate(req):

    x_token = req.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    # 总代理id
    agent_id = dict['id']
    # 需要修改的用户id
    dic = json.loads(str(req.GET['chargeForm']))
    pid = dic['id']
    # 需要修改的代理id
    aid = int(dic['agent_id'])
    if agent_id != 1:
        return JsonResponse({'code': 101, 'data': '没有权限'})

    a_user = Users.objects.get(id=aid)
    if a_user == None:
        return JsonResponse({'code': 1000, 'data': '参数不正确'})

    p_user = Users.objects.get(id=pid)
    if p_user == None:
        return JsonResponse({'code': 1000, 'data': '参数不正确'})

    # print('Login to weibo.cn...')
    # login_data = parse.urlencode([
    #     ('userId', pid),
    #     ('referrer', aid),
    # ])

    data = {
        'userId': pid,
        'referrer': aid
    }
    url_values = parse.urlencode(data)
    print(url_values)
    url = 'http://localhost:8085/game/bindReferrer'
    full_url = url + '?' + url_values
    print("绑定请求全路径:" +full_url)
    try:
        request.urlopen(full_url)
    except error.URLError as e:
        print(e)
        return JsonResponse({'code': 1000, 'data': '绑定失败:' + str(e)})
    else:
        return JsonResponse({'code': 20000, 'data': '绑定成功'})

@check_login
def charge_gold(request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']

    param = json.loads(str(request.GET['chargeForm']))
    user_id = int(str(param['userId']))
    num = int(str(param['gold_num']))

    array = Agent_user.objects.filter(Q(id=agent_id))
    entry_list = list(array.all())
    leng = len(entry_list)

    player = Users.objects.get(id=user_id)
    from_agent = Agent_user.objects.get(id=agent_id)
    str1 = '%d' % (player.referee)
    if (str1 != from_agent.invite_code) & (from_agent.id != 1):
        return JsonResponse({'code': 100, 'data': '没有权限'})

    if leng == 0:
        return JsonResponse({'code': 100, 'data': '充值失败'})

    agent_user = entry_list[0]

    if num < 0:
        if player.gold + num < 0:
            return JsonResponse({'code': 100, 'data': '金币不足'})

    else:
        if agent_user.gold < num:
            return JsonResponse({'code': 100, 'data': '金币不足'})

    if num < 0:
        if player.gold + num < 0:
            return JsonResponse({'code': 100, 'data': '充值失败'})

    rpc_client = get_client()
    order = Order(userId=user_id, num=num, type=ChargeType.gold, agentId=agent_id)
    rtn = rpc_client.charge(order)
    if rtn == 0:
        agent_user.gold -= num
        agent_user.save()
        return JsonResponse({'code': 20000, 'data': '充值成功'})
    else:
        return JsonResponse({'code': 100, 'data': '充值失败'})


@check_login
def charge(request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']

    param = json.loads(str(request.GET['chargeForm']))
    user_id = int(str(param['userId']))
    num = int(str(param['num']))

    array = Agent_user.objects.filter(id=agent_id)
    entry_list = list(array.all())
    leng = len(entry_list)

    player = Users.objects.get(id=user_id)
    from_agent = Agent_user.objects.get(id=agent_id)

    gameCategory = config.get('robot', 'gameCategory')

    if gameCategory == 'kunlun_bb':
        if from_agent.id != 1:
            return JsonResponse({'code': 100, 'data': '非总代理暂时没有权限充值房卡！'})

    str1 = '%d' % (player.referee)

    gameCategory = config.get('robot', 'gameCategory')
    if gameCategory != "zhongxin":
        if (str1 != from_agent.invite_code) & (from_agent.id != 1):
            return JsonResponse({'code': 100, 'data': '没有权限充值非自己绑定的玩家'})

    if leng == 0:
        return JsonResponse({'code': 100, 'data': '充值失败'})

    agent_user = entry_list[0]

    if agent_user.money < num:
        return JsonResponse({'code': 100, 'data': '金额不足'})

    if num < 0:
        if player.money + num < 0:
            return JsonResponse({'code': 100, 'data': '充值失败'})

    rpc_client = get_client()

    order = Order(userId=user_id, num=num, type=ChargeType.money, agentId=agent_id)
    rtn = rpc_client.charge(order)
    if rtn == 0:
        agent_user.money -= num
        agent_user.save()
        return JsonResponse({'code': 20000, 'data': '充值成功'})
    else:
        return JsonResponse({'code': 100, 'data': '充值失败'})


@check_login
def user_member_list(request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']
    agent = Agent_user.objects.get(id=agent_id)

    page = int(str(request.GET['page']))
    size = int(str(request.GET['size']))
    index_left = (page - 1) * size
    index_right = page * size
    # user_data = list(Users.objects.values()[page:page_right])
    arr = Users.objects.filter(referee=agent.invite_code).values()
    user_data = list(arr[index_left:index_right])

    total_page = arr.count()

    data = {'tableData': user_data, 'totalPage': total_page}

    return JsonResponse({'code': 20000, 'data': data})


@check_login
def user_list(request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']
    #搜索类型 0 全部 1仅搜代理 2仅搜玩家
    # type = dict['seachType']

    value = int(str(request.GET['value']))
    if agent_id == 1:
        page = int(str(request.GET['page']))
        size = int(str(request.GET['size']))
        if value == 0:
            return response_all_users(page, size)
        elif value == 1:
            return response_delegates(page, size)
        else:
            return reponse_players(page, size)
        # page = int(str(request.GET['page']))
        # size = int(str(request.GET['size']))
        # index_left = (page - 1) * size
        # index_right = page * size
        # # user_data = list(Users.objects.values()[page:page_right])
        # user_data = list(Users.objects.values()[index_left:index_right])
        #
        # # for us in user_data:
        # #     us["image"] = "https://ss1.bdstatic.com/70cFvXSh_Q1YnxGkpoWK1HF6hhy/it/u=253777390,947512827&fm=23&gp=0.jpg"
        #
        # total_page = Users.objects.count()
        # data = {'tableData': user_data, 'totalPage': total_page, "show": True}
        #
        # page = int(str(request.GET['page']))
        # size = int(str(request.GET['size']))
        # index_left = (page - 1) * size
        # index_right = page * size
        # delegate_Ids = Users.objects.only("referee").filter(referee__gt=0).values("referee").distinct()
        # # 暂时不用多表查询
        # delegate_Ids_list = list(delegate_Ids)
        # li = []
        # for t in delegate_Ids_list:
        #     li.append(t["referee"])
        # rs = list(Users.objects.filter(id__in=li).values()[index_left:index_right])
        # total_page = len(li)
        # data = {'tableData': rs, 'totalPage': total_page}
        # return JsonResponse({'code': 20000, 'data': data})


    else:
        page = int(str(request.GET['page']))
        size = int(str(request.GET['size']))
        index_left = (page - 1) * size
        index_right = page * size
        agent = Agent_user.objects.get(id=agent_id)
        user_data = list(Users.objects.filter(referee=agent.invite_code).values()[index_left:index_right])
        total_page = Users.objects.count()
        data = {'tableData': user_data, 'totalPage': total_page, "show": False}
        return JsonResponse({'code': 20000, 'data': data})


def response_all_users(page,size):
    index_left = (page - 1) * size
    index_right = page * size
    user_data = list(Users.objects.values()[index_left:index_right])
    total_page = Users.objects.count()
    data = {'tableData': user_data, 'totalPage': total_page, "show": True}
    return JsonResponse({'code': 20000, 'data': data})

def reponse_players(page,size):
    index_left = (page - 1) * size
    index_right = page * size
    delegate_Ids = Users.objects.only("referee").filter(referee__gt=0).values("referee").distinct()
    # 暂时不用多表查询
    delegate_Ids_list = list(delegate_Ids)
    li = []
    for t in delegate_Ids_list:
        li.append(t["referee"])
    vo = Users.objects.exclude(id__in=li).values()
    rs = list(vo[index_left:index_right])
    total_page = len(vo)
    data = {'tableData': rs, 'totalPage': total_page, "show": True}
    return JsonResponse({'code': 20000, 'data': data})

def response_delegates(page,size):
    index_left = (page - 1) * size
    index_right = page * size
    delegate_Ids = Users.objects.only("referee").filter(referee__gt=0).values("referee").distinct()
    # 暂时不用多表查询
    delegate_Ids_list = list(delegate_Ids)
    li = []
    for t in delegate_Ids_list:
        li.append(t["referee"])
    rs = list(Users.objects.filter(id__in=li).values()[index_left:index_right])
    total_page = len(li)
    data = {'tableData': rs, 'totalPage': total_page,  "show": True}
    return JsonResponse({'code': 20000, 'data': data})

# 奔驰宝马的代理接口
@check_login
def user_list_vip(request):
    page = int(str(request.GET['page']))
    size = int(str(request.GET['size']))
    index_left = (page - 1) * size
    index_right = page * size
    # user_data = list(Users.objects.values()[page:page_right])
    # user_data = list(Users.objects.values()[index_left:index_right])

    #   array = Agent_user.objects.filter(username__contains=title, parent_id=agent_id)
    # player_data = list(array.values()[index_left:index_right])

    qset = Users.objects.filter(vip__gt=0)
    user_data = list(qset.values()[index_left:index_right])

    total_page = Users.objects.count()

    data = {'tableData': user_data, 'totalPage': total_page}

    return JsonResponse({'code': 20000, 'data': data})


def test1(request):
    pass


def test2(request):
    pass


@check_login
def charge_list(request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']
    username = dict['username']
    value = int(str(request.GET['value']))
    if username != 'admin':

        page = int(str(request.GET['page']))
        size = int(str(request.GET['size']))
        index_left = (page - 1) * size
        index_right = page * size

        array = Charge.objects.filter(origin=agent_id).order_by('-createtime')
        player_data = list(array.values()[index_left:index_right])
        total_page = len(player_data)
        data = {'tableData': player_data, 'totalPage': total_page}
        return JsonResponse({'code': 20000, 'data': data})

    else:
        page = int(str(request.GET['page']))
        size = int(str(request.GET['size']))
        index_left = (page - 1) * size
        index_right = page * size
        total_page = 0
        array = None
        if value == 0:
            vo = Charge.objects.all().order_by('-createtime')
            total_page = len(vo)
            array = vo.all().order_by('-createtime')
        else:
            vo = Charge.objects.filter(recharge_source=value)
            total_page = len(vo)
            array = vo.all().order_by('-createtime')
        player_data = list(array.values()[index_left:index_right])
        data = {'tableData': player_data, 'totalPage': total_page}
        return JsonResponse({'code': 20000, 'data': data})

@check_login
def open_cheat(request):
    flag = int(str(request.GET['flag']))
    user_id = int(str(request.GET['userId']))
    print(flag)


    data = {'userId': user_id, 'flag': flag}

    url_parame = urllib.parse.urlencode(data)

    request = urllib.request.Request("http://localhost:8085/openCheat?" + url_parame,
                                     bytes(json.dumps(data), 'utf8'),
                                     method='GET')

    response = urllib.request.urlopen(request)

    print(response)


    data = {'userId':user_id}
    return JsonResponse({'code': 20000, 'data': data})


@check_login
def agent_change_state(request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']
    username = dict['username']

    if agent_id != 1:
        return JsonResponse({'code': 2000, 'data': '没有权限更改状态'})

    order_id = int(str(request.GET['id']))
    agent_charge = Agent_charge.objects.get(id=order_id)
    if agent_charge.charge_type == 9:
        agent_charge.charge_type = 10
    elif agent_charge.charge_type == 10:
        agent_charge.charge_type = 9

    agent_charge.save()

    data = None

    if agent_charge.charge_type == 9:
        data = "未打款"
    elif agent_charge.charge_type == 10:
        data = "已打款"

    return JsonResponse({'code': 20000, 'data': data})


# 兑换记录
@check_login
def gold_cash_list(request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id_ = dict['id']

    username = dict['username']

    page = int(str(request.GET['page']))
    size = int(str(request.GET['size']))
    index_left = (page - 1) * size
    index_right = page * size

    array = None

    if agent_id_ == 1:
        array = Agent_charge.objects.filter(Q(charge_type__startswith='9') | Q(charge_type__startswith='10'))
    else:
        array = Agent_charge.objects.filter(
            (Q(charge_type__startswith='9') | Q(charge_type__startswith='10')) & Q(agent_id=agent_id_))

    agent_data = list(array.values()[index_left:index_right])
    total_page = len(array)

    for dict in agent_data:
        dict["gold_t"] = -dict["charge_num"]
        if dict["charge_type"] == 9:
            dict["ret"] = "未打款"
        else:
            dict["ret"] = "已打款"

    data = {'tableData': agent_data, 'totalPage': total_page}

    return JsonResponse({'code': 20000, 'data': data})


@check_login
def agent_charge_list(request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']

    username = dict['username']

    if username != 'admin':

        page = int(str(request.GET['page']))
        size = int(str(request.GET['size']))
        index_left = (page - 1) * size
        index_right = page * size

        array = Agent_charge.objects.filter(agent_id=agent_id)
        agent_data = list(array.values()[index_left:index_right])
        total_page = len(array)
        data = {'tableData': agent_data, 'totalPage': total_page}

        print(data)

        return JsonResponse({'code': 20000, 'data': data})

    else:
        page = int(str(request.GET['page']))
        size = int(str(request.GET['size']))
        index_left = (page - 1) * size
        index_right = page * size
        agent_data = None
        total_page = 0
        vo = Agent_charge.objects
        total_page = len(vo)
        data = {'tableData': agent_data, 'totalPage': total_page}
        return JsonResponse({'code': 20000, 'data': data})


def logout(request):
    cache.clear()
    return JsonResponse({'code': 20000, 'data': None})


# @check_login
def fetchplayer(request):
    # 只能查自己邀请码的 id
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']
    agent_user = Agent_user.objects.get(id=agent_id)
    player_id = int(str(request.GET['id']))

    # config.read(settings.BASE_DIR + '/config.conf')
    # gameCategory = config.get('robot', 'gameCategory')


    array = Users.objects.filter(id=player_id)
    player_data = list(array.values()[0:1])
    # 不是总代理不能搜到不是自己

    gameCategory = config.get('robot', 'gameCategory')
    if gameCategory != "zhongxin":
        if agent_id != 1:
            u = array[0]
            str1 = '%d' % (u.referee)
            if str1 != agent_user.invite_code:
                return JsonResponse({'code': 2000, 'data': '没有权限查看该用户'})

    total_page = len(player_data)
    data = {'tableData': player_data, 'totalPage': total_page}
    return JsonResponse({'code': 20000, 'data': data})


@check_login
def search_player(request):
    page = int(str(request.GET['page']))
    size = int(str(request.GET['limit']))
    index_left = (page - 1) * size
    index_right = page * size
    title = None
    try:
        title = str(request.GET['title'])
    except:
        title = ""

    array = Charge.objects.filter(username__contains=title)
    player_data = list(array.values()[index_left:index_right])
    total_page = len(player_data)
    data = {'tableData': player_data, 'totalPage': total_page}
    return JsonResponse({'code': 20000, 'data': data})


@check_login
def search_agent_record(request):
    page = int(str(request.GET['page']))
    size = int(str(request.GET['limit']))
    index_left = (page - 1) * size
    index_right = page * size
    agent_id = None

    try:
        agent_id = int(request.GET['title'])
    except:
        player_data = []
        total_page = len(player_data)
        data = {'tableData': player_data, 'totalPage': total_page}
        return JsonResponse({'code': 20000, 'data': data})

    array = Agent_charge.objects.filter(Q(charge_type=10) | Q(charge_type=9), Q(agent_id=agent_id))
    player_data = list(array.values()[index_left:index_right])
    total_page = len(player_data)
    data = {'tableData': player_data, 'totalPage': total_page}
    return JsonResponse({'code': 20000, 'data': data})


@check_login
def search_agent_charge(request):
    page = int(str(request.GET['page']))
    size = int(str(request.GET['limit']))
    index_left = (page - 1) * size
    index_right = page * size
    title = None

    try:
        title = str(request.GET['title'])
    except:
        player_data = []
        total_page = len(player_data)
        data = {'tableData': player_data, 'totalPage': total_page}
        return JsonResponse({'code': 20000, 'data': data})

    array = Agent_charge.objects.filter(agent_id=title)
    player_data = list(array.values()[index_left:index_right])
    total_page = len(player_data)
    data = {'tableData': player_data, 'totalPage': total_page}
    return JsonResponse({'code': 20000, 'data': data})


# 通过邀请码搜索玩家
@check_login
def serarch_player_list_with_referee(request):
    page = int(str(request.GET['page']))
    size = int(str(request.GET['limit']))
    index_left = (page - 1) * size
    index_right = page * size
    referee = None

    try:
        referee = str(request.GET['referee'])
    except:
        referee = ""

    array = Users.objects.filter(referee=referee)
    player_data = list(array.values()[index_left:index_right])
    total_page = len(player_data)
    data = {'tableData': player_data, 'totalPage': total_page}
    return JsonResponse({'code': 20000, 'data': data})


@check_login
def serarch_player_list(request):
    page = int(str(request.GET['page']))
    size = int(str(request.GET['limit']))
    index_left = (page - 1) * size
    index_right = page * size
    title = None

    # 只能查自己邀请码的 id
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']
    agent_user = Agent_user.objects.get(id=agent_id)

    try:
        title = str(request.GET['title'])
    except:
        title = ""

    array = None
    if agent_user.username == 'admin':
        array = Users.objects.filter(username__contains=title)
    else:
        array = Users.objects.filter(username__contains=title, referee=agent_user.invite_code)

    player_data = list(array.values()[index_left:index_right])
    total_page = len(player_data)
    data = {'tableData': player_data, 'totalPage': total_page}
    return JsonResponse({'code': 20000, 'data': data})


# vip搜索
@check_login
def serarch_player_list_vip(request):
    page = int(str(request.GET['page']))
    size = int(str(request.GET['limit']))
    index_left = (page - 1) * size
    index_right = page * size
    title = None

    try:
        title = str(request.GET['title'])
    except:
        title = ""
    # user.object.filter(Q(question__startswith='Who') | Q(question__startswith='What'))
    array = Users.objects.filter(username__contains=title, vip__gt=0)
    player_data = list(array.values()[index_left:index_right])
    total_page = len(player_data)
    data = {'tableData': player_data, 'totalPage': total_page}
    return JsonResponse({'code': 20000, 'data': data})


@check_login
def fetch_delegates(request):
    page = int(str(request.GET['page']))
    size = int(str(request.GET['limit']))
    index_left = (page - 1) * size
    index_right = page * size
    title = None

    try:
        title = str(request.GET['title'])
    except:
        title = ""

    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']

    agent_name = dict['username']
    array = None

    if agent_name == 'admin':
        array = Agent_user.objects.filter(username__contains=title)
    else:
        array = Agent_user.objects.filter(username__contains=title, parent_id=agent_id)
    player_data = list(array.values()[index_left:index_right])
    total_page = len(player_data)
    data = {'tableData': player_data, 'totalPage': total_page}
    return JsonResponse({'code': 20000, 'data': data})


# 兑换金币
@check_login
def cash_gold(request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']
    username = dict['username']
    dic = json.loads(str(request.GET['model']))
    gold = int(dic["godNum"])
    agent = Agent_user.objects.get(id=agent_id)
    if agent.gold < gold:
        return JsonResponse({'code': 103, 'data': '金币不足！'})
    agent.gold -= gold
    agent_charge = Agent_charge()
    agent_charge.agent_id = agent_id
    agent_charge.charge_src_agent = agent_id
    agent_charge.charge_num = -gold
    # 9代表申请兑换金币并未兑换 10 表示兑换完成
    agent_charge.charge_type = 9
    agent.save()
    agent_charge.save()

    # agent_charge = Agent_charge()
    # agent_charge.agent_id = id
    # agent_charge.charge_src_agent = agent_id
    # agent_charge.charge_num = num
    # agent_charge.charge_type = 8
    # agent_charge.save()

    return JsonResponse({'code': 20000, 'data': agent.gold})


@check_login
# 超级管理员删除代理
def delete_delegate(request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']
    username = dict['username']

    if username == 'admin':
        pass
    else:
        pass


@check_login
def agent_fetch_slf(request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']
    array = Agent_user.objects.filter(id=agent_id)
    player_data = list(array.values()[0:1])
    total_page = len(player_data)
    data = {'tableData': player_data, 'totalPage': total_page}
    return JsonResponse({'code': 20000, 'data': data})


@check_login
def change_password(request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']
    password = request.GET['pwd']
    agent = Agent_user.objects.get(id=agent_id)
    agent.password = password

    state = 1
    try:
        agent.save()
    except:
        state = 0
    data = {"state": state}
    return JsonResponse({'code': 20000, 'data': data})


@check_login
def delete_agent(request):
    delegate_id = int(str(request.GET['id']))
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']
    agent_name = dict['username']
    if agent_name == 'admin':
        obj = Agent_user.objects.get(id=delegate_id)
        obj.delete()
        return JsonResponse({'code': 20000})
    else:
        return JsonResponse({'code': 2000, 'data': '没有权限！'})


# @csrf_exempt
@check_login
def upload(request):
    ret = {'status': False, 'data': None, 'error': None}
    try:
        user = request.GET['data']
        img = request.FILES.get('img')
        ret = random.randint(0, 9999)
        str = '%d_%s.png' % (ret, "aaa")
        f = open(os.path.join('static/wb', str), 'wb')
        for chunk in img.chunks(chunk_size=1024):
            f.write(chunk)
        ret['status'] = True
        ret['data'] = os.path.join('static', str)
    except Exception as e:
        ret['error'] = e
    finally:
        f.close()
        return JsonResponse({'code': 200, 'data': 'ok'})


@csrf_exempt
def goto_upload(request):
    if request.method == 'POST':
        ret = {'status': False, 'data': None, 'error': None}
        try:
            user = request.POST.get('user')
            img = request.FILES.get('img')
            uid = request.POST['uid']
            ret = uid
            filename = img.name
            arr = filename.split('.')
            str = arr[len(arr) - 1]

            website = "" + ret + "." + str
            f = open(os.path.join('static/wb', website), 'wb')
            for chunk in img.chunks(chunk_size=1024):
                f.write(chunk)
            ret['status'] = True
            ret['data'] = os.path.join('static', str)
        except Exception as e:
            ret['error'] = e
        finally:
            f.close()

            if str == "jpg":
                data = {}
                data["title"] = "error"
                data["msg"] = "错误：只能传png格式的二维码"
                return render(request, 'errorview.html', {"data": data})
            else:
                data = {}
                data["title"] = "success"
                data["msg"] = "上传成功"
                return render(request, 'errorview.html', {"data": data})

    uid = request.GET['uid']

    d = {}
    d['uid'] = uid
    return render(request, 'upload.html', {"data": d})


@csrf_exempt
def show_img(request):
    uid = request.GET['uid']
    agent = Agent_user.objects.get(id=uid)

    data = {}
    data["username"] = "用户名:" + agent.username
    data["userId"] = "用户ID：" + uid
    data["url"] = "../static/wb/" + uid + ".png"
    path = os.path.abspath('static/wb')
    path = path + "/" + uid + ".png"
    is_exist = os.path.isfile(path)
    if is_exist:
        return render(request, 'showImage.html', {"data": data})
    else:
        data["msg"] = "错误：该代理没有上传二维码"
        data["title"] = "error"
        return render(request, 'errorview.html', {"data": data})


# 清理打款状态
@check_login
def clear_rebate(request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dic = cache.get(x_token)
    agent_name = dic['username']
    if agent_name != 'admin':
        return JsonResponse({'code': 100, 'data': '没有权限'})

    param = json.loads(str(request.GET['chargeForm']))
    agent_id = int(str(param['id']))
    agent = Agent_user.objects.get(id=agent_id)
    agent_info = json.loads(agent.agent_info)

    first = 0
    second = 0
    for key, value in agent_info["everyDayCost"].items():
        first += value['firstLevel']
        second += value['secondLevel']

        # 所有返利总金额
    total = first + second

    agent_info_record = json.loads(agent.agent_info_record)
    clear_list = agent_info_record['clearingRecord']

    # 之前已经结算过的
    already_clear = 0;
    already_clear_first = 0
    already_clear_second = 0
    for item in clear_list:
        already_clear += item['total']
        already_clear_first += item['first']
        already_clear_second += item['second']

    clear_dict = {}
    date_key = datetime.datetime.now().strftime('%Y-%m-%d')
    # 本次结算的金额
    clear_dict['total'] = total - already_clear

    if total - already_clear == 0:
        return JsonResponse({'code': 20000, 'data': "成功"})

    clear_dict['first'] = first - already_clear_first
    clear_dict['second'] = second - already_clear_second
    clear_dict['date'] = date_key
    clear_list.append(clear_dict)
    r = json.dumps(agent_info_record)
    agent.agent_info_record = r
    agent.save()
    return JsonResponse({'code': 20000, 'data': cal_income(agent_id)})


# 打款记录
# @check_login
def rebate_record_from_admin(request):
    # x_token = request.META['HTTP_X_TOKEN']
    # print(x_token)
    # dic = cache.get(x_token)
    # agent_name = dic['username']
    # if agent_name == 'admin':
    #     return JsonResponse({'code': 100, 'data': '没有权限'})
    #
    # page = int(str(request.GET['page']))
    # size = int(str(request.GET['size']))
    # index_left = (page - 1) * size
    # index_right = page * size
    # # user_data = list(Users.objects.values()[page:page_right])
    # arr = Users.objects.filter(referee=agent.invite_code).values()
    # user_data = list(arr[index_left:index_right])
    #

    uid = int(request.GET['id'])
    page = int(request.GET['page'])
    size = 20
    index_left = (page - 1) * size
    index_right = page * size

    agent = Agent_user.objects.get(id=uid)
    agent_info_record = json.loads(agent.agent_info_record)

    clearing_record = agent_info_record["clearingRecord"]
    rs = list(clearing_record[index_left:index_right])
    agent_info_record["clearingRecord"] = rs
    agent_info_record["size"] = len(rs)

    return JsonResponse({'code': 20000, 'data': agent_info_record, })


def get_room_info(request):
    """
    获取开房信息
    :param request:
    :return:
    """
    date = str(request.GET['date'])

    date = date.split('T')[0]
    print(date)
    gameNumJson = {}
    try:
        log = Log_record.objects.get(id=date)
        gameNumJson = json.loads(log.game_num_data)

    except:
        gameNumJson = {}

    return JsonResponse({'code': 20000, 'data': gameNumJson})

# def cal_income(agent_id):
#     agent = Agent_user.objects.get(id=agent_id)
#     agent_info = json.loads(agent.agent_info)
#
#     total1 = 0
#     first_level1 = 0
#     second_level1 = 0
#
#     total2 = 0
#     first_level2 = 0
#     second_level2 = 0
#
#     for key, value in agent_info["everyDayCost"].items():
#         print(key, ' value : ', value)
#         partner = value["partner"]
#
#         # 没有结算
#         if int(partner) == 0:
#             total1 += value["firstLevel"]
#             total1 += value["secondLevel"]
#             first_level1 += value["firstLevel"]
#             second_level1 += value["secondLevel"]
#         else:
#             total2 += value["firstLevel"]
#             total2 += value["secondLevel"]
#             first_level2 += value["firstLevel"]
#             second_level2 += value["secondLevel"]
#
#         dic = {}
#         dic["total1"] = total1
#         dic["firstLevel1"] = first_level1
#         dic["secondLevel1"] = second_level1
#
#         dic["total2"] = total2
#         dic["firstLevel2"] = first_level2
#         dic["secondLevel2"] = second_level2
#
#     return dic

