"""Hooks can be used to change default behaviour of parameter, ES or model setup."""

from dataclasses import dataclass
from typing import Callable, Union
from enum import IntEnum

from django_oemof import settings


# pylint:disable=R0903
class AllScenarios:
    """Used to apply hook to all scenarios"""


ALL_SCENARIOS = AllScenarios()


class HookType(IntEnum):
    """Hook types - define where to apply hooks"""

    PARAMETER = 0
    ENERGYSYSTEM = 1
    MODEL = 2


@dataclass
class Hook:
    """Hook class is used to set up a hook for specific scenario"""

    scenario: Union[str, AllScenarios]
    function: Callable


def register_hook(hook_type: HookType, hook: Hook):
    """Registers hook depending on hook type"""
    settings.HOOKS[hook_type].append(hook)


def apply_hooks(hook_type: HookType, scenario: str, data):
    """Applies hooks for given hook type and scenario"""
    for hook in settings.HOOKS[hook_type]:
        if hook.scenario != scenario and hook.scenario is not ALL_SCENARIOS:
            continue
        data = hook.function(data)
    return data
