import { Truck } from 'lucide-react';
import { useVehicleStore } from '../../stores/vehicleStore';
import VehicleCard from './VehicleCard';

export default function VehicleList() {
  const vehicles = useVehicleStore((s) => s.vehicles);

  const sorted = [...vehicles].sort((a, b) => {
    const riskOrder = { CRITICAL: 0, WARNING: 1, CAUTION: 2, SAFE: 3 };
    return (riskOrder[a.risk_level] ?? 4) - (riskOrder[b.risk_level] ?? 4);
  });

  const live = vehicles.filter((v) => v.state === 'LIVE').length;
  const stale = vehicles.filter((v) => v.state === 'STALE').length;
  const offline = vehicles.filter((v) => v.state === 'OFFLINE').length;

  return (
    <div className="panel overflow-hidden">
      <div className="panel-header">
        <div className="flex items-center gap-2">
          <Truck size={15} className="text-brown/50" strokeWidth={1.75} />
          <h2 className="panel-title">Vehicles</h2>
          <span className="text-[13px] font-bold text-brown leading-none">{vehicles.length}</span>
        </div>
        <div className="flex items-center gap-3 text-[10px] font-semibold">
          <span className="status"><span className="dot dot--live" />Live {live}</span>
          <span className="status"><span className="dot dot--stale" />Stale {stale}</span>
          <span className="status"><span className="dot dot--offline" />Offline {offline}</span>
        </div>
      </div>
      <div className="max-h-[300px] overflow-y-auto">
        {sorted.length === 0 ? (
          <div className="panel-body text-center text-[12px] text-brown/40">No vehicles tracked</div>
        ) : (
          sorted.map((v) => <VehicleCard key={v.vehicle_id} vehicle={v} />)
        )}
      </div>
    </div>
  );
}
