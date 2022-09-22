"""Tests to parametrize oemof energysystems before simulation start"""

import pathlib

# pylint: disable=W0611
import oemof.tabular.datapackage  # noqa
import pytest
from django.test import TransactionTestCase

from django_oemof import simulation

OEMOF_DATAPACKAGE = pathlib.Path(__file__).parent / "test_data" / "dispatch" / "datapackage.json"


class OemofDParameterTest(TransactionTestCase):
    """Test case for paramtrizing oemof ES after initialization"""

    def test_without_parameterization(self):
        """Build ES from datapacakge and simulate as reference to 'test_with_parameterization'"""
        energysystem = simulation.build_energysystem(str(OEMOF_DATAPACKAGE))
        _, results_data = simulation.simulate_energysystem(energysystem)
        assert list(results_data.values())[6]["sequences"].flow[0] == pytest.approx(7.37660)
        assert list(results_data.values())[6]["sequences"].flow[1] == pytest.approx(9.20905)
        assert list(results_data.values())[6]["sequences"].flow[2] == pytest.approx(11.19685)

    def test_with_parameterization(self):
        """Build ES from datapacakge and change parameter afterwards before simulation"""
        parameters = {"wind": {"capacity": 5}}
        energysystem = simulation.build_energysystem(str(OEMOF_DATAPACKAGE), parameters)
        _, results_data = simulation.simulate_energysystem(energysystem)
        assert list(results_data.values())[6]["sequences"].flow[0] == pytest.approx(7.37660 / 10)
        assert list(results_data.values())[6]["sequences"].flow[1] == pytest.approx(9.20905 / 10)
        assert list(results_data.values())[6]["sequences"].flow[2] == pytest.approx(11.19685 / 10)
