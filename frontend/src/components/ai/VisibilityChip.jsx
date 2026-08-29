import { useAIStore } from '../../stores/aiStore';

const FOG_COLORS = {
  NONE: { text: 'text-safe', bg: 'bg-green-50', ring: 'ring-green-200' },
  MODERATE: { text: 'text-caution', bg: 'bg-orange-50', ring: 'ring-orange-200' },
  HIGH: { text: 'text-warning', bg: 'bg-orange-50', ring: 'ring-orange-300' },
  EXTREME: { text: 'text-critical', bg: 'bg-red-50', ring: 'ring-red-200' },
  UNKNOWN: { text: 'text-brown/40', bg: 'bg-cream', ring: 'ring-cream-dark' },
};

export function VisibilityChip() {
  const visibility = useAIStore((s) => s.visibility);
  const fog = FOG_COLORS[visibility.fog_severity] || FOG_COLORS.UNKNOWN;
  const visM = visibility.estimated_visibility_m;

  return (
    <div className={`flex items-center gap-3 px-3 py-2 rounded-lg ${fog.bg} ring-1 ${fog.ring}`}>
      <span className="text-lg">🌫</span>
      <div className="leading-tight">
        <div className={`text-lg font-bold ${fog.text}`}>
          {visM != null ? `${Math.round(visM)} m` : '—'}
        </div>
        <div className={`text-[10px] uppercase tracking-wider font-semibold ${fog.text}`}>
          {visibility.fog_severity === 'UNKNOWN' ? 'Visibility' : `${visibility.fog_severity} fog`}
        </div>
      </div>
      <div className="ml-auto text-right text-[10px] leading-tight">
        <div className="text-brown/60">AI</div>
        <div className={`font-bold ${fog.text}`}>{visibility.confidence}%</div>
        <div className="text-brown/30">SIM {visibility.data_mode === 'SIMULATION' ? 'sim' : ''}</div>
      </div>
    </div>
  );
}
