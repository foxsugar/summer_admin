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

@check_login
def change_user_delegate(request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
     # 总代理id
    agent_id = dict['id']
    # 需要修改的用户id
    dic = json.loads(str(request.GET['chargeForm']))
    pid = dic['id']
    # 需要修改的代理id
    aid  = int(dic['agent_id'])
    if agent_id != 1:
        return JsonResponse({'code': 101, 'data': '没有权限'})

    if aid == 0:
        user = Users.objects.get(id=pid)
        #user.referee = 0
        #user.save()ź
        rpc_client = get_client()
        rtn = rpc_client.bindReferee(pid, 0)
        if rtn == 0:
            return JsonResponse({'code': 20000, 'data': aid})
        else:
            return JsonResponse({'code': 100, 'data': '失败'})

    # Task.object.get(user_id=1)
    array = Agent_user.objects.filter(id=aid)
    entry_list = list(array.all())
    leng = len(entry_list)
    if leng == 0:
        return JsonResponse({'code': 100, 'data': '不存在该代理'})

    agent = Agent_user.objects.get(id=aid)
    # user = Users.objects.get(id=pid)
    # user.referee = agent.invite_code
    # user.save()
    rpc_client = get_client()
    rtn = rpc_client.bindReferee(pid, int(agent.invite_code))
    if rtn == 0:
        return JsonResponse({'code': 20000, 'data': aid})
    else:
        return JsonResponse({'code': 1000, 'data': '充值失败'})


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

    if agent_id == 1:
        page = int(str(request.GET['page']))
        size = int(str(request.GET['size']))
        index_left = (page - 1) * size
        index_right = page * size
        # user_data = list(Users.objects.values()[page:page_right])
        user_data = list(Users.objects.values()[index_left:index_right])
        total_page = Users.objects.count()
        data = {'tableData': user_data, 'totalPage': total_page, "show" : True}
        return JsonResponse({'code': 20000, 'data': data})
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



#奔驰宝马的代理接口
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



@check_login
def charge_list(request):

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

        array = Charge.objects.filter(origin=agent_id)
        player_data = list(array.values()[index_left:index_right])
        total_page = len(player_data)
        data = {'tableData': player_data, 'totalPage': total_page}
        return JsonResponse({'code': 20000, 'data': data})

    else:
        page = int(str(request.GET['page']))
        size = int(str(request.GET['size']))
        index_left = (page - 1) * size
        index_right = page * size
        total_page = Charge.objects.count()
        player_data = list(Charge.objects.values()[index_left:index_right])
        data = {'tableData': player_data, 'totalPage': total_page}
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
    agent_charge = Agent_charge.objects.get(id = order_id)
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

#兑换记录
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
        total_page = Agent_charge.objects.count()
        agent_data = list(Agent_charge.objects.values()[index_left:index_right])
        data = {'tableData': agent_data, 'totalPage': total_page}
        return JsonResponse({'code': 20000, 'data': data})


def logout(request):

    cache.clear()
    return JsonResponse({'code': 20000, 'data': None})

# @check_login
def fetchplayer(request):

    #只能查自己邀请码的 id
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']
    agent_user = Agent_user.objects.get(id = agent_id)
    player_id = int(str(request.GET['id']))

    # config.read(settings.BASE_DIR + '/config.conf')
    # gameCategory = config.get('robot', 'gameCategory')


    array = Users.objects.filter(id=player_id)
    player_data = list(array.values()[0:1])
    #不是总代理不能搜到不是自己

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

    array = Agent_charge.objects.filter(Q(charge_type=10) | Q(charge_type=9) , Q(agent_id=agent_id))
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


#通过邀请码搜索玩家
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
    total_page =  len(player_data)
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

    gameCategory = config.get('robot', 'gameCategory')
    if gameCategory != "zhongxin":
        array = Users.objects.filter(username__contains=title)

    player_data = list(array.values()[index_left:index_right])
    total_page =  len(player_data)
    data = {'tableData': player_data, 'totalPage': total_page}
    return JsonResponse({'code': 20000, 'data': data})

#vip搜索
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
    #user.object.filter(Q(question__startswith='Who') | Q(question__startswith='What'))
    array = Users.objects.filter(username__contains=title, vip__gt=0)
    player_data = list(array.values()[index_left:index_right])
    total_page =  len(player_data)
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

#兑换金币
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
    #9代表申请兑换金币并未兑换 10 表示兑换完成
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
#超级管理员删除代理
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
    array = Agent_user.objects.filter(id = agent_id)
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

            website = "" + ret  + "." + str
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
    return render(request, 'upload.html',{"data": d})


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
        return render(request, 'errorview.html',{"data": data})







