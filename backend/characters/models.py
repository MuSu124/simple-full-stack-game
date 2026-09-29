# Create your models here.
from django.conf import settings
from django.db import models


class Character(models.Model):#创建一个新类型，只要希望它被数据库管理，就做成orm模型
    # 被orm管理的第一步：继承自django.db.models.Model类，表示这是一个模型类，Django会为它创建一个数据库表。
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="characters",
    )
    name = models.CharField(max_length=50)
    level = models.PositiveIntegerField(default=1)
    experience = models.PositiveIntegerField(default=0)
    health = models.PositiveIntegerField(default=100)
    attack = models.PositiveIntegerField(default=10)
    gold = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    # 因为model类带了许多基本的方法，比如创建新实例，编辑instance，删除instance，查询instance等。
    # 所以我们只需要定义好字段和类型就能够使用这个类了（在python和db中都可以使用）。
    # 但是后续角色可能会加入更多的属性和方法，比如技能、装备、任务等，那时我们就需要在这个类中定义（或重写）一些方法来实现这些功能。

    def __str__(self):
        return self.name