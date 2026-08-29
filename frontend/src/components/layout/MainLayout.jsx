import MineMap from '../map/MineMap';
import VehicleList from '../panels/VehicleList';
import AlertPanel from '../panels/AlertPanel';
import SystemHealth from '../panels/SystemHealth';
import { RadarAIPanel, ProductionPanel } from '../ai/AIPanels';

export default function MainLayout() {
  return (
    <div className="flex-1 flex overflow-hidden">
      {/* Map (primary hero, 58%) */}
      <div className="w-[58%] p-3 flex flex-col gap-3 min-w-0">
        <div className="flex-1 panel overflow-hidden">
          <div className="h-full">
            <MineMap />
          </div>
        </div>
        <SystemHealth />
      </div>

      {/* Right rail (secondary/tertiary, 42%) */}
      <div className="w-[42%] p-3 pl-0 flex flex-col gap-3 min-w-0 overflow-y-auto">
        <VehicleList />
        <AlertPanel />
        <RadarAIPanel />
        <ProductionPanel />
      </div>
    </div>
  );
}
