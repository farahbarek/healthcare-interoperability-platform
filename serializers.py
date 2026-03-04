from rest_framework import serializers
from .models import Patient, Observation, Location, Medication, AllergyIntolerance, DiagnosticReport
from .validators import validate_fhir_resource, validate_patient_data, validate_observation_data
from fhir.resources.patient import Patient as FHIRPatient


class PatientFHIRSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'identifier', 'family_name', 'given_name', 'gender', 'birth_date']

    def validate(self, data):
        """Validate patient data against FHIR requirements"""
        return validate_patient_data(data)

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


class ObservationFHIRSerializer(serializers.ModelSerializer):
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        source='patient',
        write_only=True
    )
    
    class Meta:
        model = Observation
        fields = ['id', 'patient_id', 'observation_type', 'value', 'unit', 'effective_date']

    def validate(self, data):
        """Validate observation data against FHIR requirements"""
        validate_observation_data({
            'patient': data.get('patient'),
            'observation_type': data.get('observation_type'),
            'value': data.get('value'),
            'unit': data.get('unit'),
            'effective_date': data.get('effective_date')
        })
        return data

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

    def to_internal_value(self, data):
        if data.get('resourceType') != 'Observation':
            raise serializers.ValidationError({"resourceType": "Doit être 'Observation'"})
        
        internal_data = {
            "patient": self.initial_data.get('subject', {}).get('reference', '').split('/')[-1] if self.initial_data.get('subject') else None,
            "observation_type": data.get('code', {}).get('coding', [{}])[0].get('code'),
            "value": data.get('valueQuantity', {}).get('value'),
            "unit": data.get('valueQuantity', {}).get('unit'),
            "effective_date": data.get('effectiveDateTime')
        }
        return super().to_internal_value(internal_data)


class LocationFHIRSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'identifier', 'name', 'address', 'city', 'postal_code', 'phone']

    def to_representation(self, instance):
        return {
            "resourceType": "Location",
            "id": str(instance.id),
            "identifier": [
                {
                    "system": "https://hopital.fr/locations",
                    "value": str(instance.identifier)
                }
            ],
            "name": instance.name,
            "address": {
                "line": [instance.address],
                "city": instance.city,
                "postalCode": instance.postal_code
            },
            "telecom": [
                {
                    "system": "phone",
                    "value": instance.phone
                }
            ] if instance.phone else [],
            "meta": {
                "lastUpdated": instance.updated_at.isoformat()
            }
        }


class MedicationFHIRSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = ['id', 'identifier', 'code', 'name', 'description', 'form']

    def to_representation(self, instance):
        return {
            "resourceType": "Medication",
            "id": str(instance.id),
            "identifier": [
                {
                    "system": "https://hopital.fr/medications",
                    "value": str(instance.identifier)
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://www.whocc.no/atc",
                        "code": instance.code,
                        "display": instance.name
                    }
                ],
                "text": instance.name
            },
            "form": {
                "text": instance.form
            },
            "status": "active",
            "meta": {
                "lastUpdated": instance.updated_at.isoformat()
            }
        }


class AllergyIntoleranceFHIRSerializer(serializers.ModelSerializer):
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        source='patient',
        write_only=True
    )
    
    class Meta:
        model = AllergyIntolerance
        fields = ['id', 'patient_id', 'substance', 'severity', 'status', 'note']

    def to_representation(self, instance):
        return {
            "resourceType": "AllergyIntolerance",
            "id": str(instance.id),
            "clinicalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                        "code": instance.clinical_status
                    }
                ]
            },
            "verificationStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
                        "code": instance.verification_status
                    }
                ]
            },
            "patient": {
                "reference": f"Patient/{instance.patient.id}",
                "display": f"{instance.patient.family_name} {instance.patient.given_name}"
            },
            "substance": {
                "text": instance.substance
            },
            "reaction": [
                {
                    "severity": instance.severity,
                    "manifestation": [
                        {
                            "text": instance.substance
                        }
                    ]
                }
            ] if instance.substance else [],
            "note": [
                {
                    "text": instance.note
                }
            ] if instance.note else [],
            "recordedDate": instance.first_occurrence.isoformat(),
            "meta": {
                "lastUpdated": instance.last_occurrence.isoformat()
            }
        }


class DiagnosticReportFHIRSerializer(serializers.ModelSerializer):
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        source='patient',
        write_only=True
    )
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        source='location',
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = DiagnosticReport
        fields = ['id', 'patient_id', 'location_id', 'code', 'report_type', 'status', 'effective_date', 'result_text', 'conclusion']

    def to_representation(self, instance):
        return {
            "resourceType": "DiagnosticReport",
            "id": str(instance.id),
            "identifier": [
                {
                    "system": "https://hopital.fr/reports",
                    "value": str(instance.identifier)
                }
            ],
            "status": instance.status,
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": instance.code,
                        "display": instance.report_type
                    }
                ],
                "text": instance.report_type
            },
            "subject": {
                "reference": f"Patient/{instance.patient.id}",
                "display": f"{instance.patient.family_name} {instance.patient.given_name}"
            },
            "location": {
                "reference": f"Location/{instance.location.id}",
                "display": instance.location.name
            } if instance.location else None,
            "effectiveDateTime": instance.effective_date.isoformat(),
            "issued": instance.issued.isoformat(),
            "conclusion": instance.conclusion if instance.conclusion else instance.result_text,
            "presentedForm": [
                {
                    "contentType": "text/plain",
                    "data": instance.result_text
                }
            ] if instance.result_text else [],
            "meta": {
                "lastUpdated": instance.updated_at.isoformat()
            }
        }
