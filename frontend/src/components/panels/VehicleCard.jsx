import StatusBadge from '../ui/StatusBadge';
import RiskBadge from '../ui/RiskBadge';
import { VEHICLE_TYPE_ICONS } from '../../styles/theme';

export default function VehicleCard({ vehicle }) {
  const icon = VEHICLE_TYPE_ICONS[vehicle.vehicle_type] || VEHICLE_TYPE_ICONS.unknown;

  return (
    <div className={`px-4 py-3 border-b border-cream-dark/50 hover:bg-cream/30 transition-colors ${
      vehicle.risk_level === 'CRITICAL' ? 'bg-red-50 animate-pulse-critical' :
      vehicle.risk_level === 'WARNING' ? 'bg-orange-50/50' : ''
    }`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-lg">{icon}</span>
          <div>
            <div className="font-bold text-sm text-brown">{vehicle.vehicle_id}</div>
            <div className="text-xs text-brown/50">{vehicle.vehicle_type}</div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <StatusBadge status={vehicle.state} />
          <RiskBadge level={vehicle.risk_level} />
        </div>
      </div>

      <div className="mt-2 grid grid-cols-3 gap-2 text-xs">
        <div>
          <span className="text-brown/40">Speed</span>
          <div className="font-semibold text-brown">{vehicle.speed?.toFixed(1)} km/h</div>
        </div>
        <div>
          <span className="text-brown/40">GPS</span>
          <div className={`font-semibold ${vehicle.gps_quality === 'poor' ? 'text-orange' : 'text-brown'}`}>
            {vehicle.gps_quality}
          </div>
        </div>
        <div>
          <span className="text-brown/40">Segment</span>
          <div className="font-semibold text-brown text-[10px]">{vehicle.current_segment || '—'}</div>
        </div>
      </div>

      {vehicle.risk_reason && vehicle.risk_level !== 'SAFE' && (
        <div className="mt-2 text-[11px] text-brown/70 bg-orange/5 px-2 py-1 rounded border border-orange/10">
          {vehicle.risk_reason}
        </div>
      )}
    </div>
  );
}
