from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

router = DefaultRouter()
router.register(r'patients', views.PatientViewSet)
router.register(r'observations', views.ObservationViewSet)
router.register(r'locations', views.LocationViewSet)
router.register(r'medications', views.MedicationViewSet)
router.register(r'allergies', views.AllergyIntoleranceViewSet)
router.register(r'diagnostic-reports', views.DiagnosticReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
