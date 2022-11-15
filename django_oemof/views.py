"""Views for django_oemof"""

from rest_framework.response import Response
from rest_framework.views import APIView

from django_oemof import results


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
        calculations = request.GET.get("calculations")
        calculated_results = results.get_results(scenario, parameters, calculations)
        return Response(calculated_results)
