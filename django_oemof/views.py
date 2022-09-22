"""Views for django_oemof"""

from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from django_oemof import simulation


class BuildEnergysystem(APIView):
    """View to build and simulate Oemof energysystem from datapackage"""

    def get(self, request):
        """
        Takes path to oemof datapackage, simulates ES and returns OemofDataset result ID

        Parameters
        ----------
        request
            Request

        Returns
        -------
        Response
        """
        scenario = request.GET["scenario"]
        oemof_datapackage = f"{settings.MEDIA_ROOT}/oemof/{scenario}/datapackage.json"
        energysystem = simulation.build_energysystem(oemof_datapackage)
        result_id = simulation.multiprocess_energysystem(energysystem)
        return Response(f"{result_id=}")
