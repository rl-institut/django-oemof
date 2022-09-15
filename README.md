# Django-Oemof

Django-Oemof is a Django app to provide an API to build and optimize oemof.solph models and deliver results via JSON response.

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
