import json

import requests
import simplejson

from .config_dispose import ConfigDispose


class PrometheusApi:
    def __init__(self, url=ConfigDispose.get_value("monitoring", "prometheus_url")):
        self.url = url
        self.session = requests.session()
        self.session.headers = {"Content-Type": "application/json;charset=utf-8"}

    def execute(self, query):
        url = f"{self.url}/api/v1/query?query={query}"
        response = self.session.post(url, data=json.dumps({"query": query}))
        if response.status_code == 200:
            return (
                simplejson.loads(response.content.decode("utf-8"))["data"]["result"], True
            )
        else:
            return self.connect_error()

    @classmethod
    def reload(cls, scheme, addr, port):
        url = f"{scheme}://{addr}:{port}/-/reload"
        response = cls().session.post(url)
        if response.status_code == 200:
            return "", True
        else:
            return cls().connect_error()

    def connect_error(self):
        return "连接Prometheus服务器错误，请在系统设置中进行修改。", False


PrometheusApi = PrometheusApi(ConfigDispose.get_value("monitoring", "prometheus_url"))
