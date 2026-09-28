import json

from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST

from .models import Character


def character_data(character):
    """把 Character 模型实例转换成可以返回给前端的字典。"""
    return {
        "id": character.id,
        "name": character.name,
        "level": character.level,
        "experience": character.experience,
        "health": character.health,
        "attack": character.attack,
        "gold": character.gold,
        "created_at": character.created_at.isoformat(),
    }


def unauthenticated_response():
    return JsonResponse({"message": "请先登录"}, status=401)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def characters(request):
    """GET 查询当前用户的角色；POST 为当前用户创建角色。"""
    if not request.user.is_authenticated:
        return unauthenticated_response()

    if request.method == "GET":
        user_characters = Character.objects.filter(user=request.user).order_by("id")
        return JsonResponse(
            {"characters": [character_data(character) for character in user_characters]}
        )

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"message": "请求数据不是有效的 JSON"}, status=400)

    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        return JsonResponse({"message": "角色名称不能为空"}, status=400)

    name = name.strip()
    if len(name) > 50:
        return JsonResponse({"message": "角色名称不能超过 50 个字符"}, status=400)

    character = Character.objects.create(
        user=request.user,
        name=name,
    )

    return JsonResponse(
        {
            "message": "角色创建成功",
            "character": character_data(character),
        },
        status=201,
    )


@csrf_exempt
@require_POST
def upgrade_character(request, character_id):
    """强化当前用户拥有的角色。"""
    if not request.user.is_authenticated:
        return unauthenticated_response()

    with transaction.atomic():
        character = (
            Character.objects.select_for_update()
            .filter(id=character_id, user=request.user)
            .first()
        )

        if character is None:
            return JsonResponse({"message": "没有找到这个角色"}, status=404)

        character.level += 1
        character.health += 20
        character.attack += 5
        character.save(update_fields=["level", "health", "attack"])

    return JsonResponse(
        {
            "message": "角色强化成功",
            "character": character_data(character),
        }
    )
