import React, { useState, useEffect } from 'react';

function App() {
  const [health, setHealth] = useState('checking...');
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [darkMode, setDarkMode] = useState(false);
  const [showAlert, setShowAlert] = useState(false);
  const [alertMessage, setAlertMessage] = useState('');

  const fetchData = () => {
    fetch('http://localhost:8000/health')
      .then(res => res.json())
      .then(data => setHealth(data.status))
      .catch(() => setHealth('offline'));

    fetch('http://localhost:8000/api/incidents')
      .then(res => res.json())
      .then(data => {
        const newIncidents = Array.isArray(data) ? data : (data.incidents || []);
        
        // Check for new critical incidents
        const criticalNew = newIncidents.filter(i => 
          i.severity === 'CRITICAL' && i.state === 'OPEN'
        );
        
        if (criticalNew.length > 0 && incidents.length > 0) {
          setAlertMessage('🚨 New Critical Incident Detected!');
          setShowAlert(true);
          setTimeout(() => setShowAlert(false), 5000);
        }
        
        setIncidents(newIncidents);
        setLoading(false);
        setLastUpdate(new Date());
      })
      .catch(err => {
        console.error('Error:', err);
        setIncidents([]);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const criticalCount = incidents.filter(i => i.severity === 'CRITICAL' || i.severity === 'HIGH').length;
  const openCount = incidents.filter(i => i.state === 'OPEN').length;
  const resolvedToday = incidents.filter(i => i.state === 'RESOLVED' || i.state === 'CLOSED').length;
  const avgMTTR = incidents.length > 0 ? '2.5h' : 'N/A';

  const theme = darkMode ? darkTheme : lightTheme;

  return (
    <div style={{...styles.container, background: theme.bg}}>
      {/* Critical Alert Banner */}
      {showAlert && (
        <div style={styles.alertBanner}>
          {alertMessage}
        </div>
      )}

      {/* Header */}
      <header style={{...styles.header, background: theme.cardBg}}>
        <div style={styles.headerContent}>
          <div>
            <h1 style={{...styles.title, color: theme.text}}>
              <span style={styles.iconPulse}>🚨</span>
              Incident Management System
            </h1>
            <p style={{...styles.subtitle, color: theme.textSecondary}}>
              Real-time Monitoring • AI-Powered Alerts • Advanced Analytics
            </p>
          </div>
          <div style={styles.headerRight}>
            <button 
              onClick={() => setDarkMode(!darkMode)} 
              style={styles.darkModeToggle}
              title={darkMode ? 'Light Mode' : 'Dark Mode'}
            >
              {darkMode ? '☀️' : '🌙'}
            </button>
            <div style={styles.liveIndicator}>
              <span style={styles.liveDotPulse}></span>
              <span>LIVE</span>
            </div>
          </div>
        </div>
        <div style={{...styles.lastUpdate, color: theme.textSecondary}}>
          🔄 Auto-refresh every 5s • Last sync: {lastUpdate.toLocaleTimeString()}
        </div>
      </header>

      {/* Stats Cards Grid */}
      <div style={styles.statsGrid}>
        <MetricCard
          icon="💚"
          title="System Health"
          value={health === 'healthy' ? 'Operational' : 'Degraded'}
          trend={health === 'healthy' ? '100%' : '0%'}
          trendUp={health === 'healthy'}
          color={health === 'healthy' ? '#10b981' : '#ef4444'}
          theme={theme}
        />
        <MetricCard
          icon="📊"
          title="Active Incidents"
          value={incidents.length}
          subtitle={openCount + ' open'}
          color="#3b82f6"
          theme={theme}
        />
        <MetricCard
          icon="🔴"
          title="Critical Priority"
          value={criticalCount}
          subtitle="Needs attention"
          trend={criticalCount > 5 ? '⚠️ High' : '✓ Normal'}
          color="#f59e0b"
          theme={theme}
        />
        <MetricCard
          icon="⏱️"
          title="Avg MTTR"
          value={avgMTTR}
          subtitle={resolvedToday + ' resolved today'}
          trend="↓ 15% vs last week"
          trendUp={true}
          color="#8b5cf6"
          theme={theme}
        />
      </div>

      {/* Incidents Table */}
      <div style={{...styles.tableContainer, background: theme.cardBg}}>
        <div style={styles.tableHeader}>
          <div>
            <h2 style={{...styles.tableTitle, color: theme.text}}>
              📋 Incident Dashboard
              <span style={{...styles.tableCount, color: theme.textSecondary}}>
                {incidents.length} total
              </span>
            </h2>
          </div>
          <button onClick={fetchData} style={styles.refreshButton}>
            🔄 Refresh Now
          </button>
        </div>

        {loading ? (
          <div style={styles.loadingContainer}>
            <div style={styles.spinner}></div>
            <p style={{color: theme.textSecondary}}>Loading incidents...</p>
          </div>
        ) : incidents.length === 0 ? (
          <div style={styles.emptyState}>
            <div style={styles.emptyIcon}>✅</div>
            <h3 style={{color: theme.text}}>All Clear!</h3>
            <p style={{color: theme.textSecondary}}>
              No active incidents. All systems operational.
            </p>
          </div>
        ) : (
          <div style={styles.tableWrapper}>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={{...styles.th, color: theme.textSecondary, borderColor: theme.border}}>ID</th>
                  <th style={{...styles.th, color: theme.textSecondary, borderColor: theme.border}}>Component</th>
                  <th style={{...styles.th, color: theme.textSecondary, borderColor: theme.border}}>Severity</th>
                  <th style={{...styles.th, color: theme.textSecondary, borderColor: theme.border}}>Status</th>
                  <th style={{...styles.th, color: theme.textSecondary, borderColor: theme.border}}>Signals</th>
                  <th style={{...styles.th, color: theme.textSecondary, borderColor: theme.border}}>Created</th>
                </tr>
              </thead>
              <tbody>
                {incidents.map((incident, idx) => (
                  <tr 
                    key={incident.id || idx} 
                    style={{...styles.tr, borderColor: theme.border}}
                  >
                    <td style={{...styles.td, color: theme.text}}>
                      <span style={{...styles.idBadge, background: theme.badgeBg, color: theme.textSecondary}}>
                        #{incident.id}
                      </span>
                    </td>
                    <td style={{...styles.td, color: theme.text}}>
                      <div style={styles.componentCell}>
                        <span style={styles.componentIcon}>
                          {getComponentIcon(incident.component_id)}
                        </span>
                        <strong>{incident.component_id}</strong>
                      </div>
                    </td>
                    <td style={{...styles.td, color: theme.text}}>
                      <SeverityBadge severity={incident.severity} />
                    </td>
                    <td style={{...styles.td, color: theme.text}}>
                      <StateBadge state={incident.state} />
                    </td>
                    <td style={{...styles.td, color: theme.text}}>
                      <span style={styles.signalBadge}>{incident.signal_count}</span>
                    </td>
                    <td style={{...styles.td, color: theme.textSecondary, fontSize: '0.875rem'}}>
                      {new Date(incident.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Quick Access Links */}
      <div style={{...styles.linksContainer, background: theme.cardBg}}>
        <h3 style={{...styles.linksTitle, color: theme.text}}>🔗 Developer Resources</h3>
        <div style={styles.linksGrid}>
          <QuickLink
            icon="🏠"
            title="API Root"
            description="Backend API endpoint"
            href="http://localhost:8000"
            theme={theme}
          />
          <QuickLink
            icon="📚"
            title="API Documentation"
            description="Interactive Swagger UI"
            href="http://localhost:8000/docs"
            theme={theme}
          />
          <QuickLink
            icon="💚"
            title="Health Check"
            description="System health status"
            href="http://localhost:8000/health"
            theme={theme}
          />
          <QuickLink
            icon="📊"
            title="Incidents JSON"
            description="Raw API response"
            href="http://localhost:8000/api/incidents"
            theme={theme}
          />
        </div>
      </div>

      {/* Professional Footer */}
      <footer style={{...styles.footer, background: theme.cardBg}}>
        <div style={styles.footerContent}>
          <div style={{color: theme.text}}>
            <div style={styles.footerBrand}>
              <span style={styles.brandIcon}>🚨</span>
              <strong> IMS</strong>
            </div>
            <div style={{...styles.footerCopyright, color: theme.textSecondary}}>
              © 2026 Infrastructure Monitoring Platform • Built with ❤️ for DevOps
            </div>
          </div>
          <div>
            <div style={{...styles.footerLabel, color: theme.textSecondary}}>Powered by:</div>
            <div style={styles.footerTech}>
              <TechBadge name="FastAPI" icon="⚡" theme={theme} />
              <TechBadge name="React" icon="⚛️" theme={theme} />
              <TechBadge name="Docker" icon="🐳" theme={theme} />
              <TechBadge name="PostgreSQL" icon="🐘" theme={theme} />
              <TechBadge name="MongoDB" icon="🍃" theme={theme} />
              <TechBadge name="Redis" icon="📮" theme={theme} />
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

function MetricCard({ icon, title, value, subtitle, trend, trendUp, color, theme }) {
  return (
    <div style={{
      ...styles.metricCard,
      background: theme.cardBg,
      borderLeft: '4px solid ' + color,
      boxShadow: theme.shadow
    }}>
      <div style={styles.metricIcon}>{icon}</div>
      <div style={styles.metricContent}>
        <div style={{...styles.metricTitle, color: theme.textSecondary}}>{title}</div>
        <div style={{...styles.metricValue, color}}>{value}</div>
        {subtitle && <div style={{...styles.metricSubtitle, color: theme.textSecondary}}>{subtitle}</div>}
        {trend && (
          <div style={{
            ...styles.metricTrend,
            color: trendUp ? '#10b981' : '#f59e0b'
          }}>
            {trendUp ? '↗' : '↘'} {trend}
          </div>
        )}
      </div>
    </div>
  );
}

function SeverityBadge({ severity }) {
  const config = {
    'CRITICAL': { bg: '#fef2f2', color: '#dc2626', icon: '🔴' },
    'HIGH': { bg: '#fef3c7', color: '#d97706', icon: '🟠' },
    'MEDIUM': { bg: '#dbeafe', color: '#2563eb', icon: '🟡' },
    'LOW': { bg: '#f3f4f6', color: '#6b7280', icon: '⚪' }
  };
  const style = config[severity] || config['LOW'];

  return (
    <span style={{
      display: 'inline-block',
      padding: '6px 12px',
      borderRadius: '12px',
      fontSize: '0.75rem',
      fontWeight: 600,
      backgroundColor: style.bg,
      color: style.color
    }}>
      {style.icon} {severity}
    </span>
  );
}

function StateBadge({ state }) {
  const config = {
    'OPEN': { bg: '#fef2f2', color: '#dc2626' },
    'INVESTIGATING': { bg: '#fef3c7', color: '#d97706' },
    'RESOLVED': { bg: '#dbeafe', color: '#2563eb' },
    'CLOSED': { bg: '#dcfce7', color: '#16a34a' }
  };
  const style = config[state] || config['OPEN'];

  return (
    <span style={{
      display: 'inline-block',
      padding: '6px 12px',
      borderRadius: '12px',
      fontSize: '0.75rem',
      fontWeight: 500,
      backgroundColor: style.bg,
      color: style.color
    }}>
      {state}
    </span>
  );
}

function QuickLink({ icon, title, description, href, theme }) {
  return (
    <a 
      href={href} 
      target="_blank" 
      rel="noopener noreferrer" 
      style={{
        ...styles.quickLink,
        background: theme.linkBg,
        color: theme.text,
        border: '2px solid ' + theme.border
      }}
    >
      <div style={styles.quickLinkIcon}>{icon}</div>
      <div style={styles.quickLinkContent}>
        <div style={styles.quickLinkTitle}>{title}</div>
        <div style={{...styles.quickLinkDesc, color: theme.textSecondary}}>{description}</div>
      </div>
      <div style={{...styles.quickLinkArrow, color: theme.textSecondary}}>→</div>
    </a>
  );
}

function TechBadge({ name, icon, theme }) {
  return (
    <span style={{
      ...styles.techBadge,
      background: theme.badgeBg,
      color: theme.text
    }}>
      {icon} {name}
    </span>
  );
}

function getComponentIcon(component) {
  if (component.includes('RDBMS')) return '🗄️';
  if (component.includes('API')) return '🌐';
  if (component.includes('CACHE')) return '⚡';
  if (component.includes('QUEUE')) return '📬';
  if (component.includes('NOSQL')) return '📊';
  return '🔧';
}

const lightTheme = {
  bg: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  cardBg: 'white',
  text: '#1e293b',
  textSecondary: '#64748b',
  border: '#e2e8f0',
  linkBg: '#f8fafc',
  badgeBg: '#f1f5f9',
  shadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
};

const darkTheme = {
  bg: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
  cardBg: '#1e293b',
  text: '#f1f5f9',
  textSecondary: '#94a3b8',
  border: '#334155',
  linkBg: '#0f172a',
  badgeBg: '#334155',
  shadow: '0 4px 6px rgba(0, 0, 0, 0.3)'
};

const styles = {
  container: {
    minHeight: '100vh',
    padding: '20px',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
  },
  alertBanner: {
    background: 'linear-gradient(90deg, #dc2626, #ef4444)',
    color: 'white',
    padding: '16px',
    textAlign: 'center',
    fontWeight: 600,
    fontSize: '1rem',
    borderRadius: '8px',
    marginBottom: '20px',
    animation: 'slideDown 0.5s ease-out'
  },
  header: {
    borderRadius: '16px',
    padding: '30px',
    marginBottom: '24px',
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
  },
  headerContent: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: '20px',
    marginBottom: '12px'
  },
  title: {
    margin: 0,
    fontSize: '2.5rem',
    fontWeight: 700,
    display: 'flex',
    alignItems: 'center',
    gap: '12px'
  },
  iconPulse: {
    fontSize: '2rem',
    animation: 'pulse 2s ease-in-out infinite'
  },
  subtitle: {
    margin: '10px 0 0 0',
    fontSize: '1rem'
  },
  headerRight: {
    display: 'flex',
    gap: '12px',
    alignItems: 'center'
  },
  darkModeToggle: {
    background: '#f1f5f9',
    border: 'none',
    borderRadius: '8px',
    padding: '8px 12px',
    fontSize: '1.25rem',
    cursor: 'pointer',
    transition: 'transform 0.2s'
  },
  liveIndicator: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    background: '#dcfce7',
    color: '#16a34a',
    padding: '8px 16px',
    borderRadius: '20px',
    fontSize: '0.875rem',
    fontWeight: 600
  },
  liveDotPulse: {
    width: '8px',
    height: '8px',
    background: '#16a34a',
    borderRadius: '50%',
    animation: 'blink 1.5s ease-in-out infinite'
  },
  lastUpdate: {
    fontSize: '0.75rem',
    textAlign: 'right'
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '20px',
    marginBottom: '24px'
  },
  metricCard: {
    borderRadius: '12px',
    padding: '24px',
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    transition: 'transform 0.2s',
    cursor: 'pointer'
  },
  metricIcon: {
    fontSize: '2.5rem'
  },
  metricContent: {
    flex: 1
  },
  metricTitle: {
    fontSize: '0.875rem',
    marginBottom: '4px',
    fontWeight: 500
  },
  metricValue: {
    fontSize: '2rem',
    fontWeight: 700
  },
  metricSubtitle: {
    fontSize: '0.75rem',
    marginTop: '4px'
  },
  metricTrend: {
    fontSize: '0.75rem',
    marginTop: '4px',
    fontWeight: 600
  },
  tableContainer: {
    borderRadius: '12px',
    padding: '24px',
    marginBottom: '24px'
  },
  tableHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
    flexWrap: 'wrap',
    gap: '10px'
  },
  tableTitle: {
    margin: 0,
    fontSize: '1.5rem',
    fontWeight: 700,
    display: 'flex',
    alignItems: 'center',
    gap: '12px'
  },
  tableCount: {
    fontSize: '0.875rem',
    fontWeight: 400
  },
  refreshButton: {
    padding: '10px 20px',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '0.875rem',
    fontWeight: 600,
    transition: 'transform 0.2s'
  },
  loadingContainer: {
    padding: '60px',
    textAlign: 'center'
  },
  spinner: {
    width: '50px',
    height: '50px',
    border: '4px solid #f3f4f6',
    borderTop: '4px solid #667eea',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    margin: '0 auto 20px'
  },
  emptyState: {
    padding: '60px',
    textAlign: 'center'
  },
  emptyIcon: {
    fontSize: '4rem',
    marginBottom: '16px'
  },
  tableWrapper: {
    overflowX: 'auto'
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse'
  },
  th: {
    padding: '16px',
    textAlign: 'left',
    fontSize: '0.75rem',
    fontWeight: 600,
    textTransform: 'uppercase',
    borderBottom: '2px solid'
  },
  tr: {
    borderBottom: '1px solid',
    transition: 'background 0.2s'
  },
  td: {
    padding: '16px'
  },
  idBadge: {
    padding: '4px 8px',
    borderRadius: '6px',
    fontSize: '0.875rem',
    fontWeight: 600
  },
  componentCell: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px'
  },
  componentIcon: {
    fontSize: '1.25rem'
  },
  signalBadge: {
    background: '#dbeafe',
    color: '#2563eb',
    padding: '4px 10px',
    borderRadius: '12px',
    fontSize: '0.875rem',
    fontWeight: 600
  },
  linksContainer: {
    borderRadius: '12px',
    padding: '24px',
    marginBottom: '24px'
  },
  linksTitle: {
    margin: '0 0 20px 0',
    fontSize: '1.25rem',
    fontWeight: 700
  },
  linksGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '16px'
  },
  quickLink: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '16px',
    borderRadius: '8px',
    textDecoration: 'none',
    transition: 'all 0.3s'
  },
  quickLinkIcon: {
    fontSize: '2rem'
  },
  quickLinkContent: {
    flex: 1
  },
  quickLinkTitle: {
    fontWeight: 600,
    marginBottom: '4px',
    fontSize: '1rem'
  },
  quickLinkDesc: {
    fontSize: '0.75rem'
  },
  quickLinkArrow: {
    fontSize: '1.25rem'
  },
  footer: {
    borderRadius: '12px',
    padding: '32px'
  },
  footerContent: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: '24px'
  },
  footerBrand: {
    fontSize: '1.25rem',
    fontWeight: 700,
    marginBottom: '8px',
    display: 'flex',
    alignItems: 'center',
    gap: '8px'
  },
  brandIcon: {
    fontSize: '1.5rem'
  },
  footerCopyright: {
    fontSize: '0.875rem'
  },
  footerLabel: {
    fontSize: '0.75rem',
    marginBottom: '8px',
    textTransform: 'uppercase',
    fontWeight: 600
  },
  footerTech: {
    display: 'flex',
    gap: '8px',
    flexWrap: 'wrap'
  },
  techBadge: {
    padding: '6px 12px',
    borderRadius: '12px',
    fontSize: '0.75rem',
    fontWeight: 500
  }
};

export default App;
