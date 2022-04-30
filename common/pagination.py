from common.response import api_ok_response

from collections import OrderedDict
from rest_framework import pagination


class StandardResultSetPagination(pagination.PageNumberPagination):
    page_size = 10
    max_page_size = 100
    page_query_param = "page"
    page_size_query_param = "size"

    def get_paginated_response(self, data):
        return api_ok_response(data=OrderedDict([
            ('count', self.page.paginator.count),
            ('page', self.page.number),
            ('size', self.page.paginator.per_page),
            ('num_pages', self.page.paginator.num_pages),
            ('result', data)
        ]))

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'count': {
                    'type': 'integer',
                    'example': 123,
                },
                'page': {
                    'type': 'integer',
                    'example': 1,
                },
                'size': {
                    'type': 'integer',
                    'example': 10,
                },
                'num_pages': {
                    'type': 'integer',
                    'example': 123,
                },
                'results': schema
            }
        }
