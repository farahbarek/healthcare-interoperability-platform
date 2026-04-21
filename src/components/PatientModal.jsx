import React, { useState } from 'react';
import { X } from 'lucide-react';
import { patientApi } from '../api';

const PatientModal = ({ isOpen, onClose, onRefresh }) => {
  const [formData, setFormData] = useState({
    family: '',
    given: '',
    gender: 'male',
    birthDate: ''
  });
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Format as FHIR Patient
      const fhirPatient = {
        resourceType: "Patient",
        name: [{
          family: formData.family,
          given: [formData.given]
        }],
        gender: formData.gender,
        birthDate: formData.birthDate
      };
      await patientApi.create(fhirPatient);
      onRefresh();
      onClose();
    } catch (error) {
      console.error("Error creating patient:", error);
      alert("Erreur lors de la création du patient. Vérifiez le format FHIR.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content animate-fade-in">
        <button className="btn" onClick={onClose} style={{ position: 'absolute', right: '1rem', top: '1rem', background: 'transparent' }}>
          <X size={24} color="var(--text-muted)" />
        </button>
        <div className="modal-header">
          <h2>Ajouter un Nouveau Patient</h2>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Nom (Family Name)</label>
            <input 
              className="form-control"
              required
              value={formData.family}
              onChange={e => setFormData({...formData, family: e.target.value})}
              placeholder="Ex: Dupont"
            />
          </div>
          <div className="form-group">
            <label>Prénom (Given Name)</label>
            <input 
              className="form-control"
              required
              value={formData.given}
              onChange={e => setFormData({...formData, given: e.target.value})}
              placeholder="Ex: Jean"
            />
          </div>
          <div className="form-group">
            <label>Genre</label>
            <select 
              className="form-control"
              value={formData.gender}
              onChange={e => setFormData({...formData, gender: e.target.value})}
            >
              <option value="male">Homme</option>
              <option value="female">Femme</option>
              <option value="other">Autre</option>
              <option value="unknown">Inconnu</option>
            </select>
          </div>
          <div className="form-group">
            <label>Date de Naissance</label>
            <input 
              type="date"
              className="form-control"
              required
              value={formData.birthDate}
              onChange={e => setFormData({...formData, birthDate: e.target.value})}
            />
          </div>
          <div className="modal-footer">
            <button type="button" className="btn" onClick={onClose}>Annuler</button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Création...' : 'Enregistrer'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PatientModal;
