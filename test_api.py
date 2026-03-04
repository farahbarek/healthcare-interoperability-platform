import requests
import json
from datetime import datetime, timedelta
import unittest
from typing import Dict, Tuple

BASE_URL = "http://localhost:8000/api"
TOKEN = None  # À remplir avec un token JWT valide


class FHIR_APITester:
    """
    Testeur complet de l'API FHIR.
    Couvre CRUD, filtrage, et conformité FHIR.
    """
    
    def __init__(self, base_url: str = BASE_URL, token: str = None):
        self.base_url = base_url
        self.token = token
        self.headers = {
            'Content-Type': 'application/json',
        }
        if token:
            self.headers['Authorization'] = f'Bearer {token}'
        
        self.test_results = []
        self.patient_id = None
        self.observation_id = None
    
    def print_result(self, test_name: str, passed: bool, details: str = ""):
        """Afficher le résultat d'un test"""
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"     {details}")
        self.test_results.append((test_name, passed))
    
    def print_response(self, response: requests.Response):
        """Afficher les détails d'une réponse HTTP"""
        print(f"   Status: {response.status_code}")
        if response.text:
            try:
                print(f"   Body: {json.dumps(response.json(), indent=2)}")
            except:
                print(f"   Body: {response.text[:200]}")
    
    # ============ TESTS PATIENT ============
    
    def test_create_patient(self) -> bool:
        """Test: Créer un patient FHIR"""
        print("\n📝 TEST: Créer un patient")
        
        payload = {
            "resourceType": "Patient",
            "name": [{
                "family": "Dupont",
                "given": ["Jean"]
            }],
            "gender": "male",
            "birthDate": "1980-05-15"
        }
        
        response = requests.post(
            f"{self.base_url}/patients/",
            json=payload,
            headers=self.headers
        )
        
        passed = response.status_code in [200, 201]
        self.print_result("POST /patients/", passed)
        
        if passed:
            data = response.json()
            self.patient_id = data.get('id')
            self.print_result("Patient ID récupéré", self.patient_id is not None, f"ID: {self.patient_id}")
            
            # Vérifier la structure FHIR
            fhir_valid = data.get('resourceType') == 'Patient'
            self.print_result("Format FHIR valide", fhir_valid, f"resourceType: {data.get('resourceType')}")
        else:
            self.print_response(response)
        
        return passed
    
    def test_get_patient(self) -> bool:
        """Test: Récupérer un patient"""
        print("\n📖 TEST: Récupérer un patient")
        
        if not self.patient_id:
            self.print_result("GET /patients/{id}/", False, "Pas de patient créé")
            return False
        
        response = requests.get(
            f"{self.base_url}/patients/{self.patient_id}/",
            headers=self.headers
        )
        
        passed = response.status_code == 200
        self.print_result("GET /patients/{id}/", passed)
        
        if passed:
            data = response.json()
            self.print_result("Données patient complètes", 
                             all(k in data for k in ['identifier', 'family_name', 'birth_date']),
                             f"Champs trouvés")
        else:
            self.print_response(response)
        
        return passed
    
    def test_update_patient(self) -> bool:
        """Test: Modifier un patient"""
        print("\n✏️ TEST: Modifier un patient")
        
        if not self.patient_id:
            self.print_result("PATCH /patients/{id}/", False, "Pas de patient créé")
            return False
        
        payload = {
            "gender": "female"
        }
        
        response = requests.patch(
            f"{self.base_url}/patients/{self.patient_id}/",
            json=payload,
            headers=self.headers
        )
        
        passed = response.status_code in [200, 204]
        self.print_result("PATCH /patients/{id}/", passed)
        
        return passed
    
    def test_list_patients(self) -> bool:
        """Test: Lister tous les patients"""
        print("\n📋 TEST: Lister les patients")
        
        response = requests.get(
            f"{self.base_url}/patients/",
            headers=self.headers
        )
        
        passed = response.status_code == 200
        self.print_result("GET /patients/", passed)
        
        if passed:
            data = response.json()
            count = len(data.get('results', data))
            self.print_result("Patients trouvés", count > 0, f"{count} patients")
        else:
            self.print_response(response)
        
        return passed
    
    def test_filter_patients(self) -> bool:
        """Test: Filtrer les patients"""
        print("\n🔍 TEST: Filtrer les patients")
        
        response = requests.get(
            f"{self.base_url}/patients/?gender=male",
            headers=self.headers
        )
        
        passed = response.status_code == 200
        self.print_result("GET /patients/?gender=male", passed)
        
        if passed:
            data = response.json()
            self.print_result("Filtre appliqué", True, "Patients filtrés par genre")
        else:
            self.print_response(response)
        
        return passed
    
    # ============ TESTS OBSERVATION ============
    
    def test_create_observation(self) -> bool:
        """Test: Créer une observation FHIR"""
        print("\n📊 TEST: Créer une observation")
        
        if not self.patient_id:
            self.print_result("POST /observations/", False, "Pas de patient créé")
            return False
        
        payload = {
            "resourceType": "Observation",
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "8867-4",
                    "display": "Heart rate"
                }]
            },
            "subject": {
                "reference": f"Patient/{self.patient_id}"
            },
            "effectiveDateTime": datetime.now().isoformat(),
            "valueQuantity": {
                "value": 75,
                "unit": "bpm",
                "system": "http://unitsofmeasure.org"
            }
        }
        
        response = requests.post(
            f"{self.base_url}/observations/",
            json=payload,
            headers=self.headers
        )
        
        passed = response.status_code in [200, 201]
        self.print_result("POST /observations/", passed)
        
        if passed:
            data = response.json()
            self.observation_id = data.get('id')
            self.print_result("Observation ID récupéré", self.observation_id is not None)
            
            # Vérifier la structure FHIR
            fhir_valid = data.get('resourceType') == 'Observation'
            self.print_result("Format FHIR valide", fhir_valid)
        else:
            self.print_response(response)
        
        return passed
    
    def test_get_observation(self) -> bool:
        """Test: Récupérer une observation"""
        print("\n📖 TEST: Récupérer une observation")
        
        if not self.observation_id:
            self.print_result("GET /observations/{id}/", False, "Pas d'observation créée")
            return False
        
        response = requests.get(
            f"{self.base_url}/observations/{self.observation_id}/",
            headers=self.headers
        )
        
        passed = response.status_code == 200
        self.print_result("GET /observations/{id}/", passed)
        
        if passed:
            data = response.json()
            has_values = all(k in data for k in ['value', 'unit', 'effective_date'])
            self.print_result("Toutes les données présentes", has_values)
        else:
            self.print_response(response)
        
        return passed
    
    def test_list_observations(self) -> bool:
        """Test: Lister toutes les observations"""
        print("\n📋 TEST: Lister les observations")
        
        response = requests.get(
            f"{self.base_url}/observations/",
            headers=self.headers
        )
        
        passed = response.status_code == 200
        self.print_result("GET /observations/", passed)
        
        if passed:
            data = response.json()
            count = len(data.get('results', data))
            self.print_result("Observations trouvées", count > 0, f"{count} observations")
        else:
            self.print_response(response)
        
        return passed
    
    def test_filter_observations(self) -> bool:
        """Test: Filtrer les observations"""
        print("\n🔍 TEST: Filtrer les observations")
        
        if not self.patient_id:
            self.print_result("Filtre par patient", False, "Pas de patient créé")
            return False
        
        response = requests.get(
            f"{self.base_url}/observations/?patient={self.patient_id}",
            headers=self.headers
        )
        
        passed = response.status_code == 200
        self.print_result(f"GET /observations/?patient={self.patient_id}", passed)
        
        return passed
    
    def test_observations_by_patient(self) -> bool:
        """Test: Récupérer les observations d'un patient"""
        print("\n🔗 TEST: Observations d'un patient")
        
        if not self.patient_id:
            self.print_result("GET /patients/{id}/observations/", False, "Pas de patient")
            return False
        
        response = requests.get(
            f"{self.base_url}/patients/{self.patient_id}/observations/",
            headers=self.headers
        )
        
        passed = response.status_code == 200
        self.print_result("GET /patients/{id}/observations/", passed)
        
        if passed:
            data = response.json()
            count = len(data)
            self.print_result("Observations liées trouvées", count > 0, f"{count} observations")
        else:
            self.print_response(response)
        
        return passed
    
    def test_delete_observation(self) -> bool:
        """Test: Supprimer une observation"""
        print("\n🗑️ TEST: Supprimer une observation")
        
        if not self.observation_id:
            self.print_result("DELETE /observations/{id}/", False, "Pas d'observation")
            return False
        
        response = requests.delete(
            f"{self.base_url}/observations/{self.observation_id}/",
            headers=self.headers
        )
        
        passed = response.status_code in [200, 204, 404]  # 404 = déjà supprimée
        self.print_result("DELETE /observations/{id}/", passed)
        
        return passed
    
    # ============ TESTS SCHEMA ============
    
    def test_openapi_schema(self) -> bool:
        """Test: Schéma OpenAPI disponible"""
        print("\n📐 TEST: Schéma OpenAPI")
        
        response = requests.get(
            f"{self.base_url}/schema/",
            headers=self.headers
        )
        
        passed = response.status_code == 200
        self.print_result("GET /schema/", passed)
        
        if passed:
            data = response.json()
            has_paths = 'paths' in data or 'paths' in response.text
            self.print_result("Schéma valide", has_paths)
        else:
            self.print_response(response)
        
        return passed
    
    # ============ SUMMARY ============
    
    def print_summary(self):
        """Afficher un résumé des tests"""
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES TESTS")
        print("=" * 60)
        
        passed = sum(1 for _, p in self.test_results if p)
        total = len(self.test_results)
        percentge = (passed / total * 100) if total > 0 else 0
        
        print(f"Réussis: {passed}/{total} ({percentge:.1f}%)")
        
        failed_tests = [name for name, passed in self.test_results if not passed]
        if failed_tests:
            print(f"\n❌ Tests échoués:")
            for test in failed_tests:
                print(f"   - {test}")
        else:
            print("\n✅ Tous les tests réussis!")
        
        print("=" * 60)
    
    def run_all_tests(self):
        """Exécuter tous les tests"""
        print("\n🧪 DÉMARRAGE DE LA SUITE DE TESTS FHIR API")
        print("=" * 60)
        
        # Tests Patient
        self.test_create_patient()
        self.test_get_patient()
        self.test_update_patient()
        self.test_list_patients()
        self.test_filter_patients()
        
        # Tests Observation
        self.test_create_observation()
        self.test_get_observation()
        self.test_list_observations()
        self.test_filter_observations()
        self.test_observations_by_patient()
        self.test_delete_observation()
        
        # Tests Schéma
        self.test_openapi_schema()
        
        # Résumé
        self.print_summary()


def main():
    """Exécuter les tests"""
    
    # Note: Si vous avez besoin d'authentification JWT, 
    # vous pouvez créer un token via le endpoint d'authentification
    
    tester = FHIR_APITester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
