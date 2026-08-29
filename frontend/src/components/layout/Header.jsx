import { useState } from 'react';
import { useSystemStore } from '../../stores/systemStore';
import { runScenario } from '../../api/client';

const SCENARIO_INFO = {
  1: {
    label: 'Scenario 1',
    short: 'S1',
    color: 'bg-primary',
    hoverColor: 'hover:bg-primary-dark',
    activeColor: 'bg-primary ring-2 ring-primary/50',
    title: 'Blind Corner Collision',
    desc: 'Vehicles approaching blind corner — risk escalation',
  },
  2: {
    label: 'Scenario 2',
    short: 'S2',
    color: 'bg-orange',
    hoverColor: 'hover:bg-orange-dark',
    activeColor: 'bg-orange ring-2 ring-orange/50',
    title: 'Network Failure',
    desc: 'Gateway degraded — radar fallback active',
  },
  3: {
    label: 'Scenario 3',
    short: 'S3',
    color: 'bg-critical',
    hoverColor: 'hover:bg-red-700',
    activeColor: 'bg-critical ring-2 ring-red-500/50',
    title: 'Non-Equipped Vehicle',
    desc: 'Radar detected unknown vehicle at blind corner',
  },
};

const AI_SCENARIO_INFO = {
  fog: {
    label: 'Dense Fog',
    short: '🌫',
    color: 'bg-orange',
    activeColor: 'bg-orange ring-2 ring-orange/50',
    title: 'Dense Fog (AI)',
    desc: 'Visibility AI: ~80m HIGH fog — risk engine more conservative',
    scenarioName: 'scenario_ai_fog',
  },
  radar_false: {
    label: 'Radar False+',
    short: '🪨',
    color: 'bg-brown-light',
    activeColor: 'bg-brown ring-2 ring-brown/50',
    title: 'Radar False Positive (AI)',
    desc: 'AI classifier: ROCK — no vehicle alert',
    scenarioName: 'scenario_ai_radar_false_positive',
  },
  radar_vehicle: {
    label: 'Radar Vehicle',
    short: '🚚',
    color: 'bg-primary',
    activeColor: 'bg-primary ring-2 ring-primary/50',
    title: 'Radar Vehicle (AI)',
    desc: 'AI classifier: VEHICLE — local warning',
    scenarioName: 'scenario_ai_radar_vehicle',
  },
  hotspot: {
    label: 'Hotspots',
    short: '📍',
    color: 'bg-critical',
    activeColor: 'bg-critical ring-2 ring-red-500/50',
    title: 'Historical Hotspot (AI)',
    desc: 'Map shows high-risk zone from historical alerts',
    scenarioName: 'scenario_ai_hotspot',
  },
  production: {
    label: 'Forecast',
    short: '📈',
    color: 'bg-primary',
    activeColor: 'bg-primary ring-2 ring-primary/50',
    title: 'Production Forecast (AI)',
    desc: 'Visibility reduces haul-cycle — estimate',
    scenarioName: 'scenario_ai_production',
  },
};

