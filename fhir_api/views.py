from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from .models import Patient, Observation, Location, Medication, AllergyIntolerance, DiagnosticReport
from .serializers import (
    PatientFHIRSerializer, ObservationFHIRSerializer,
    LocationFHIRSerializer, MedicationFHIRSerializer,
    AllergyIntoleranceFHIRSerializer, DiagnosticReportFHIRSerializer
)
from rest_framework.permissions import AllowAny  # Pour développement


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by('-created_at')
    serializer_class = PatientFHIRSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['gender', 'family_name']
    permission_classes = [AllowAny]  # Pour développement et tests

    @action(detail=True, methods=['get'])
    def observations(self, request, pk=None):
        obs = self.get_object().observations.all()
        if date_from := request.query_params.get('date_from'):
            obs = obs.filter(effective_date__gte=date_from)
        if date_to := request.query_params.get('date_to'):
            obs = obs.filter(effective_date__lte=date_to)
        return Response(ObservationFHIRSerializer(obs, many=True).data)


class ObservationViewSet(viewsets.ModelViewSet):
    queryset = Observation.objects.select_related('patient').all().order_by('-effective_date')
    serializer_class = ObservationFHIRSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = {
        'patient': ['exact'],
        'observation_type': ['exact'],
        'effective_date': ['gte', 'lte', 'exact'],
        'value': ['gte', 'lte']
    }
    permission_classes = [AllowAny]  # Pour développement et tests


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all().order_by('-created_at')
    serializer_class = LocationFHIRSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['name', 'city']
    permission_classes = [AllowAny]


class MedicationViewSet(viewsets.ModelViewSet):
    queryset = Medication.objects.all().order_by('-created_at')
    serializer_class = MedicationFHIRSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['code', 'name', 'form']
    permission_classes = [AllowAny]


class AllergyIntoleranceViewSet(viewsets.ModelViewSet):
    queryset = AllergyIntolerance.objects.select_related('patient').all().order_by('-last_occurrence')
    serializer_class = AllergyIntoleranceFHIRSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = {
        'patient': ['exact'],
        'substance': ['icontains'],
        'severity': ['exact'],
        'status': ['exact']
    }
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def by_patient(self, request):
        """Get all allergies for a specific patient"""
        patient_id = request.query_params.get('patient_id')
        if not patient_id:
            return Response({"error": "patient_id parameter required"}, status=400)
        allergies = self.queryset.filter(patient_id=patient_id)
        return Response(self.serializer_class(allergies, many=True).data)


class DiagnosticReportViewSet(viewsets.ModelViewSet):
    queryset = DiagnosticReport.objects.select_related('patient', 'location').all().order_by('-effective_date')
    serializer_class = DiagnosticReportFHIRSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = {
        'patient': ['exact'],
        'status': ['exact'],
        'code': ['icontains'],
        'effective_date': ['gte', 'lte', 'exact']
    }
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def by_patient(self, request):
        """Get all diagnostic reports for a specific patient"""
        patient_id = request.query_params.get('patient_id')
        if not patient_id:
            return Response({"error": "patient_id parameter required"}, status=400)
        reports = self.queryset.filter(patient_id=patient_id)
        return Response(self.serializer_class(reports, many=True).data)
