from apps.pgo_monitor.models import Node
from .consul_client import ConsulClient
from .hash_handle import ConsistentHashRing


def play_load_prometheus():
    all_node = Node.objects.filter(status=True, master=False)
    a_l = []
    for node in all_node:
        a_l.append(
            {
                "port": node.port,
                "name": node.host.get_unique_data(),
                "label": node.host.get_service_tree_env(),
            }
        )


from apps.pgo_monitor.models import Group


def play_load_application():
    all_group = Group.objects.filter()
    for group in all_group:
        asset_all = group.application.filter(status=True)
        for asset in asset_all:
            print(
                {
                    "port": asset.port,
                    "name": asset.asset.get_unique_data(),
                    "label": asset.asset.get_service_tree_env(),
                }
            )


class MonitorTargets:
    def __int__(self):
        self._hash = ConsistentHashRing

    @classmethod
    def prometheus_targets(cls):
        all_node = Node.objects.filter(status=True, master=False)
        targets_n = []
        targets_l = []
        for node in all_node:
            unique_name = node.host.get_unique_data()
            if not unique_name:
                continue
            service_id = f"prometheus_{unique_name}"
            targets_n.append(service_id)
            targets_l.append(
                {
                    "port": node.port,
                    "host": unique_name,
                    "meta": node.host.get_service_tree_env(),
                    "service_id": f"{service_id}",
                }
            )
        cls().diff("prometheus", targets_n)
        cls().send("prometheus", targets_l)

    @classmethod
    def application_targets(cls):
        all_group = Group.objects.all().exclude(name__in=["prometheus"])
        # all_group = Group.objects.all().exclude(name__in=[ 'prometheus', 'alertmanator'])
        for group in all_group:
            targets_l = []
            asset_all = group.application.filter(status=True)
            for asset in asset_all:
                unique_name = asset.asset.get_unique_data()
                if not unique_name:
                    continue
                targets_l.append(
                    {
                        "port": asset.port,
                        "host": unique_name,
                        "meta": asset.asset.get_service_tree_env(),
                    }
                )
            if targets_l:
                if not group.name.endswith("export"):
                    cls().hash_server_name(f"{group.name}_export", targets_l)
                else:
                    cls().hash_server_name(group.name, targets_l)

    def hash_server_name(self, tag_prefix, targets_list):
        prometheus_list = Node.objects.filter(status=True, master=False)
        if len(prometheus_list) == 1:
            service_id_list = []
            for t in targets_list:
                service_id = f'{tag_prefix}_{t["host"]}'
                service_id_list.append(service_id)
                t["service_id"] = service_id
            service_name = f"{tag_prefix}_{prometheus_list[0].host.get_unique_data()}"
            self.diff(service_name, service_id_list)
            self.send(service_name, targets_list)
        else:
            hash_ring_dic = self.hash_ring(prometheus_list, tag_prefix, targets_list)
            for k, v in hash_ring_dic.items():
                self.diff(k, v)
                self.send(k, v)

    def hash_ring(self, node, tag_prefix, target):
        c = ConsistentHashRing(100000, node)
        hash_ring_dic = {}
        for i in target:
            target_node_name = c.get_node(i["host"])
            i["service_id"] = f'{target_node_name}_{i["host"]}'
            # service_id = f'{prometheus_list[0]}_{t["host"]}'
            if f"{tag_prefix}_{target_node_name}" in hash_ring_dic:
                hash_ring_dic[f"{tag_prefix}_{target_node_name}"].append(i)
            else:
                hash_ring_dic[f"{tag_prefix}_{target_node_name}"] = []
                hash_ring_dic[f"{tag_prefix}_{target_node_name}"].append(i)
        return hash_ring_dic

    def diff(self, service_name, target_name):
        old = ConsulClient.get_service_id_list(service_name)
        if old:
            difference = set(old).difference(target_name)
            for name in difference:
                ConsulClient.deregister(name)

    def send(self, service_name, target):
        for t in target:
            ConsulClient.register(name=service_name, **t)
