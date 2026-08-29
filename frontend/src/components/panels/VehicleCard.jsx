import StatusBadge from '../ui/StatusBadge';
import RiskBadge from '../ui/RiskBadge';
import VehicleIcon from '../ui/VehicleIcon';

export default function VehicleCard({ vehicle }) {
  const riskBg =
    vehicle.risk_level === 'CRITICAL' ? 'bg-red-50/60' :
    vehicle.risk_level === 'WARNING' ? 'bg-orange-50/40' : '';

  return (
    <div className={`px-4 py-3 border-b border-cream-dark/50 hover:bg-cream/40 transition-colors ${riskBg}`}>
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2.5 min-w-0">
          <span className="w-8 h-8 shrink-0 flex items-center justify-center rounded-md bg-cream text-brown/60">
            <VehicleIcon type={vehicle.vehicle_type} size={16} />
          </span>
          <div className="min-w-0">
            <div className="font-semibold text-[13px] text-brown leading-tight">
              {vehicle.vehicle_id}
            </div>
            <div className="text-[11px] text-brown/45 capitalize">{vehicle.vehicle_type}</div>
          </div>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          {vehicle.risk_level && vehicle.risk_level !== 'SAFE' && (
            <RiskBadge level={vehicle.risk_level} />
          )}
          <StatusBadge status={vehicle.state} />
        </div>
      </div>

      <div className="mt-2.5 pl-[42px] grid grid-cols-3 gap-2">
        <div className="leading-tight">
          <div className="text-[10px] text-brown/40 uppercase tracking-wide">Speed</div>
          <div className="text-[12px] font-semibold text-brown">
            {vehicle.speed != null ? `${vehicle.speed.toFixed(1)} km/h` : '—'}
          </div>
        </div>
        <div className="leading-tight">
          <div className="text-[10px] text-brown/40 uppercase tracking-wide">GPS</div>
          <div className={`text-[12px] font-semibold ${vehicle.gps_quality === 'poor' ? 'text-warning' : 'text-brown'}`}>
            {vehicle.gps_quality || '—'}
          </div>
        </div>
        <div className="leading-tight">
          <div className="text-[10px] text-brown/40 uppercase tracking-wide">Segment</div>
          <div className="text-[12px] font-medium text-brown">{vehicle.current_segment || '—'}</div>
        </div>
      </div>

      {vehicle.risk_reason && vehicle.risk_level !== 'SAFE' && (
        <div className="mt-2 pl-[42px] text-[11px] text-brown/70 border-l-2 border-orange/40 pl-3">
          {vehicle.risk_reason}
        </div>
      )}
    </div>
  );
}
