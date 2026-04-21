from rest_framework.exceptions import ValidationError

# Try to import FHIR resources, but don't fail if they are missing or have version issues
try:
    from fhir.resources.patient import Patient as FHIRPatient
    from fhir.resources.observation import Observation as FHIRObservation
    HAS_FHIR_RESOURCES = True
except ImportError:
    HAS_FHIR_RESOURCES = False


def validate_fhir_resource(data, resource_type='Patient'):
    """
    Validate data against FHIR resource schema.
    """
    if not HAS_FHIR_RESOURCES:
        return True

    try:
        if resource_type == 'Patient':
            FHIRPatient(**data)
        elif resource_type == 'Observation':
            FHIRObservation(**data)
        return True
    except Exception as e:
        raise ValidationError({"fhir_validation": str(e)})


def validate_patient_data(data, partial=False):
    """
    Validate patient-specific FHIR requirements.
    """
    errors = {}
    
    # Check required fields only if not a partial update
    if not partial:
        if not data.get('family_name'):
            errors['family_name'] = 'Family name is required'
        if not data.get('given_name'):
            errors['given_name'] = 'Given name is required'
        if not data.get('gender'):
            errors['gender'] = 'Gender is required'
        if not data.get('birth_date'):
            errors['birth_date'] = 'Birth date is required'
    
    # Validate gender choices if present
    valid_genders = ['male', 'female', 'other', 'unknown']
    if data.get('gender') and data['gender'] not in valid_genders:
        errors['gender'] = f"Gender must be one of: {', '.join(valid_genders)}"
    
    if errors:
        raise ValidationError(errors)
    
    return data


def validate_observation_data(data, partial=False):
    """
    Validate observation-specific FHIR requirements.
    """
    errors = {}
    
    # Check required fields only if not a partial update
    if not partial:
        if not data.get('patient'):
            errors['patient'] = 'Patient reference is required'
        if not data.get('observation_type'):
            errors['observation_type'] = 'Observation type is required'
        if data.get('value') is None:
            errors['value'] = 'Observation value is required'
        if not data.get('unit'):
            errors['unit'] = 'Unit is required'
        if not data.get('effective_date'):
            errors['effective_date'] = 'Effective date is required'
    
    # Validate observation type choices if present
    valid_types = ['blood-pressure', 'heart-rate', 'temperature', 'weight', 'height']
    if data.get('observation_type') and data['observation_type'] not in valid_types:
        errors['observation_type'] = f"Observation type must be one of: {', '.join(valid_types)}"
    
    # Validate value is numeric if present
    if data.get('value') is not None:
        try:
            float(data['value'])
        except (ValueError, TypeError):
            errors['value'] = 'Value must be a number'
    
    if errors:
        raise ValidationError(errors)
    
    return data
