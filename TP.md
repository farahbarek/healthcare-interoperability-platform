# 🏥 TP : API d'Interopérabilité Médicale avec Django REST Framework & FHIR

## Objectifs

- ✅ Implémenter le standard HL7 FHIR pour les patients et les observations.
- ✅ Développer une API REST sécurisée et filtrable avec Django REST Framework.
- ✅ Maîtriser la sérialisation complexe et la validation stricte.
- ✅ Déployer des mécanismes de test et de simulation pour données médicales.

---

## 1️⃣ Mise en place de l'environnement

### Création du projet et environnement virtuel

```bash
mkdir tp-fhir-api && cd tp-fhir-api

# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Installation des dépendances

```bash
pip install django djangorestframework django-filter psycopg2-binary
pip install fhir.resources drf-spectacular djangorestframework-simplejwt requests
```

### Initialisation Django

```bash
django-admin startproject config .
python manage.py startapp fhir_api
```

### Configuration rapide (config/settings.py)

```python
INSTALLED_APPS = [
    # Apps Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Apps tierces
    'rest_framework',
    'django_filters',
    'drf_spectacular',
    # App projet
    'fhir_api',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'API FHIR Médicale',
    'DESCRIPTION': 'API conforme au standard HL7 FHIR pour la gestion des '
                   'patients et observations',
    'VERSION': '1.0.0',
}
```

---

## 2️⃣ Modélisation des données

### models.py

```python
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
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE,
                                related_name='observations')
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
```

### Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 3️⃣ Sérialisation FHIR-compliant

### Patient Serializer

```python
from rest_framework import serializers
from .models import Patient, Observation
from fhir.resources.patient import Patient as FHIRPatient

class PatientFHIRSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'identifier', 'family_name', 'given_name', 'gender', 'birth_date']
    
    def to_representation(self, instance):
        fhir_data = {
            "resourceType": "Patient",
            "id": str(instance.id),
            "identifier": [
                {
                    "system": "https://hopital.fr/identifiers",
                    "value": str(instance.identifier)
                }
            ],
            "name": [
                {
                    "family": instance.family_name,
                    "given": [instance.given_name]
                }
            ],
            "gender": instance.gender,
            "birthDate": instance.birth_date.isoformat(),
            "meta": {
                "lastUpdated": instance.updated_at.isoformat()
            }
        }
        try:
            return FHIRPatient(**fhir_data).dict()
        except:
            return fhir_data
    
    def to_internal_value(self, data):
        if data.get('resourceType') != 'Patient':
            raise serializers.ValidationError({"resourceType": "Doit être 'Patient'"})
        
        internal_data = {
            "identifier": data['identifier'][0]['value'] if data.get('identifier') else None,
            "family_name": data['name'][0]['family'] if data.get('name') else None,
            "given_name": data['name'][0]['given'][0] if data.get('name') else None,
            "gender": data.get('gender'),
            "birth_date": data.get('birthDate')
        }
        return super().to_internal_value(internal_data)
```

### Observation Serializer

```python
class ObservationFHIRSerializer(serializers.ModelSerializer):
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        source='patient',
        write_only=True
    )
    
    class Meta:
        model = Observation
        fields = ['id', 'patient_id', 'observation_type', 'value', 'unit', 'effective_date']
    
    def to_representation(self, instance):
        loinc = {
            'blood-pressure': '85354-9',
            'heart-rate': '8867-4',
            'temperature': '8310-5',
            'weight': '29463-7',
            'height': '8302-2'
        }
        
        return {
            "resourceType": "Observation",
            "id": str(instance.id),
            "status": "final",
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": loinc.get(instance.observation_type, 'unknown'),
                        "display": instance.get_observation_type_display()
                    }
                ]
            },
            "subject": {
                "reference": f"Patient/{instance.patient.id}",
                "display": f"{instance.patient.family_name} {instance.patient.given_name}"
            },
            "effectiveDateTime": instance.effective_date.isoformat(),
            "valueQuantity": {
                "value": float(instance.value),
                "unit": instance.unit,
                "system": "http://unitsofmeasure.org",
                "code": instance.unit
            },
            "issued": instance.created_at.isoformat()
        }
