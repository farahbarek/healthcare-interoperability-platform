# 🏥 API d'Interopérabilité Médicale FHIR

**TP complet** : API REST Django conforme au standard HL7 FHIR pour la gestion des données médicales (Patients, Observations, Médicaments, Allergies, Rapports Diagnostiques, Lieux).

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-darkgreen.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14-orange.svg)](https://www.django-rest-framework.org/)
[![FHIR](https://img.shields.io/badge/FHIR-R4-red.svg)](https://www.hl7.org/fhir/)

## 📋 Contenu

- ✅ **6 ressources FHIR** : Patient, Observation, Location, Medication, AllergyIntolerance, DiagnosticReport
- ✅ **API REST complète** avec Django REST Framework
- ✅ **Authentification JWT** avec SimpleJWT
- ✅ **Documentation interactive** Swagger/OpenAPI
- ✅ **Filtrage avancé** par patient, date, type, sévérité
- ✅ **Validation FHIR stricte** avec codes LOINC/ATC
- ✅ **Tests complets** et script de population

## 🚀 Installation Rapide

### 1. Cloner le repo
```bash
git clone https://github.com/ton-username/tp-fhir-api.git
cd tp-fhir-api
```

### 2. Créer un environnement virtuel
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Appliquer les migrations
```bash
python manage.py migrate
```

### 5. Créer un utilisateur admin (optionnel)
```bash
python manage.py createsuperuser
```

### 6. Peupler la BD avec des données de test
```bash
python populate_fhir.py
```

### 7. Lancer le serveur
```bash
python manage.py runserver
```

## 📚 Utilisation

### Interface Web (Swagger UI)
```
http://localhost:8000/api/docs/
```

### Endpoints Principaux

#### 👨‍⚕️ Patients
```bash
GET    /api/patients/              # Lister
POST   /api/patients/              # Créer
GET    /api/patients/{id}/         # Détails
PATCH  /api/patients/{id}/         # Modifier
DELETE /api/patients/{id}/         # Supprimer
GET    /api/patients/{id}/observations/  # Observations du patient
```

#### 📊 Observations
```bash
GET    /api/observations/              # Lister avec filtrage
POST   /api/observations/              # Créer
GET    /api/observations/{id}/         # Détails
PATCH  /api/observations/{id}/         # Modifier
DELETE /api/observations/{id}/         # Supprimer
```

#### 🏥 Lieux
```bash
GET    /api/locations/
POST   /api/locations/
GET    /api/locations/{id}/
```

#### 💊 Médicaments
```bash
GET    /api/medications/
POST   /api/medications/
GET    /api/medications/{id}/
```

#### 🚨 Allergies
```bash
GET    /api/allergies/                      # Lister avec filtrage
GET    /api/allergies/by_patient/?patient_id=1
POST   /api/allergies/
```

#### 📋 Rapports Diagnostiques
```bash
GET    /api/diagnostic-reports/                    # Lister avec filtrage
GET    /api/diagnostic-reports/by_patient/?patient_id=1
POST   /api/diagnostic-reports/
```

### Exemple de requête
```bash
curl -X GET http://localhost:8000/api/patients/ \
  -H "Content-Type: application/json"
```

## 🗂️ Structure du Projet

```
tp-fhir-api/
├── config/
│   ├── settings.py          ← Configuration Django
│   ├── urls.py              ← Routage principal
│   └── wsgi.py
│
├── fhir_api/
│   ├── models.py            ← 6 modèles FHIR
│   ├── serializers.py       ← Sérialisation FHIR-compliant
│   ├── views.py             ← 6 ViewSets
│   ├── urls.py              ← Routage API
│   ├── validators.py        ← Validation FHIR
│   └── migrations/
│
├── manage.py
├── requirements.txt         ← Dépendances
├── populate_fhir.py         ← Script de population
├── test_api.py              ← Tests automatisés
├── test.rest                ← Tests VSCode REST Client
├── TP.md                    ← Documentation pédagogique
└── db.sqlite3
```

## 🔧 Configuration

### settings.py
```python
INSTALLED_APPS = [
    'rest_framework',
    'django_filters',
    'drf_spectacular',
    'fhir_api',
]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}
```

## 📝 Modèles Disponibles

| Modèle | Champs | Description |
|--------|--------|-------------|
| **Patient** | identifier, name, gender, birthDate | Patient FHIR |
| **Observation** | patient, type, value, unit, date | Mesures vitales |
| **Location** | name, address, city, phone | Lieu/Département |
| **Medication** | code (ATC), name, form | Médicament |
| **AllergyIntolerance** | patient, substance, severity | Allergie/Intolérance |
| **DiagnosticReport** | patient, code (LOINC), status | Rapport diagnostic |

## 🧪 Tests

### Lancer les tests
```bash
python test_api.py
```

### Tests manuels avec VSCode REST Client
```
Ouvrir test.rest et cliquer "Send Request"
```

## 🔐 Authentification (optionnel)

Pour activer JWT:

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

Obtenir un token:
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin", "password":"password"}'
```

## 📚 Ressources FHIR

- [HL7 FHIR Standard](https://www.hl7.org/fhir/)
- [LOINC Codes](https://loinc.org/)
- [ATC Codes](https://www.whocc.no/atc/)

## 🛠️ Dépendances

```
Django==6.0.2
djangorestframework==3.14.0
django-filter==24.2
drf-spectacular==0.26.1
djangorestframework-simplejwt==5.3.2
fhir.resources==7.0.1
psycopg2-binary==2.9.9
requests==2.31.0
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

MIT License - voir LICENSE pour les détails

## 👨‍💻 Auteur

**Travail Pratique (TP)** - API d'Interopérabilité Médicale avec Django & FHIR
- Année: 2026
- Standard: HL7 FHIR R4
- Framework: Django REST Framework

## ❓ Support

Pour les questions ou problèmes:
- 📧 Ouvrir une issue sur GitHub
- 📚 Consulter TP.md pour la documentation pédagogique

---

**Status**: ✅ Production-ready
