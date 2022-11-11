
from django.test import SimpleTestCase
from oemoflex.postprocessing import postprocessing

from django_oemof import simulation


OEMOF_DATAPACKAGE = "test_scenario"


class OemofDBTest(SimpleTestCase):
    """
    SimpleTestCase in combination with `database` and overrideen `tearDown` is used to preserve data in database,
    as `--keepdb` only keeps tables, not records
    """
    databases = "__all__"  # This is used to preserve data in database (--keepdb only keeps tables, not records)

    @classmethod
    def setUpTestData(cls):
        simulation.simulate_scenario(OEMOF_DATAPACKAGE, parameters={})

    def test_postprocessing(self):
        input_data, results_data = simulation.simulate_scenario(OEMOF_DATAPACKAGE, parameters={})
        calculator = postprocessing.Calculator(input_data, results_data)
        total_system_costs = postprocessing.TotalSystemCosts(calculator)
        print(total_system_costs.result)

    def tearDown(self) -> None:
        pass

    @classmethod
    def tearDownClass(cls):
        pass
