import os

import casbin
from django.conf import settings
from rest_framework.permissions import BasePermission

from apps.pgo_permission.utils.adapter import Adapter


def verify_permission(*args):
    # username, path, method
    adapter = Adapter()
    model_conf_file = os.path.join(settings.BASE_DIR, "config", "prem_model.conf")
    e = casbin.Enforcer(model_conf_file, adapter=adapter)
    return e.enforce(*args)


class ApiRBACPermission(BasePermission):
    def has_permission(self, request, view):
        path = request.META["PATH_INFO"]
        username = request.user.username
        method = request.method
        return verify_permission(username, path, method)
