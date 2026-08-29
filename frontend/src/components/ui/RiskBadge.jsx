import { AlertTriangle, CircleAlert, ShieldCheck } from 'lucide-react';
import { RISK_COLORS } from '../../styles/theme';

const ICONS = {
  CRITICAL: AlertTriangle,
  WARNING: AlertTriangle,
  CAUTION: CircleAlert,
  SAFE: ShieldCheck,
};

export default function RiskBadge({ level, size = 'md' }) {
  const Icon = ICONS[level] || ShieldCheck;
  const color = RISK_COLORS[level] || RISK_COLORS.SAFE;
  const iconSize = size === 'lg' ? 15 : 13;
  const cls = size === 'lg' ? 'text-[12px] font-bold' : 'text-[11px] font-semibold';

  return (
    <span className={`inline-flex items-center gap-1 ${cls}`} style={{ color }}>
      <Icon size={iconSize} strokeWidth={2.25} />
      {level === 'CRITICAL' ? <span className="animate-pulse-critical">{level}</span> : level}
    </span>
  );
}
