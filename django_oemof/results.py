import inspect
from oemoflex.postprocessing import core, postprocessing


CALCULATIONS = {
    member.name: member
    for (name, member) in inspect.getmembers(postprocessing)
    if inspect.isclass(member) and not inspect.isabstract(member) and issubclass(member, core.Calculation)
}


def register_calculation(calculation: core.Calculation):
    CALCULATIONS[calculation.name] = calculation


def calculate_results(input_data, output_data, calculations: list[str]):
    calculator = postprocessing.Calculator(input_data, output_data)
    return {calculation_name: CALCULATIONS[calculation_name](calculator).result for calculation_name in calculations}
