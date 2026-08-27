<div align="center">

# 🏔️ HaulSight

### Smart Mine Vehicle Safety & Collision Risk Monitoring System

**Smart India Hackathon 2026**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![Tailwind](https://img.shields.io/badge/Tailwind-4-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

</div>

---

## 🎯 Problem

In open-cast iron ore mines, dense fog severely limits visibility on haul roads. Drivers cannot see approaching vehicles, blind corners, or stopped hazards early enough. This leads to collisions, injuries, and operational downtime.

**HaulSight** provides an additional safety layer by tracking equipped vehicles, modelling the mine's haul-road network, calculating collision risk in real time, and generating targeted warnings — even when GPS or network connectivity fails.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     HaulSight Architecture                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────────┐  │
│  │   Vehicle    │───▶│   Roadside   │───▶│   Control Room      │ │
│  │   Unit       │LoRa│   Gateway    │API │   Backend           │ │
│  │  (GPS+IMU)   │    │  (ESP32)     │    │  (FastAPI+SQLite)   │ │
│  └─────────────┘    └──────────────┘    └───────── ┬───────────┘ │
│                                                    │             │
│                                      ┌─────────────┼───────────┐ │
│                                      │  WebSocket  │ REST API  │ │
│                                      ▼             ▼           │ │
│                              ┌─────────────────────────────┐   │ │
│                              │      Control Room           │   │ │
│                              │      Dashboard              │   │ │
│                              │  (React + Leaflet + Tailwind│   │ │
│                              └─────────────────────────────┘   │ │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │          Independent Radar Fallback (LoRa-free)          │    │
│  │    Blind Corner Beacons → Local Visual + Audible Alert   │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🗺️ **Live Mine Map** | Interactive Leaflet map showing haul roads, blind corners, and vehicle positions |
| 🚛 **Vehicle Tracking** | Real-time position, speed, heading, and status for all equipped vehicles |
| ⚠️ **Collision Risk Engine** | Deterministic pairwise evaluation using TTC (time-to-conflict) and closing distance |
| 🔔 **Targeted Alerts** | Alerts identify specific vehicle pairs and explain WHY a risk was generated |
| 📡 **Radar Fallback** | Independent radar beacons at blind corners detect non-equipped vehicles |
| 📉 **State Machine** | Vehicles transition through LIVE → STALE → OFFLINE with configurable thresholds |
| 🔄 **Anti-Oscillation** | Hysteresis and debouncing prevent rapid SAFE↔WARNING flickering |
| 🎮 **Demo Scenarios** | 3 scripted scenarios for live demonstration |
| ⚙️ **Configurable** | All thresholds tunable via YAML config file |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- pip
- npm

### 1. Clone the repository

```bash
git clone https://github.com/your-team/haulshight.git
cd haulshight
```

### 2. Start the Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Backend runs at **http://localhost:8000**

### 3. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard runs at **http://localhost:5173**

> The frontend proxies API and WebSocket requests to the backend automatically.

---

## 🎮 Demo Scenarios

Once both servers are running, open the dashboard and use the scenario buttons in the header:

| Button | Scenario | What Happens |
|--------|----------|--------------|
| **Scenario 1** | Normal Operation | Two vehicles approach a blind corner, risk escalates SAFE → CAUTION → WARNING → CRITICAL |
| **Scenario 2** | Network Failure | Gateway connectivity drops, dashboard shows degraded state, radar continues working |
| **Scenario 3** | Non-Equipped Vehicle | Radar detects an unknown vehicle at a blind corner, generates local warning |
| **Reset** | Restore Normal | All systems return to normal operation |

---

## 📁 Project Structure

```
haulshight/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Configuration loader
│   │   ├── database.py          # SQLite connection + schema
│   │   ├── models.py            # Pydantic data models
│   │   ├── state.py             # In-memory vehicle state store
│   │   ├── api/
│   │   │   ├── vehicles.py      # Vehicle endpoints
│   │   │   ├── roads.py         # Road graph endpoints
│   │   │   ├── alerts.py        # Alert endpoints
│   │   │   ├── radar.py         # Radar endpoints
│   │   │   └── websocket.py     # WebSocket broadcaster
│   │   ├── services/
│   │   │   ├── telemetry.py     # Telemetry ingestion + validation
│   │   │   ├── vehicle_state.py # State machine transitions
│   │   │   ├── risk_engine.py   # Pairwise collision risk
│   │   │   ├── alert_manager.py # Alert lifecycle + debounce
│   │   │   ├── radar_service.py # Radar beacon management
│   │   │   ├── stale_detector.py# Background stale/offline check
│   │   │   └── road_graph.py    # Road graph in-memory model
│   │   └── simulator/
│   │       ├── vehicle_sim.py   # Vehicle telemetry simulator
│   │       ├── radar_sim.py     # Radar detection simulator
│   │       └── scenarios.py     # Demo scenario scripts
│   ├── data/
│   │   ├── mine_graph.json      # Road network definition
│   │   └── default_config.yaml  # Configurable thresholds
│   ├── requirements.txt
│   └── run.py                   # Entry point
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Root component + WS setup
│   │   ├── api/
│   │   │   ├── client.js        # REST API helpers
│   │   │   └── websocket.js     # WebSocket manager
│   │   ├── stores/              # Zustand state stores
│   │   ├── components/
│   │   │   ├── layout/          # Header, MainLayout
│   │   │   ├── map/             # MineMap, VehicleMarker, RadarBeaconMarker
│   │   │   ├── panels/          # VehicleList, AlertPanel, SystemHealth
│   │   │   └── ui/              # StatusBadge, RiskBadge
│   │   └── styles/theme.js     # Color palette
│   ├── vite.config.js
│   └── package.json
└── README.md
```

---

## ⚙️ Configuration

All thresholds are in `backend/data/default_config.yaml`:

```yaml
# Vehicle state detection
stale_threshold_seconds: 10      # No telemetry for this → STALE
offline_threshold_seconds: 30    # No telemetry for this → OFFLINE

# Risk engine thresholds
ttc_critical_seconds: 5.0        # Time-to-conflict for CRITICAL
ttc_warning_seconds: 10.0        # Time-to-conflict for WARNING
ttc_caution_seconds: 15.0        # Time-to-conflict for CAUTION
dist_critical_meters: 20.0       # Distance for CRITICAL
dist_warning_meters: 50.0        # Distance for WARNING
dist_caution_meters: 100.0       # Distance for CAUTION

# Alert debouncing
risk_debounce_ticks: 3           # Ticks before alert fires
risk_downgrade_ticks: 6          # Ticks before alert resolves
blind_corner_threshold_multiplier: 0.7  # Tighter thresholds at blind corners
```

---

## 🧠 Risk Engine Logic

HaulSight does **not** use ML for collision detection. It uses deterministic, explainable rule-based logic:

```
For each vehicle pair (A, B):
  1. Are they on the same or connected road segments?
  2. Are they heading toward each other? (closing speed > 0)
  3. Calculate time-to-conflict (TTC) = distance / closing_speed
  4. Compare TTC against thresholds:
       TTC < 5s  → CRITICAL
       TTC < 10s → WARNING
       TTC < 15s → CAUTION
  5. Apply blind-corner multiplier (30% tighter)
  6. Apply hysteresis (immediate upgrade, gradual downgrade)
```

Every alert includes a human-readable reason explaining the risk.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/telemetry` | Ingest vehicle telemetry |
| `GET` | `/api/v1/vehicles` | List all vehicles with live state |
| `GET` | `/api/v1/roads` | Full road graph |
| `GET` | `/api/v1/alerts` | Active alerts |
| `GET` | `/api/v1/alerts/history` | Alert history |
| `GET` | `/api/v1/radar/beacons` | Radar beacon status |
| `POST` | `/api/v1/radar/detections` | Report radar detection |
| `POST` | `/api/v1/scenario/{name}` | Trigger demo scenario |
| `GET` | `/api/v1/health` | System health |
| `WS` | `/ws` | Real-time updates |

---

## 🎨 Design System

| Color | Hex | Usage |
|-------|-----|-------|
| Primary Blue | `#2FA4D7` | Actions, normal states, SAFE risk |
| Warm Cream | `#F5E9D8` | Backgrounds, surfaces |
| Dark Brown | `#3E2C23` | Text, structural elements |
| Orange | `#E76F2E` | Warnings, CAUTION risk |
| Red | `#DC2626` | CRITICAL risk |

Risk badges maintain semantic meaning regardless of theme.

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, Vite 8, Tailwind CSS 4, Zustand |
| Map | React-Leaflet + OpenStreetMap |
| Backend | Python 3.11+, FastAPI, aiosqlite |
| Database | SQLite |
| Real-time | WebSocket (FastAPI native) |
| Communication | REST + WebSocket |
| Hardware Interface | Modular telemetry API (LoRa/ESP32 ready) |

---

## 📝 Edge Cases Handled

- **GPS Jumps** — Rejects impossible position changes
- **Duplicate Packets** — Deduplication via message ID
- **Out-of-Order Packets** — Sequence number validation
- **Missing Telemetry** — LIVE → STALE → OFFLINE state machine
- **Stopped Vehicles** — Treated as static hazards, not ignored
- **Non-Equipped Vehicles** — Radar-only detection at blind corners
- **Alert Oscillation** — Hysteresis prevents rapid flickering
- **GPS Degradation** — Marked as DEGRADED, conservative thresholds
- **Malformed Packets** — Rejected safely, logged
- **Road Changes** — Graph is JSON-configurable

---

## 🧪 Testing the Backend

```bash
# Test health endpoint
curl http://localhost:8000/api/v1/health

# List tracked vehicles
curl http://localhost:8000/api/v1/vehicles

# Get road graph
curl http://localhost:8000/api/v1/roads

# Trigger scenario
curl -X POST http://localhost:8000/api/v1/scenario/1
```

---

## 👥 Team

Built for **Smart India Hackathon 2026**

| Name | Role | Department |
|------|------|-------------|
| Priyansha Gour (Captain) |  |Electronics and Telecommunication Engineering (E&TC)|
| Dhakshayini Usha R |  | Electronics and Telecommunication Engineering (E&TC) |
| Mishree Kalaria|  |Electronics and Telecommunication Engineering (E&TC)|
| Yash Rastogi |  | Electronics and Telecommunication Engineering (E&TC) |
| Yash Pratap Singh |  | Electronics and Telecommunication Engineering (E&TC) |
| Harman |  |Computer Science Engineering Student (CSE) |



---

## 📄 License

MIT License

---

<div align="center">

**HaulSight** — Because every miner deserves to go home safe.

</div>
