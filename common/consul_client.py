import consul
from .config_dispose import ConfigDispose


class Consul(object):
    def __init__(self, host, port):
        """初始化，连接consul服务器"""
        self._consul = consul.Consul(host, port, timeout=5)

    def deregister(self, service_id):
        self._consul.agent.service.deregister(service_id=service_id)

    def register(self, name, service_id, host, port, meta=None, tags=None):
        tags = tags or []
        # 注册服务
        self._consul.agent.service.register(
            name=name,
            service_id=service_id,
            address=host,
            port=port,
            tags=tags,
            meta=meta,
            # 健康检查ip端口，检查时间：5,超时时间：30，注销时间：30s
            check=consul.Check().tcp(
                host,
                port,
                "30s",
                "10s",
            ),
        )

    def get_instances(self, service_id):
        origin_instances = self._consul.catalog.service(service_id)[1]
        res = []
        for oi in origin_instances:
            res.append(
                {
                    "service_id": oi.get("ServiceID"),
                    "service_address": oi.get("ServiceAddress"),
                    "service_port": oi.get("ServicePort"),
                    "service_meta": oi.get("ServiceMeta"),
                    "service_tags": oi.get("ServiceTags"),
                }
            )
        return res

    def get_service_id_list(self, service):
        origin_instances = self._consul.catalog.service(service)[1]
        res = []
        for oi in origin_instances:
            res.append(oi.get("ServiceID"))
        return res

    def get_service(self):
        return self._consul.catalog.services()[1].keys()


ConsulClient = Consul(
    ConfigDispose.get_default("consul_addr"), ConfigDispose.get_default("consul_port")
)
