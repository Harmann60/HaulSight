import { acknowledgeAlert } from '../../api/client';
import RiskBadge from '../ui/RiskBadge';

const SEVERITY_BORDER = {
  CRITICAL: 'border-l-red-500 bg-red-50/30',
  WARNING: 'border-l-orange bg-orange-50/30',
  CAUTION: 'border-l-orange/50 bg-orange-50/10',
};

export default function AlertCard({ alert }) {
  const borderClass = SEVERITY_BORDER[alert.severity] || 'border-l-gray-300';

  const handleAcknowledge = async () => {
    await acknowledgeAlert(alert.alert_id);
  };

  const timeStr = alert.created_at
    ? new Date(alert.created_at).toLocaleTimeString()
    : '';

  return (
    <div className={`px-4 py-3 border-b border-cream-dark/50 border-l-4 ${borderClass}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <RiskBadge level={alert.severity} size="lg" />
          <div>
            <div className="font-bold text-sm text-brown">
              {alert.vehicle_ids?.join(' ↔ ')}
            </div>
            <div className="text-xs text-brown/50 mt-0.5">{timeStr}</div>
          </div>
        </div>
        {alert.status === 'active' && (
          <button
            onClick={handleAcknowledge}
            className="text-xs px-2 py-1 bg-cream hover:bg-cream-dark text-brown rounded transition-colors"
          >
            Ack
          </button>
        )}
      </div>
      <div className="mt-2 text-xs text-brown/70">
        {alert.reason}
      </div>
    </div>
  );
}
