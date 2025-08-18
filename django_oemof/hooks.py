"""Hooks can be used to change default behaviour of parameter, ES or model setup."""
import logging
from inspect import signature
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Union


from django_oemof import settings


# pylint:disable=R0903
class AllScenarios:
    """Used to apply hook to all scenarios"""

    def __str__(self):
        return "ALL_SCENARIOS"


ALL_SCENARIOS = AllScenarios()


class HookType(Enum):
    """Hook types - define where to apply hooks"""

    SETUP = ("setup", ())
    PARAMETER = ("parameter", ())
    ENERGYSYSTEM = ("energysystem", ("energysystem", ))
    MODEL = ("model", ("model", ))
    POSTPROCESSING = ("postprocessing", ("model", "meta"))

    def __init__(self, label, parameters):
        self.label = label
        self.parameters = parameters


@dataclass
class Hook:
    """Hook class is used to set up a hook for specific scenario"""

    scenario: Union[str, AllScenarios]
    function: Callable

    def __str__(self):
        return f"<Hook '{self.function.__name__}' @{self.scenario}>"


def register_hook(hook_type: HookType, hook: Hook):
    """Registers hook depending on hook type"""
    # TODO: Test new hooking system with ReEnAct
    sig = signature(hook.function)
    function_parameters = sig.parameters.keys()
    if any(parameter not in function_parameters for parameter in hook_type.parameters):
        raise KeyError("Hook function misses parameters. Needed parameters: {}".format(function_parameters))
    settings.HOOKS[hook_type].append(hook)


def apply_hooks(hook_type: HookType, scenario: str, data: Any, **kwargs) -> dict:
    """Applies hooks for a given hook type and scenario"""
    hooked_data = deepcopy(data) if hook_type in (HookType.SETUP, HookType.PARAMETER) else data
    for hook in settings.HOOKS[hook_type]:
        if hook.scenario != scenario and hook.scenario is not ALL_SCENARIOS:
            continue
        logging.info(f"Applying {hook}")
        hooked_data = hook.function(scenario, hooked_data, **kwargs)
    return hooked_data
