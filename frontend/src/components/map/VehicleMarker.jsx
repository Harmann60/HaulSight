import { CircleMarker, Popup } from 'react-leaflet';
import { RISK_COLORS, STATE_COLORS } from '../../styles/theme';

const SIZE_MAP = {
  SAFE: 11,
  CAUTION: 13,
  WARNING: 15,
  CRITICAL: 17,
};

export default function VehicleMarker({ vehicle }) {
  const riskColor = RISK_COLORS[vehicle.risk_level] || RISK_COLORS.SAFE;
  const stateColor = STATE_COLORS[vehicle.state] || STATE_COLORS.UNKNOWN;
  const size = SIZE_MAP[vehicle.risk_level] || 11;

  return (
    <>
      {vehicle.risk_level === 'CRITICAL' && (
        <CircleMarker
          center={[vehicle.latitude, vehicle.longitude]}
          radius={size + 6}
          pathOptions={{
            color: riskColor,
            fillColor: riskColor,
            fillOpacity: 0.15,
            weight: 1,
            dashArray: '3, 3',
          }}
        />
      )}
      <CircleMarker
        center={[vehicle.latitude, vehicle.longitude]}
        radius={size}
        pathOptions={{
          color: '#fff',
          fillColor: riskColor,
          fillOpacity: 0.95,
          weight: 2,
        }}
        className={vehicle.risk_level === 'CRITICAL' ? 'animate-pulse-critical' : 'vehicle-marker-cicle'}
      />
      <Popup>
        <div className="text-sm min-w-[180px] font-sans">
          <div className="font-bold text-base mb-0.5">{vehicle.vehicle_id}</div>
          <div className="text-xs text-gray-500 mb-2 capitalize">
            {vehicle.vehicle_type || 'Vehicle'} · {vehicle.is_equipped ? 'Equipped' : 'Radar-only'}
          </div>

          <div className="grid grid-cols-2 gap-1 text-xs">
            <span className="text-gray-500">State</span>
            <span className="font-semibold capitalize" style={{ color: stateColor }}>{vehicle.state}</span>

            <span className="text-gray-500">Speed</span>
            <span>{vehicle.speed != null ? `${vehicle.speed.toFixed(1)} km/h` : '—'}</span>

            <span className="text-gray-500">GPS</span>
            <span className={vehicle.gps_quality === 'poor' ? 'text-orange font-semibold' : 'capitalize'}>
              {vehicle.gps_quality || '—'}
            </span>

            <span className="text-gray-500">Risk</span>
            <span className="font-bold" style={{ color: riskColor }}>{vehicle.risk_level}</span>

            <span className="text-gray-500">Segment</span>
            <span>{vehicle.current_segment || 'N/A'}</span>
          </div>

          {vehicle.risk_reason && (
            <div className="mt-2 text-xs bg-orange/10 p-2 rounded border border-orange/20">
              {vehicle.risk_reason}
            </div>
          )}
        </div>
      </Popup>
    </>
  );
}
