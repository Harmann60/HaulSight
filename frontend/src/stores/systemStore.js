import { create } from 'zustand';

export const useSystemStore = create((set) => ({
  wsConnected: false,
  gatewayStatus: 'unknown',
  health: {
    status: 'unknown',
    vehicles_tracked: 0,
    active_alerts: 0,
    radar_beacons_online: '0/0',
    uptime_seconds: 0,
  },
  radarBeacons: [],
  scenario: null,

  setWsConnected: (connected) => set({ wsConnected: connected }),
  setGatewayStatus: (status) => set({ gatewayStatus: status }),
  setHealth: (health) => set({ health }),
  setRadarBeacons: (beacons) => set({ radarBeacons: beacons }),
  setScenario: (scenario) => set({ scenario }),
}));
