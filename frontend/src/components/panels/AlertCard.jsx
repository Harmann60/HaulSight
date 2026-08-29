import { acknowledgeAlert } from '../../api/client';
import { useAIStore } from '../../stores/aiStore';

const SEVERITY_ACCENT = {
  CRITICAL: { bar: 'bg-critical', text: 'text-critical', chip: 'bg-red-50 text-critical border-critical/20' },
  WARNING: { bar: 'bg-warning', text: 'text-warning', chip: 'bg-orange-50 text-warning border-orange/25' },
  CAUTION: { bar: 'bg-orange/70', text: 'text-caution', chip: 'bg-cream text-caution border-caution/20' },
};

export default function AlertCard({ alert }) {
  const acc = SEVERITY_ACCENT[alert.severity] || SEVERITY_ACCENT.CAUTION;
  const visibility = useAIStore((s) => s.visibility);
  const hasLowVis = /low visibility/i.test(alert.reason);

  const handleAcknowledge = async () => {
    await acknowledgeAlert(alert.alert_id);
  };

  const timeStr = alert.created_at
    ? new Date(alert.created_at).toLocaleTimeString()
    : '';

  return (
    <div className="relative px-4 py-3 border-b border-cream-dark/50 pl-0">
      <span className={`absolute left-0 top-0 bottom-0 w-1 ${acc.bar}`} />
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span className={`text-[11px] font-bold uppercase tracking-wide px-1.5 py-0.5 rounded ${acc.chip}`}>
              {alert.severity}
            </span>
            <span className="text-[11px] text-brown/40">{timeStr}</span>
          </div>
          <div className="mt-1.5 font-semibold text-[13px] text-brown">
            {alert.vehicle_ids?.join(' ↔ ')}
          </div>
        </div>
        {alert.status === 'active' && (
          <button
            onClick={handleAcknowledge}
            className="shrink-0 text-[11px] font-semibold px-2 py-1 rounded border border-cream-dark text-brown/70 hover:bg-cream transition-colors"
          >
            Acknowledge
          </button>
        )}
      </div>

      <div className="mt-1.5 text-[12px] text-brown/70 leading-snug">
        {alert.reason}
      </div>

      {hasLowVis && visibility.estimated_visibility_m != null && (
        <div className="mt-1.5 text-[11px] text-brown/55">
          Visibility {Math.round(visibility.estimated_visibility_m)}m · {visibility.fog_severity} fog · est. {visibility.confidence}% conf
        </div>
      )}
    </div>
  );
}
