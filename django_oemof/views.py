"""Views for django_oemof"""

from rest_framework.response import Response
from rest_framework.views import APIView

from django_oemof import results, simulation


class SimulateEnergysystem(APIView):
    """View to build and simulate Oemof energysystem from datapackage"""

    @staticmethod
    def get(request):
        """
        Simulates ES given by scenario and parameters

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
        simulation.simulate_scenario(scenario, parameters)
        return Response()


class CalculateResults(APIView):
    """View calculate results from oemof simulation"""

    @staticmethod
    def get(request):
        """
        Calculates results for given scenario (with parameters)

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
