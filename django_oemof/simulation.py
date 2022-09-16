"""Simulation module"""

import multiprocessing as mp

# pylint: disable=W0611
import oemof.tabular.datapackage  # noqa
from oemof import solph
from oemof.network.energy_system import EnergySystem
from oemof.tabular.facades import TYPEMAP

from django_oemof import models


def multiprocess_energysystem(oemof_datapackage):
    """
    Starts multiprocessed simulation of Oemof energysystem

    Multiprocessing is needed as pyomo solver must be run in main thread

    Parameters
    ----------
    oemof_datapackage: str
        Path to datapackage.json of oemof.tabular energysystem datapackage

    Returns
    -------
    result_id: int
        Primary key of stored OemofDataset
    """
    energysystem = EnergySystem.from_datapackage(oemof_datapackage, typemap=TYPEMAP)
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
