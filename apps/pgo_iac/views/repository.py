import os.path
import tarfile
from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import action

from common.request_info import get_user
from common.viewsets import StandardModelViewSet
from common.response import api_ok_response, api_error_response
from common.file import File

from ..models import Repository, TaskPeriodic
from ..serializers import RepositorySerializer
from ..runner import PrepareHandler


class RepositoryModelViewSet(StandardModelViewSet):
    queryset = Repository.objects.filter().order_by("-id")
    serializer_class = RepositorySerializer
    ordering_fields = ("id",)
    filter_fields = ("name",)
    search_fields = ("name",)

    def create(self, request, *args, **kwargs):

        code_package = request.data.get("code_package")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            package_name = PrepareHandler(code_package).create()
            instance = serializer.save(
                created_by=get_user(request),
                updated_by=get_user(request),
                name=package_name,
            )
            return api_ok_response(self.serializer_class(instance).data)
        except Exception as e:
            name = code_package.name.split(".")[0]
            if not self.queryset.filter(name=name).first():
                if File.if_dir_exists(
                    os.path.join(settings.MEDIA_ROOT, settings.IAC_WORK_DIR, name)
                ):
                    File.rm_dirs(
                        os.path.join(settings.MEDIA_ROOT, settings.IAC_WORK_DIR, name)
                    )
            return api_error_response(str(e))

    def update(self, request, *args, **kwargs):
        request.POST._mutable = True
        re_data = request.data
        code_package = re_data.pop("code_package", False)[0]
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        if code_package and code_package != "undefined":
            PrepareHandler(code_package).update()
            name = code_package.name.split(".")[0]
            if instance.name != name:
                return api_error_response(
                    f"包名不同请重新上传,新包名: {name}, 旧包名: {instance.name}"
                )

        serializer = self.get_serializer(instance, data=re_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(
            created_by=get_user(request), updated_by=get_user(request)
        )

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return api_ok_response(self.serializer_class(instance).data)

    @action(methods=["get"], detail=True)
    def download(self, request, *args, **kwargs):
        instance: Repository = self.get_object()
        if not File.if_dir_exists(instance.get_package_path()):
            return api_error_response(f"项目文件找不到，请联系管理员，项目: {instance.name}")
        self._tar(
            os.path.join(settings.MEDIA_ROOT, settings.IAC_WORK_DIR), instance.name
        )
        download_url = f"{request.scheme}://{request.get_host()}{settings.MEDIA_URL}{settings.IAC_WORK_DIR}/iac_download/{instance.name}.tar.xz"
        return api_ok_response(data={"download_url": download_url})

    @action(methods=["get"], url_path="main-info", detail=True)
    def main_info(self, request, *args, **kwargs):
        instance: Repository = self.get_object()
        abs_file = instance.get_main_file()
        if not File.if_file_exists(abs_file):
            return api_error_response(f"入口文件找不到: {abs_file}")
        with open(abs_file, "r", encoding="utf-8") as f:
            return api_ok_response(data={"main_info": f.read()})

    def _tar(self, base_dir, project):
        try:
            path = os.getcwd()
            os.chdir(base_dir)
            File.rm_dirs("iac_download")
            if not File.if_dir_exists("iac_download"):
                File.create_dir("iac_download")
            tar_abs_name = os.path.join("iac_download", f"{project}.tar.xz")
            t = tarfile.open(tar_abs_name, "w:xz")
            for root, dir, files in os.walk(project):
                for file in files:
                    fullpath = os.path.join(root, file)
                    t.add(fullpath)
            t.close()
            os.chdir(path)
            return tar_abs_name
        except Exception as e:
            os.chdir(settings.BASE_DIR)
            # if File.if_file_exists(tar_abs_name):
            #     File.rm_file(tar_abs_name)
            raise e

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        task_periodic_query = TaskPeriodic.objects.filter(
            repository=instance,
        )
        if task_periodic_query:
            return api_error_response("无法删除项目，任务调度依赖")
        return super(RepositoryModelViewSet, self).destroy(request, *args, **kwargs)
