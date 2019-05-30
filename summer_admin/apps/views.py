import datetime
import json
import math
import os
import random
import uuid

from django.core.cache import cache
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from summer_admin.apps.models import *
from summer_admin.robot.robot import config
from summer_admin.rpc.rpc import *

TIME_OUT = 60 * 60 * 2


def check_login(func):
    """
    检测登录装饰器
    """

    def wrapper(req):
        print(req)
        x_token = req.META['HTTP_X_TOKEN']
        print(x_token)
        agent = cache.get(x_token)
        if agent is None:
            return JsonResponse({'code': 50014, 'message': '请登录'})
        else:
            return func(req)

    return wrapper


@csrf_exempt
def login(request):
    # test_mongo()
    """A view of all bands."""
    data = json.loads(request.body.decode())
    # print(dict(request.body.decode()))
    username = data['username']
    password = data['password']
    users = Agent_user.objects.filter(username=username).filter(password=password)
    if users.values().count() > 0:
        user = users.values()[0]
        # 放入缓存
        user_cache = {'id': user['id'], 'level': user['level'], 'username': user['username']}
        token = uuid.uuid4().hex
        cache.set(token, user_cache, TIME_OUT)
        result = {'code': 20000, 'data': {'token': token}}
        return JsonResponse(result)
    else:
        return JsonResponse({'code': 2000, 'data': '账户密码错误'})


