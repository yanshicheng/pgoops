import os.path
import re
import socket
import tarfile
import zipfile
from datetime import datetime

import ansible_runner
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from common.file import File
from pgoops.settings import MEDIA_ROOT
from .models import Task, TaskEvent, TaskState, TaskStats, EventState, Repository

stats_keys = {'changed', 'dark', 'failures', 'ignored', 'ok', 'rescued', 'skipped'}


def resolv(host: str):
    try:
        return socket.gethostbyname(host)
    except:
        return None


class PrepareHandler:
    def __init__(self, code_package):
        self.code_package = code_package
        self.work_dir = settings.IAC_WORK_DIR
        # 包名
        self.package_name = self.code_package.name.split('.')[0]
        # 包解压父路径
        self.base_package_path = os.path.join(MEDIA_ROOT, self.work_dir)
        # 包解压路径
        self.abs_package_path = os.path.join(MEDIA_ROOT, self.work_dir, self.package_name)
        # django 机制写入
        self.tmp_package_name = f'{self.work_dir}/iac_tmp/{self.code_package.name}'
        # 软件包读取目录
        self.tmp_package_path = os.path.join(MEDIA_ROOT, self.tmp_package_name)

    def create(self):
        # match self.code_package.:
        try:
            if Repository.objects.filter(name=self.package_name).first():
                raise Exception(f'同名项目已经存在，如需更换请选择更新. 项目名: {self.package_name}')
            self._tmp_save()
            if zipfile.is_zipfile(self.code_package):
                self._package_verify('zip', 'r')
                self._un_zip()
            elif tarfile.is_tarfile(self.code_package):
                match self.code_package.name.split('.')[-1]:
                    case 'tar':
                        self._package_verify('tar', 'r')
                        self._un_tar()
                    case 'gz':
                        self._package_verify('tar', 'r:gz')
                        self._un_tar('r:gz')
                    case 'xz':
                        self._package_verify('tar', 'r:xz')
                        self._un_tar('r:xz')
                    case _:
                        raise Exception('非法结尾，暂时不支持')
            else:
                raise Exception('不支持的包')
            return self.package_name
        except Exception as e:
            self._tmp_rm()
            raise e

    def update(self):
        try:
            self._tmp_save()
            if zipfile.is_zipfile(self.code_package):
                self._package_verify('zip', 'r')
                self._un_zip(method='update')
            elif tarfile.is_tarfile(self.code_package):
                match self.code_package.name.split('.')[-1]:
                    case 'tar':
                        self._package_verify('tar', 'r', 'update')
                        self._un_tar(method='update')
                    case 'gz':
                        self._package_verify('tar', 'r:gz', 'update')
                        self._un_tar('r:gz', method='update')
                    case 'xz':
                        self._package_verify('tar', 'r:xz', 'update')
                        self._un_tar('r:xz', method='update')
                    case _:
                        raise Exception('非法结尾，暂时不支持', 'update')
            else:
                raise Exception('不支持的包')
        except Exception as e:
            self._tmp_rm()
            raise e

    def _un_zip(self, mode='r', method='create'):
        try:
            if method != 'create':
                if File.if_dir_exists(self.abs_package_path):
                    File.rm_dirs(self.abs_package_path)

            with zipfile.ZipFile(self.tmp_package_path, mode) as f:
                f.extractall(self.base_package_path)
            self._tmp_rm()
        except Exception as e:
            self._tmp_rm()
            raise e

    def _un_tar(self, mode='r', method='create'):
        try:
            if method != 'create':
                if File.if_dir_exists(self.abs_package_path):
                    File.rm_dirs(self.abs_package_path)
            with tarfile.TarFile.open(self.tmp_package_path, mode) as f:
                # File.create_dir(self.abs_package_path)
                f.extractall(self.base_package_path)
            self._tmp_rm()
        except Exception as e:
            self._tmp_rm()
            raise e

    def _package_verify(self, layout, mode='r', method='create'):
        try:
            dir_num = 0
            site, hosts = False, False
            if layout == 'tar':
                with tarfile.TarFile.open(self.tmp_package_path, mode) as f:
                    for name in f.getnames():
                        if re.match('\./\w*$', name):
                            dir_num += 1
                            self.package_name = name.split('/')[1]
                        elif re.match('\./\w*/project/deploy.yaml$', name):
                            site = True
                        elif re.match('\./\w*/inventory/hosts$', name):
                            hosts = True
            else:
                if self.code_package.name.split('.')[-1] == 'zip':
                    with zipfile.ZipFile(self.code_package, mode) as f:
                        for name in f.namelist():
                            if re.match('\./\w*$', name):
                                dir_num += 1
                                self.package_name = name.split('/')[1]
                            elif re.match('\./\w*/project/deploy.yaml$', name):
                                site = True
                            elif re.match('\./\w*/inventory/hosts$', name):
                                hosts = True
                else:
                    raise Exception('非法结尾，暂时不支持, 支持: tar, tar.gz, tar.xz, zip')

            if dir_num != 1:
                raise Exception('项目包应该有一个顶级目录')
            if not site or not hosts:
                raise Exception('必须包含入口文件:./package_name/project/deploy.yaml， hosts文件: ./package_name/project/hosts')
            if self.package_name.startswith('/') or '..' in self.package_name:
                raise Exception("code_package 名称存在目录溢出风险，请更换包名")
            self.abs_package_path = os.path.join(MEDIA_ROOT, self.work_dir, self.package_name)
            if method == 'create':
                if File.if_dir_exists(self.abs_package_path):
                    raise Exception(f'code_package 重名，请更换包名。{self.package_name}')
        except Exception as e:
            self._tmp_rm()
            raise e

    def _tmp_save(self):
        default_storage.save(self.tmp_package_name, ContentFile(self.code_package.read()))

    def _tmp_rm(self):
        if File.if_file_exists(self.tmp_package_path):
            File.rm_file(self.tmp_package_path)


