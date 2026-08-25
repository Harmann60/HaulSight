import { useVehicleStore } from '../../stores/vehicleStore';
import VehicleCard from './VehicleCard';

export default function VehicleList() {
  const vehicles = useVehicleStore((s) => s.vehicles);

  const sorted = [...vehicles].sort((a, b) => {
    const riskOrder = { CRITICAL: 0, WARNING: 1, CAUTION: 2, SAFE: 3 };
    return (riskOrder[a.risk_level] ?? 4) - (riskOrder[b.risk_level] ?? 4);
  });

  return (
    <div className="bg-white rounded-xl shadow-md border border-cream-dark overflow-hidden">
      <div className="px-4 py-3 bg-brown/5 border-b border-cream-dark flex items-center justify-between">
        <h2 className="font-bold text-brown text-sm uppercase tracking-wider">
          Vehicles ({vehicles.length})
        </h2>
        <div className="flex gap-2 text-xs">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-green-500" /> LIVE
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-yellow-500" /> STALE
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-gray-400" /> OFF
          </span>
        </div>
      </div>
      <div className="max-h-[280px] overflow-y-auto">
        {sorted.length === 0 ? (
          <div className="p-4 text-center text-brown/40 text-sm">No vehicles tracked</div>
        ) : (
          sorted.map((v) => <VehicleCard key={v.vehicle_id} vehicle={v} />)
        )}
      </div>
    </div>
  );
}
