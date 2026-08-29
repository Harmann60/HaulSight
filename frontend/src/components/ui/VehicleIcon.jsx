import { Truck, Tractor, Drill, Droplets, Bus, Car } from 'lucide-react';

const ICON_MAP = {
  dumper: Truck,
  grader: Tractor,
  excavator: Tractor,
  drill: Drill,
  water_tanker: Droplets,
  bus: Bus,
  light_vehicle: Car,
};

export default function VehicleIcon({ type, size = 14, className }) {
  const Icon = ICON_MAP[type] || Truck;
  return <Icon size={size} className={className} strokeWidth={1.75} />;
}
