
# 🚨 Zeotap IMS - Incident Management System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2.0-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)](https://prometheus.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

> **Production-grade incident management system for distributed infrastructure**  
> Zeotap Infrastructure/SRE Intern Assignment 2026

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [API Documentation](#-api-documentation)
- [Monitoring](#-monitoring)
- [Screenshots](#-screenshots)

---

## 🎯 Overview

Zeotap IMS is a scalable incident management system designed for monitoring distributed infrastructure with:

- 🚀 High-throughput signal ingestion (10,000+ signals/second)
- 🧠 Intelligent incident grouping (debouncing)
- 🔄 State machine-based workflow
- 📊 Real-time monitoring (Prometheus + Grafana)

---

## ✨ Features

| Feature | Description | Status |
|---------|-------------|--------|
| **Signal Ingestion** | 10K signals/second | ✅ |
| **Debouncing** | 10-second windows | ✅ |
| **State Machine** | Lifecycle management | ✅ |
| **Monitoring** | Prometheus + Grafana | ✅ |
| **API Docs** | Interactive Swagger UI | ✅ |

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- 4GB RAM minimum

### Installation

\`\`\`bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/zeotap-ims.git
cd zeotap-ims

# Start all services
docker-compose up -d

# Generate test data
cd scripts
python3 create_realistic_incidents.py
\`\`\`

### Access Points

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **API Docs** | http://localhost:8000/docs |
| **Prometheus** | http://localhost:9090 |
| **Grafana** | http://localhost:3001 |

---

## 🏗️ Architecture

\`\`\`
┌─────────┐    ┌──────────┐    ┌────────────┐
│ Signals │───▶│ Processor│───▶│ Debouncing │
└─────────┘    └──────────┘    └────────────┘
                                      │
                                      ▼
┌─────────┐    ┌──────────┐    ┌────────────┐
│ Alerts  │◀───│ Work Items│◀───│  Groups    │
└─────────┘    └──────────┘    └────────────┘
      │              │
      ▼              ▼
┌──────────────────────┐
│ Prometheus + Grafana │
└──────────────────────┘
\`\`\`

**Data Flow:**
1. Signals → Async Processing
2. Debouncing (10s windows)
3. Incident Creation
4. State Machine Transitions
5. Prometheus Metrics
6. Grafana Visualization

---

## 📚 API Documentation

### Swagger UI

Access interactive API docs: http://localhost:8000/docs

### Key Endpoints

**1. Ingest Signal**
\`\`\`bash
POST /api/signals
Content-Type: application/json

{
  "component_id": "RDBMS_MASTER_01",
  "error_message": "Connection timeout",
  "severity": "CRITICAL"
}
\`\`\`

**2. List Incidents**
\`\`\`bash
GET /api/incidents?state=OPEN&severity=CRITICAL
\`\`\`

**3. Get Incident**
\`\`\`bash
GET /api/incidents/{id}
\`\`\`

**4. Update State**
\`\`\`bash
PATCH /api/incidents/{id}/state?new_state=INVESTIGATING
\`\`\`

---

## 📊 Monitoring

### Prometheus Metrics

Access: http://localhost:9090

**Available Metrics:**
- \`ims_signals_total\` - Total signals ingested
- \`ims_incidents_total\` - Total incidents created
- \`ims_active_incidents\` - Active incidents
- \`ims_buffer_size\` - Signal buffer size

**Sample Queries:**
\`\`\`promql
# Incident creation rate
rate(ims_incidents_total[5m]) * 60

# Signal ingestion rate
rate(ims_signals_total[1m])

# Active critical incidents
ims_active_incidents{severity="CRITICAL"}
\`\`\`

### Grafana Dashboards

Access: http://localhost:3001  
Login: admin/admin

Pre-configured dashboards for:
- Signal ingestion rate
- Active incidents
- API performance
- Buffer utilization

---

## 📸 Screenshots

### Frontend Dashboard
Real-time incident monitoring with filters

### Swagger UI
Beautiful interactive API documentation

### Prometheus
Metrics queries and visualization

### Grafana
Pre-configured monitoring dashboards

*All screenshots available in: \`docs/screenshots/\`*

---

## 🛠️ Tech Stack

**Backend:**
- FastAPI 0.109.0
- Python 3.11+
- SQLAlchemy
- Prometheus Client

**Frontend:**
- React 18.2.0
- Inline CSS

**Infrastructure:**
- Docker Compose
- Prometheus
- Grafana

---

## 🎨 Design Patterns

### Strategy Pattern (Alerting)

| Component | Severity | Priority | SLA |
|-----------|----------|----------|-----|
| RDBMS_* | CRITICAL | P0 | 15 min |
| API_* | CRITICAL | P0 | 15 min |
| CACHE_* | HIGH | P1 | 1 hour |

### State Pattern (Lifecycle)

\`\`\`
OPEN → INVESTIGATING → RESOLVED → CLOSED
  ↑           ↓             ↓
  └───────────┘      (RCA Required)
\`\`\`

---

## 📦 Project Structure

\`\`\`
zeotap-ims/
├── backend/
│   ├── src/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── metrics.py
│   │   └── api/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   └── App.js
│   ├── Dockerfile
│   └── package.json
├── scripts/
│   └── create_realistic_incidents.py
├── docker-compose.yml
├── prometheus.yml
└── README.md
\`\`\`

---

## 👨‍💻 Author

**Afreen Ansari**  
© 2026 Infrastructure Monitoring Platform 

- GitHub: (https://github.com/afreenans)
- Email: afreenansari3107@gmail.com

---

## 📄 License

MIT License

---

## 🙏 Acknowledgments

- FastAPI for async framework
- React for UI library
- Prometheus & Grafana for monitoring
- Docker for containerization

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

Built with ❤️ for 

</div>
FINALREADME
