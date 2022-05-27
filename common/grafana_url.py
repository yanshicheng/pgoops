from enum import Enum
from django.core.cache import cache
import requests
from urllib import parse
from common.config_dispose import ConfigDispose

dashboard_dic = {
    "physical_server": ConfigDispose.get_value("monitoring", "grafana_node_uri"),
    "server": ConfigDispose.get_value("monitoring", "grafana_all_node_uri"),
}


def explain_url(
        ds: dashboard_dic,
):
    """
    返回 grafana url
    http://10.211.55.11:3000/
    d/aka/fu-wu-qi-xin-xi-mian-ban?orgId=1&from=1651844138725&to=1651854938725&theme=light
    """
    url = ConfigDispose.get_value("monitoring", "grafana_url")
    grafana_url = cache.get(ds)
    if grafana_url and url in grafana_url:
        return grafana_url, True
    else:
        grafana_url = parse.urljoin(
            url,
            dashboard_dic[ds],
        )
        grafana_url = grafana_url + "?theme=light&kiosk=tv&to=now&refresh=5s&from=now-30m"

    try:
        status_req = requests.get(grafana_url, timeout=2)
        if status_req.status_code == 200:
            cache.set(ds, grafana_url, timeout=86400)
            return grafana_url, True
        else:
            cache.delete(ds)
            return f"Grafana连接异常，请在系统设置中进行修改。\n当前连接地址: {url}", False
    except Exception:
        cache.delete(ds)
        return f"Grafana连接异常，请在系统设置中进行修改。\n当前连接地址: {url}", False


def application_explain_url(uri, search):
    url = ConfigDispose.get_value("monitoring", "grafana_url")
    grafana_url = parse.urljoin(
        url,
        uri,
    )
    url = cache.get(grafana_url)
    if not url:
        try:
            status_req = requests.get(grafana_url, timeout=2)
            if status_req.status_code != 200:
                return f"Grafana连接异常，请在系统设置中进行修改Grafana连接地址和在应用组中修改Grafana Uri。\n当前连接地址: {grafana_url}", False
            else:
                cache.set(grafana_url, grafana_url, timeout=86400)
                url = grafana_url
        except Exception:
            return f"Grafana连接异常，请在系统设置中进行修改Grafana连接地址和在应用组中修改Grafana Uri。\n当前连接地址: {grafana_url}", False

    grafana_url = (
            url
            + f"?theme=light&kiosk=tv&var-prometheus=Prometheus&var-project=All&var-env=All&var-instance={search}&from=now-5m&to=now&refresh=5s&var-interval=30s&"
    )
    return grafana_url, True
