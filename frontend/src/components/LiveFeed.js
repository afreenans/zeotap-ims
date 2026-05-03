import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';

function LiveFeed() {
  const [incidents, setIncidents] = useState([]);
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchIncidents();
    const interval = setInterval(fetchIncidents, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, [filter]);

  const fetchIncidents = async () => {
    try {
      const data = await api.getIncidents(filter || null);
      setIncidents(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching incidents:', error);
      setLoading(false);
    }
  };

  const getSeverityClass = (severity) => `severity-badge severity-${severity}`;
  const getStateClass = (state) => `state-badge state-${state}`;

  if (loading) {
    return <div className="container"><div className="loading">Loading incidents...</div></div>;
  }

  return (
    <div className="container">
      <div className="feed-header">
        <h2>🔴 Live Incident Feed</h2>
        <div className="filter-controls">
          <label htmlFor="state-filter">Filter by State: </label>
          <select 
            id="state-filter"
            className="form-control"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            style={{ width: '200px', display: 'inline-block', marginLeft: '10px' }}
          >
            <option value="">All States</option>
            <option value="OPEN">Open</option>
            <option value="INVESTIGATING">Investigating</option>
            <option value="RESOLVED">Resolved</option>
            <option value="CLOSED">Closed</option>
          </select>
        </div>
      </div>

      {incidents.length === 0 ? (
        <div className="card">
          <p>No incidents found. System is healthy! ✅</p>
        </div>
      ) : (
        <div className="incidents-grid">
          {incidents.map((incident) => (
            <Link 
              to={`/incident/${incident.id}`} 
              key={incident.id}
              style={{ textDecoration: 'none', color: 'inherit' }}
            >
              <div className="card incident-card">
                <div className="incident-header">
                  <h3>{incident.component_id}</h3>
                  <span className={getSeverityClass(incident.severity)}>
                    {incident.severity}
                  </span>
                </div>
                
                <div className="incident-details">
                  <div className="detail-row">
                    <span className="label">State:</span>
                    <span className={getStateClass(incident.state)}>
                      {incident.state}
                    </span>
                  </div>
                  
                  <div className="detail-row">
                    <span className="label">Signals:</span>
                    <span>{incident.signal_count}</span>
                  </div>
                  
                  <div className="detail-row">
                    <span className="label">Created:</span>
                    <span>{new Date(incident.created_at).toLocaleString()}</span>
                  </div>
                  
                  <div className="detail-row">
                    <span className="label">RCA:</span>
                    <span>{incident.has_rca ? '✅ Completed' : '⏳ Pending'}</span>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      <style jsx>{`
        .feed-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 2rem;
        }

        .filter-controls {
          display: flex;
          align-items: center;
        }

        .incidents-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
          gap: 1.5rem;
        }

        .incident-card {
          cursor: pointer;
        }

        .incident-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
          padding-bottom: 1rem;
          border-bottom: 2px solid #e2e8f0;
        }

        .incident-header h3 {
          margin: 0;
          color: #2d3748;
          font-size: 1.25rem;
        }

        .incident-details {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .detail-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .detail-row .label {
          color: #718096;
          font-weight: 500;
        }
      `}</style>
    </div>
  );
}

export default LiveFeed;
