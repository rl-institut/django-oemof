"""Simulation module"""
import logging
from typing import Optional

# pylint: disable=W0611
import oemof.tabular.datapackage  # noqa
from celery import shared_task
from django.conf import settings
from oemof import solph
from oemof.tabular.facades import TYPEMAP

from django_oemof import hooks, models


class SimulationError(Exception):
    """Raised if simulation failed or simulation is not present"""


@shared_task
def simulate_scenario(scenario: str, parameters: dict, lp_file: Optional[str] = None) -> int:
    """
    Returns ID to oemof results from simulated/restored scenario

    Already stored scenarios are identified by scenario name and
    adapted parameters.

    Parameters
    ----------
    scenario: str
        Name of scenario (used to load related datapackage)
    parameters: dict
        Parameters which are adapted to ES before simulation
    lp_file: Optional[str]
        If set, LP file is stored under given path

    Returns
    -------
    int
        Simulation ID where results are stored
    """
    try:
        simulation = models.Simulation.objects.get(scenario=scenario, parameters=parameters)  # pylint: disable=E1101
        logging.info(f"Simulation for {scenario=} and {parameters=} already present.")
    except models.Simulation.DoesNotExist:  # pylint: disable=E1101
        logging.info(f"Simulating energysystem for {scenario=} and {parameters=}.")
        oemof_datapackage = f"{settings.MEDIA_ROOT}/oemof/{scenario}/datapackage.json"
        energysystem = build_energysystem(oemof_datapackage)
        build_parameters = hooks.apply_hooks(hook_type=hooks.HookType.PARAMETER, scenario=scenario, data=parameters)
        energysystem = adapt_energysystem(energysystem, build_parameters)
        energysystem = hooks.apply_hooks(hook_type=hooks.HookType.ENERGYSYSTEM, scenario=scenario, data=energysystem)
        input_data, results_data = simulate_energysystem(scenario, energysystem, lp_file)
        dataset = models.OemofDataset.store_results(input_data, results_data)
        # pylint: disable=E1101
        simulation = models.Simulation.objects.create(scenario=scenario, parameters=parameters, dataset=dataset)
        simulation.save()
        logging.info(f"Stored simulation results for {scenario=} and {parameters=}.")
    return simulation.id


def build_energysystem(oemof_datapackage: str):
    """
    Builds energysystem from datapackage

    Parameters
    ----------
    oemof_datapackage: str
        Path to oemof.tabular datapackage

    Returns
    -------
    energysystem: Energysystem build from datapacakge
    """
    logging.info(f"Building energysystem from datapackage at '{oemof_datapackage}'.")
    return solph.EnergySystem.from_datapackage(oemof_datapackage, typemap=TYPEMAP)


def adapt_energysystem(energysystem: solph.EnergySystem, parameters: dict):
    """
    Adapt parameters in ES

    This allows loading standard ES and changing specific parameters after build.

    Parameters
    ----------
    energysystem: EnergySystem
        Components in Energysystem are changed by given parameters

    parameters: dict
        Parameters which shall be adapted in ES

    Returns
    -------
    energysystem: Energysystem with changed parameters
    """
    parameters = parameters or {}

    # Very simple attribute adaption of parameters - may be too simple in case of more complex facades
    for group, attributes in parameters.items():
        if group not in energysystem.groups:
            logging.warning(f"Cannot adapt component '{group}', as it cannot be found in energysystem.")
            continue
        for attribute, value in attributes.items():
            if not hasattr(energysystem.groups[group], attribute):
                logging.warning(
                    f"Attribute '{attribute}' not found in component '{group}' in energysystem. "
                    "Adapting the attribute might have no effect."
                )
            setattr(energysystem.groups[group], attribute, value)
        energysystem.groups[group].update()

    return energysystem


def simulate_energysystem(scenario, energysystem, lp_file: Optional[str] = None):
    """
    Simulates ES, stores results to DB and returns simulation ID

    Parameters
    ----------
    scenario: str
        Name of current scenario (used to apply hooks)
    energysystem : EnergySystem
        Built energysystem to be solved
    lp_file: Optional[str]
        If set, LP file is stored under given path

    Returns
    -------
    results : tuple(dict, dict)
        Simulation input and results
    """
    logging.info(f"Starting simulation for {scenario=}...")
    model = solph.Model(energysystem)
    model = hooks.apply_hooks(hook_type=hooks.HookType.MODEL, scenario=scenario, data=model)
    model.solve(solver="cbc")
    if lp_file:
        model.write(lp_file, io_options={'symbolic_solver_labels': True})
    logging.info(f"Simulation for {scenario=} finished.")

    input_data = solph.processing.parameter_as_dict(
        energysystem,
        exclude_attrs=["bus", "from_bus", "to_bus", "from_node", "to_node"],
    )
    results_data = solph.processing.results(model)

    return map(solph.processing.convert_keys_to_strings, (input_data, results_data))
