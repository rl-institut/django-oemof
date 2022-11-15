"""Module to calculate oemof results"""

import inspect
from typing import Union
import pandas

from oemoflex.postprocessing import core, postprocessing

from . import simulation, models


CALCULATIONS = {
    member.name: member
    for (name, member) in inspect.getmembers(postprocessing)
    if inspect.isclass(member) and not inspect.isabstract(member) and issubclass(member, core.Calculation)
}


def register_calculation(*calculations: core.Calculation):
    """
    Custom calculations have to be registered first, in order to use them via API
    """
    for calculation in calculations:
        CALCULATIONS[calculation.name] = calculation


def get_results(
    scenario: str, parameters: dict, calculations: list[str]
) -> dict[str, Union[pandas.Series, pandas.DataFrame]]:
    """
    Tries to load results from database.
    If result is not found, simulation data is loaded from db or simulated (if not in DB yet)
    and results are calculated.

    Parameters
    ----------
    scenario : dict
        Scenario name
    parameters : dict
        Adapted parameters
    calculations : list[str]
        List of calculations (by name) which shall be calculated

    Returns
    -------
    dict
        Dict containing calculation name as key and calculation result as value
    """
    try:
        sim = models.Simulation.objects.get(scenario=scenario, parameters=parameters)  # pylint: disable=E1101
    except models.Simulation.DoesNotExist:  # pylint: disable=E1101
        # pylint: disable=W0707
        raise simulation.SimulationError(f"Simulation for {scenario=} with {parameters=} not present in database.")

    results = {}
    for calculation in calculations:
        try:
            calculation_instance = sim.results.get(name=calculation)
        except models.Result.DoesNotExist:  # pylint: disable=E1101
            continue
        result = pandas.read_json(calculation_instance.data, orient="table")
        results[calculation] = result["values"] if calculation_instance.data_type == "series" else result

    if any(calculation not in results for calculation in calculations):
        sim = simulation.simulate_scenario(scenario, parameters)
        calculator = postprocessing.Calculator(*sim.dataset.restore_results())
        for calculation in calculations:
            if calculation in results:
                continue
            result = CALCULATIONS[calculation](calculator).result
            models.Result(
                simulation=sim,
                name=calculation,
                data=result.to_json(orient="table"),
                data_type="series" if isinstance(result, pandas.Series) else "frame",
            ).save()
            results[calculation] = result
    return results