class BaseEventHandler:
    def __init__(self, Task: Task, pattern: str):
        self.Task = Task
        self.pattern = pattern

    def __call__(self, event: dict):
        if hasattr(self, 'on_any'):
            self.on_any(event)
        if event.get('stdout') and hasattr(self, 'on_output'):
            self.on_output(event['stdout'])
        if hasattr(self, event['event']):
            return getattr(self, event['event'])(event['event_data'])
        return True


class EventHandler(BaseEventHandler):
    def _save_event(self, data: dict, state: EventState):
        host = data.get('remote_addr', data['host'])

        TaskEvent.objects.create(
            task_record=self.Task,
            state=state,
            play=data['play'],
            task=data['task'],
            host=host,
            ip=resolv(host),
            start=datetime.fromisoformat(data['start']),
            end=datetime.fromisoformat(data['end']),
            duration=data['duration'],
            changed=data['res'].get('changed') if 'changed' in data['res'] else data['res']['_ansible_no_log'],
            detail=data['res']
        )

    def runner_on_failed(self, data: dict):
        self._save_event(data, EventState.FAILED)
        return True

    def runner_on_ok(self, data: dict):
        self._save_event(data, EventState.OK)
        return True

    def runner_on_skipped(self, data: dict):
        self._save_event(data, EventState.SKIPPED)
        return True

    def runner_on_unreachable(self, data: dict):
        self._save_event(data, EventState.UNREACHABLE)
        return True

    def playbook_on_stats(self, data: dict):
        # 获取简述，每个IP的失败成功数量
        # {'playbook': 'deploy.yaml', 'playbook_uuid': 'a05cc953-998b-4ec2-b6f1-93055d6d7f6f',
        # 'changed': {'localhost': 2}, 'dark': {}, 'failures': {}, 'ignored': {}, 'ok':
        # {'localhost': 4}, 'processed': {'localhost': 1}, 'rescued': {}, 'skipped': {},
        # 'artifact_data': {}, 'uuid': '97a38271-3585-41e9-9d47-a8b0749dcacb'}
        stats_map = {}
        for k, v in data.items():
            if k not in stats_keys:
                continue
            for host, count in v.items():
                stats = stats_map.get(host, TaskStats(task_record=self.Task, host=host, ip=resolv(host)))
                setattr(stats, k, count)
                stats_map[host] = stats
        for stats in stats_map.values():
            stats.save()
        return True

    def on_output(self, out: str):
        if self.Task.output:
            self.Task.output = f'{self.Task.output}\n{out}'
        else:
            self.Task.output = out
        self.Task.save()
        if self.pattern:
            self.Task.handle_changed()


class TaskRunner:
    def __init__(self, instance: Task, pattern=None):
        self.instance = instance
        self.pattern = pattern
        # self.work_dir = settings.BASE_DIR.joinpath('playbook', instance.repository)
        self.work_dir = self.instance.repository.get_package_path()

    def on_status_change(self, runner_status, **kwargs):
        status = runner_status.get('status')
        if status == 'running' or status == 'starting':
            self.instance.state = TaskState.RUNNING
        elif status == 'successful':
            self.instance.state = TaskState.COMPLETED
        elif status == 'canceled':
            self.instance.state = TaskState.CANCELED
        elif status == 'timeout':
            self.instance.state = TaskState.TIMEOUT
        elif status == 'failed':
            self.instance.state = TaskState.FAILED
        self.instance.save()
        if self.pattern:
            self.instance.handle_changed()

    def on_finished(self, runner):
        self.instance.output = runner.stdout.read()
        self.instance.save()

    def execute(self, ):
        try:
            ansible_runner.run(private_data_dir=self.work_dir,
                               status_handler=self.on_status_change,
                               # finished_callback=self.on_finished,
                               event_handler=EventHandler(self.instance, self.pattern),
                               **self.instance.to_runner_kwargs()
                               )
        except Exception as e:
            self.instance.state = 3
            self.instance.output = str(e)
            self.instance.save()
            raise e
