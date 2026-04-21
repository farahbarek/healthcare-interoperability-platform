import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const patientApi = {
  list: () => api.get('/patients/'),
  get: (id) => api.get(`/patients/${id}/`),
  create: (data) => api.post('/patients/', data),
  observations: (id) => api.get(`/patients/${id}/observations/`),
};

export const observationApi = {
  list: () => api.get('/observations/'),
  create: (data) => api.post('/observations/', data),
};


export default api;
