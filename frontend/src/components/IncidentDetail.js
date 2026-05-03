import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import RCAForm from './RCAForm';

function IncidentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [incident, setIncident] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showRCAForm, setShowRCAForm] = useState(false);

  useEffect(() => {
    fetchIncident();
  }, [id]);

  const fetchIncident = async () => {
    try {
      const data = await api.getIncident(id);
      setIncident(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching incident:', error);
      setLoading(false);
    }
  };

  const handleStateTransition = async (newState) => {
    try {
      await api.updateIncidentState(id, newState);
      fetchIncident();
    } catch (error) {
      alert(`Error: ${error.message}`);
    }
  };

  const handleRCASubmit = () => {
    setShowRCAForm(false);
    fetchIncident();
  };

  if (loading) {
    return <div className="container"><div className="loading">Loading incident details...</div></div>;
  }

  if (!incident) {
    return <div className="container"><div className="error">Incident not found</div></div>;
  }

  return (
    <div className="container">
      <button className="btn btn-secondary" onClick={() => navigate('/')}>
        ← Back to Dashboard
      </button>

      <div className="card" style={{ marginTop: '1rem' }}>
        <div className="incident-detail-header">
          <div>
            <h2>{incident.component_id}</h2>
            <p style={{ color: '#718096', marginTop: '0.5rem' }}>
              Incident ID: #{incident.id}
            </p>
          </div>
          <div>
            <span className={`severity-badge severity-${incident.severity}`}>
              {incident.severity}
            </span>
            <span className={`state-badge state-${incident.state}`} style={{ marginLeft: '1rem' }}>
              {incident.state}
            </span>
          </div>
        </div>

        <div className="incident-info">
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Created At:</span>
              <span className="info-value">{new Date(incident.created_at).toLocaleString()}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Updated At:</span>
              <span className="info-value">{new Date(incident.updated_at).toLocaleString()}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Signal Count:</span>
              <span className="info-value">{incident.signal_count}</span>
            </div>
            <div className="info-item">
              <span className="info-label">RCA Status:</span>
              <span className="info-value">{incident.has_rca ? '✅ Completed' : '⏳ Pending'}</span>
            </div>
          </div>
        </div>

        {/* State Transition Buttons */}
        <div className="state-actions">
          <h3>State Transitions</h3>
          <div className="action-buttons">
            {incident.state === 'OPEN' && (
              <button 
                className="btn btn-primary"
                onClick={() => handleStateTransition('INVESTIGATING')}
              >
                Start Investigation →
              </button>
            )}
            
            {incident.state === 'INVESTIGATING' && (
              <>
                <button 
                  className="btn btn-secondary"
                  onClick={() => handleStateTransition('OPEN')}
                >
                  ← Reopen
                </button>
                <button 
                  className="btn btn-primary"
                  onClick={() => handleStateTransition('RESOLVED')}
                >
                  Mark as Resolved →
                </button>
              </>
            )}
            
            {incident.state === 'RESOLVED' && (
              <>
                <button 
                  className="btn btn-secondary"
                  onClick={() => handleStateTransition('INVESTIGATING')}
                >
                  ← Back to Investigation
                </button>
                <button 
                  className="btn btn-success"
                  onClick={() => setShowRCAForm(true)}
                  disabled={incident.has_rca}
                >
                  {incident.has_rca ? 'RCA Already Submitted' : 'Submit RCA & Close →'}
                </button>
              </>
            )}
            
            {incident.state === 'CLOSED' && (
              <div className="alert-success">
                ✅ This incident is closed. RCA has been submitted.
              </div>
            )}
          </div>
        </div>

        {/* Raw Signals */}
        <div className="signals-section">
          <h3>Raw Signals ({incident.signals?.length || 0})</h3>
          {incident.signals && incident.signals.length > 0 ? (
            <div className="signals-list">
              {incident.signals.map((signal, idx) => (
                <div key={idx} className="signal-item">
                  <div className="signal-time">
                    {new Date(signal.timestamp).toLocaleString()}
                  </div>
                  <div className="signal-message">
                    {signal.error_message}
                  </div>
                  <div className="signal-severity">
                    <span className={`severity-badge severity-${signal.severity}`}>
                      {signal.severity}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p>No signals found.</p>
          )}
        </div>
      </div>

      {/* RCA Form Modal */}
      {showRCAForm && (
        <RCAForm 
          incidentId={id}
          onClose={() => setShowRCAForm(false)}
          onSubmit={handleRCASubmit}
        />
      )}

      <style jsx>{`
        .incident-detail-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          padding-bottom: 1.5rem;
          border-bottom: 2px solid #e2e8f0;
          margin-bottom: 1.5rem;
        }

        .incident-info {
          margin-bottom: 2rem;
        }

        .info-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1.5rem;
        }

        .info-item {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .info-label {
          color: #718096;
          font-weight: 500;
          font-size: 0.875rem;
        }

        .info-value {
          color: #2d3748;
          font-weight: 600;
          font-size: 1rem;
        }

        .state-actions {
          margin: 2rem 0;
          padding: 1.5rem;
          background: #f7fafc;
          border-radius: 8px;
        }

        .state-actions h3 {
          margin-bottom: 1rem;
        }

        .action-buttons {
          display: flex;
          gap: 1rem;
          flex-wrap: wrap;
        }

        .alert-success {
          background: #e6ffed;
          color: #38a169;
          padding: 1rem;
          border-radius: 5px;
          font-weight: 500;
        }

        .signals-section {
          margin-top: 2rem;
        }

        .signals-section h3 {
          margin-bottom: 1rem;
        }

        .signals-list {
          max-height: 400px;
          overflow-y: auto;
        }

        .signal-item {
          background: #f7fafc;
          padding: 1rem;
          margin-bottom: 0.75rem;
          border-radius: 5px;
          display: grid;
          grid-template-columns: 200px 1fr auto;
          gap: 1rem;
          align-items: center;
        }

        .signal-time {
          color: #718096;
          font-size: 0.875rem;
        }

        .signal-message {
          color: #2d3748;
        }
      `}</style>
    </div>
  );
}

export default IncidentDetail;
