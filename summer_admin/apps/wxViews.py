from summer_admin.apps.views import *
import itchat


from summer_admin.robot import robot


def create_room(request):
    account = str(request.GET['account'])
    password = str(request.GET['password'])
    room_type = request.GET['type']
    rtn = robot.create_room(account, password, room_type)
    print(rtn)
    return JsonResponse(json.loads(rtn))

def qr_callback():
    print('qr callback')


def run_wx(request):
    itchat.auto_login(qrCallback=qr_callback())










