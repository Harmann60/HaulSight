import { RISK_COLORS } from '../../styles/theme';

const SIZE_CLASSES = {
  sm: 'px-1.5 py-0.5 text-[9px]',
  md: 'px-2 py-0.5 text-[10px]',
  lg: 'px-2.5 py-1 text-xs',
};

export default function RiskBadge({ level, size = 'md' }) {
  const color = RISK_COLORS[level] || RISK_COLORS.SAFE;
  const sizeClass = SIZE_CLASSES[size] || SIZE_CLASSES.md;

  return (
    <span
      className={`inline-flex items-center font-bold uppercase tracking-wide text-white rounded ${sizeClass} ${
        level === 'CRITICAL' ? 'animate-pulse-critical' : ''
      }`}
      style={{ backgroundColor: color }}
    >
      {level}
    </span>
  );
}