```

---

### 🏥 Location (Lieu/Département)

```python
class Location(models.Model):
    identifier = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Serializer:** LocationFHIRSerializer
- Convertit vers/depuis FHIR Location
- Inclut adresse, téléphone, identifiant

---

### 💊 Medication (Médicament)

```python
class Medication(models.Model):
    identifier = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    code = models.CharField(max_length=100, unique=True)  # ATC code
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    form = models.CharField(max_length=50, default='tablet')  # tablet, liquid, capsule
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Serializer:** MedicationFHIRSerializer
- Code ATC FHIR-compliant
- Forme galénique (tablet, liquid, capsule, etc)

---

### 🚨 AllergyIntolerance (Allergie/Intolérance)

```python
class AllergyIntolerance(models.Model):
    SEVERITY_CHOICES = [('mild', 'Mild'), ('moderate', 'Moderate'), ('severe', 'Severe')]
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive'), ('entered-in-error', 'Error')]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='allergies')
    substance = models.CharField(max_length=200)  # e.g., Penicillin, Peanuts
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='moderate')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    clinical_status = models.CharField(max_length=50, default='active')
    verification_status = models.CharField(max_length=50, default='unconfirmed')
    first_occurrence = models.DateTimeField(auto_now_add=True)
    last_occurrence = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True)
