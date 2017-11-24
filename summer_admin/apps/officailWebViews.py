from django.http import JsonResponse
from django.shortcuts import render
from summer_admin.robot.robot import config
from summer_admin.apps.views import *

def officail_web(request):
    category = config.get('robot', 'gameCategory')
    url = None;
    if category == "tongcheng":
        url = "http://fir.im/ncdp"
    elif category == "laotie":
        url = "http://fir.im/ncjb"
    else:
        url = ""
    dict = {"url": url, "category": category}
    return render(request, "officialWeb.html", {"data": dict})