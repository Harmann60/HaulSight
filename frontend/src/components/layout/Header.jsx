import { useSystemStore } from '../../stores/systemStore';
import { runScenario } from '../../api/client';

export default function Header() {
  const wsConnected = useSystemStore((s) => s.wsConnected);
  const health = useSystemStore((s) => s.health);
  const gatewayStatus = health.gateway_status || 'unknown';

  return (
    <header className="bg-brown text-cream px-6 py-3 flex items-center justify-between shrink-0 shadow-md">
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-bold tracking-wide">
          <span className="text-primary">Haul</span>Sight
        </h1>
        <span className="text-xs text-cream/60 uppercase tracking-widest">
          Mine Vehicle Safety System
        </span>
      </div>

      <div className="flex items-center gap-5 text-sm">
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-400' : 'bg-red-400'}`} />
          <span className="text-cream/70">WS {wsConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${gatewayStatus === 'online' ? 'bg-green-400' : gatewayStatus === 'degraded' ? 'bg-yellow-400' : 'bg-red-400'}`} />
          <span className="text-cream/70">Gateway {gatewayStatus}</span>
        </div>
        <div className="text-cream/50 text-xs">
          Uptime: {Math.floor((health.uptime_seconds || 0) / 60)}m {Math.floor((health.uptime_seconds || 0) % 60)}s
        </div>

        <div className="flex gap-2 ml-4">
          <button
            onClick={() => runScenario('1')}
            className="px-2 py-1 text-xs bg-primary/20 text-cream rounded hover:bg-primary/40 transition-colors"
          >
            Scenario 1
          </button>
          <button
            onClick={() => runScenario('2')}
            className="px-2 py-1 text-xs bg-orange/20 text-cream rounded hover:bg-orange/40 transition-colors"
          >
            Scenario 2
          </button>
          <button
            onClick={() => runScenario('3')}
            className="px-2 py-1 text-xs bg-orange/20 text-cream rounded hover:bg-orange/40 transition-colors"
          >
            Scenario 3
          </button>
          <button
            onClick={() => runScenario('reset')}
            className="px-2 py-1 text-xs bg-cream/20 text-cream rounded hover:bg-cream/30 transition-colors"
          >
            Reset
          </button>
        </div>
      </div>
    </header>
  );
}
