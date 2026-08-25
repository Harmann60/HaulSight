import { useEffect } from 'react';
import { connectWebSocket, onMessage, disconnectWebSocket } from './api/websocket';
import { useVehicleStore } from './stores/vehicleStore';
import { useAlertStore } from './stores/alertStore';
import { useSystemStore } from './stores/systemStore';
import { fetchRoadGraph, fetchBeacons } from './api/client';
import Header from './components/layout/Header';
import MainLayout from './components/layout/MainLayout';

export default function App() {
  const setVehicles = useVehicleStore((s) => s.setVehicles);
  const setActiveAlerts = useAlertStore((s) => s.setActiveAlerts);
  const addAlert = useAlertStore((s) => s.addAlert);
  const updateAlert = useAlertStore((s) => s.updateAlert);
  const removeAlert = useAlertStore((s) => s.removeAlert);
  const setWsConnected = useSystemStore((s) => s.setWsConnected);
  const setHealth = useSystemStore((s) => s.setHealth);
  const setRadarBeacons = useSystemStore((s) => s.setRadarBeacons);
  const setScenario = useSystemStore((s) => s.setScenario);

  useEffect(() => {
    connectWebSocket();

    const unsub = onMessage((msg) => {
      switch (msg.type) {
        case 'vehicle_update':
          setVehicles(msg.data);
          break;
        case 'alert_new':
          addAlert(msg.data);
          break;
        case 'alert_update':
          updateAlert(msg.data);
          break;
        case 'alert_resolved':
          removeAlert(msg.data.alert_id);
          break;
        case 'alert_update':
          setActiveAlerts(msg.data);
          break;
        case 'system_health':
          setHealth(msg.data);
          break;
        case 'radar_warning':
          console.log('[Radar Warning]', msg.data);
          break;
        case 'scenario':
          setScenario(msg.data);
          break;
        case 'ws_connected':
          setWsConnected(true);
          break;
        case 'ws_disconnected':
          setWsConnected(false);
          break;
      }
    });

    // Initial fetches
    fetchBeacons().then(setRadarBeacons).catch(console.error);

    return () => {
      unsub();
      disconnectWebSocket();
    };
  }, []);

  return (
    <div className="h-screen flex flex-col bg-cream overflow-hidden">
      <Header />
      <MainLayout />
    </div>
  );
}