@check_login
def get_info(request):
    """获得用户信息"""

    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']
    username = dict['username']

    roles = None
    if username == 'admin':
        roles = ['admin']
    else:
        roles = ['delegate']

    array = Agent_user.objects.filter(id=agent_id)
    au = array[0]

    data = {'name': username, 'role': roles, 'money': au.money,
            'avatar': 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif'}
    return JsonResponse({'code': 20000, 'data': data})


@check_login
def agent_list(request):
    """代理列表"""
    page = int(str(request.GET['page']))
    size = int(str(request.GET['size']))
    index_left = (page - 1) * size
    index_right = page * size

    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']
    agent_name = dict['username']

    if_show = False
    array = None
    if agent_name == 'admin':
        if 'agent_type' in request.GET:
            array = Agent_user.objects.filter(agent_type=request.GET['agent_type']).order_by('-id').all()
            pass
        else:
            print('没有')
            array = Agent_user.objects.order_by('-id').all()
            pass
        if_show = True
    else:
        if 'agent_type' in request.GET:
            array = Agent_user.objects.filter(parent_id=agent_id, agent_type=request.GET['agent_type']).order_by('-id')
            pass
        else:
            array = Agent_user.objects.filter(Q(parent_id=agent_id)|Q(id=agent_id)).order_by('-id')
            pass


    # array = Agent_user.objects.filter((Agent_user(parent_id=agent_id) | Agent_user(id=agent_id)))
    table_data = list(array.values()[index_left:index_right])
    total_page = len(table_data)

    td = []
    for t in table_data:
        td.append(agent2vo(t))

    total_page = Agent_user.objects.count()

    data = {'tableData': td, "ifShow": if_show, 'totalPage': total_page}

    print(data)

    return JsonResponse({'code': 20000, 'data': data})


@check_login
def agent(request):
    param = json.loads(str(request.GET['agentForm']))
    # param['invite_code'] = 'in'
    param['level'] = 0
    param['parentId'] = 0
    param['idCard'] = "000000000000000000"
    # param['area'] = '1'
    param['address'] = '1'
    param['payDeduct'] = 0
    param['shareDeduct'] = 0
    param['parentPayDeduct'] = 0
    param['parentShareDeduct'] = 0
    param['email'] = '1@qq.com'
    param['cell'] = '11111111111'
    # param['invite_code'] = '0'
    # param['invite_code'] = '0'
    param['realName'] = '0'
    method = request.method

    array = Agent_user.objects.filter(username=param['username'])

    print(len(array))
    if len(array) != 0:
        return JsonResponse({'code': 100, 'data': '该用户名已存在'})

    # 添加代理
    if method == "POST":
        create_agent_user(param, request)

        print("--")
        return JsonResponse({'code': 20000, 'data': param})


@check_login
def agent_charge_gold(request):
    x_token = request.META['HTTP_X_TOKEN']
    dict = cache.get(x_token)
    slf_name = dict["username"]
    slf_id = dict["id"]

    array = Agent_user.objects.filter(id=slf_id)
    t_data = list(array.all())
    agent_user = t_data[0]

    """代理充值"""
    param = json.loads(str(request.GET['chargeForm']))
    id = param['id']
    num = int(str(param['gold_num']))
    isadd = None

    try:
        isadd = param['isadd']
    except:
        isadd = 1

    if isadd == 0:
        num = -num;

    if agent_user.gold < num:
        str1 = None
        if isadd:
            str1 = "充值失败"
        else:
            str1 = "减值失败"
        return JsonResponse({'code': 100, 'data': '充值失败'})

    agent = Agent_user.objects.get(id=id)
    agent.gold += num
    agent.save()

    if slf_name != 'admin':
        agent_user.gold -= num
        agent_user.save()

    # int
    # WX = 1;
    # int
    # ZFB = 2;
    # int
    # SHARE = 3;
    # int
    # CHARGE_CARD = 4;
    # int
    # BIND_REFERRER = 5;
    # int
    # AGENT = 7;

    level = dict["level"]
    agent_id = dict['id']
    agent_charge = Agent_charge()
    agent_charge.agent_id = id
    agent_charge.charge_src_agent = agent_id
    agent_charge.charge_num = num
    agent_charge.charge_type = 8
    agent_charge.save()

    return JsonResponse({'code': 20000, 'data': agent.gold})


@check_login
def agent_charge(request):
    x_token = request.META['HTTP_X_TOKEN']
    dict = cache.get(x_token)
    slf_name = dict["username"]
    slf_id = dict["id"]

    array = Agent_user.objects.filter(id=slf_id)
    t_data = list(array.all())
    agent_user = t_data[0]

    """代理充值"""
    param = json.loads(str(request.GET['chargeForm']))
    id = param['id']
    num = int(param['num'])

    #
    # if not ret:
    #     return JsonResponse({'code': 100, 'data': ' 下分失败'})

    if slf_id == id:
        return JsonResponse({'code': 100, 'data': '不能给自己充值'})

    if num >= 0:
        str1 = "充值失败"
    else:
        str1 = "减值失败"

    if agent_user.money < num:

        if agent_user.gold < num:
            str1 = None

            return JsonResponse({'code': 100, 'data': str1})
        return JsonResponse({'code': 100, 'data': str1})

    agent = Agent_user.objects.get(id=id)
    agent.money += num
    agent.save()

    if slf_name != 'admin':
        agent_user.money -= num
        agent_user.save()

    # int
    # WX = 1;
    # int
    # ZFB = 2;
    # int
    # SHARE = 3;
    # int
    # CHARGE_CARD = 4;
    # int
    # BIND_REFERRER = 5;
    # int
    # AGENT = 7;

    level = dict["level"]
    agent_id = dict['id']
    agent_charge = Agent_charge()
    agent_charge.agent_id = id
    agent_charge.charge_src_agent = agent_id
    agent_charge.charge_num = num
    agent_charge.charge_type = 7
    agent_charge.save()

    return JsonResponse({'code': 20000, 'data': agent.money})


@check_login
def agent_upGoal(request):
    param = json.loads(str(request.GET['chargeForm']))
    uid = int(param['userId'])
    gold = int(param['goal'])
    x_token = request.META['HTTP_X_TOKEN']

    dic = cache.get(x_token)
    slf_id = dic["id"]
    agent_user = Agent_user.objects.get(id=slf_id)

    if gold < 0 and agent_user.id != 1:
        return JsonResponse({'code': 100, 'data': '失败, 没有权限'})

    if agent_user.gold < gold:
        return JsonResponse({'code': 100, 'data': '金币不足，请充值'})

    user = Users.objects.get(id=uid)

    if gold < 0:
        if user.gold + gold < 0:
            return JsonResponse({'code': 100, 'data': '操作错误'})

    # if user.id != 1:
    #     if user.referee != agent_user.invite_code:
    #         return JsonResponse({'code': 100, 'data': '您不能给该用户上下分'})

    rpc_client = get_client()
    o = Order(userId=uid, num=gold, type=ChargeType.gold, agentId=1)
    rtn = rpc_client.charge(o)
    if rtn == 0:
        agent_user.gold -= gold
        agent_user.save()
        return JsonResponse({'code': 20000, 'data': user.gold + gold})
    else:
        return JsonResponse({'code': 100, 'data': '失败'})


@check_login
def agent_downGoal(request):
    param = json.loads(str(request.GET['chargeForm']))
    uid = int(param['userId'])
    gold = int(param['goal'])
    user = Users.objects.get(id=uid)
    rpc_client = get_client()
    order = Order(userId=uid, num=-gold, type=ChargeType.gold, agentId=1)
    rtn = rpc_client.charge(order)
    if rtn == 0:
        return JsonResponse({'code': 20000, 'data': user.gold - gold})
    else:
        return JsonResponse({'code': 100, 'data': ' 下分失败'})


@check_login
def constant(request):
    con = Constant.objects.filter(id=1).values()[0]

    return JsonResponse({'code': 20000, 'data': con})


@check_login
def constant_update(request):
    param = json.loads(str(request.GET['constantForm']))
    constant = Constant.objects.get(id=1)
    constant.init_money = param['init_money']
    constant.apple_check = param['apple_check']
    constant.download = param['download']
    constant.marquee = param['marquee']
    constant.marquee1 = param['marquee1']
    constant.marquee2 = param['marquee2']
    constant.version_of_android = param['version_of_android']
    constant.version_of_ios = param['version_of_ios']
    constant.apple_check = param['apple_check']
    constant.income1 = param['income1']
    constant.income2 = param['income2']
    category = config.get('robot', 'gameCategory')
    if category == 'bcbm':
        constant.access_code = param['access_code']
    constant.save()

    # 刷新游戏服务器数据
    client = get_client()
    # 调用这个是为了刷新服务器内存
    client.getBlackList()
    # client.modifyAndroidVersion(constant.version_of_android)
    return JsonResponse({'code': 20000, 'data': 'ok'})


def agent2vo(agent):
    """代理显示"""

    dic = cal_income(int(agent["id"]))
    print(dic)
    return {
        'id': agent['id'],
        'username': agent['username'],
        'password': agent['password'],
        'invite_code': agent['invite_code'],
        'realName': agent['real_name'],
        'level': agent['level'],
        'parentId': agent['parent_id'],
        'email': agent['email'],
        'createTime': agent['create_time'],
        'idCard': agent['id_card'],
        'cell': agent['cell'],
        'area': agent['area'],
        'address': agent['address'],
        'money': agent['money'],
        'gold': agent['gold'],
        'agent_type': agent['agent_type'],
        'payDeduct': agent['pay_deduct'],
        'shareDeduct': agent['share_deduct'],
        'parentPayDeduct': agent['parent_pay_deduct'],
        'parentShareDeduct': agent['parent_share_deduct'],
        'total1': "¥" + str(dic["total1"]),
        'firstLevel1': "¥" + str(dic['firstLevel1']),
        'secondLevel1': " ¥" + str(dic['secondLevel1']),
        'total2': "¥" + str(dic["total2"]),
        'firstLevel2': "¥" + str(dic['firstLevel2']),
        'secondLevel2': "¥" + str(dic['secondLevel2']),
    }


def cal_income(agent_id):
    agent = Agent_user.objects.get(id=agent_id)
    agent_info = json.loads(agent.agent_info)

    total = 0
    first_level = 0
    second_level = 0

    for key, value in agent_info["everyDayCost"].items():
        first_level += value["firstLevel"]
        second_level += value["secondLevel"]

    total = first_level + second_level

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

    dic = {}
    dic["total1"] = total - already_clear
    dic["firstLevel1"] = first_level - already_clear_first
    dic["secondLevel1"] = second_level - already_clear_second

    dic["total2"] = already_clear
    dic["firstLevel2"] = already_clear_first
    dic["secondLevel2"] = already_clear_second

    return dic


def create_agent_user(agent, request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    level = dict["level"]
    agent_id = dict['id']
    agent_name = dict['username']
    """创建代理"""
    user = Agent_user()
    data = agent
    print(data)
    user.username = data['username']
    user.password = data['password']
    user.invite_code = 0
    user.real_name = data['realName']
    user.level = data['level']
    user.parent_id = agent_id
    user.email = data['email']
    user.create_time = datetime.datetime.now()
    user.id_card = data['idCard']
    user.cell = data['cell']
    user.area = data['area']
    user.address = data['address']
    user.money = 0
    user.gold = 0
    user.pay_deduct = data['payDeduct']
    user.share_deduct = data['shareDeduct']
    user.parent_pay_deduct = data['parentPayDeduct']
    user.parent_share_deduct = data['parentShareDeduct']

    j = {"allRebate": 0, "everyDayCost": {}, "everyDayRebate": {}, "everyPartnerRebate": {}}

    jr = {"clearingRecord": []}
    user.agent_info_record = json.dumps(jr)
    user.agent_info = json.dumps(j)
    # 保存
    user.save()
    user.invite_code = str(user.id)
    user.save()


# 商品分组列表
def get_goods_categories_list(request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    print(dict)
    try:
        categories = list(GoodsCategory.objects.all().values("id", "name"))
        data = {"code": 20000, 'data': categories}
        return JsonResponse(data)
    except:
        data = {"code": 50000}
        return JsonResponse(data)
        pass


# 商品列表
def get_goods_list(request):
    page = int(str(request.GET['page']))
    size = int(str(request.GET['size']))
    index_left = (page - 1) * size
    index_right = page * size
    goods_list = list(Goods.objects.filter(enabled=True).all().order_by("-id").values(
        "id",
        "name",
        "create_date",
        "last_modified_date",
        "logo",
        "price",
        "goods_category_id",
        "gift_voucher"
    )[index_left:index_right])

    totalElements = Goods.objects.filter(enabled=True).all().count()
    totalPages = math.ceil(totalElements / size)

    for goods in goods_list:
        id = goods["goods_category_id"]
        goods_category_name = GoodsCategory.objects.get(id=id).name
        goods["goods_category"] = {"name": goods_category_name}
        pass
    data = {"code": 20000, 'data': goods_list, "total_elements": totalElements,
            "total_pages": totalPages}
    return JsonResponse(data)


# 商品详情
def goods_detail(request):
    try:
        x_token = request.META['HTTP_X_TOKEN']
        print(x_token)
        dict = cache.get(x_token)
        print(dict)
        goods_id = int(request.GET["id"])
        goods = Goods.objects.values("id",
                                     "name",
                                     "create_date",
                                     "last_modified_date",
                                     "logo",
                                     "price",
                                     "goods_category_id",
                                     "gift_voucher").get(id=goods_id)
        data = {"code": 20000, 'data': goods}
        return JsonResponse(data)
    except:
        data = {"code": 50000}
        return JsonResponse(data)
        pass


# 保存商品
def save_goods(request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    print(dict)
    data = json.loads(request.body.decode())
    goods = Goods()
    if "id" in data:
        goods = Goods.objects.get(id=data["id"])
        pass
    goods.name = data["name"]
    goods.logo = data["logo"]
    goods.goods_category_id = data["goods_category_id"]
    goods.price = data["price"]
    goods.gift_voucher = data["gift_voucher"]
    goods.enabled = True
    goods.save()
    data = {"code": 20000, 'data': 1}
    return JsonResponse(data)


# 删除商品
def delete_goods(request):
    try:
        x_token = request.META['HTTP_X_TOKEN']
        print(x_token)
        dict = cache.get(x_token)
        print(dict)
        data = json.loads(request.body.decode())
        goods = Goods.objects.get(id=data["id"])
        goods.enabled = False
        goods.save()
        data = {"code": 20000, 'data': 1}
        return JsonResponse(data)
    except:
        data = {"code": 50000}
        return JsonResponse(data)
        pass


# 批量删除商品
def delete_batch_goods(request):
    try:
        x_token = request.META['HTTP_X_TOKEN']
        print(x_token)
        dict = cache.get(x_token)
        print(dict)
        data = json.loads(request.body.decode())
        for obj in data:
            goods = Goods.objects.get(id=obj["id"])
            goods.enabled = False
            goods.save()
            pass
        data = {"code": 20000, 'data': 1}
        return JsonResponse(data)
    except:
        data = {"code": 50000}
        return JsonResponse(data)
        pass


# 商品兑换列表
def goods_exchange_record_list(request):
    page = int(str(request.GET['page']))
    size = int(str(request.GET['size']))
    index_left = (page - 1) * size
    index_right = page * size
    records = list(GoodsExchangeRecord.objects.all().order_by("-created_date").values(
        "id",
        "users_id",
        "goods_id",
        "id_card",
        "location",
        "status",
        "phone",
        "name",
        "created_date"
    )[index_left:index_right])
    for record in records:
        goods = Goods.objects.values("id",
                                     "name",
                                     "create_date",
                                     "last_modified_date",
                                     "logo",
                                     "price",
                                     "goods_category_id",
                                     "gift_voucher").get(id=record["goods_id"])
        record["goods"] = dict(goods)
        users = Users.objects.values().get(id=record["users_id"])
        record["users"] = dict(users)
        pass
    data = {"code": 20000, 'data': records}
    return JsonResponse(data)


# 公告列表
def notice_list(request):
    try:
        page = int(str(request.GET['page']))
        size = int(str(request.GET['size']))
        index_left = (page - 1) * size
        index_right = page * size
        objects = list(
            Notice.objects.filter(enabled=True).all().order_by("-created_date").values('id', 'content', 'created_date')[
            index_left:index_right])
        totalElements = Notice.objects.filter(enabled=True).all().count()
        totalPages = math.ceil(totalElements / size)
        data = {"code": 20000, 'data': objects, "total_elements": totalElements,
                "total_pages": totalPages}
        return JsonResponse(data)
    except:
        data = {"code": 50000}
        return JsonResponse(data)
        pass


# 公告详情
def notice_detail(request):
    id = int(str(request.GET['id']))
    object = dict(Notice.objects.values('id', 'content', 'created_date').get(id=id))
    data = {"code": 20000, 'data': object}
    return JsonResponse(data)


# 公告保存
def notice_save(request):
    data = json.loads(request.body.decode())
    print(data)
    obj = Notice()
    if "id" in data:
        obj = Notice.objects.get(id=data["id"])
        pass
    obj.content = data["content"]
    obj.enabled = True
    obj.save()
    data = {"code": 20000, 'data': 1}
    return JsonResponse(data)


# 公告删除
def notice_delete(request):
    data = json.loads(request.body.decode())
    print(data)
    obj = Notice.objects.get(id=data["id"])
    obj.enabled = False
    obj.save()
    data = {"code": 20000, 'data': 1}
    return JsonResponse(data)


# 图文列表
def image_text_list(request):
    x_token = request.META['HTTP_X_TOKEN']
    print(x_token)
    dict = cache.get(x_token)
    page = int(str(request.GET['page']))
    size = int(str(request.GET['size']))
    index_left = (page - 1) * size
    index_right = page * size
    if dict['level'] == 1:
        objects = list(
            ImageText.objects.filter(enabled=True).all().order_by("-created_date").values('id', 'content', 'url',
                                                                                          'created_date')[
            index_left:index_right])
        pass
    else:
        objects = list(
            ImageText.objects.filter(enabled=True, agent_enabled=True).all().order_by("-created_date").values('id',
                                                                                                              'content',
                                                                                                              'url',
                                                                                                              'created_date')[
            index_left:index_right])
        pass
    totalElements = ImageText.objects.filter(enabled=True).all().count()
    totalPages = math.ceil(totalElements / size)
    data = {"code": 20000, 'data': objects, "total_elements": totalElements,
            "total_pages": totalPages}
    return JsonResponse(data)


# 图文详情
def image_text_detail(request):
    id = int(str(request.GET['id']))
    object = dict(ImageText.objects.values('id', 'content', 'url', 'created_date').get(id=id))
    data = {"code": 20000, 'data': object}
    return JsonResponse(data)


# 图文保存
def image_text_save(request):
    data = json.loads(request.body.decode())
    obj = ImageText()
    if "id" in data:
        obj = ImageText.objects.get(id=data["id"])
        pass
    obj.content = data["content"]
    obj.enabled = True
    obj.save()
    data = {"code": 20000, 'data': 1}
    return JsonResponse(data)


# 图文删除
def image_text_delete(request):
    data = json.loads(request.body.decode())
    obj = ImageText.objects.get(id=data["id"])
    obj.enabled = False
    obj.save()
    data = {"code": 20000, 'data': 1}
    return JsonResponse(data)


# Every day share settings
def set_share(request):
    data = json.loads(request.body.decode())
    print(data)
    file = open('share.json', 'w')
    file.write(json.dumps(data))
    data = {"code": 20000, 'data': 1}
    return JsonResponse(data)


def share_detail(request):
    file = open('share.json', 'r')
    lines = file.readlines()
    obj = {}
    for line in lines:
        obj = line
        break
    data = {"code": 20000, 'data': json.loads(obj)}
    return JsonResponse(data)


def agent_withdraw(request):
    data = json.loads(request.body.decode())
    agentWithdraw = AgentWithdraw()
    agentWithdraw.money = data['money']
    agentWithdraw.name = data['name']
    agentWithdraw.number = data['number']
    agentWithdraw.phone = data['phone']
    agentWithdraw.type = data['type']
    agentWithdraw.agent_user_id = data['agent_user_id']
    agentWithdraw.enabled = 0
    agentWithdraw.save()
    data = {"code": 20000, 'data': 1}
    return JsonResponse(data)


# 提现申请列表
def agent_withdraw_list(request):
    page = int(str(request.GET['page']))
    size = int(str(request.GET['size']))
    index_left = (page - 1) * size
    index_right = page * size

    objects = list(AgentWithdraw.objects.all().order_by("-created_date").values(
        'id',
        'created_date',
        'enabled',
        'money',
        'name',
        'number',
        'phone',
        'type',
        'agent_user_id')[index_left:index_right])

    totalElements = AgentWithdraw.objects.all().count()
    totalPages = math.ceil(totalElements / size)

    data = {"code": 20000, 'data': objects, "total_elements": totalElements,
            "total_pages": totalPages}
    return JsonResponse(data, safe=False)


# 确认提现
def agent_withdraw_confirm(request):
    data = json.loads(request.body.decode())
    agentWithdraw = AgentWithdraw.objects.get(id=data['id'])
    agentWithdraw.enabled = 1
    agentWithdraw.save()

    user_id = agentWithdraw.agent_user_id
    agent_user = Agent_user.objects.get(id=user_id)
    agent_user.gold = agent_user.gold - float(agentWithdraw.money)
    agent_user.save()

    data = {"code": 20000, 'data': 1}
    return JsonResponse(data)


# 图片上传
def upload(request):
    if request.method == 'POST':
        file_obj = request.FILES.get('file')
        filename = ''.join(str(random.choice(range(20))) for _ in range(20)) + '.jpg'
        print(filename)
        path = os.path.join('/usr/local/nginx/html/upload', filename)
        # path = os.path.join('C:\\Users\\Administrator\\IdeaProjects\\summer-admin\\static\\upload', filename)
        print(path)
        f = open(path, 'wb')
        print(file_obj, type(file_obj))
        for chunk in file_obj.chunks():
            f.write(chunk)
        f.close()
        data = {"code": 20000, 'data': 'upload/%s' % filename}
        return JsonResponse(data)


# 代理申请列表
@check_login
def agent_apply_list(request):
    page = int(str(request.GET['page']))
    size = int(str(request.GET['size']))
    index_left = (page - 1) * size
    index_right = page * size
    objects = list(Wechat_Agent_Apply.objects.all().order_by("-id").values(
        'id',
        'union_id',
        'username',
        'password',
        'real_name',
        'area',
        'agent_type',
        'audited'
    )[index_left:index_right])
    totalElements = Wechat_Agent_Apply.objects.all().count()
    totalPages = math.ceil(totalElements / size)
    data = {"code": 20000, 'data': objects, "total_elements": totalElements,
            "total_pages": totalPages}
    return JsonResponse(data)


# 同意代理申请
def agent_apply_agree(request):
    try:
        with transaction.atomic():
            unionId = str(request.GET['union_id'])
            wechat_Agent_Apply = Wechat_Agent_Apply.objects.values(
                'id',
                'union_id',
                'username',
                'password',
                'real_name',
                'area',
                'agent_type',
                'audited'
            ).get(union_id=unionId)
            param = dict(wechat_Agent_Apply)
            param['level'] = 0
            param['parentId'] = 1
            param['idCard'] = "000000000000000000"
            param['address'] = '1'
            param['payDeduct'] = 0
            param['shareDeduct'] = 0
            param['parentPayDeduct'] = 0
            param['parentShareDeduct'] = 0
            param['email'] = '1@qq.com'
            param['cell'] = '11111111111'
            param['realName'] = param['real_name']
            method = request.method
            array = Agent_user.objects.filter(username=param['username'])
            if len(array) != 0:
                return JsonResponse({'code': 100, 'data': '该用户名已存在'})
            # 添加代理
            create_agent_user(param, request)
            print(wechat_Agent_Apply)
            agent_Apply = Wechat_Agent_Apply.objects.get(id=param['id'])
            agent_Apply.audited = 1
            agent_Apply.save()
            users = Users.objects.get(unionId=unionId)
            users.vip = param['agent_type']
            users.save()
            return JsonResponse({'code': 20000, 'data': 1})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'code': 500})
