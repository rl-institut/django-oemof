
from rest_framework.views import APIView
from rest_framework.response import Response


class BuildEnergysystem(APIView):
    def post(self, request):
        return Response("jo!")