"""Simulation module"""

import multiprocessing as mp

# pylint: disable=W0611
import oemof.tabular.datapackage  # noqa
from oemof import solph
from oemof.network.energy_system import EnergySystem
from oemof.tabular.facades import TYPEMAP

from django_oemof import models


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
    energysystem = EnergySystem.from_datapackage(oemof_datapackage, typemap=TYPEMAP)
    return energysystem


def adapt_energysystem(energysystem: EnergySystem, parameters: dict):
    """
    Adapt parameters in ES

    This allows loading standard ES and changing specific parameters after build.

    Parameters
    ----------
    energysystem: EnergySystem
        Energysystem to change parameters
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


def multiprocess_energysystem(energysystem):
    """
    Starts multiprocessed simulation of Oemof energysystem

    Multiprocessing is needed as pyomo solver must be run in main thread

    Parameters
    ----------
    energysystem: EnergySystem
        Energysystem which shall be optimized

    Returns
    -------
    result_id: int
        Primary key of stored OemofDataset
    """
    queue = mp.Queue()
    process = mp.Process(target=simulate_and_store_results, args=(queue, energysystem))
    process.start()
    result_id = queue.get()
    process.join()
    return result_id


def simulate_and_store_results(queue, energysystem):
    """
    Simulates energysystem and stores data in database

    Parameters
    ----------
    queue: Queue
        Multiprocessing queue to put results on
    energysystem: EnergySystem
        Oemof Energysystem to simulate
    """
    input_data, result_data = simulate_energysystem(energysystem)
    result_id = models.OemofDataset.store_results(input_data, result_data)
    queue.put(result_id)


def simulate_energysystem(energysystem):
    """
    Simulates ES, stores results to DB and returns simulation ID

    Parameters
    ----------
    energysystem : EnergySystem
        Built energysystem to be solved

    Returns
    -------
    simulation_id : int
        Simulation ID to restore results from
    """
    model = solph.Model(energysystem)
    model.solve(solver="cbc")

    input_data = solph.processing.parameter_as_dict(
        energysystem,
        exclude_attrs=["bus", "from_bus", "to_bus", "from_node", "to_node"],
    )
    results_data = solph.processing.results(model)

    return input_data, results_data
