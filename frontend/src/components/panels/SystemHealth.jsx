import { useSystemStore } from '../../stores/systemStore';
import { VisibilityChip } from '../ai/VisibilityChip';

export default function SystemHealth() {
  const health = useSystemStore((s) => s.health);
  const wsConnected = useSystemStore((s) => s.wsConnected);

  const items = [
    {
      label: 'Gateway',
      value: health.gateway_status || 'unknown',
      ok: health.gateway_status === 'online',
      degraded: health.gateway_status === 'degraded',
    },
    {
      label: 'Backend',
      value: health.status || 'unknown',
      ok: health.status === 'ok',
    },
    {
      label: 'Radar',
      value: health.radar_beacons_online || '0/0',
      ok: true,
    },
    {
      label: 'WebSocket',
      value: wsConnected ? 'Connected' : 'Disconnected',
      ok: wsConnected,
    },
  ];

  return (
    <div className="bg-white rounded-xl shadow-md border border-cream-dark px-4 py-3 flex items-center gap-6">
      <span className="text-xs font-bold text-brown/40 uppercase tracking-wider">System</span>
      {items.map((item) => (
        <div key={item.label} className="flex items-center gap-2 text-xs">
          <span
            className={`w-2 h-2 rounded-full ${
              item.ok ? 'bg-green-500' : item.degraded ? 'bg-yellow-500' : 'bg-red-500'
            }`}
          />
          <span className="text-brown/60">{item.label}</span>
          <span className="font-semibold text-brown">{item.value}</span>
        </div>
      ))}
      <div className="ml-auto flex items-center gap-3">
        <VisibilityChip />
        <div className="text-xs text-brown/40">
          Vehicles: {health.vehicles_tracked || 0} • Alerts: {health.active_alerts || 0}
        </div>
      </div>
    </div>
  );
}
