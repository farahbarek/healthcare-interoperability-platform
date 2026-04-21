from rest_framework import serializers
from .models import Patient, Observation, Location, Medication, AllergyIntolerance, DiagnosticReport
from .validators import validate_fhir_resource, validate_patient_data, validate_observation_data
from fhir.resources.patient import Patient as FHIRPatient
from fhir.resources.observation import Observation as FHIRObservation
import uuid


class PatientFHIRSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'identifier', 'family_name', 'given_name', 'gender', 'birth_date']

    def validate(self, data):
        """Validate patient data against FHIR requirements"""
        # data here is already in "internal" format (model fields)
        return validate_patient_data(data, partial=self.partial)

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
            "birthDate": instance.birth_date.isoformat() if instance.birth_date else None,
            "meta": {
                "lastUpdated": instance.updated_at.isoformat()
            }
        }
        try:
            fhir_obj = FHIRPatient(**fhir_data)
            return fhir_obj.dict() if hasattr(fhir_obj, 'dict') else fhir_obj.model_dump()
        except:
            return fhir_data

    def to_internal_value(self, data):
        if data.get('resourceType') and data.get('resourceType') != 'Patient':
            raise serializers.ValidationError({"resourceType": "Doit être 'Patient'"})
        
        # If it's FHIR format (has 'name')
        if 'name' in data and isinstance(data['name'], list) and len(data['name']) > 0:
            name = data['name'][0]
            internal_data = data.copy()
            internal_data['family_name'] = name.get('family')
            internal_data['given_name'] = name.get('given', [None])[0] if isinstance(name.get('given'), list) else None
            internal_data['birth_date'] = data.get('birthDate')
            
            if 'identifier' in data and isinstance(data['identifier'], list) and len(data['identifier']) > 0:
                internal_data['identifier'] = data['identifier'][0].get('value')
            
            # Use only model fields for super().to_internal_value to avoid errors with extra FHIR fields
            model_data = {}
            for field in ['family_name', 'given_name', 'gender', 'birth_date', 'identifier']:
                if field in internal_data:
                    model_data[field] = internal_data[field]
            
            return super().to_internal_value(model_data)
        
        # Standard DRF format or partial update
        return super().to_internal_value(data)


class ObservationFHIRSerializer(serializers.ModelSerializer):
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        source='patient',
        write_only=True,
        required=True
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
        }, partial=self.partial)
        return data

    def to_representation(self, instance):
        loinc = {
            'blood-pressure': '85354-9',
            'heart-rate': '8867-4',
            'temperature': '8310-5',
            'weight': '29463-7',
            'height': '8302-2'
        }
        
        fhir_data = {
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
            "effectiveDateTime": instance.effective_date.isoformat() if instance.effective_date else None,
            "valueQuantity": {
                "value": float(instance.value),
                "unit": instance.unit,
                "system": "http://unitsofmeasure.org",
                "code": instance.unit
            },
            "issued": instance.created_at.isoformat()
        }
        try:
            fhir_obj = FHIRObservation(**fhir_data)
            return fhir_obj.dict() if hasattr(fhir_obj, 'dict') else fhir_obj.model_dump()
        except:
            return fhir_data

    def to_internal_value(self, data):
        if data.get('resourceType') and data.get('resourceType') != 'Observation':
            raise serializers.ValidationError({"resourceType": "Doit être 'Observation'"})
        
        # Mapping for FHIR format
        loinc_map = {
            '85354-9': 'blood-pressure',
            '8867-4': 'heart-rate',
            '8310-5': 'temperature',
            '29463-7': 'weight',
            '8302-2': 'height'
        }
        
        internal_data = data.copy()
        
        # Extract patient from subject
        if 'subject' in data and isinstance(data['subject'], dict):
            ref = data['subject'].get('reference', '')
            if 'Patient/' in ref:
                internal_data['patient_id'] = ref.split('/')[-1]
        
        # Extract type from code
        if 'code' in data and isinstance(data['code'], dict):
            coding = data['code'].get('coding', [{}])
            if coding:
                code_val = coding[0].get('code')
                if code_val in loinc_map:
                    internal_data['observation_type'] = loinc_map[code_val]

        # Extract value and unit
        if 'valueQuantity' in data and isinstance(data['valueQuantity'], dict):
            internal_data['value'] = data['valueQuantity'].get('value')
            internal_data['unit'] = data['valueQuantity'].get('unit')
            
        # Extract date
        if 'effectiveDateTime' in data:
            internal_data['effective_date'] = data['effectiveDateTime']
            
        # Clean up for model fields
        model_data = {}
        for field in ['patient_id', 'observation_type', 'value', 'unit', 'effective_date']:
            if field in internal_data:
                model_data[field] = internal_data[field]
        
        return super().to_internal_value(model_data)


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
                "line": [instance.address] if instance.address else [],
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

    def to_internal_value(self, data):
        if 'address' in data or 'telecom' in data:
            internal_data = data.copy()
            if 'address' in data and isinstance(data['address'], dict):
                addr = data['address']
                if 'line' in addr and isinstance(addr['line'], list) and addr['line']:
                    internal_data['address'] = addr['line'][0]
                internal_data['city'] = addr.get('city')
                internal_data['postal_code'] = addr.get('postalCode')
            
            if 'telecom' in data and isinstance(data['telecom'], list) and data['telecom']:
                internal_data['phone'] = data['telecom'][0].get('value')
                
            if 'identifier' in data and isinstance(data['identifier'], list) and data['identifier']:
                internal_data['identifier'] = data['identifier'][0].get('value')
            
            model_data = {}
            for field in ['name', 'address', 'city', 'postal_code', 'phone', 'identifier']:
                if field in internal_data:
                    model_data[field] = internal_data[field]
            return super().to_internal_value(model_data)
        return super().to_internal_value(data)


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

    def to_internal_value(self, data):
        if 'code' in data or 'form' in data:
            internal_data = data.copy()
            if 'code' in data and isinstance(data['code'], dict):
                c = data['code']
                coding = c.get('coding', [{}])
                if coding:
                    internal_data['code'] = coding[0].get('code')
                    internal_data['name'] = coding[0].get('display') or c.get('text')
                else:
                    internal_data['name'] = c.get('text')
            
            if 'form' in data and isinstance(data['form'], dict):
                internal_data['form'] = data['form'].get('text')
            
            if 'identifier' in data and isinstance(data['identifier'], list) and data['identifier']:
                internal_data['identifier'] = data['identifier'][0].get('value')

            model_data = {}
            for field in ['code', 'name', 'description', 'form', 'identifier']:
                if field in internal_data:
                    model_data[field] = internal_data[field]
            return super().to_internal_value(model_data)
        return super().to_internal_value(data)


