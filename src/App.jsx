import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <div className="app-container">
      <Sidebar />
      <Routes>
        <Route path="/" element={<Dashboard view="dashboard" />} />
        <Route path="/patients" element={<Dashboard view="patients" />} />
        <Route path="/observations" element={<Dashboard view="observations" />} />
        <Route path="/fhir" element={<Dashboard view="fhir" />} />
        <Route path="/about" element={<Dashboard view="about" />} />
        <Route path="/settings" element={<Dashboard view="settings" />} />
      </Routes>
    </div>
  );
}

export default App;
