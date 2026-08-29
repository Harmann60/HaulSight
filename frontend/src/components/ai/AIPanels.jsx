import { Radio, TrendingUp } from 'lucide-react';
import { useAIStore } from '../../stores/aiStore';

const CLASS_DOT = {
  VEHICLE: 'bg-safe',
  ANIMAL: 'bg-warning',
  ROCK: 'bg-orange',
  UNKNOWN: 'bg-brown/40',
};

export function RadarAIPanel() {
  const classifications = useAIStore((s) => s.radarClassifications);
  const latest = classifications[0];

  const details = [
    { label: 'Range', value: latest?.features?.range_m != null ? `${latest.features.range_m.toFixed(0)} m` : '—' },
    { label: 'Relative speed', value: latest?.features?.relative_speed_mps != null ? `${latest.features.relative_speed_mps.toFixed(1)} m/s` : '—' },
    { label: 'Size', value: latest?.features?.size != null ? `${latest.features.size.toFixed(1)} m` : '—' },
  ];

  return (
    <div className="panel overflow-hidden">
      <div className="panel-header">
        <div className="flex items-center gap-2">
          <Radio size={15} className="text-brown/50" strokeWidth={1.75} />
          <h2 className="panel-title">Radar Classification</h2>
        </div>
        <span className="text-[10px] uppercase tracking-wide text-brown/35">Model · Classifier v1</span>
      </div>

      <div className="panel-body">
        {!latest ? (
          <div className="text-[12px] text-brown/40">Waiting for radar detections…</div>
        ) : (
          <>
            <div className="flex items-center gap-2.5">
              <span className={`w-2.5 h-2.5 rounded-full ${CLASS_DOT[latest.object_class] || 'bg-brown/40'}`} />
              <span className="text-lg font-bold text-brown">{latest.object_class}</span>
              <span className="text-[12px] text-brown/45">{latest.confidence}% confidence</span>
            </div>

            <div className="mt-3 grid grid-cols-3 gap-2 border-t border-cream-dark/60 pt-3">
              {details.map((d) => (
                <div key={d.label} className="leading-tight">
                  <div className="text-[10px] text-brown/40 uppercase tracking-wide">{d.label}</div>
                  <div className="text-[13px] font-semibold text-brown">{d.value}</div>
                </div>
              ))}
            </div>

            {latest.is_false_positive && (
              <div className="mt-2 text-[11px] text-brown/55">
                Non-vehicle detection — no collision alert raised.
              </div>
            )}
          </>
        )}
      </div>
      <div className="px-4 pb-3 text-[10px] text-brown/35">Simulation data · {latest?.data_mode || 'SIMULATION'}</div>
    </div>
  );
}

export function ProductionPanel() {
  const production = useAIStore((s) => s.production);
  const increase = production.increase_pct || 0;
  const impact = production.production_impact_pct || 0;
  const ready = production.normal_cycle_min > 0;

  return (
    <div className="panel overflow-hidden">
      <div className="panel-header">
        <div className="flex items-center gap-2">
          <TrendingUp size={15} className="text-brown/50" strokeWidth={1.75} />
          <h2 className="panel-title">Production Forecast</h2>
        </div>
      </div>

      <div className="panel-body">
        {!ready ? (
          <div className="text-[12px] text-brown/40">Forecast pending…</div>
        ) : (
          <>
            <div className="grid grid-cols-3 gap-2">
              <div className="leading-tight">
                <div className="text-[10px] text-brown/40 uppercase tracking-wide">Normal cycle</div>
                <div className="text-lg font-bold text-brown">
                  {Math.round(production.normal_cycle_min)}<span className="text-[11px] font-medium text-brown/50"> min</span>
                </div>
              </div>
              <div className="leading-tight">
                <div className="text-[10px] text-brown/40 uppercase tracking-wide">Predicted</div>
                <div className={`text-lg font-bold ${increase > 5 ? 'text-warning' : 'text-brown'}`}>
                  {Math.round(production.predicted_cycle_min)}<span className="text-[11px] font-medium text-brown/50"> min</span>
                </div>
              </div>
              <div className="leading-tight">
                <div className="text-[10px] text-brown/40 uppercase tracking-wide">Impact</div>
                <div className={`text-lg font-bold ${impact < 0 ? 'text-warning' : 'text-safe'}`}>{impact}%</div>
              </div>
            </div>

            <div className="mt-3 flex items-center justify-between border-t border-cream-dark/60 pt-2">
              <span className="text-[11px] text-brown/55">Haul-cycle {increase > 0 ? '+' : ''}{increase}%</span>
              <span className="text-[11px] text-brown/55">est. {production.confidence || 0}% confidence</span>
            </div>
            <div className="mt-1 text-[10px] text-brown/35">Simulation estimate · not actual mine production</div>
          </>
        )}
      </div>
    </div>
  );
}