class AllergyIntoleranceFHIRSerializer(serializers.ModelSerializer):
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        source='patient',
        write_only=True,
        required=True
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

    def to_internal_value(self, data):
        if 'patient' in data or 'substance' in data or 'reaction' in data:
            internal_data = data.copy()
            if 'patient' in data and isinstance(data['patient'], dict):
                ref = data['patient'].get('reference', '')
                if 'Patient/' in ref:
                    internal_data['patient_id'] = ref.split('/')[-1]
            
            if 'substance' in data and isinstance(data['substance'], dict):
                internal_data['substance'] = data['substance'].get('text')
            
            if 'reaction' in data and isinstance(data['reaction'], list) and data['reaction']:
                internal_data['severity'] = data['reaction'][0].get('severity')
            
            if 'clinicalStatus' in data and isinstance(data['clinicalStatus'], dict):
                coding = data['clinicalStatus'].get('coding', [{}])
                if coding:
                    internal_data['status'] = coding[0].get('code')
            
            if 'note' in data and isinstance(data['note'], list) and data['note']:
                internal_data['note'] = data['note'][0].get('text')
            
            model_data = {}
            for field in ['patient_id', 'substance', 'severity', 'status', 'note']:
                if field in internal_data:
                    model_data[field] = internal_data[field]
            return super().to_internal_value(model_data)
        return super().to_internal_value(data)


class DiagnosticReportFHIRSerializer(serializers.ModelSerializer):
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        source='patient',
        write_only=True,
        required=True
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
            "effectiveDateTime": instance.effective_date.isoformat() if instance.effective_date else None,
            "issued": instance.issued.isoformat() if instance.issued else None,
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

    def to_internal_value(self, data):
        if 'subject' in data or 'code' in data or 'presentedForm' in data:
            internal_data = data.copy()
            if 'subject' in data and isinstance(data['subject'], dict):
                ref = data['subject'].get('reference', '')
                if 'Patient/' in ref:
                    internal_data['patient_id'] = ref.split('/')[-1]
            
            if 'location' in data and isinstance(data['location'], dict):
                ref = data['location'].get('reference', '')
                if 'Location/' in ref:
                    internal_data['location_id'] = ref.split('/')[-1]
            
            if 'code' in data and isinstance(data['code'], dict):
                coding = data['code'].get('coding', [{}])
                if coding:
                    internal_data['code'] = coding[0].get('code')
                    internal_data['report_type'] = coding[0].get('display') or data['code'].get('text')
                else:
                    internal_data['report_type'] = data['code'].get('text')
            
            if 'effectiveDateTime' in data:
                internal_data['effective_date'] = data['effectiveDateTime']
            
            if 'presentedForm' in data and isinstance(data['presentedForm'], list) and data['presentedForm']:
                internal_data['result_text'] = data['presentedForm'][0].get('data')

            model_data = {}
            for field in ['patient_id', 'location_id', 'code', 'report_type', 'status', 'effective_date', 'result_text', 'conclusion']:
                if field in internal_data:
                    model_data[field] = internal_data[field]
            return super().to_internal_value(model_data)
        return super().to_internal_value(data)
