import React, { useState } from 'react';
import { api } from '../services/api';

function RCAForm({ incidentId, onClose, onSubmit }) {
  const [formData, setFormData] = useState({
    root_cause_category: '',
    fix_applied: '',
    prevention_steps: '',
    start_time: '',
    end_time: ''
  });

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const categories = [
    'Infrastructure Failure',
    'Software Bug',
    'Configuration Error',
    'Network Issue',
    'Resource Exhaustion',
    'Security Incident',
    'Human Error',
    'Third-party Service',
    'Other'
  ];

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      // Validate dates
      const start = new Date(formData.start_time);
      const end = new Date(formData.end_time);

      if (end <= start) {
        throw new Error('End time must be after start time');
      }

      await api.createRCA(incidentId, formData);
      onSubmit();
    } catch (err) {
      setError(err.message || 'Failed to submit RCA');
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>📝 Submit Root Cause Analysis</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit}>
          {error && <div className="error">{error}</div>}

          <div className="form-group">
            <label htmlFor="root_cause_category">Root Cause Category *</label>
            <select
              id="root_cause_category"
              name="root_cause_category"
              className="form-control"
              value={formData.root_cause_category}
              onChange={handleChange}
              required
            >
              <option value="">Select a category...</option>
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="start_time">Incident Start Time *</label>
            <input
              type="datetime-local"
              id="start_time"
              name="start_time"
              className="form-control"
              value={formData.start_time}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="end_time">Incident End Time *</label>
            <input
              type="datetime-local"
              id="end_time"
              name="end_time"
              className="form-control"
              value={formData.end_time}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="fix_applied">Fix Applied *</label>
            <textarea
              id="fix_applied"
              name="fix_applied"
              className="form-control"
              value={formData.fix_applied}
              onChange={handleChange}
              placeholder="Describe the fix that was applied to resolve this incident..."
              required
              rows="4"
            />
          </div>

          <div className="form-group">
            <label htmlFor="prevention_steps">Prevention Steps *</label>
            <textarea
              id="prevention_steps"
              name="prevention_steps"
              className="form-control"
              value={formData.prevention_steps}
              onChange={handleChange}
              placeholder="Describe steps to prevent this incident from happening again..."
              required
              rows="4"
            />
          </div>

          <div className="form-actions">
            <button 
              type="button" 
              className="btn btn-secondary"
              onClick={onClose}
              disabled={submitting}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="btn btn-success"
              disabled={submitting}
            >
              {submitting ? 'Submitting...' : 'Submit RCA & Close Incident'}
            </button>
          </div>
        </form>

        <style jsx>{`
          .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
          }

          .modal-content {
            background: white;
            border-radius: 8px;
            padding: 2rem;
            max-width: 600px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
          }

          .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid #e2e8f0;
          }

          .modal-header h2 {
            margin: 0;
          }

          .close-btn {
            background: none;
            border: none;
            font-size: 2rem;
            cursor: pointer;
            color: #718096;
            padding: 0;
            width: 30px;
            height: 30px;
            line-height: 1;
          }

          .close-btn:hover {
            color: #2d3748;
          }

          .form-actions {
            display: flex;
            gap: 1rem;
            justify-content: flex-end;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #e2e8f0;
          }
        `}</style>
      </div>
    </div>
  );
}

export default RCAForm;
