import { STATE_COLORS } from '../../styles/theme';

export default function StatusBadge({ status }) {
  const color = STATE_COLORS[status] || STATE_COLORS.UNKNOWN;

  return (
    <span
      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide text-white"
      style={{ backgroundColor: color }}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-white/60" />
      {status}
    </span>
  );
}
