# Django-Oemof

Django-Oemof is a Django app to provide an API to build and optimize oemof.solph models and deliver results via JSON response.

## Requirements

CBC solver has to be installed. Install it via (conda):
```
conda install -c conda-forge coincbc
```

## Quick start

1. Add "oemof" to your INSTALLED_APPS setting like this::
    ```
        INSTALLED_APPS = [
            ...
            'oemof',
        ]
    ```

2. Include the oemof URLconf in your project urls.py like this::

    path('oemof/', include('oemof.urls')),

3. Run ``python manage.py migrate`` to create the oemof models.


## OEMOF Datapackages

Have to be put in folder `oemof` within djangos `MEDIA_ROOT` folder.
Name of datapackage folder is used in request for building ES.

## Tests

Run tests for standalone app via `python runtests.py`
