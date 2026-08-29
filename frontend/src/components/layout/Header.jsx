import { useState } from 'react';
import { ShieldCheck, CloudFog, Radio, MapPin, TrendingUp } from 'lucide-react';
import { useSystemStore } from '../../stores/systemStore';
import { runScenario } from '../../api/client';

const SCENARIO_ITEMS = [
  { key: 1, short: 'S1', label: 'Blind Corner', scenarioName: 'scenario_1' },
  { key: 2, short: 'S2', label: 'Network Loss', scenarioName: 'scenario_2' },
  { key: 3, short: 'S3', label: 'Unlisted Vehicle', scenarioName: 'scenario_3' },
];

const AI_SCENARIO_INFO = {
  fog: { label: 'Fog', Icon: CloudFog, desc: 'Visibility AI: ~80m HIGH fog', scenarioName: 'scenario_ai_fog' },
  radar_false: { label: 'Radar', Icon: Radio, desc: 'AI classifier: ROCK — no vehicle alert', scenarioName: 'scenario_ai_radar_false_positive' },
  radar_vehicle: { label: 'Radar', Icon: Radio, desc: 'AI classifier: VEHICLE', scenarioName: 'scenario_ai_radar_vehicle' },
  hotspot: { label: 'Hotspots', Icon: MapPin, desc: 'Historical high-risk zone', scenarioName: 'scenario_ai_hotspot' },
  production: { label: 'Forecast', Icon: TrendingUp, desc: 'Visibility reduces haul-cycle — estimate', scenarioName: 'scenario_ai_production' },
};

export default function Header() {
  const wsConnected = useSystemStore((s) => s.wsConnected);
  const health = useSystemStore((s) => s.health);
  const scenario = useSystemStore((s) => s.scenario);
  const gatewayStatus = health.gateway_status || 'unknown';
  const [loading, setLoading] = useState(null);

  const activeScenarioName = scenario?.name || null;
  const isReset = activeScenarioName === 'reset' || activeScenarioName === null;
  const activeInfo = Object.values(AI_SCENARIO_INFO)
    .find((a) => a.scenarioName === activeScenarioName) || null;
  const activeCore = SCENARIO_ITEMS.find((s) => s.scenarioName === activeScenarioName) || null;
  const bannerInfo = activeCore || activeInfo;

  const gatewayOk = gatewayStatus === 'online';
  const gatewayDeg = gatewayStatus === 'degraded';

  const handleScenario = async (num) => {
    setLoading(`core-${num}`);
    try { await runScenario(String(num)); }
    catch (e) { console.error('Scenario error:', e); }
    setTimeout(() => setLoading(null), 800);
  };

  const handleAIScenario = async (key) => {
    const name = AI_SCENARIO_INFO[key].scenarioName;
    setLoading(`ai-${key}`);
    try { await runScenario(name); }
    catch (e) { console.error('AI Scenario error:', e); }
    setTimeout(() => setLoading(null), 800);
  };

  const handleReset = async () => {
    setLoading('reset');
    try { await runScenario('reset'); }
    catch (e) { console.error('Reset error:', e); }
    setTimeout(() => setLoading(null), 800);
  };

  const coreCls = (isActive) =>
    `px-3 py-1.5 text-[11px] font-semibold transition-colors ${
      isActive
        ? 'bg-primary text-white'
        : 'text-cream/75 hover:bg-white/10 hover:text-cream'
    }`;

  return (
    <header className="bg-brown text-cream shrink-0 shadow-md border-b border-black/20">
      {/* Top bar */}
      <div className="px-6 h-14 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-baseline gap-3">
          <h1 className="text-lg font-bold tracking-tight">
            <span className="text-primary">Haul</span>Sight
          </h1>
          <span className="text-[11px] text-cream/45 uppercase tracking-[0.18em] hidden lg:inline">
            Mine Vehicle Safety System
          </span>
        </div>

        {/* Right: status + controls */}
        <div className="flex items-center gap-6">
          {/* Connection status */}
          <div className="hidden xl:flex items-center gap-4 text-xs text-cream/60">
            <span className="flex items-center gap-2">
              <span className={`dot w-2 h-2 rounded-full ${wsConnected ? 'bg-healthy' : 'bg-critical'}`} />
              WebSocket {wsConnected ? 'live' : 'down'}
            </span>
            <span className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${gatewayOk ? 'bg-healthy' : gatewayDeg ? 'bg-orange' : 'bg-critical'}`} />
              Gateway {gatewayStatus}
            </span>
            <span className="text-cream/40">
              Uptime {Math.floor((health.uptime_seconds || 0) / 60)}m {(health.uptime_seconds || 0) % 60}s
            </span>
          </div>

          {/* Scenario controls */}
          <div className="flex items-center gap-4">
            <div className="flex flex-col leading-tight">
              <span className="text-[10px] uppercase tracking-[0.15em] text-cream/40">Scenario</span>
              <div className="flex items-center bg-black/25 rounded-md overflow-hidden">
                {SCENARIO_ITEMS.map((item) => (
                  <button
                    key={item.key}
                    onClick={() => handleScenario(item.key)}
                    disabled={loading === `core-${item.key}`}
                    title={item.label}
                    className={coreCls(activeScenarioName === item.scenarioName)}
                  >
                    {loading === `core-${item.key}` ? '…' : item.short}
                  </button>
                ))}
                <button
                  onClick={handleReset}
                  disabled={loading === 'reset'}
                  title="Reset to nominal conditions"
                  className={coreCls(isReset)}
                >
                  {loading === 'reset' ? '…' : 'Reset'}
                </button>
              </div>
            </div>

            {/* Intelligence scenario controls */}
            <div className="flex flex-col leading-tight">
              <span className="text-[10px] uppercase tracking-[0.15em] text-cream/40">Intelligence</span>
              <div className="flex items-center gap-1.5">
                {Object.entries(AI_SCENARIO_INFO).map(([key, info]) => {
                  const isLoading = loading === `ai-${key}`;
                  const isActive = activeScenarioName === info.scenarioName;
                  return (
                    <button
                      key={key}
                      onClick={() => handleAIScenario(key)}
                      disabled={isLoading}
                      title={info.desc}
                      className={`p-1.5 rounded transition-colors ${
                        isActive
                          ? 'bg-primary text-white'
                          : 'text-cream/55 hover:bg-white/10 hover:text-cream'
                      }`}
                    >
                      <info.Icon size={15} strokeWidth={1.75} />
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Active scenario banner */}
      {bannerInfo && (
        <div className="px-6 py-1.5 flex items-center gap-2.5 text-xs bg-primary/15 border-t border-primary/20">
          {bannerInfo.Icon ? (
            <bannerInfo.Icon size={14} className="text-primary" strokeWidth={1.75} />
          ) : (
            <ShieldCheck size={14} className="text-primary" strokeWidth={1.75} />
          )}
          <span className="font-semibold text-cream">{bannerInfo.label || bannerInfo.short}</span>
          <span className="text-cream/45">·</span>
          <span className="text-cream/70">{bannerInfo.desc}</span>
        </div>
      )}
    </header>
  );
}
