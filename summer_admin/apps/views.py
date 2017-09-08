import json
from django.http import HttpResponse
from django.http import HttpRequest
from django.http import JsonResponse
from summer_admin.apps.models import models
from summer_admin.apps.models import Agent_user
from summer_admin.apps.models import Users
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from summer_admin.apps.menu import *


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
        print(user)
        # 放入session
        user_cache = {'id': user['id'], 'level': user['level']}
        request.session['user'] = user_cache
        result = {'success': True, 'message': 'ok'}
        return JsonResponse(result)
    else:
        return JsonResponse({'success': False, 'message': '账户密码错误'})


def check_login(func):
    """
    检测登录装饰器
    """

    def wrapper(req):
        # request.session['usenname']
        if req.session.get('user') is None:
            return JsonResponse({'success': False, 'message': '请登录'})
        else:
            return func(req)

    return wrapper


# @check_login
def get_user(req):
    # user_cache = req.session['user']
    user_cache = {}
    user_cache['id'] = 1
    user_cache['level'] = 1
    user_cache['username'] = 'sun'
    permissions = {'role': 'admin'}
    user_cache['permissions'] = permissions
    return JsonResponse({'success': True, 'user': user_cache})


@check_login
def get_agent(req):
    users = Agent_user.objects.all()
    count = Agent_user.objects.count()

    p = Paginator(users.values(), 3)

    print(users.values())

    print(p.page(1))

    data = {'count': count, "values": list(users.values())}
    response = {'code': 0, 'data': data}
    return JsonResponse(response)


def menus(req):
    get_menu(1)
    ss = str(get_menu(1))
    return HttpResponse(ss)
    # return JsonResponse(get_menu(1))


def dashboard(req):
    # return HttpResponse(get_dash())
    return JsonResponse(get_dash())


def overview(req):
    return JsonResponse({'success': True, 'userId': '1', 'username': 'sun'})


def create_agent_user(req):
    user = Agent_user()
    data = eval(req.POST.get("data"))
    user.username = data['username']
    user.password = data['password']
    user.invite_code = data['invite_code']
    user.real_name = data['real_name']
    user.level = data['level']
    user.parent_id = data['parent_id']
    user.email = data['email']
    user.create_time = data['create_time']
    user.id_card = data['id_card']
    user.cell = data['cell']
    user.area = data['area']
    user.address = data['address']
    user.money = data['money']
    user.pay_deduct = data['pay_deduct']
    user.share_deduct = data['share_deduct']
    user.parent_pay_deduct = data['parent_pay_deduct']
    user.parent_share_deduct = data['parent_share_deduct']
    # 保存
    user.save()
