"""Postprocessing test module"""

from django.test import SimpleTestCase
from oemoflex.postprocessing import core, postprocessing

from django_oemof import simulation, results as dor


OEMOF_DATAPACKAGE = "test_scenario"


class TestCalculation(core.Calculation):
    """Example calculation for testing"""

    name = "test"
    depends_on = {"summed_flows": postprocessing.AggregatedFlows}

    def calculate_result(self):
        return self.dependency("summed_flows") * 5


class PostprocessingTest(SimpleTestCase):
    """
    SimpleTestCase in combination with `database` and overrideen `tearDown` is used to preserve data in database,
    as `--keepdb` only keeps tables, not records
    """

    databases = "__all__"  # This is used to preserve data in database (--keepdb only keeps tables, not records)

    def test_postprocessing(self):
        """Tests postprocessing of oemof simulation"""
        sim = simulation.simulate_scenario(OEMOF_DATAPACKAGE, {})
        calculator = core.Calculator(*sim.dataset.restore_results())
        total_system_costs = postprocessing.TotalSystemCosts(calculator)
        print(total_system_costs.result)
        assert not total_system_costs.result.empty

    def test_results(self):
        """Tests registration of custom calculation"""
        # Register calculation test:
        dor.register_calculation(TestCalculation)
        sim = simulation.simulate_scenario(OEMOF_DATAPACKAGE, {})
        results = dor.get_results(sim.id, calculations=["test"])
        assert "test" in results
        assert not results["test"].empty

    def test_results_with_calculation_cls(self):
        """Tests registration of custom calculation"""
        # Register calculation test:
        dor.register_calculation(TestCalculation)
        sim = simulation.simulate_scenario(OEMOF_DATAPACKAGE, {})
        results = dor.get_results(sim.id, calculations=[TestCalculation])
        assert "test" in results
        assert not results["test"].empty

    def tearDown(self) -> None:
        # Must stay empty in order to keep simulation data in test db
        pass

    @classmethod
    def tearDownClass(cls):
        # Must stay empty in order to keep simulation data in test db
        pass
