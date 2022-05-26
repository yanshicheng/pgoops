import re
from urllib.request import urlopen

from common.response import api_ok_response, api_error_response
from common.views import StandardApiView, StandardOpenApiView
from common.config_dispose import ConfigDispose


class ConfigApiView(StandardOpenApiView):
    """
    通过token用户信息
    config.items('bitbucket.org')
    """

    def post(self, request, *args, **kwargs):
        section = request.data.get("section")
        data = request.data.get("data")
        match section:
            case "monitoring":
                if self.monitoring(data):
                    for k, v in data.items():
                        self.save_conf(section, k, v)
                else:
                    return api_error_response(
                        "数据上传格式错误，正确格式为: http://www.pgoops/grafana/"
                    )
            case "alert.provider":
                for k, v in data.items():
                    if "******" in v:
                        continue
                    self.save_conf(section, k, v)
        return api_ok_response("ok")

    def get(self, request, *args, **kwargs):
        l_dic = {
            "monitoring": ConfigDispose.get_options_dic("monitoring"),
            "alert_provider": ConfigDispose.get_options_dic("alert.provider"),
        }
        return api_ok_response(l_dic)

    def monitoring(self, data):
        for k, v in data.items():
            if k == "grafana_node_uri" or k == "grafana_all_node_uri":
                continue
            if not self.check_url(v):
                return False
        return True

    def check_url(self, url):
        if re.match(r"^(http|ftp)s?:/{2}\w.+$", url):
            return True
        else:
            return False

    def save_conf(self, section, key, val):
        ConfigDispose.set_val(section, key, val)
