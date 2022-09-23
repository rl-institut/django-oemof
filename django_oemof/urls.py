"""Urls for django-oemof package"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from django_oemof import views

router = DefaultRouter()


urlpatterns = [
    path("", include(router.urls)),
    path("simulate", views.SimulateEnergysystem.as_view()),
]
