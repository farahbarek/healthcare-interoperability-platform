from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Patient, Observation, Location, Medication, AllergyIntolerance, DiagnosticReport

@admin.register(Patient)
class PatientAdmin(ModelAdmin):
    list_display = ('family_name', 'given_name', 'identifier', 'gender', 'birth_date')
    search_fields = ('family_name', 'given_name', 'identifier')
    list_filter = ('gender', 'created_at')

@admin.register(Observation)
class ObservationAdmin(ModelAdmin):
    list_display = ('patient', 'observation_type', 'value', 'unit', 'effective_date')
    list_filter = ('observation_type', 'effective_date')
    search_fields = ('patient__family_name', 'patient__given_name')

@admin.register(Location)
class LocationAdmin(ModelAdmin):
    list_display = ('name', 'city', 'phone')
    search_fields = ('name', 'city')

@admin.register(Medication)
class MedicationAdmin(ModelAdmin):
    list_display = ('name', 'code', 'form')
    search_fields = ('name', 'code')

@admin.register(AllergyIntolerance)
class AllergyIntoleranceAdmin(ModelAdmin):
    list_display = ('patient', 'substance', 'severity', 'status')
    list_filter = ('severity', 'status')
    search_fields = ('patient__family_name', 'substance')

@admin.register(DiagnosticReport)
class DiagnosticReportAdmin(ModelAdmin):
    list_display = ('patient', 'report_type', 'status', 'effective_date')
    list_filter = ('status', 'effective_date')
    search_fields = ('patient__family_name', 'report_type')