export default function Header() {
  const wsConnected = useSystemStore((s) => s.wsConnected);
  const health = useSystemStore((s) => s.health);
  const scenario = useSystemStore((s) => s.scenario);
  const gatewayStatus = health.gateway_status || 'unknown';
  const [loading, setLoading] = useState(null);

  const activeScenarioName = scenario?.name || null;
  const isReset = activeScenarioName === 'reset' || activeScenarioName === null;
  const activeInfo = activeScenarioName && activeScenarioName !== 'reset'
    ? SCENARIO_INFO[activeScenarioName?.replace('scenario_', '')]
      || Object.values(AI_SCENARIO_INFO).find((a) => a.scenarioName === activeScenarioName)
    : null;

  const handleScenario = async (num) => {
    setLoading(num);
    try {
      await runScenario(String(num));
    } catch (e) {
      console.error('Scenario error:', e);
    }
    setTimeout(() => setLoading(null), 800);
  };

  const handleAIScenario = async (name) => {
    setLoading(name);
    try {
      await runScenario(name);
    } catch (e) {
      console.error('AI Scenario error:', e);
    }
    setTimeout(() => setLoading(null), 800);
  };

  const handleReset = async () => {
    setLoading('reset');
    try {
      await runScenario('reset');
    } catch (e) {
      console.error('Reset error:', e);
    }
    setTimeout(() => setLoading(null), 800);
  };

  return (
    <header className="bg-brown text-cream shrink-0 shadow-md">
      {/* Main header row */}
      <div className="px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold tracking-wide">
            <span className="text-primary">Haul</span>Sight
          </h1>
          <span className="text-xs text-cream/60 uppercase tracking-widest hidden lg:inline">
            Mine Vehicle Safety System
          </span>
        </div>

        <div className="flex items-center gap-5 text-sm">
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-400' : 'bg-red-400'}`} />
            <span className="text-cream/70">WS {wsConnected ? 'Connected' : 'Disconnected'}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${
              gatewayStatus === 'online' ? 'bg-green-400' :
              gatewayStatus === 'degraded' ? 'bg-yellow-400 animate-pulse' :
              'bg-red-400'
            }`} />
            <span className="text-cream/70">Gateway {gatewayStatus}</span>
          </div>
          <div className="text-cream/50 text-xs">
            {Math.floor((health.uptime_seconds || 0) / 60)}m {Math.floor((health.uptime_seconds || 0) % 60)}s
          </div>

          {/* Scenario buttons */}
          <div className="flex gap-2 ml-4">
            {[1, 2, 3].map((num) => {
              const info = SCENARIO_INFO[num];
              const isActive = activeScenarioName === `scenario_${num}`;
              const isLoading = loading === num;
              return (
                <button
                  key={num}
                  onClick={() => handleScenario(num)}
                  disabled={isLoading}
                  className={`px-3 py-1.5 text-xs font-semibold rounded transition-all ${
                    isActive
                      ? info.activeColor + ' text-white'
                      : info.color + '/30 text-cream hover:' + info.color + '/50'
                  } ${isLoading ? 'opacity-50 cursor-wait' : ''}`}
                  title={info.desc}
                >
                  {isLoading ? '...' : info.short}
                </button>
              );
            })}
            <button
              onClick={handleReset}
              disabled={loading === 'reset'}
              className={`px-3 py-1.5 text-xs font-semibold rounded transition-all ${
                isReset
                  ? 'bg-cream/10 text-cream/50 cursor-default'
                  : 'bg-cream/20 text-cream hover:bg-cream/30'
              } ${loading === 'reset' ? 'opacity-50 cursor-wait' : ''}`}
            >
              Reset
            </button>
          </div>
        </div>
      </div>

      {/* Active scenario banner */}
      {activeInfo ? (
        <div className={`px-6 py-2 flex items-center gap-3 text-sm animate-pulse ${
          activeScenarioName === 'scenario_2' ? 'bg-yellow-600/30' :
          activeScenarioName === 'scenario_3' ? 'bg-red-600/30' :
          'bg-primary/20'
        }`}>
          <span className="w-2 h-2 rounded-full bg-current animate-pulse" />
          <span className="font-bold">{activeInfo.title}</span>
          <span className="text-cream/60">—</span>
          <span className="text-cream/80">{activeInfo.desc}</span>
        </div>
      ) : (
        /* AI scenario row (visible when no active scenario banner) */
        <div className="px-6 py-2 flex items-center gap-2 bg-brown-light/20">
          <span className="text-[10px] uppercase tracking-widest text-cream/50 mr-1">AI Demo</span>
          {Object.entries(AI_SCENARIO_INFO).map(([key, info]) => {
            const isActive = activeScenarioName === info.scenarioName;
            const isLoading = loading === key;
            return (
              <button
                key={key}
                onClick={() => handleAIScenario(key)}
                disabled={isLoading}
                title={info.desc}
                className={`px-2.5 py-1 text-[11px] font-semibold rounded transition-all ${
                  isActive
                    ? info.activeColor + ' text-white'
                    : info.color + '/30 text-cream hover:brightness-125'
                } ${isLoading ? 'opacity-50 cursor-wait' : ''}`}
              >
                {info.short}
              </button>
            );
          })}
        </div>
      )}
    </header>
  );
}
