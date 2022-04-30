from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.db import models
from common.models import StandardModelMixin

from apps.pgo_permission.models import Role

# Create your models here.
__all__ = ["Department", "UserProfile"]


# 定义部门
class Department(StandardModelMixin, models.Model):
    name = models.CharField(max_length=32, verbose_name="部门名称")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "pgo_user_department"
        verbose_name = "部门管理"
        verbose_name_plural = "部门管理"


class UserProfile(AbstractUser):
    name = models.CharField(max_length=20, default="", verbose_name="中文姓名")
    icon = models.ImageField(upload_to="icon/user/%Y/%m/%d/", default='icon/user/2022/04/17/pgoops.png', blank=True,
                             null=True)
    email = models.EmailField(
        verbose_name="邮箱", max_length=255)
    position = models.CharField(max_length=50, null=True, blank=True, verbose_name="职位")
    department = models.ForeignKey(
        verbose_name="部门",
        to=Department,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="user",
    )
    staff_id = models.IntegerField(null=True, blank=True, verbose_name="员工编号")
    job_status = models.BooleanField(default=True, verbose_name="员工在职状态")
    phone = models.CharField(verbose_name="手机号码", max_length=32)
    remarks = models.TextField(verbose_name="备注", blank=True, null=True, default=None)
    role = models.ManyToManyField(
        to=Role,
        related_name="user",
        verbose_name="角色",
        blank=True,
    )

    class Meta:
        db_table = "pgo_user_userprofile"
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name
        ordering = ["id"]

    def __str__(self):
        return self.username

    # def check_password(self, raw_password):
    #     """
    #     Return a boolean of whether the raw_password was correct. Handles
    #     hashing formats behind the scenes.
    #     """
    #
    #     def setter(raw_password):
    #         self.set_password(raw_password)
    #         # Password hash upgrades shouldn't be considered password changes.
    #         self._password = None
    #         self.save(update_fields=["password"])
    #
    #     return check_password(raw_password, self.password, setter)
