import { CloudFog } from 'lucide-react';
import { useAIStore } from '../../stores/aiStore';

const FOG_META = {
  NONE: { text: 'text-safe', accent: 'bg-safe/10 text-safe' },
  MODERATE: { text: 'text-caution', accent: 'bg-orange/10 text-caution' },
  HIGH: { text: 'text-warning', accent: 'bg-orange/10 text-warning' },
  EXTREME: { text: 'text-critical', accent: 'bg-red-50 text-critical' },
  UNKNOWN: { text: 'text-brown/40', accent: 'bg-cream text-brown/45' },
};

export function VisibilityChip() {
  const visibility = useAIStore((s) => s.visibility);
  const meta = FOG_META[visibility.fog_severity] || FOG_META.UNKNOWN;
  const visM = visibility.estimated_visibility_m;

  return (
    <div className="flex items-center gap-3 pl-3 pr-4 py-1.5 rounded-md bg-white border border-cream-dark shadow-sm">
      <CloudFog size={18} className={`${meta.text} `} strokeWidth={1.75} />
      <div className="leading-tight">
        <div className="text-xs text-brown/45 uppercase tracking-wide">Visibility</div>
        <div className={`text-base font-bold ${meta.text}`}>
          {visM != null ? `${Math.round(visM)} m` : '—'}
          {visM != null && (
            <span className={`ml-2 text-[10px] font-semibold px-1.5 py-0.5 rounded ${meta.accent}`}>
              {visibility.fog_severity === 'UNKNOWN' ? '—' : `${visibility.fog_severity} fog`}
            </span>
          )}
        </div>
        <div className="text-[10px] text-brown/40">
          est. {visibility.confidence || 0}% conf · simulation
        </div>
      </div>
    </div>
  );
}
