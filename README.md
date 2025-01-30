from django_oemof.tests.test_oemof_parameters import OEMOF_DATAPACKAGE

# Django-Oemof

Django-Oemof is a Django app to provide an API to build and optimize oemof.solph models and deliver results via JSON response.

## Requirements

- `oemof.tabular` has to be installed 
- CBC solver has to be installed. Install it via (conda):
```
conda install -c conda-forge coincbc
```

Django project must use celery and automatically detect celery tasks. (follow https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html to setup celery)

## Quick start

1. Add "oemof" to your INSTALLED_APPS setting like this::
    ```
        INSTALLED_APPS = [
            ...
            'rest_framework'
            'django_oemof',
        ]
    ```

2. Include the oemof URLconf in your project urls.py like this::

    path('oemof/', include('django_oemof.urls')),

3. Run ``python manage.py migrate`` to create the oemof models.

## Configuration

You can set following configs via environment:

- DJANGO_OEMOF_IGNORE_SIMULATION_PARAMETERS
  list of parameter keys which shall be ignored when initializing a simulation 

## OEMOF Datapackages

Have to be put in folder `oemof` within djangos `MEDIA_ROOT` folder.
Name of datapackage folder is used in request for building ES.

## Hooks

Hooks can be used to change default behaviour of parameter setup, energysystem build and model solving.
This is done by defining custom functions which can be registered in django_oemof and are applied when simulating an ES.
Depending on hook type (Parameter/Energysystem/Model), the defined custom functions are applied to parameters, build Es or after creating the model.
See following flow chart for order of hooks:

![Hook Flow Chart](./docs/images/oemof_flow.png)

Every hook is scenario-dependent to allow different hooks per scenario, but you can use `hooks.ALL_SCENARIO` as scenario to aplly hook to all scenarios.
An example hook (changing default behaviour of parameter setup) could be set up as follows:

```python

from django_oemof import hooks


def converting_demand_to_kW(data):
   data["demand"] = data["demand"] * 1000
   return data


demand_kW_hook = hooks.Hook(scenario="dispatch", function=converting_demand_to_kW)
hooks.register_hook(hooks.HookType.PARAMETER, demand_kW_hook)

```

## Tests

Run tests for standalone app via `python runtests.py`

## Standalone

This section is about using django-oemof without necessity to set up a django webserver.
You can store/restore simulated oemof.tabular datapackages using djangos ORM.
Additionally, hooks from django-oemof to 
- change parameters before simulation,
- change ES after building from datapackage or 
- changing model before simulating 

are available.

### Usage

Steps to run simulation:
1. Set up database url as `DATABASE_URL` in `.env` file in working directory
2. Migrate django models via `python -m django_oemof.standalone migrate`
3. Download or create a valid oemof.tabular datapackage and store it in folder `media/oemof`
   (Media folder can be changed via `MEDIA_ROOT` in `.env` file)
4. Create script which imports `init_django` from `django_oemof.standalone` 
5. Now, you can save/restore oemof results to/from DB using:
```python
# Example with some hooks
from django_oemof import simulation, hooks

OEMOF_DATAPACKAGE = "dispatch"

# Hook functions must be defined beforehand
ph = hooks.Hook(OEMOF_DATAPACKAGE, test_parameter_hook)
esh = hooks.Hook(OEMOF_DATAPACKAGE, test_es_hook)
mh = hooks.Hook(OEMOF_DATAPACKAGE, test_model_hook)

hooks.register_hook(hook_type=hooks.HookType.PARAMETER, hook=ph)
hooks.register_hook(hook_type=hooks.HookType.ENERGYSYSTEM, hook=esh)
hooks.register_hook(hook_type=hooks.HookType.MODEL, hook=mh)

parameters = {}
simulation_id = simulation.simulate_scenario(scenario=OEMOF_DATAPACKAGE, parameters=parameters)
print("Simulation ID:", simulation_id)

# Restore oemof results from DB
from django_oemof import models
sim = models.Simulation.objects.get(id=1)
inputs, outputs = sim.dataset.restore_results()
```
   
*Note*: `django_oemof.models` must be loaded *AFTER* `init_django()` call. 
Thus, import of `django.models` might look unusual and linter might complain - 
but otherwise django models are not ready yet and a django error will occur! 

