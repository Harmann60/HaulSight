import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Polyline, CircleMarker, Popup, useMap } from 'react-leaflet';
import { fetchRoadGraph } from '../../api/client';
import { useVehicleStore } from '../../stores/vehicleStore';
import { useSystemStore } from '../../stores/systemStore';
import VehicleMarker from './VehicleMarker';
import RadarBeaconMarker from './RadarBeaconMarker';
import HotspotLayer from './HotspotLayer';

const MINE_CENTER = [22.2540, 85.8360];
const DEFAULT_ZOOM = 15;

function MapUpdater({ vehicles }) {
  const map = useMap();
  return null;
}

export default function MineMap() {
  const [roadGraph, setRoadGraph] = useState({ nodes: [], segments: [] });
  const vehicles = useVehicleStore((s) => s.vehicles);
  const radarBeacons = useSystemStore((s) => s.radarBeacons);

  useEffect(() => {
    fetchRoadGraph().then(setRoadGraph).catch(console.error);
  }, []);

  const segmentColor = (seg) => {
    if (!seg.is_active) return '#9CA3AF';
    if (seg.blind_corner) return '#E76F2E';
    return '#3E2C23';
  };

  return (
    <MapContainer
      center={MINE_CENTER}
      zoom={DEFAULT_ZOOM}
      className="h-full w-full"
      zoomControl={true}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* Road segments */}
      {roadGraph.segments.map((seg) => (
        <Polyline
          key={seg.segment_id}
          positions={[
            [seg.start_lat, seg.start_lon],
            [seg.end_lat, seg.end_lon],
          ]}
          pathOptions={{
            color: segmentColor(seg),
            weight: seg.blind_corner ? 5 : 3,
            dashArray: seg.blind_corner ? '8, 6' : null,
            opacity: seg.is_active ? 0.9 : 0.4,
          }}
        >
          <Popup>
            <div className="text-sm font-sans">
              <strong>{seg.segment_id}</strong><br />
              Speed limit: {seg.speed_limit} km/h<br />
              Width: {seg.width}m · Gradient: {seg.gradient}%<br />
              {seg.blind_corner && <span className="text-orange font-semibold">Blind corner</span>}
            </div>
          </Popup>
        </Polyline>
      ))}

      {/* Blind corner zones */}
      {roadGraph.segments
        .filter((s) => s.blind_corner)
        .map((seg) => {
          const centerLat = (seg.start_lat + seg.end_lat) / 2;
          const centerLon = (seg.start_lon + seg.end_lon) / 2;
          return (
            <CircleMarker
              key={`zone-${seg.segment_id}`}
              center={[centerLat, centerLon]}
              radius={25}
              pathOptions={{
                color: '#E76F2E',
                fillColor: '#E76F2E',
                fillOpacity: 0.1,
                weight: 1,
                dashArray: '4, 4',
              }}
            />
          );
        })}

      {/* Node markers */}
      {roadGraph.nodes.map((node) => (
        <CircleMarker
          key={node.node_id}
          center={[node.latitude, node.longitude]}
          radius={4}
          pathOptions={{
            color: node.node_type === 'blind_corner' ? '#E76F2E' : '#3E2C23',
            fillColor: node.node_type === 'blind_corner' ? '#E76F2E' : '#3E2C23',
            fillOpacity: 0.8,
          }}
        >
          <Popup>
            <div className="text-sm">
              <strong>{node.name || node.node_id}</strong><br />
              Type: {node.node_type}
            </div>
          </Popup>
        </CircleMarker>
      ))}

      {/* Radar beacons */}
      {radarBeacons.map((beacon) => (
        <RadarBeaconMarker key={beacon.beacon_id} beacon={beacon} />
      ))}

      {/* Vehicle markers */}
      {vehicles
        .filter((v) => v.latitude !== 0 && v.longitude !== 0)
        .map((vehicle) => (
          <VehicleMarker key={vehicle.vehicle_id} vehicle={vehicle} />
        ))}

      {/* AI risk-hotspot layer */}
      <HotspotLayer segments={roadGraph.segments} />

      <MapUpdater vehicles={vehicles} />
    </MapContainer>
  );
}
