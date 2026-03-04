from django.db import models
import uuid


class Patient(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('unknown', 'Unknown')
    ]
    
    identifier = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    family_name = models.CharField(max_length=100)
    given_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    birth_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['identifier']),
            models.Index(fields=['family_name', 'given_name'])
        ]
    
    def __str__(self):
        return f"{self.family_name} {self.given_name}"


class Observation(models.Model):
    OBS_TYPES = [
        ('blood-pressure', 'Tension artérielle'),
        ('heart-rate', 'Fréquence cardiaque'),
        ('temperature', 'Température corporelle'),
        ('weight', 'Poids'),
        ('height', 'Taille')
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='observations')
    observation_type = models.CharField(max_length=50, choices=OBS_TYPES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20)
    effective_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['patient', 'effective_date'])
        ]
    
    def __str__(self):
        return f"{self.patient} - {self.observation_type}: {self.value} {self.unit}"


class Location(models.Model):
    """FHIR Location - Lieu/Département/Salle"""
    identifier = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['city'])
        ]
    
    def __str__(self):
        return f"{self.name} - {self.city}"


class Medication(models.Model):
    """FHIR Medication - Médicament"""
    identifier = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    code = models.CharField(max_length=100, unique=True)  # ATC code
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    form = models.CharField(max_length=50, default='tablet')  # tablet, liquid, capsule, etc
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['name'])
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class AllergyIntolerance(models.Model):
    """FHIR AllergyIntolerance - Allergie/Intolérance"""
    SEVERITY_CHOICES = [
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe')
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('entered-in-error', 'Entered in Error')
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='allergies')
    substance = models.CharField(max_length=200)  # e.g., Penicillin, Peanuts
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='moderate')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    clinical_status = models.CharField(max_length=50, default='active')
    verification_status = models.CharField(max_length=50, default='unconfirmed')
    first_occurrence = models.DateTimeField(auto_now_add=True)
    last_occurrence = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['patient', 'substance']),
            models.Index(fields=['status'])
        ]
        verbose_name_plural = 'Allergies'
    
    def __str__(self):
        return f"{self.patient} - {self.substance} ({self.severity})"


class DiagnosticReport(models.Model):
    """FHIR DiagnosticReport - Rapport Diagnostic"""
    STATUS_CHOICES = [
        ('registered', 'Registered'),
        ('partial', 'Partial'),
        ('preliminary', 'Preliminary'),
        ('final', 'Final'),
        ('amended', 'Amended'),
        ('corrected', 'Corrected'),
        ('cancelled', 'Cancelled'),
        ('entered-in-error', 'Entered in Error')
    ]
    
    identifier = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='diagnostic_reports')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    code = models.CharField(max_length=100)  # LOINC code
    report_type = models.CharField(max_length=100)  # e.g., "Blood Test", "X-Ray"
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='preliminary')
    effective_date = models.DateTimeField()
    issued = models.DateTimeField(auto_now_add=True)
    result_text = models.TextField(blank=True)
    conclusion = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['patient', 'effective_date']),
            models.Index(fields=['code']),
            models.Index(fields=['status'])
        ]
        ordering = ['-effective_date']
    
    def __str__(self):
        return f"{self.patient} - {self.report_type} ({self.status})"
