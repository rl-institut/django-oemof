
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django_oemof import views


router = DefaultRouter()
# router.register(r'snippets', views.SnippetViewSet,basename="snippets")
# router.register(r'users', views.UserViewSet,basename="users")

urlpatterns = [
    path('', include(router.urls)),
    path('build_es', views.BuildEnergysystem.as_view()),
]