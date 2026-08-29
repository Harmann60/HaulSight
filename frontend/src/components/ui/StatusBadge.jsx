import { STATE_COLORS } from '../../styles/theme';

export default function StatusBadge({ status }) {
  const cls =
    status === 'LIVE' ? 'dot--live' :
    status === 'STALE' ? 'dot--stale' :
    status === 'OFFLINE' ? 'dot--offline' :
    status === 'DEGRADED' ? 'dot--degraded' : 'dot--offline';

  return (
    <span className="status" style={{ color: STATE_COLORS[status] || '#6B7280' }} title={`Status: ${status}`}>
      <span className={`dot ${cls}`} />
      {status}
    </span>
  );
}
