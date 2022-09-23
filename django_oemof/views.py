"""Views for django_oemof"""

from rest_framework.response import Response
from rest_framework.views import APIView

from django_oemof import simulation


class SimulateEnergysystem(APIView):
    """View to build and simulate Oemof energysystem from datapackage"""

    @staticmethod
    def get(request):
        """
        Takes path to oemof datapackage, simulates ES and returns results

        Parameters
        ----------
        request
            Request

        Returns
        -------
        Response
        """
        scenario = request.GET["scenario"]
        parameters = request.GET.get("parameters", {})
        _, _ = simulation.simulate_scenario(scenario, parameters)
        return Response()
