import { CircleMarker, Popup } from 'react-leaflet';

export default function RadarBeaconMarker({ beacon }) {
  const isOnline = beacon.status === 'online';
  const color = isOnline ? '#2FA4D7' : '#9CA3AF';

  return (
    <>
      <CircleMarker
        center={[beacon.latitude, beacon.longitude]}
        radius={isOnline ? 14 : 10}
        pathOptions={{
          color: color,
          fillColor: color,
          fillOpacity: isOnline ? 0.12 : 0.1,
          weight: 1,
          dashArray: '3, 3',
        }}
        className={isOnline ? 'radar-pulse' : ''}
      />
      <CircleMarker
        center={[beacon.latitude, beacon.longitude]}
        radius={6}
        pathOptions={{
          color: '#fff',
          fillColor: color,
          fillOpacity: 0.85,
          weight: 2,
        }}
      />
      <Popup>
        <div className="text-sm font-sans">
          <div className="font-bold">{beacon.beacon_id}</div>
          <div className="text-xs text-gray-500">Node: {beacon.node_id}</div>
          <div className="text-xs mt-1">
            Status: <span className={isOnline ? 'text-green-600 font-semibold' : 'text-red-500'}>{beacon.status}</span>
          </div>
          {beacon.last_heartbeat && (
            <div className="text-xs text-gray-400">Last heartbeat: {new Date(beacon.last_heartbeat).toLocaleTimeString()}</div>
          )}
        </div>
      </Popup>
    </>
  );
}
