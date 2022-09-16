"""
run these tests with `pytest tests/test_something.py` or `pytest tests` or simply `pytest`
pytest will look for all files starting with "test_" and run all functions
within this file. For basic example of tests you can look at our workshop
https://github.com/rl-institut/workshop/tree/master/test-driven-development.
Otherwise https://docs.pytest.org/en/latest/ and https://docs.python.org/3/library/unittest.html
are also good support.
"""
import pytest
import pathlib

# pylint: disable=W0611
import oemof.tabular.datapackage  # noqa
from oemof import solph
from oemof.network.energy_system import EnergySystem
from oemof.tabular.facades import TYPEMAP

from django_oemof import models


OEMOF_DATAPACKAGE = "test_data/dispatch"


def test_store_oemof_results():
    energysystem = EnergySystem.from_datapackage(OEMOF_DATAPACKAGE, typemap=TYPEMAP)
    model = solph.Model(energysystem)
    model.solve(solver="cbc")

    input_data = solph.processing.parameter_as_dict(
        energysystem,
        exclude_attrs=["bus", "from_bus", "to_bus", "from_node", "to_node"],
    )
    results_data = solph.processing.results(model)
    result_id = models.OemofDataset.store_results(input_data, results_data)
    assert result_id == 1

