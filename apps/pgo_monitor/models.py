import os
from collections import OrderedDict

import simplejson
import yaml
from django.db import models
from apps.pgo_data_map.models import Asset, Classify
from apps.pgo_message_center.models import Level

# Create your models here.
from common.models import StandardModelMixin

schemeChoices = ((0, "http"), (1, "https"))


class Node(StandardModelMixin):
    host = models.OneToOneField(to=Asset, on_delete=models.CASCADE, verbose_name="绑定主机")
    config_path = models.CharField(max_length=128, verbose_name="配置文件路径")
    rules_path = models.CharField(max_length=128, verbose_name="规则文件路径")
    scheme = models.IntegerField(choices=schemeChoices, default=0)
    port = models.IntegerField()
    status = models.BooleanField(default=True)
    master = models.BooleanField(default=False)

    class Meta:
        db_table = "pgo_monitor_node"
        verbose_name = "服务器组"
        verbose_name_plural = verbose_name

    def get_config_path(self):
        config_path = self.config_path
        if not config_path.startswith("/"):
            raise ValueError("prometheus 配置文件需要使用绝对路径")
        if config_path.endswith(".yml") or config_path.endswith(".yaml"):
            return config_path
        else:
            return os.path.join(config_path, "prometheus.yml")

    def get_rules_path(self):
        rule_path = self.rules_path
        if rule_path.endswith(".yml") or rule_path.endswith(".yaml"):
            pass
        else:
            rule_path = rule_path + "/rules.yml"
        if not rule_path.startswith("/"):
            config_path = self.get_config_path()
            if config_path.endswith(".yml") or config_path.endswith(".yaml"):
                config_path = config_path.rsplit("/", 1)[0]
            return os.path.join(config_path, rule_path)
        else:
            return os.path.join(rule_path)


class Group(StandardModelMixin):
    name = models.CharField(max_length=32)
    scheme = models.IntegerField(choices=schemeChoices, default=0)
    metrics_path = models.CharField(max_length=64)
    consul_tag = models.CharField(max_length=64)
    grafana_path = models.CharField(max_length=280, default="")

    class Meta:
        db_table = "pgo_monitor_group"
        verbose_name = "应用分组"
        verbose_name_plural = verbose_name

    def get_group_rules(self):
        # data = {'groups': [{'name': f'{self.name}', 'rules': []}]}
        data = OrderedDict([("name", f"{self.name}"), ("rules", [])])
        rules_query = self.rules.all()
        if not rules_query:
            return None
        for rule in rules_query:
            rod = OrderedDict()
            rod["alert"] = rule.name
            rod[
                "expr"
            ] = f"{rule.promeql} {rule.get_condition_display()} {rule.threshold_value}"
            rod["for"] = rule.duration
            rod["annotations"] = OrderedDict(
                [("summary", f"{rule.summary}"), ("description", f"{rule.description}")]
            )
            rod["labels"] = (
                OrderedDict([("severity", f"{rule.severity.name}")])
                if not rule.extend_labels
                else OrderedDict(
                    [("severity", f"{rule.severity.name}"), rule.extend_labels]
                )
            )
            data["rules"].append(rod)
        # return str(yaml.dump(simplejson.loads(simplejson.dumps()), allow_unicode=True))
        return data


class LinkClassify(StandardModelMixin):
    """
    节点下关联CMDB类型
    """

    classify = models.OneToOneField(
        to=Classify,
        on_delete=models.CASCADE,
        related_name="monitor_link_classify",
    )

    class Meta:
        db_table = "pgo_monitor_link_classify"
        verbose_name = "节点关联CMDB类型"
        verbose_name_plural = verbose_name


class Application(StandardModelMixin):
    group = models.ForeignKey(
        to=Group, on_delete=models.PROTECT, related_name="application"
    )
    port = models.IntegerField()
    status = models.BooleanField(default=True)
    asset = models.ForeignKey(to=Asset, on_delete=models.CASCADE)
    scheme = models.IntegerField(choices=schemeChoices, default=0)

    class Meta:
        unique_together = ("group", "asset")
        db_table = "pgo_monitor_application"
        verbose_name = "应用分组"
        verbose_name_plural = verbose_name


ConditionChoices = ((0, "=="), (1, "!="), (2, ">"), (3, ">="), (4, "<"), (5, "<="))


class Rules(StandardModelMixin):
    group = models.ForeignKey(to=Group, on_delete=models.PROTECT, related_name="rules")
    name = models.CharField(max_length=128)
    promeql = models.CharField(max_length=1024, null=True, blank=True)
    threshold_value = models.IntegerField(null=True, blank=True)
    condition = models.IntegerField(choices=ConditionChoices, default=0)

    duration = models.CharField(max_length=16, null=True, blank=True)
    severity = models.ForeignKey(
        to=Level, on_delete=models.PROTECT, null=True, blank=True
    )
    summary = models.CharField(max_length=1024, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=True)
    extend_labels = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "pgo_monitor_rules"
        verbose_name = "告警规则"
        verbose_name_plural = verbose_name
