from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'analytics'

router = DefaultRouter()
# Aquí se registrarán los ViewSets cuando se implementen

urlpatterns = [
    path('', include(router.urls)),
    # URLs adicionales se añadirán cuando se implementen las vistas
] 