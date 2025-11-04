# api/views.py
# Create your views here.

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def contact_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        name = data.get("name")
        email = data.get("email")
        message = data.get("message")

        # 这里只是示例：打印在后台日志
        print(f"收到留言：{name} <{email}>：{message}")

        return JsonResponse({"status": "ok", "msg": "Message received"})
    else:
        return JsonResponse({"error": "Invalid request"}, status=400)

