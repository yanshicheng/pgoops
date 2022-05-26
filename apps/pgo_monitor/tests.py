# import sys
#
from collections import OrderedDict

import simplejson
from django.test import TestCase

#
# # Create your tests here.
#
# import ansible_runner
#
# import ansible_runner
# r = ansible_runner.run(private_data_dir='./', host_pattern='localhost', module='shell', module_args='whoami')
# # successful: 0
# for each_host_event in r.events:
#     pass
# out, err, rc = ansible_runner.run_command(
#     executable_cmd='python',
#     cmdline_args=['-c', 'print(123)'],
#     runner_mode='subprocess',
#     input_fd=sys.stdin,
#     output_fd=sys.stdout,
#     error_fd=sys.stderr,
#     host_cwd='./',
# )
#
# # print("rc: {}".format(rc))
# # print("out: {}".format(out))
# # print("err: {}".format(err))


import yaml

xx = """
groups:
- name: Allinstances     # 组名
  rules:
  - alert: instanceDown  # 规则名称
    expr: up == 0        # 匹配规则 实例宕机 promQl 表达式
    for: 10s             # 检测持续时间
    annotations:         # 告警自己也是一个时间序列 注解
      title: "instance down" # 告警标题
      description: 'Instance has been down for more than 1 minute.' # 告警详情
    labels:              # 新标签
      serverity: "critical"

  - alert: 主机内存不足
    expr: node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes * 100 < 20
    for: 10s
    labels:
      severity: "critical"
    annotations:
      summary: 主机内存不足 (主机地址 {{ $labels.instance }})
      description: "主机内存已满 当前内存小于百分之70\n  VALUE = {{ $value }}\n  LABELS = {{ $labels }}"

  - alert: warning 测试内存
    expr: node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes * 100 < 20                                                                                                                                              
    for: 10s
    labels:
      severity: "warning"
    annotations:
      summary: warning 主机内存不足 (主机地址 {{ $labels.instance }})
      description: "主机内存已满 当前内存小于百分之70\n  VALUE = {{ $value }}\n  LABELS = {{ $labels }}"
"""
# dicx = {"k", "v", "v", "v"}
# print(yaml.load(stream=xx, Loader=yaml.FullLoader))
# print(OrderedDict([(1,2), (3,4), dicx]))
#
# xxx = {'groups': [{'name': 'mysql', 'rules': [{'alert': '122', 'expr': '323 == 60', 'for': 60, 'annotations': {'summary': '323', 'description': ''}, 'labels': {'severity': 'warning'}}, {'alert': '123你好中国', 'expr': '333322 == 60', 'for': 60, 'annotations': {'summary': '3233', 'description': ''}, 'labels': {'severity': 'error'}}]}]}
#
#
#
# print(yaml.dump(xxx, allow_unicode=True))

# xxxx = 'ssss'
# print(xxxx.endswith('s'))

#
# xxx = 'com.pgoops.ops.pgo.pgo_django.dev'
# print(xxx.split('.')[-2])
l1 = [1, 2, 3, 4]

l2 = [2, 3, 4, 5]

# print(list(set(l1).difference(l2)))

conf = """
# my global config
global:
  scrape_interval: 15s     # 采集间隔时间
  evaluation_interval: 15s # 计算报警和预聚合间隔
  scrape_timeout: 10s      # 采集超时时间
  query_log_file: /var/log/prometheus_query_log  # 查询日志，包含各阶段耗时统计
  external_labels:          # 全局标签组
    account: 'huawei-main'  # 通过本实例采集的数据都会叠加下面的标签

# Alertmanager configuration
alerting:
  alertmanagers:
    - file_sd_configs:
      - files:
        - targets/alertmanager-server.yaml   

# Load rules once and periodically evaluate them according to the global 'evaluation_interval'.
rule_files:
  - recording_rules/*.yaml
  - alerting_rules/*.yml                     # 告警文件
  # - "first_rules.yml"
  # - "second_rules.yml"

# A scrape configuration containing exactly one endpoint to scrape:
# Here it's Prometheus itself.
scrape_configs:
  # The job name is added as a label `job=<job_name>` to any timeseries scraped from this config.
  - job_name: "prometheus"

    # metrics_path defaults to '/metrics'
    # scheme defaults to 'http'.

    static_configs:
      - targets: ["localhost:9090"]

  - job_name: 'alertmanager'             # alertmanager 纳入 prometheus  监控
    file_sd_configs:
    - files:
      - targets/alertmanager-server.yaml

  - job_name: "nodes"
    scrape_interval: 15s
    scrape_timeout: 10s
    metrics_path: /metrics
    scheme: http
    file_sd_configs:
    - files:
      - targets/nodes-*.yml
      refresh_interval: 1m

  - job_name: 'nginx' # 采集nginx的指标
    metrics_path: '/metrics' # 拉取指标的接口路径
    scrape_interval: 10s # 采集指标的间隔周期
    static_configs:
    - targets: ['10.211.55.12:9113'] 
      labels:
        app:  nginx
        env:  prod
        project: jjpgo
        department: all
    - targets: ['10.211.55.11:9113'] 
      labels:
        app:  nginx
        env:  test
        project: jj
        department: all 

  - job_name: 'mysql' # 采集nginx的指标
    metrics_path: '/metrics' # 拉取指标的接口路径
    scrape_interval: 10s # 采集指标的间隔周期
    static_configs:
    - targets: ['10.211.55.11:9104'] 
      labels:
        app: mysql
        env: test
        project: pgoops
        department: all

  - job_name: 'redis' # 采集nginx的指标
    metrics_path: '/metrics' # 拉取指标的接口路径
    scrape_interval: 10s # 采集指标的间隔周期
    static_configs:
    - targets: ['10.211.55.12:9121']
      labels:
        app: redis
        env:  dev
        project: devpgo
        department: all
    - targets: ['10.211.55.11:9121']
      labels:
        app: redis
        env:  prod
        project: pgo
        department: all
  - job_name: "node_export"
    consul_sd_configs:
    - server: '172.16.1.61:8500'
      tags:
        - "nodes"
    relabel_configs:
    - action: labelmap
      regex: '__meta_consul_service_metadata_(.*)'
      replacement: ${1}
"""

# from common.config_dispose import ConfigDispose
# from .models import Group, Node

xxx = "/xx/tt/dd/prometheus.yaml"
print(xxx.split("."))
#
# print(yaml.load(conf, Loader=yaml.FullLoader))
# ids = 'https://127.0.0.1:9090/'
# print(ids.split('/'))
