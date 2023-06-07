"""Hooks can be used to change default behaviour of parameter, ES or model setup."""
import logging
from copy import deepcopy
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Callable, Optional, Union

from django import http

from django_oemof import settings


# pylint:disable=R0903
class AllScenarios:
    """Used to apply hook to all scenarios"""

    def __str__(self):
        return "ALL_SCENARIOS"


ALL_SCENARIOS = AllScenarios()


class HookType(IntEnum):
    """Hook types - define where to apply hooks"""

    SETUP = 0
    PARAMETER = 1
    ENERGYSYSTEM = 2
    MODEL = 3


@dataclass
class Hook:
    """Hook class is used to set up a hook for specific scenario"""

    scenario: Union[str, AllScenarios]
    function: Callable

    def __str__(self):
        return f"<Hook '{self.function.__name__}' @{self.scenario}>"


def register_hook(hook_type: HookType, hook: Hook):
    """Registers hook depending on hook type"""
    settings.HOOKS[hook_type].append(hook)


def apply_hooks(hook_type: HookType, scenario: str, data: Any, request: Optional[http.HttpRequest] = None) -> dict:
    """Applies hooks for given hook type and scenario"""
    hooked_data = deepcopy(data) if hook_type in (HookType.SETUP, HookType.PARAMETER) else data
    for hook in settings.HOOKS[hook_type]:
        if hook.scenario != scenario and hook.scenario is not ALL_SCENARIOS:
            continue
        logging.info(f"Applying {hook}")
        hooked_data = hook.function(scenario, hooked_data, request)
    return hooked_data
