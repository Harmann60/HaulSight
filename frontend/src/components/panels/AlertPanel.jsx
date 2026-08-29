import { Bell, ShieldCheck } from 'lucide-react';
import { useAlertStore } from '../../stores/alertStore';
import AlertCard from './AlertCard';

export default function AlertPanel() {
  const activeAlerts = useAlertStore((s) => s.activeAlerts);

  const sorted = [...activeAlerts].sort((a, b) => {
    const order = { CRITICAL: 0, WARNING: 1, CAUTION: 2 };
    return (order[a.severity] ?? 3) - (order[b.severity] ?? 3);
  });

  return (
    <div className="panel overflow-hidden">
      <div className="panel-header">
        <div className="flex items-center gap-2">
          <Bell size={15} className="text-brown/50" strokeWidth={1.75} />
          <h2 className="panel-title">Active Alerts</h2>
          {activeAlerts.length > 0 && (
            <span className="text-[12px] font-bold text-warning leading-none">{activeAlerts.length}</span>
          )}
        </div>
      </div>
      <div className="max-h-[320px] overflow-y-auto">
        {sorted.length === 0 ? (
          <div className="panel-body flex items-start gap-3 py-6">
            <span className="w-9 h-9 shrink-0 flex items-center justify-center rounded-md bg-healthy/10 text-healthy">
              <ShieldCheck size={18} strokeWidth={1.75} />
            </span>
            <div>
              <div className="text-[13px] font-semibold text-brown">No active alerts</div>
              <div className="text-[12px] text-brown/50 mt-0.5">All tracked vehicles operating safely</div>
            </div>
          </div>
        ) : (
          sorted.map((alert) => <AlertCard key={alert.alert_id} alert={alert} />)
        )}
      </div>
    </div>
  );
}
