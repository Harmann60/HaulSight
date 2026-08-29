const API_BASE = 'https://haulsight.onrender.com';

export async function fetchVehicles() {
  const res = await fetch(`${API_BASE}/api/v1/vehicles`);
  return res.json();
}

export async function fetchRoadGraph() {
  const res = await fetch(`${API_BASE}/api/v1/roads`);
  return res.json();
}

export async function fetchActiveAlerts() {
  const res = await fetch(`${API_BASE}/api/v1/alerts`);
  return res.json();
}

export async function fetchAlertHistory(limit = 50) {
  const res = await fetch(`${API_BASE}/api/v1/alerts/history?limit=${limit}`);
  return res.json();
}

export async function fetchBeacons() {
  const res = await fetch(`${API_BASE}/api/v1/radar/beacons`);
  return res.json();
}

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/api/v1/health`);
  return res.json();
}

export async function acknowledgeAlert(alertId) {
  const res = await fetch(`${API_BASE}/api/v1/alerts/${alertId}/acknowledge`, {
    method: 'PUT',
  });
  return res.json();
}

export async function runScenario(name) {
  const res = await fetch(`${API_BASE}/api/v1/scenario/${name}`, {
    method: 'POST',
  });
  return res.json();
}

export async function fetchVisibility() {
  const res = await fetch(`${API_BASE}/api/v1/ai/visibility`);
  return res.json();
}

export async function fetchAIHotspots() {
  const res = await fetch(`${API_BASE}/api/v1/ai/hotspots`);
  return res.json();
}

export async function fetchProduction() {
  const res = await fetch(`${API_BASE}/api/v1/ai/production`);
  return res.json();
}

export async function fetchRadarAI() {
  const res = await fetch(`${API_BASE}/api/v1/ai/radar`);
  return res.json();
}
