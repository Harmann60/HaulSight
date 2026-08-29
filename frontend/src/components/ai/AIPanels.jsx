import { useAIStore } from '../../stores/aiStore';

const CLASS_COLOR = {
  VEHICLE: 'text-safe bg-blue-50 border-blue-200',
  ANIMAL: 'text-warning bg-orange-50 border-orange-200',
  ROCK: 'text-brown bg-cream border-cream-dark',
  UNKNOWN: 'text-brown/50 bg-cream border-cream-dark',
};

export function RadarAIPanel() {
  const classifications = useAIStore((s) => s.radarClassifications);

  return (
    <div className="bg-white rounded-xl shadow-md border border-cream-dark overflow-hidden">
      <div className="px-4 py-3 bg-brown/5 border-b border-cream-dark flex items-center justify-between">
        <h2 className="font-bold text-brown text-sm uppercase tracking-wider">Radar AI Classification</h2>
        <span className="text-[10px] text-brown/40 uppercase">simulation</span>
      </div>
      <div className="max-h-[200px] overflow-y-auto">
        {classifications.length === 0 ? (
          <div className="p-4 text-center text-xs text-brown/40">
            Waiting for radar detections…
          </div>
        ) : (
          classifications.map((c, i) => {
            const cls = CLASS_COLOR[c.object_class] || CLASS_COLOR.UNKNOWN;
            return (
              <div key={c.detection_id || i} className="px-4 py-2.5 border-b border-cream-dark/50">
                <div className="flex items-center justify-between">
                  <span className={`text-xs font-bold px-2 py-0.5 rounded border ${cls}`}>
                    {c.object_class}
                  </span>
                  <span className="text-xs font-semibold text-brown">{c.confidence}%</span>
                </div>
                <div className="mt-1 text-[10px] text-brown/50">
                  range {c.features?.range_m?.toFixed(0)}m • rel speed {c.features?.relative_speed_mps?.toFixed(1)} m/s {
                    c.is_false_positive ? '• ✅ no alert (non-vehicle)' : ''
                  }
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

export function ProductionPanel() {
  const production = useAIStore((s) => s.production);
  const increase = production.increase_pct || 0;
  const impact = production.production_impact_pct || 0;

  return (
    <div className="bg-white rounded-xl shadow-md border border-cream-dark overflow-hidden">
      <div className="px-4 py-3 bg-brown/5 border-b border-cream-dark flex items-center justify-between">
        <h2 className="font-bold text-brown text-sm uppercase tracking-wider">Production Forecast</h2>
        <span className="text-[10px] text-brown/40 uppercase">estimate</span>
      </div>
      <div className="px-4 py-3">
        <div className="grid grid-cols-3 gap-2 text-center">
          <div>
            <div className="text-[10px] text-brown/40 uppercase">Normal</div>
            <div className="font-bold text-brown">{Math.round(production.normal_cycle_min)}<span className="text-xs"> min</span></div>
          </div>
          <div>
            <div className="text-[10px] text-brown/40 uppercase">Predicted</div>
            <div className={`font-bold ${increase > 5 ? 'text-warning' : 'text-brown'}`}>
              {Math.round(production.predicted_cycle_min)}<span className="text-xs"> min</span>
            </div>
          </div>
          <div>
            <div className="text-[10px] text-brown/40 uppercase">Impact</div>
            <div className={`font-bold ${impact < 0 ? 'text-critical' : 'text-safe'}`}>{impact}%</div>
          </div>
        </div>
        <div className="mt-2 flex items-center justify-between text-[10px] text-brown/40">
          <span>+{increase}% cycle time</span>
          <span>AI {production.confidence}% conf</span>
        </div>
        <div className="mt-1.5 text-[9px] text-brown/30 italic">
          Simulation estimate only, not actual mine production.
        </div>
      </div>
    </div>
  );
}
