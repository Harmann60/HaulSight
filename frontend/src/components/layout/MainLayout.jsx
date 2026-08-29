import MineMap from '../map/MineMap';
import VehicleList from '../panels/VehicleList';
import AlertPanel from '../panels/AlertPanel';
import SystemHealth from '../panels/SystemHealth';
import { RadarAIPanel, ProductionPanel } from '../ai/AIPanels';

export default function MainLayout() {
  return (
    <div className="flex-1 flex overflow-hidden">
      {/* Map takes 60% */}
      <div className="w-[60%] p-3 flex flex-col gap-3 min-w-0">
        <div className="flex-1 rounded-xl overflow-hidden shadow-md border border-cream-dark">
          <MineMap />
        </div>
        <SystemHealth />
      </div>

      {/* Side panels take 40% */}
      <div className="w-[40%] p-3 pl-0 flex flex-col gap-3 min-w-0 overflow-y-auto">
        <VehicleList />
        <AlertPanel />
        <RadarAIPanel />
        <ProductionPanel />
      </div>
    </div>
  );
}
