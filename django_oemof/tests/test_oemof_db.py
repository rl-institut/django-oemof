"""
run these tests with `pytest tests/test_something.py` or `pytest tests` or simply `pytest`
pytest will look for all files starting with "test_" and run all functions
within this file. For basic example of tests you can look at our workshop
https://github.com/rl-institut/workshop/tree/master/test-driven-development.
Otherwise https://docs.pytest.org/en/latest/ and https://docs.python.org/3/library/unittest.html
are also good support.
"""
import pathlib

# pylint: disable=W0611
import oemof.tabular.datapackage  # noqa
from django.test import TransactionTestCase
from oemof import solph
from oemof.network.energy_system import EnergySystem
from oemof.tabular.facades import TYPEMAP

from django_oemof import models

OEMOF_DATAPACKAGE = pathlib.Path(__file__).parent / "test_data" / "dispatch" / "datapackage.json"


class OemofDBTest(TransactionTestCase):
    """Test case for (re-)storing oemof results in DB"""

    def test_store_and_restore(self):
        """Stores and restores results from simple oemof example"""
        energysystem = EnergySystem.from_datapackage(str(OEMOF_DATAPACKAGE), typemap=TYPEMAP)
        model = solph.Model(energysystem)
        model.solve(solver="cbc")

        input_data = solph.processing.parameter_as_dict(
            energysystem,
            exclude_attrs=["bus", "from_bus", "to_bus", "from_node", "to_node"],
        )
        input_data = solph.processing.convert_keys_to_strings(input_data)
        results_data = solph.processing.results(model)
        results_data = solph.processing.convert_keys_to_strings(results_data)
        result_id = models.OemofDataset.store_results(input_data, results_data)
        assert result_id == 1
        dataset = models.OemofDataset.objects.get(pk=result_id)
        restored_input, restored_results = dataset.restore_results()
        assert len(input_data) == len(restored_input)
        assert len(input_data) == len(restored_input)
        assert len(results_data) == len(restored_results)
        assert len(results_data) == len(restored_results)
