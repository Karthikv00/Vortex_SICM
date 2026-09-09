import React from 'react';

export default function MetricCard({
  label,
  value,
  unit = '',
  delta,
  deltaType = 'positive', // 'positive' (green/good), 'negative' (red/bad), 'neutral'
  subtext,
  status = 'neutral',
  icon
}) {
  let statusBorder = 'var(--border-subtle)';
  let glowStyle = {};
  
  if (status === 'critical') {
    statusBorder = 'var(--border-critical)';
    glowStyle = { boxShadow: '0 0 12px rgba(255, 51, 85, 0.15)' };
  } else if (status === 'success') {
    statusBorder = 'rgba(0, 255, 136, 0.3)';
    glowStyle = { boxShadow: '0 0 12px rgba(0, 255, 136, 0.12)' };
  } else if (status === 'cyan') {
    statusBorder = 'var(--border-medium)';
    glowStyle = { boxShadow: 'var(--glow-cyan)' };
  }

  return (
    <div style={{
      background: 'rgba(14, 22, 38, 0.7)',
      border: `1px solid ${statusBorder}`,
      borderRadius: 'var(--radius-sm)',
      padding: '12px 14px',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      position: 'relative',
      minWidth: '140px',
      ...glowStyle
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span className="text-micro">{label}</span>
        {icon && <span style={{ opacity: 0.7, fontSize: '12px' }}>{icon}</span>}
      </div>

      <div style={{ margin: '6px 0 2px' }}>
        <span style={{
          fontSize: '22px',
          fontWeight: 800,
          fontFamily: 'var(--font-mono)',
          color: 'var(--text-primary)',
          letterSpacing: '-0.02em'
        }}>
          {value}
        </span>
        {unit && (
          <span style={{ fontSize: '12px', color: 'var(--text-muted)', marginLeft: '4px' }}>
            {unit}
          </span>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '11px' }}>
        {subtext && (
          <span style={{ color: 'var(--text-muted)', fontSize: '10px' }}>
            {subtext}
          </span>
        )}
        {delta && (
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontWeight: 700,
            fontSize: '10px',
            color: deltaType === 'positive' ? 'var(--signal-success)' : (deltaType === 'negative' ? 'var(--signal-critical)' : 'var(--accent-cyan)')
          }}>
            {delta}
          </span>
        )}
      </div>
    </div>
  );
}
