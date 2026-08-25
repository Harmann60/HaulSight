import { CircleMarker, Popup, Tooltip } from 'react-leaflet';
import { RISK_COLORS, STATE_COLORS, VEHICLE_TYPE_ICONS } from '../../styles/theme';

const SIZE_MAP = {
  SAFE: 12,
  CAUTION: 14,
  WARNING: 16,
  CRITICAL: 18,
};

export default function VehicleMarker({ vehicle }) {
  const riskColor = RISK_COLORS[vehicle.risk_level] || RISK_COLORS.SAFE;
  const stateColor = STATE_COLORS[vehicle.state] || STATE_COLORS.UNKNOWN;
  const size = SIZE_MAP[vehicle.risk_level] || 12;
  const icon = VEHICLE_TYPE_ICONS[vehicle.vehicle_type] || VEHICLE_TYPE_ICONS.unknown;

  return (
    <CircleMarker
      center={[vehicle.latitude, vehicle.longitude]}
      radius={size}
      pathOptions={{
        color: 'white',
        fillColor: riskColor,
        fillOpacity: 0.9,
        weight: 2,
      }}
      className={vehicle.risk_level === 'CRITICAL' ? 'animate-pulse-critical' : ''}
    >
      <Tooltip
        permanent
        direction="center"
        className="!bg-transparent !border-0 !shadow-none !p-0"
      >
        <span className="text-white text-[10px] font-bold drop-shadow-md">
          {icon}
        </span>
      </Tooltip>
      <Popup>
        <div className="text-sm min-w-[180px]">
          <div className="font-bold text-base mb-1">{vehicle.vehicle_id}</div>
          <div className="text-xs text-gray-500 mb-2">
            {vehicle.vehicle_type?.toUpperCase()} • {vehicle.is_equipped ? 'Equipped' : 'Radar-Only'}
          </div>

          <div className="grid grid-cols-2 gap-1 text-xs">
            <span className="text-gray-500">State:</span>
            <span className="font-semibold" style={{ color: stateColor }}>{vehicle.state}</span>

            <span className="text-gray-500">Speed:</span>
            <span>{vehicle.speed?.toFixed(1)} km/h</span>

            <span className="text-gray-500">GPS:</span>
            <span className={vehicle.gps_quality === 'poor' ? 'text-orange font-semibold' : ''}>
              {vehicle.gps_quality}
            </span>

            <span className="text-gray-500">Risk:</span>
            <span className="font-bold" style={{ color: riskColor }}>{vehicle.risk_level}</span>

            <span className="text-gray-500">Segment:</span>
            <span className="text-xs">{vehicle.current_segment || 'N/A'}</span>
          </div>

          {vehicle.risk_reason && (
            <div className="mt-2 text-xs bg-orange/10 p-2 rounded border border-orange/20">
              {vehicle.risk_reason}
            </div>
          )}
        </div>
      </Popup>
    </CircleMarker>
  );
}
