"""Simulation module"""

import multiprocessing as mp

# pylint: disable=W0611
import oemof.tabular.datapackage  # noqa
from django.conf import settings
from oemof import solph
from oemof.network.energy_system import EnergySystem
from oemof.tabular.facades import TYPEMAP

from django_oemof import models, hooks


class SimulationError(Exception):
    """Raised if simulation failed or simulation is not present"""


def simulate_scenario(scenario: str, parameters: dict):
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

    Returns
    -------
    simulation: models.Simulation
        Instance of Simulation
    """
    try:
        simulation = models.Simulation.objects.get(scenario=scenario, parameters=parameters)  # pylint: disable=E1101
    except models.Simulation.DoesNotExist:  # pylint: disable=E1101
        oemof_datapackage = f"{settings.MEDIA_ROOT}/oemof/{scenario}/datapackage.json"
        energysystem = build_energysystem(oemof_datapackage)
        energysystem = adapt_energysystem(energysystem, parameters)
        energysystem = hooks.apply_hooks(hook_type=hooks.HookType.ENERGYSYSTEM, scenario=scenario, data=energysystem)
        input_data, results_data = multiprocess_simulation(scenario, energysystem)
        dataset = models.OemofDataset.store_results(input_data, results_data)
        # pylint: disable=E1101
        simulation = models.Simulation.objects.create(scenario=scenario, parameters=parameters, dataset=dataset)
        simulation.save()
    return simulation


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
    return EnergySystem.from_datapackage(oemof_datapackage, typemap=TYPEMAP)


def adapt_energysystem(energysystem: EnergySystem, parameters: dict):
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
        for attribute, value in attributes.items():
            setattr(energysystem.groups[group], attribute, value)
        energysystem.groups[group].update()

    return energysystem


def multiprocess_simulation(scenario, energysystem):
    """
    Starts multiprocessed simulation of Oemof energysystem

    Multiprocessing is needed as pyomo solver must be run in main thread

    Parameters
    ----------
    scenario: str
        Name of current scenario
    energysystem: EnergySystem
        Energysystem which shall be optimized

    Returns
    -------
    result_id: int
        Primary key of stored OemofDataset
    """
    queue = mp.Queue()
    process = mp.Process(target=simulate_and_store_results, args=(queue, scenario, energysystem))
    process.start()
    results = queue.get()
    process.join()
    return results


def simulate_and_store_results(queue, scenario, energysystem):
    """
    Simulates energysystem and stores data in database

    Parameters
    ----------
    queue: Queue
        Multiprocessing queue to put results on
    scenario: str
        Name of current scenario
    energysystem: EnergySystem
        Oemof Energysystem to simulate
    """
    results = simulate_energysystem(scenario, energysystem)
    queue.put(results)


def simulate_energysystem(scenario, energysystem):
    """
    Simulates ES, stores results to DB and returns simulation ID

    Parameters
    ----------
    scenario: str
        Name of current scenario (used to apply hooks)
    energysystem : EnergySystem
        Built energysystem to be solved

    Returns
    -------
    results : tuple(dict, dict)
        Simulation input and results
    """
    model = solph.Model(energysystem)
    model = hooks.apply_hooks(hook_type=hooks.HookType.MODEL, scenario=scenario, data=model)
    model.solve(solver="cbc")

    input_data = solph.processing.parameter_as_dict(
        energysystem,
        exclude_attrs=["bus", "from_bus", "to_bus", "from_node", "to_node"],
    )
    results_data = solph.processing.results(model)

    return map(solph.processing.convert_keys_to_strings, (input_data, results_data))
