"""Views for django_oemof"""
import json
import logging

from celery.result import AsyncResult
from rest_framework.response import Response
from rest_framework.views import APIView

from django_oemof import hooks, results, simulation


class SimulateEnergysystem(APIView):
    """View to build and simulate Oemof energysystem from datapackage"""

    @staticmethod
    def get(request):
        """
        Checks simulation run using celery task ID

        Parameters
        ----------
        request
            Holding celery task ID

        Returns
        -------
        Response
            holding simulation ID if simulation is ready, otherwise simulation ID is None
        """
        task_id = request.GET["task_id"]
        task = AsyncResult(task_id)
        if task.ready():
            logging.info(f"Task #{task.task_id} finished.")
            return Response({"simulation_id": task.get()})
        return Response({"simulation_id": None})

    @staticmethod
    def post(request):
        """
        Simulates ES given by scenario and parameters

        Parameters
        ----------
        request
            Request holding scenario and parameters as JSON

        Returns
        -------
        Response
            holding celery task ID
        """
        scenario = request.POST["scenario"]
        parameters_raw = request.POST.get("parameters")
        parameters = json.loads(parameters_raw) if parameters_raw else {}
        parameters = hooks.apply_hooks(
            hook_type=hooks.HookType.SETUP, scenario=scenario, data=parameters, request=request
        )
        task = simulation.simulate_scenario.delay(scenario, parameters)
        logging.info(f"Started simulation task #{task.task_id}.")
        return Response({"task_id": task.task_id})

    @staticmethod
    def delete(request):
        """
        Delete task for given task ID

        Parameters
        ----------
        request
            Holding celery task ID

        Returns
        -------
        Response
            whether task deletion has been successful
        """
        task_id = request.GET["task_id"]
        task = AsyncResult(task_id)
        task.revoke(terminate=True)
        logging.info(f"Terminated task #{task_id}.")
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
        simulation_id = request.GET["simulation_id"]
        calculations = request.GET.getlist("calculations")
        calculated_results = results.get_results(simulation_id, calculations)
        return Response(calculated_results)
