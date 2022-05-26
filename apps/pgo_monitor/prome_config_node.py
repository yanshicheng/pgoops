import os.path
from collections import OrderedDict

from apps.pgo_monitor.models import Node, Group
from common.config_dispose import ConfigDispose


class PromeConfig:
    @classmethod
    def parse(cls, instance: Node):
        # config = OrderedDict([('global', cls().global_config()),
        #                       ('alerting', cls().alerting_config()),
        #                       ('rule_files', cls().rule_config(instance)),
        #                       ('scrape_configs', cls().scrape_config(instance.host.get_unique_data()))])
        config = {
            "global": cls().global_config(),
            "alerting": cls().alerting_config(),
            "rule_files": cls().rule_config(instance),
            "scrape_configs": cls().scrape_config(instance.host.get_unique_data()),
        }
        return config

    def global_config(self):
        return {
            "scrape_interval": "15s",
            "evaluation_interval": "15s",
            "scrape_timeout": "10s",
            "query_log_file": "/var/log/prometheus_query_log",
            "external_labels": {"account": "huawei-main"},
        }

    def alerting_config(self):
        return {
            "alertmanagers": [
                {
                    "static_configs": [
                        {
                            "targets": [
                                f'{ConfigDispose.get_value("monitoring", "alertmanager_url").split("/")[2]}'
                            ]
                        }
                    ]
                }
            ]
        }

    def rule_config(self, instance: Node):
        rule_path = instance.get_rules_path()
        return [
            f"{rule_path}",
        ]

    def scrape_config(self, node_name):
        scrape_list = []
        scrape_list.append(
            {
                "job_name": "prometheus",
                "static_configs": [{"targets": ["localhost:9090"]}],
            }
        )
        all_group = Group.objects.all()
        for group in all_group:
            scrape_list.append(
                {
                    "job_name": f"{group.name}_export",
                    "consul_sd_configs": [
                        {
                            "server": f'{ConfigDispose.get_default("consul_addr")}:{ConfigDispose.get_default("consul_port")}',
                            "services": [f"{group.name}_export_{node_name}"],
                        }
                    ],
                    "relabel_configs": [
                        {
                            "action": "labelmap",
                            "regex": "__meta_consul_service_metadata_(.*)",
                            "replacement": "$1",
                        }
                    ],
                }
            )
        return scrape_list
