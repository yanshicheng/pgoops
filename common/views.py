from rest_framework.views import APIView


class StandardApiView(APIView):
    pass


class StandardOpenApiView(APIView):
    """
    APIView视图类
    """
    authentication_classes = []
    permission_classes = []
