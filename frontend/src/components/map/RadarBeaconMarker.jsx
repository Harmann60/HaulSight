import { CircleMarker, Popup, Tooltip } from 'react-leaflet';

export default function RadarBeaconMarker({ beacon }) {
  const isOnline = beacon.status === 'online';

  return (
    <CircleMarker
      center={[beacon.latitude, beacon.longitude]}
      radius={8}
      pathOptions={{
        color: 'white',
        fillColor: isOnline ? '#2FA4D7' : '#9CA3AF',
        fillOpacity: 0.8,
        weight: 2,
      }}
    >
      <Tooltip
        permanent
        direction="center"
        className="!bg-transparent !border-0 !shadow-none !p-0"
      >
        <span className="text-white text-[9px] font-bold">📡</span>
      </Tooltip>
      <Popup>
        <div className="text-sm">
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
    </CircleMarker>
  );
}
