"""Urls for django-oemof package"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from django_oemof import views

router = DefaultRouter()

# pylint:disable=C0103
app_name = "django_oemof"

urlpatterns = [
    path("", include(router.urls)),
    path("simulate", views.SimulateEnergysystem.as_view(), name="simulate"),  # param 'scenario' and 'parameters'
    path("terminate", views.TerminateSimulationView.as_view()),  # param 'task_id'
    path("calculate", views.CalculateResults.as_view()),  # param 'simulation_id' and 'calculation_list'
    path("delete", views.DeleteSimulationView.as_view(), name="delete"),  # param 'simulation_id'
]