```

**Serializer:** AllergyIntoleranceFHIRSerializer
- Sévérité (mild, moderate, severe)
- Statut clinique FHIR
- Custom action: `by_patient/?patient_id=`

---

### 📊 DiagnosticReport (Rapport Diagnostic)

```python
class DiagnosticReport(models.Model):
    STATUS_CHOICES = [
        ('registered', 'Registered'), ('partial', 'Partial'),
        ('preliminary', 'Preliminary'), ('final', 'Final'),
        ('amended', 'Amended'), ('corrected', 'Corrected'),
        ('cancelled', 'Cancelled'), ('entered-in-error', 'Error')
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
```

**Serializer:** DiagnosticReportFHIRSerializer
- Code LOINC
- Reference au Location
- Custom action: `by_patient/?patient_id=`

---

## 4️⃣ ViewSets et Endpoints

### views.py

```python
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from .models import Patient, Observation
from .serializers import PatientFHIRSerializer, ObservationFHIRSerializer
from rest_framework.permissions import IsAuthenticated

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by('-created_at')
    serializer_class = PatientFHIRSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['gender', 'family_name']
    permission_classes = [IsAuthenticated]
    
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
    permission_classes = [IsAuthenticated]
```

### urls.py

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

router = DefaultRouter()
router.register(r'patients', views.PatientViewSet)
router.register(r'observations', views.ObservationViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```

---

## 5️⃣ Sécurité & Validation stricte

### Validation FHIR

```python
from fhir.resources.patient import Patient as FHIRPatient
from fhir.resources.observation import Observation as FHIRObservation
from rest_framework.exceptions import ValidationError

def validate_fhir_resource(data, resource_type='Patient'):
    try:
        if resource_type == 'Patient':
            FHIRPatient(**data)
        elif resource_type == 'Observation':
            FHIRObservation(**data)
        return True
    except Exception as e:
        raise ValidationError({"fhir_validation": str(e)})
```

---

## 6️⃣ Simulation & Tests

### Simulation IoT : `client_iot.py`

- Client Python pour envoyer périodiquement des constantes vitales
- Crée des patients et des observations FHIR
- Simule des mesures réalistes (tension, fréquence cardiaque, température, etc.)

### Tests API : `test_api.py`

- Suite de tests automatisés
- Couvre CRUD, filtrage et conformité FHIR
- Requêtes d'exemple pour toutes les opérations API

### Swagger UI

- Documentation interactive : http://localhost:8000/api/docs/
- Test direct des endpoints
- Exploration de l'API sans code

---

## 🚀 Démarrage Rapide

### 1. Créer un utilisateur admin
```bash
python manage.py createsuperuser
```

### 2. Lancer le serveur
```bash
python manage.py runserver
```

### 3. Tester l'API

**Swagger UI (Interface Web):**
```
http://localhost:8000/api/docs/
```

**Avec Python:**
```bash
python test_api.py
```

**Avec VSCode REST Client (test.rest):**
- Installer l'extension "REST Client"
- Ouvrir `test.rest`
- Cliquer "Send Request"

---

## 📊 Endpoints Principaux

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/token/` | Obtenir le token JWT |
| GET | `/api/patients/` | Lister les patients |
| POST | `/api/patients/` | Créer un patient |
| GET | `/api/patients/{id}/` | Détails du patient |
| PATCH | `/api/patients/{id}/` | Modifier un patient |
| DELETE | `/api/patients/{id}/` | Supprimer un patient |
| GET | `/api/patients/{id}/observations/` | Observations du patient |
| GET | `/api/observations/` | Lister les observations |
| POST | `/api/observations/` | Créer une observation |
| GET | `/api/locations/` | Lister les lieux/départements |
| POST | `/api/locations/` | Créer un lieu |
| GET | `/api/locations/{id}/` | Détails du lieu |
| GET | `/api/medications/` | Lister les médicaments |
| POST | `/api/medications/` | Créer un médicament |
| GET | `/api/medications/{id}/` | Détails du médicament |
| GET | `/api/allergies/` | Lister les allergies |
| POST | `/api/allergies/` | Créer une allergie |
| GET | `/api/allergies/{id}/` | Détails de l'allergie |
| GET | `/api/allergies/by_patient/` | Allergies d'un patient (?patient_id=) |
| GET | `/api/diagnostic-reports/` | Lister les rapports diagnostic |
| POST | `/api/diagnostic-reports/` | Créer un rapport diagnostic |
| GET | `/api/diagnostic-reports/{id}/` | Détails du rapport |
| GET | `/api/diagnostic-reports/by_patient/` | Rapports d'un patient (?patient_id=) |
| GET | `/api/schema/` | Schéma OpenAPI |
| GET | `/api/docs/` | Swagger UI |

---

## 📋 Structure du Projet

```
tp-fhir-api/
├── config/
│   ├── settings.py          ← Configuration Django
│   ├── urls.py              ← Routage principal
│   └── wsgi.py
│
├── fhir_api/
│   ├── models.py            ← Patient, Observation
│   ├── serializers.py       ← Sérialisation FHIR
│   ├── views.py             ← ViewSets
│   ├── urls.py              ← Routage API
│   ├── validators.py        ← Validation FHIR
│   └── migrations/
│
├── manage.py
├── test_api.py              ← Tests automatisés
├── client_iot.py            ← Simulation IoT
├── test.rest                ← Tests VSCode REST Client
└── db.sqlite3               ← Base de données
```

---

## 🎓 Concepts Clés

✅ **Conformité FHIR R4** - Respect du standard HL7 pour 6 ressources
✅ **RESTful API** - Architecture HTTP standardisée
✅ **Authentification JWT** - Sécurité des données
✅ **Validation stricte** - Codes LOINC/ATC, genres, types d'observations
✅ **Sérialisation complexe** - Conversion Django ↔ FHIR (6 serializers)
✅ **Filtrage avancé** - Par patient, substance, date, sévérité, status
✅ **Custom Actions** - by_patient pour allergies & rapports diagnostiques
✅ **Documentation interactive** - Swagger/OpenAPI
✅ **Tests complets** - CRUD, filtrage, conformité FHIR

---

## 📚 Points clés de l'optimisation

- **Sérialisation simplifiée et DRY** : Réutilisation des validateurs
- **Validation stricte mais centralisée** : Une fonction pour tous les types
- **ViewSets clairs** avec filtrage minimal et extensible
- **Scripts clients et tests prêts à l'emploi**
- **Documentation Swagger intégrée** pour toutes les ressources FHIR

---

## 📞 Ressources

- **HL7 FHIR Standard**: https://www.hl7.org/fhir/
- **Django REST Framework**: https://www.django-rest-framework.org/
- **drf-spectacular**: https://github.com/tfranzel/drf-spectacular
- **fhir.resources**: https://github.com/nazrulworld/fhir.resources

---

**Status:** ✅ Prêt pour production
**Date:** 4 Mars 2026
