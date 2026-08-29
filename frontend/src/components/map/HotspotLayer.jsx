import { CircleMarker, Tooltip } from 'react-leaflet';
import { useAIStore } from '../../stores/aiStore';

const LEVEL_COLOR = {
  CRITICAL: 'rgba(220,38,38,0.55)',
  HIGH: 'rgba(231,111,46,0.45)',
  MODERATE: 'rgba(231,111,46,0.25)',
  LOW: 'rgba(47,164,215,0.2)',
};

export default function HotspotLayer({ segments }) {
  const hotspots = useAIStore((s) => s.hotspots);
  const zones = hotspots.zones || [];

  if (!zones.length) return null;

  return zones.map((zone) => {
    // Find the matching segment to position the hotspot marker
    const seg = segments.find((s) => s.segment_id === zone.segment_id);
    if (!seg) return null;
    const centerLat = (seg.start_lat + seg.end_lat) / 2;
    const centerLon = (seg.start_lon + seg.end_lon) / 2;
    const radius = 10 + (zone.score || 0) * 28;
    const color = LEVEL_COLOR[zone.level] || LEVEL_COLOR.LOW;

    return (
      <CircleMarker
        key={`hotspot-${zone.segment_id}`}
        center={[centerLat, centerLon]}
        radius={radius}
        pathOptions={{
          color: 'rgba(220,38,38,0.6)',
          fillColor: color,
          fillOpacity: 0.6,
          weight: 2,
        }}
      >
        <Tooltip opacity={0.95}>
          <div className="text-sm min-w-[150px]">
            <div className="font-bold">⚠ {zone.level} RISK ZONE</div>
            <div className="text-xs text-gray-600">{zone.segment_id}</div>
            <div className="mt-1 text-xs">Alerts: <b>{zone.alerts}</b></div>
            <div className="text-xs">Critical: <b>{zone.critical}</b></div>
            <div className="text-xs">Top risk: <b>{zone.highest_risk_shift} shift</b></div>
          </div>
        </Tooltip>
      </CircleMarker>
    );
  });
}
