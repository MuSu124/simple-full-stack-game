import json

from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@csrf_exempt
@require_POST
def register(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"message": "请求数据不是有效的 JSON"},
            status=400,
        )

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return JsonResponse(
            {"message": "用户名和密码不能为空"},
            status=400,
        )

    if User.objects.filter(username=username).exists():
    # 这是个orm查询，查询的是db这个默认库的user表（也是django自带的表），
    # 查询条件是username=username，意思是查找username字段等于传入的username的记录，如果存在就返回True，否则返回False。
        return JsonResponse(
            {"message": "用户名已经存在"},
            status=409,
        )

    User.objects.create_user(
    # 这是user这个模型类（因为auth_user是个自带的表，user就是其对应的模型类）的create_user方法，会自动对密码进行哈希处理，并保存到数据库中。
    # create_user方法会创建一个新的User对象，并将其保存到数据库中。它接受两个参数：username和password，分别对应用户名和密码。
    # 这里的username和password是从前端传过来的数据，已经在上面进行了验证，确保不为空且用户名不存在。
    # 这个方法会返回一个User对象，但是我们这里不需要使用它，所以没有赋值给任何变量。
        username=username,
        password=password,
    )

    return JsonResponse(
        {"message": "注册成功"},
        status=201,
    )


@csrf_exempt
@require_POST
def login_view(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"message": "请求数据不是有效的 JSON"},
            status=400,
        )

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return JsonResponse(
            {"message": "用户名和密码不能为空"},
            status=400,
        )

    user = authenticate(
        request,
        username=username,
        password=password,
    )

    if user is None:
        return JsonResponse(
            {"message": "用户名或密码错误"},
            status=401,
        )

    auth_login(request, user)

    return JsonResponse(
        {
            "message": "登录成功",
            "user": {
                "id": user.id,
                "username": user.username,
            },
        }
    )
