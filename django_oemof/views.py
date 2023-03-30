"""Views for django_oemof"""
import json

from rest_framework.response import Response
from rest_framework.views import APIView

from django_oemof import results, simulation, hooks


class SimulateEnergysystem(APIView):
    """View to build and simulate Oemof energysystem from datapackage"""

    @staticmethod
    def post(request):
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
        scenario = request.POST["scenario"]
        parameters_raw = request.POST.get("parameters")
        parameters = json.loads(parameters_raw) if parameters_raw else {}
        parameters = hooks.apply_hooks(
            hook_type=hooks.HookType.SETUP, scenario=scenario, data=parameters, request=request
        )
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
        parameters_raw = request.GET.get("parameters")
        parameters = json.loads(parameters_raw) if parameters_raw else {}
        parameters = hooks.apply_hooks(hook_type=hooks.HookType.PARAMETER, scenario=scenario, data=parameters)
        calculations = request.GET.getlist("calculations")
        calculated_results = results.get_results(scenario, parameters, calculations)
        return Response(calculated_results)
