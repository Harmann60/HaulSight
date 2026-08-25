const API_BASE = '';

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
