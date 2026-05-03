const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = {
  // Get all incidents
  getIncidents: async (state = null) => {
    const url = state ? `${API_URL}/api/incidents?state=${state}` : `${API_URL}/api/incidents`;
    const response = await fetch(url);
    return response.json();
  },

  // Get specific incident
  getIncident: async (id) => {
    const response = await fetch(`${API_URL}/api/incidents/${id}`);
    return response.json();
  },

  // Update incident state
  updateIncidentState: async (id, newState) => {
    const response = await fetch(`${API_URL}/api/incidents/${id}/state?new_state=${newState}`, {
      method: 'PATCH',
    });
    return response.json();
  },

  // Create RCA
  createRCA: async (id, rcaData) => {
    const response = await fetch(`${API_URL}/api/incidents/${id}/rca`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(rcaData),
    });
    return response.json();
  },

  // Get signals for component
  getSignals: async (componentId) => {
    const response = await fetch(`${API_URL}/api/signals/${componentId}`);
    return response.json();
  },

  // Health check
  getHealth: async () => {
    const response = await fetch(`${API_URL}/health`);
    return response.json();
  }
};
