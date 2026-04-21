import React, { useState, useEffect } from 'react';
import { patientApi, observationApi } from '../api';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area 
} from 'recharts';
import { Users, Activity, Thermometer, Heart, Search, Filter, Plus } from 'lucide-react';
import PatientModal from './PatientModal';

const Dashboard = ({ view = 'dashboard' }) => {
  const [patients, setPatients] = useState([]);
  const [observations, setObservations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isPatientModalOpen, setIsPatientModalOpen] = useState(false);

  const fetchData = async () => {
    try {
      const [pRes, oRes] = await Promise.all([
        patientApi.list(),
        observationApi.list()
      ]);
      setPatients(pRes.data.results || pRes.data);
      setObservations(oRes.data.results || oRes.data);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const chartData = observations.length > 0 
    ? observations.map(o => ({
        name: new Date(o.issued || o.effectiveDateTime).toLocaleTimeString(),
        value: o.valueQuantity?.value || o.value
      }))
    : [
        { name: '08:00', value: 72 },
        { name: '10:00', value: 75 },
        { name: '12:00', value: 82 },
        { name: '14:00', value: 78 },
        { name: '16:00', value: 74 },
      ];

  if (loading) return <div className="loading">Chargement des données FHIR...</div>;

  const renderDashboard = () => (
    <>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon"><Users size={24} /></div>
          <div className="stat-info">
            <h3>Total Patients</h3>
            <p>{patients.length}</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon"><Activity size={24} /></div>
          <div className="stat-info">
            <h3>Observations</h3>
            <p>{observations.length}</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ color: '#06b6d4', background: 'rgba(6, 182, 212, 0.1)' }}>
            <Heart size={24} />
          </div>
          <div className="stat-info">
            <h3>Pouls Moyen</h3>
            <p>76 bpm</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ color: '#10b981', background: 'rgba(16, 185, 129, 0.1)' }}>
            <Thermometer size={24} />
          </div>
          <div className="stat-info">
            <h3>Alertes</h3>
            <p>0</p>
          </div>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="glass-card">
          <div className="card-header">
            <h2>Activité des Signes Vitaux</h2>
            <div className="badge badge-primary">LIVE</div>
          </div>
          <div style={{ width: '100%', height: 300, marginTop: '2rem' }}>
            <ResponsiveContainer>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#a855f7" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#a855f7" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis dataKey="name" stroke="#6b7280" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#6b7280" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip 
                  contentStyle={{ background: '#111827', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  itemStyle={{ color: '#a855f7' }}
                />
                <Area type="monotone" dataKey="value" stroke="#a855f7" fillOpacity={1} fill="url(#colorValue)" strokeWidth={3} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-card">
          <div className="card-header">
            <h2>Derniers Patients</h2>
            <button className="btn" style={{ padding: '0.4rem', background: 'rgba(255,255,255,0.05)' }}>
              <Filter size={18} />
            </button>
          </div>
          <div className="patient-mini-list" style={{ marginTop: '1rem' }}>
            {patients.slice(0, 5).map(p => (
              <div key={p.id} className="patient-mini-item">
                <div className="avatar">
                  {p.name?.[0]?.family?.[0] || p.family_name?.[0] || 'P'}
                </div>
                <div>
                  <div style={{ fontWeight: '500' }}>
                    {p.name?.[0]?.family || p.family_name} {p.name?.[0]?.given?.[0] || p.given_name}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    FHIR ID: {p.id}
                  </div>
                </div>
                <div style={{ marginLeft: 'auto' }}>
                   <div className={`badge ${p.gender === 'male' ? 'badge-primary' : 'badge-secondary'}`}>
                     {p.gender?.[0]?.toUpperCase()}
                   </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );

  const renderPatients = () => (
    <div className="glass-card">
      <div className="card-header">
        <h2>Registre des Patients</h2>
        <div style={{ position: 'relative' }}>
          <Search size={18} style={{ position: 'absolute', left: '10px', top: '10px', color: 'var(--text-muted)' }} />
          <input type="text" placeholder="Rechercher un patient..." className="search-input" />
        </div>
      </div>
      <table className="fhir-table">
        <thead>
          <tr>
            <th>Nom</th>
            <th>ID FHIR</th>
            <th>Genre</th>
            <th>Date de Naissance</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {patients.map(p => (
            <tr key={p.id}>
              <td>{p.name?.[0]?.family || p.family_name} {p.name?.[0]?.given?.join(' ') || p.given_name}</td>
              <td><code>{p.id}</code></td>
              <td><span className={`badge ${p.gender === 'male' ? 'badge-primary' : 'badge-secondary'}`}>{p.gender}</span></td>
              <td>{p.birthDate || p.birth_date}</td>
              <td><button className="btn btn-sm">Détails</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  const renderObservations = () => (
    <div className="glass-card">
      <div className="card-header">
        <h2>Registre des Observations</h2>
        <div style={{ position: 'relative' }}>
          <Search size={18} style={{ position: 'absolute', left: '10px', top: '10px', color: 'var(--text-muted)' }} />
          <input type="text" placeholder="Rechercher une observation..." className="search-input" />
        </div>
      </div>
      <table className="fhir-table">
        <thead>
          <tr>
            <th>Type</th>
            <th>ID</th>
            <th>Patient</th>
            <th>Valeur</th>
            <th>Date</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {observations.map(o => (
            <tr key={o.id}>
              <td><span className="badge badge-secondary">{o.observation_type || 'Observation'}</span></td>
              <td>{o.id}</td>
              <td>{o.subject?.display || o.patient_name || 'Patient ' + o.patient_id}</td>
              <td><strong>{o.valueQuantity?.value || o.value}</strong> {o.valueQuantity?.unit || o.unit}</td>
              <td>{new Date(o.issued || o.effectiveDateTime).toLocaleString()}</td>
              <td><span className="badge badge-success">Final</span></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  const renderAbout = () => (
    <div className="glass-card animate-fade-in" style={{ lineHeight: '1.6' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.8rem', color: 'var(--primary)', marginBottom: '1rem' }}>À propos du Projet FHIR Care</h2>
        <p style={{ fontSize: '1.1rem', color: 'var(--text-main)' }}>
          Cette plateforme est une solution d'interopérabilité médicale conçue pour centraliser et standardiser les données de santé 
          en utilisant le standard international <strong>HL7 FHIR R4</strong>.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem' }}>
        <div className="glass-card" style={{ background: 'rgba(255,255,255,0.02)' }}>
          <h3 style={{ color: 'var(--secondary)', marginBottom: '1rem' }}>Architecture Technique</h3>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            <li style={{ marginBottom: '0.5rem' }}>🔹 <strong>Backend :</strong> Django 6.0 & Django REST Framework</li>
            <li style={{ marginBottom: '0.5rem' }}>🔹 <strong>Frontend :</strong> React 19 & Vite (Fast Refresh)</li>
            <li style={{ marginBottom: '0.5rem' }}>🔹 <strong>Standard :</strong> HL7 FHIR Release 4</li>
            <li style={{ marginBottom: '0.5rem' }}>🔹 <strong>Base de données :</strong> SQLite avec support JSON</li>
          </ul>
        </div>
        <div className="glass-card" style={{ background: 'rgba(255,255,255,0.02)' }}>
          <h3 style={{ color: 'var(--success)', marginBottom: '1rem' }}>Fonctionnalités Clés</h3>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            <li style={{ marginBottom: '0.5rem' }}>✅ Gestion complète du cycle de vie des Patients</li>
            <li style={{ marginBottom: '0.5rem' }}>✅ Collecte d'Observations (signes vitaux, labo)</li>
            <li style={{ marginBottom: '0.5rem' }}>✅ Validation stricte des codes LOINC et ATC</li>
            <li style={{ marginBottom: '0.5rem' }}>✅ Dashboard temps réel avec visualisations</li>
          </ul>
        </div>
      </div>

      <div className="glass-card" style={{ background: 'rgba(168, 85, 247, 0.05)' }}>
        <h3 style={{ marginBottom: '1rem' }}>Interopérabilité FHIR</h3>
        <p>
          Toutes les données sont sérialisées au format FHIR JSON. Le système supporte nativement les ressources :
          <code>Patient</code>, <code>Observation</code>, <code>Location</code>, <code>Medication</code>, 
          <code>AllergyIntolerance</code> et <code>DiagnosticReport</code>. 
          Cela garantit que les données peuvent être échangées de manière transparente avec d'autres systèmes hospitaliers (HIS/DPI).
        </p>
      </div>
    </div>
  );

  const getTitle = () => {
    switch(view) {
      case 'patients': return 'Gestion des Patients';
      case 'observations': return 'Registre des Observations';
      case 'fhir': return 'Ressources FHIR';
      case 'about': return 'Documentation du Projet';
      case 'settings': return 'Paramètres';
      default: return 'Tableau de Bord Médical';
    }
  };

  return (
    <div className="main-content animate-fade-in">
      <header className="header">
        <div className="title-area">
          <h1>{getTitle()}</h1>
          <p>Gestion de l'interopérabilité FHIR en temps réel</p>
        </div>
        <div className="actions">
          <button className="btn btn-primary" onClick={() => setIsPatientModalOpen(true)}>
            <Plus size={18} />
            Nouveau Patient
          </button>
        </div>
      </header>

      {view === 'dashboard' && renderDashboard()}
      {view === 'patients' && renderPatients()}
      {view === 'observations' && renderObservations()}
      {view === 'fhir' && renderObservations()}
      {view === 'about' && renderAbout()}
      {view === 'settings' && <div className="glass-card"><h2>Paramètres du Système</h2><p>Configuration de l'API FHIR et des préférences.</p></div>}

      <PatientModal 
        isOpen={isPatientModalOpen} 
        onClose={() => setIsPatientModalOpen(false)} 
        onRefresh={fetchData} 
      />
    </div>
  );
};

export default Dashboard;
