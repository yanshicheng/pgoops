# import ansible_runner
#
# work_dir = '/data/ops/pgoops/upload/iac/helloworld'
# ansible_runner.run(private_data_dir=work_dir,
#                    playbook='deploy.yaml',
#                    # finished_callback=self.on_finished,
#                    )


{
    'playbook': 'deploy.yaml',
    'playbook_uuid': 'f81c41e7-cae0-4b05-8c32-1f55cb0525bb',
 'play': 'this is a  hello world example', 'play_uuid': 'cb193779-be2b-5ff0-6f63-000000000007', 'play_pattern': 'all',
 'task': 'Gathering Facts', 'task_uuid': 'cb193779-be2b-5ff0-6f63-00000000000f', 'task_action': 'gather_facts',
 'task_args': '', 'task_path': '/data/ops/pgoops/upload/iac/helloworld/project/deploy.yaml:2', 'host': '127.0.0.1',
 'remote_addr': '127.0.0.1',
    'res': {
    'msg': "Unable to execute ssh command line on a controller due to: [Errno 2] No such file or directory: b'ssh'",
    '_ansible_no_log': False}, 'start': '2022-05-01T10:28:47.872449', 'end': '2022-05-01T10:28:47.903364',
 'duration': 0.030915, 'ignore_errors': None, 'event_loop': None, 'uuid': '52d84da8-fb77-4a30-a1f5-164bdebf1fb1'}