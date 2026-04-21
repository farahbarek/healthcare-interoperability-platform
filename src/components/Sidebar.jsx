import { NavLink } from 'react-router-dom';
import { Activity, Users, Clipboard, Database, Settings, Home, Info } from 'lucide-react';

const Sidebar = () => {
  return (
    <div className="sidebar">
      <div className="logo">
        <Activity size={32} strokeWidth={2.5} />
        <span>FHIR Care</span>
      </div>
      <nav className="nav-links">
        <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <Home size={20} />
          <span>Dashboard</span>
        </NavLink>
        <NavLink to="/patients" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <Users size={20} />
          <span>Patients</span>
        </NavLink>
        <NavLink to="/observations" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <Clipboard size={20} />
          <span>Observations</span>
        </NavLink>
        <NavLink to="/fhir" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <Database size={20} />
          <span>FHIR Resources</span>
        </NavLink>
        <div style={{ marginTop: 'auto' }}>
          <NavLink to="/about" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <Info size={20} />
            <span>À propos</span>
          </NavLink>
          <NavLink to="/settings" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <Settings size={20} />
            <span>Paramètres</span>
          </NavLink>
        </div>
      </nav>
    </div>
  );
};

export default Sidebar;
