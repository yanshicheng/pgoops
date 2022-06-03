import re
from urllib.parse import urlparse

import requests
from django.http import QueryDict, HttpResponse
from rest_framework.response import Response
from rest_framework.status import HTTP_502_BAD_GATEWAY, HTTP_200_OK

from apps.pgo_message_center.views.webhook import WebHookBaseOpenApiView
from common.response import api_ok_response


def grafana_proxy(request, url, requests_args=None):
    requests_args = (requests_args or {}).copy()
    headers = {}
    for key, value in request.META.items():
        if key.startswith("HTTP_") and key != "HTTP_HOST":
            headers[key[5:].replace("_", "-")] = value
        elif key in ("CONTENT_TYPE", "CONTENT_LENGTH"):
            headers[key.replace("_", "-")] = value
    params = request.GET.copy()
    if "headers" not in requests_args:
        requests_args["headers"] = {}
    if "data" not in requests_args:
        requests_args["data"] = request.body
    if "params" not in requests_args:
        requests_args["params"] = QueryDict("", mutable=True)
    headers.update(requests_args["headers"])
    auth = ""
    for key in list(headers.keys()):
        if key.lower() == "content-length":
            del headers[key]
        if key.upper() == "AUTHORIZATION":
            auth = headers.pop(key)
    headers["X-WEBAUTH-USER"] = "admin"
    requests_args["headers"] = headers
    requests_args["params"] = params
    response = requests.request("GET", url, **requests_args)
    proxy_response = api_ok_response(response.content)
    excluded_headers = {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
        "content-encoding",
        "content-length",
    }
    proxy_response.headers["X-Frame-Options"] = "sameorigin"
    if auth:
        proxy_response.headers["AUTHORIZATION"] = auth

    for key, value in response.headers.items():
        if key.lower() in excluded_headers:
            continue
        elif key.lower() == "location":
            absolute_pattern = re.compile(r"^[a-zA-Z]+://.*$")
            if absolute_pattern.match(value):
                proxy_response[key] = value
            parsed_url = urlparse(response.url)
            if value.startswith("//"):
                proxy_response[key] = parsed_url.scheme + ":" + value
            elif value.startswith("/"):
                proxy_response[key] = (
                    parsed_url.scheme + "://" + parsed_url.netloc + value
                )
            else:
                proxy_response[key] = (
                    parsed_url.scheme
                    + "://"
                    + parsed_url.netloc
                    + parsed_url.path.rsplit("/", 1)[0]
                    + "/"
                    + value
                )
        else:
            proxy_response[key] = value

    return proxy_response


class WebHookPromeOpenApiView(WebHookBaseOpenApiView):
    """
    通过token用户信息
    """

    def post(self, request, *args, **kwargs):
        try:
            # path = 'd/aka/fu-wu-qi-xin-xi-mian-ban'
            # grafana_ins = "10.211.55.11:3000"
            # grafana = f"http://{grafana_ins}"
            # remote_url = f'{grafana}/' + path
            # print(grafana_proxy(request, remote_url))
            # return grafana_proxy(request, remote_url)
            return api_ok_response(
                {
                    "url": "http://10.211.55.11:3000/d/aka/fu-wu-qi-xin-xi-mian-ban?orgId=1&var-instance=10.211.55.12%3A9100&var-interval=30m&from=1651815691070&to=1651826491070"
                }
            )
        except Exception as e:
            return Response(data="error", status=HTTP_502_BAD_GATEWAY)

    def parse(self, data_list):
        return None
