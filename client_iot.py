import requests
import json
import time
from datetime import datetime, timedelta
import random
from typing import Dict, List

BASE_URL = "http://localhost:8000/api"
TOKEN = None  # À remplir avec un token JWT valide


class FHIRIoTClient:
    """
    Client IoT pour simuler l'envoi périodique de constantes vitales.
    Envoie des observations FHIR à intervalle régulier.
    """
    
    def __init__(self, base_url: str = BASE_URL, token: str = None):
        self.base_url = base_url
        self.token = token
        self.headers = {
            'Content-Type': 'application/json',
        }
        if token:
            self.headers['Authorization'] = f'Bearer {token}'
        self.patient_id = None
    
    def create_patient(self, family_name: str, given_name: str, gender: str, birth_date: str) -> Dict:
        """Créer un patient FHIR"""
        payload = {
            "resourceType": "Patient",
            "name": [{
                "family": family_name,
                "given": [given_name]
            }],
            "gender": gender,
            "birthDate": birth_date
        }
        
        response = requests.post(
            f"{self.base_url}/patients/",
            json=payload,
            headers=self.headers
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            self.patient_id = data.get('id')
            print(f"✓ Patient créé: {data.get('id')}")
            return data
        else:
            print(f"✗ Erreur création patient: {response.status_code} - {response.text}")
            return None
    
    def send_observation(self, observation_type: str, value: float, unit: str) -> Dict:
        """Envoyer une observation FHIR"""
        if not self.patient_id:
            print("✗ Aucun patient assigné. Créez un patient d'abord.")
            return None
        
        payload = {
            "resourceType": "Observation",
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": observation_type
                }]
            },
            "subject": {
                "reference": f"Patient/{self.patient_id}"
            },
            "effectiveDateTime": datetime.now().isoformat(),
            "valueQuantity": {
                "value": value,
                "unit": unit
            }
        }
        
        response = requests.post(
            f"{self.base_url}/observations/",
            json=payload,
            headers=self.headers
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"✓ Observation enregistrée: {observation_type} = {value} {unit}")
            return data
        else:
            print(f"✗ Erreur envoi observation: {response.status_code} - {response.text}")
            return None
    
    def get_patient_observations(self) -> List[Dict]:
        """Récupérer toutes les observations d'un patient"""
        if not self.patient_id:
            print("✗ Aucun patient assigné.")
            return []
        
        response = requests.get(
            f"{self.base_url}/patients/{self.patient_id}/observations/",
            headers=self.headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ {len(data)} observations trouvées")
            return data
        else:
            print(f"✗ Erreur récupération: {response.status_code}")
            return []
    
    def simulate_vitals(self, interval: int = 5, duration: int = 60):
        """
        Simuler l'envoi de constantes vitales à intervalle régulier.
        
        Args:
            interval (int): Intervalle entre les envois en secondes
            duration (int): Durée totale de la simulation en secondes
        """
        print(f"\n🏥 Démarrage simulation IoT (durée: {duration}s, intervalle: {interval}s)")
        print("=" * 60)
        
        vitals_templates = [
            {
                'type': 'blood-pressure',
                'value': random.randint(100, 140),
                'unit': 'mmHg',
                'display': 'Tension artérielle'
            },
            {
                'type': 'heart-rate',
                'value': random.randint(60, 100),
                'unit': 'bpm',
                'display': 'Fréquence cardiaque'
            },
            {
                'type': 'temperature',
                'value': round(random.uniform(36.5, 37.5), 1),
                'unit': '°C',
                'display': 'Température'
            },
            {
                'type': 'weight',
                'value': round(random.uniform(70, 85), 1),
                'unit': 'kg',
                'display': 'Poids'
            },
            {
                'type': 'height',
                'value': round(random.uniform(165, 190), 1),
                'unit': 'cm',
                'display': 'Taille'
            }
        ]
        
        start_time = time.time()
        observation_count = 0
        
        while time.time() - start_time < duration:
            # Sélectionner aléatoirement une constante vitale
            vital = random.choice(vitals_templates)
            
            # Envoyer l'observation
            self.send_observation(vital['type'], vital['value'], vital['unit'])
            observation_count += 1
            
            # Attendre avant le prochain envoi
            time.sleep(interval)
        
        print("=" * 60)
        print(f"✓ Simulation terminée: {observation_count} observations envoyées")
        
        # Afficher les observations enregistrées
        observations = self.get_patient_observations()
        print(f"\n📊 Observations finales ({len(observations)}):")
        for obs in observations[:5]:  # Afficher les 5 dernières
            print(f"  - {obs.get('code', {}).get('coding', [{}])[0].get('display', 'Unknown')}: "
                  f"{obs.get('valueQuantity', {}).get('value', 'N/A')} "
                  f"{obs.get('valueQuantity', {}).get('unit', '')}")


def main():
    """Exemple d'utilisation du client IoT"""
    
    # Note: Vous devez d'abord créer un token JWT via l'API
    # ou désactiver temporairement l'authentification pour les tests
    
    print("🚀 Client IoT FHIR")
    print("=" * 60)
    
    client = FHIRIoTClient()
    
    # Créer un patient test
    patient_data = client.create_patient(
        family_name="Dupont",
        given_name="Jean",
        gender="male",
        birth_date="1980-05-15"
    )
    
    if patient_data:
        # Simuler l'envoi de constantes vitales
        client.simulate_vitals(interval=2, duration=30)


if __name__ == "__main__":
    main()
