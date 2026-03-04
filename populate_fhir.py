#!/usr/bin/env python
"""
Script de population des données FHIR
Crée des patients avec allergies, lieux, médicaments et rapports diagnostiques
"""

import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from fhir_api.models import Patient, Observation, Location, Medication, AllergyIntolerance, DiagnosticReport
from datetime import date

def populate_database():
    print("🏥 Démarrage du peuplement de la base FHIR...")
    
    # Créer des lieux
    print("\n📍 Création des lieux...")
    loc_emergency = Location.objects.create(
        name="Urgences",
        address="123 Rue de l'Hôpital",
        city="Paris",
        postal_code="75001",
        phone="+33 1 23 45 67 89"
    )
    print(f"  ✓ {loc_emergency.name} créé")
    
    loc_lab = Location.objects.create(
        name="Laboratoire d'Analyse",
        address="456 Avenue Pasteur",
        city="Paris",
        postal_code="75002",
        phone="+33 1 98 76 54 32"
    )
    print(f"  ✓ {loc_lab.name} créé")
    
    # Créer des médicaments
    print("\n💊 Création des médicaments...")
    med_penicillin = Medication.objects.create(
        code="J01CE01",
        name="Penicilline G",
        description="Antibiotique beta-lactamine",
        form="injectable"
    )
    print(f"  ✓ {med_penicillin.name} créé")
    
    med_aspirin = Medication.objects.create(
        code="N02BA01",
        name="Acide Acétylsalicylique (Aspirin)",
        description="Anti-inflammatoire et analgésique",
        form="tablet"
    )
    print(f"  ✓ {med_aspirin.name} créé")
    
    med_metformin = Medication.objects.create(
        code="A10BA02",
        name="Metformine",
        description="Antidiabétique oral",
        form="tablet"
    )
    print(f"  ✓ {med_metformin.name} créé")
    
    # Créer des patients
    print("\n👨‍⚕️ Création des patients...")
    patient1 = Patient.objects.create(
        family_name="Dupont",
        given_name="Jean",
        gender="male",
        birth_date=date(1965, 3, 15)
    )
    print(f"  ✓ Patient {patient1} créé")
    
    patient2 = Patient.objects.create(
        family_name="Martin",
        given_name="Marie",
        gender="female",
        birth_date=date(1978, 7, 22)
    )
    print(f"  ✓ Patient {patient2} créé")
    
    # Créer des allergies
    print("\n🚨 Création des allergies...")
    allergy1 = AllergyIntolerance.objects.create(
        patient=patient1,
        substance="Penicilline",
        severity="severe",
        status="active",
        clinical_status="active",
        verification_status="confirmed",
        note="Réaction allergique severe avec rash systémique"
    )
    print(f"  ✓ Allergie {allergy1.substance} (sévère) pour {patient1.given_name}")
    
    allergy2 = AllergyIntolerance.objects.create(
        patient=patient2,
        substance="Lactose",
        severity="mild",
        status="active",
        clinical_status="active",
        verification_status="unconfirmed",
        note="Intolérance légère au lactose"
    )
    print(f"  ✓ Allergie {allergy2.substance} (légère) pour {patient2.given_name}")
    
    # Créer des observations
    print("\n📊 Création des observations...")
    obs1 = Observation.objects.create(
        patient=patient1,
        observation_type="blood-pressure",
        value=140,
        unit="mmHg",
        effective_date=datetime.now() - timedelta(hours=2)
    )
    print(f"  ✓ Observation {obs1.observation_type} pour {patient1.given_name}")
    
    obs2 = Observation.objects.create(
        patient=patient2,
        observation_type="heart-rate",
        value=75,
        unit="bpm",
        effective_date=datetime.now() - timedelta(hours=1)
    )
    print(f"  ✓ Observation {obs2.observation_type} pour {patient2.given_name}")
    
    # Créer des rapports diagnostiques
    print("\n📋 Création des rapports diagnostiques...")
    report1 = DiagnosticReport.objects.create(
        patient=patient1,
        location=loc_lab,
        code="2345-7",  # LOINC pour Glucose
        report_type="Analyse Sanguine Complète",
        status="final",
        effective_date=datetime.now() - timedelta(days=1),
        result_text="Glucose: 126 mg/dL, Cholesterol: 210 mg/dL",
        conclusion="Résultats légèrement élevés. Suivi recommandé."
    )
    print(f"  ✓ {report1.report_type} pour {patient1.given_name}")
    
    report2 = DiagnosticReport.objects.create(
        patient=patient2,
        location=loc_emergency,
        code="71020-1",  # LOINC pour Chest X-ray
        report_type="Radiographie Thoracique",
        status="preliminary",
        effective_date=datetime.now() - timedelta(hours=3),
        result_text="Poumons clairs, pas d'anomalie détectée",
        conclusion="Résultats normaux"
    )
    print(f"  ✓ {report2.report_type} pour {patient2.given_name}")
    
    print("\n✅ Population complète! Vérifiez avec:")
    print("   GET http://localhost:8000/api/patients/")
    print("   GET http://localhost:8000/api/allergies/?patient=1")
    print("   GET http://localhost:8000/api/diagnostic-reports/?patient=1")
    print("   GET http://localhost:8000/api/locations/")
    print("   GET http://localhost:8000/api/medications/")

if __name__ == "__main__":
    populate_database()
