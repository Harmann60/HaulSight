import { useAlertStore } from '../../stores/alertStore';
import AlertCard from './AlertCard';

export default function AlertPanel() {
  const activeAlerts = useAlertStore((s) => s.activeAlerts);

  const sorted = [...activeAlerts].sort((a, b) => {
    const order = { CRITICAL: 0, WARNING: 1, CAUTION: 2 };
    return (order[a.severity] ?? 3) - (order[b.severity] ?? 3);
  });

  return (
    <div className="bg-white rounded-xl shadow-md border border-cream-dark overflow-hidden">
      <div className="px-4 py-3 bg-brown/5 border-b border-cream-dark">
        <h2 className="font-bold text-brown text-sm uppercase tracking-wider">
          Active Alerts ({activeAlerts.length})
        </h2>
      </div>
      <div className="max-h-[320px] overflow-y-auto">
        {sorted.length === 0 ? (
          <div className="p-6 text-center">
            <div className="text-2xl mb-1">✅</div>
            <div className="text-sm text-brown/40">No active alerts</div>
            <div className="text-xs text-brown/30 mt-1">All vehicles operating safely</div>
          </div>
        ) : (
          sorted.map((alert) => <AlertCard key={alert.alert_id} alert={alert} />)
        )}
      </div>
    </div>
  );
}
