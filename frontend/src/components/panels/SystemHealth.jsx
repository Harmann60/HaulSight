import { Wifi, Server, Radio, Activity } from 'lucide-react';
import { useSystemStore } from '../../stores/systemStore';
import { VisibilityChip } from '../ai/VisibilityChip';

export default function SystemHealth() {
  const health = useSystemStore((s) => s.health);
  const wsConnected = useSystemStore((s) => s.wsConnected);

  const items = [
    {
      label: 'Gateway',
      value: health.gateway_status || 'unknown',
      Icon: Wifi,
      state: health.gateway_status === 'online' ? 'live' :
             health.gateway_status === 'degraded' ? 'degraded' : 'critical',
    },
    {
      label: 'Backend',
      value: health.status || 'unknown',
      Icon: Server,
      state: health.status === 'ok' ? 'live' : 'critical',
    },
    {
      label: 'Radar',
      value: health.radar_beacons_online || '0/0',
      Icon: Radio,
      state: 'live',
    },
    {
      label: 'WebSocket',
      value: wsConnected ? 'Connected' : 'Disconnected',
      Icon: Activity,
      state: wsConnected ? 'live' : 'critical',
    },
  ];

  return (
    <div className="panel px-4 py-2.5 flex items-center gap-6 overflow-x-auto">
      <span className="text-[11px] font-semibold text-brown/45 uppercase tracking-wider shrink-0">System</span>
      {items.map((item) => (
        <div key={item.label} className="flex items-center gap-2 text-xs shrink-0">
          <item.Icon size={14} className="text-brown/40" strokeWidth={1.75} />
          <span className="meta-label">{item.label}</span>
          <span className={`dot w-2 h-2 rounded-full ${
            item.state === 'live' ? 'bg-healthy' :
            item.state === 'degraded' ? 'bg-orange' : 'bg-critical'
          }`} />
          <span className="font-semibold text-brown capitalize">{item.value}</span>
        </div>
      ))}

      <div className="ml-auto flex items-center gap-3 shrink-0">
        <VisibilityChip />
        <div className="text-[11px] text-brown/45 whitespace-nowrap">
          {health.vehicles_tracked || 0} vehicles · {health.active_alerts || 0} alerts
        </div>
      </div>
    </div>
  );
}
