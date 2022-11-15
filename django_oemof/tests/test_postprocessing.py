
from django.test import SimpleTestCase
from oemoflex.postprocessing import core, postprocessing

from django_oemof import simulation, results as dor


OEMOF_DATAPACKAGE = "dispatch"


class TestCalculation(core.Calculation):
    name = "test"
    depends_on = [postprocessing.SummedFlows]

    def calculate_result(self):
        return self.dependency("summed_flows") * 5


class PostprocessingTest(SimpleTestCase):
    """
    SimpleTestCase in combination with `database` and overrideen `tearDown` is used to preserve data in database,
    as `--keepdb` only keeps tables, not records
    """
    databases = "__all__"  # This is used to preserve data in database (--keepdb only keeps tables, not records)

    def test_postprocessing(self):
        input_data, results_data = simulation.simulate_scenario(OEMOF_DATAPACKAGE, parameters={})
        calculator = postprocessing.Calculator(input_data, results_data)
        total_system_costs = postprocessing.TotalSystemCosts(calculator)
        print(total_system_costs.result)
        assert not total_system_costs.result.empty

    def test_results(self):
        # Register calculation test:
        dor.register_calculation(TestCalculation)
        results = dor.get_results(OEMOF_DATAPACKAGE, parameters={}, calculations=["test"])
        assert "test" in results
        assert not results["test"].empty

    def tearDown(self) -> None:
        # Must stay empty in order to keep simulation data in test db
        pass

    @classmethod
    def tearDownClass(cls):
        # Must stay empty in order to keep simulation data in test db
        pass
