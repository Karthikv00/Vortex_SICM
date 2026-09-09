import React from 'react';

export default function SectionHeader({ title, subtitle, badge, action }) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: '14px',
      borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
      paddingBottom: '8px',
      gap: '8px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{
          width: '4px',
          height: '14px',
          background: 'var(--accent-cyan)',
          borderRadius: '1px',
          boxShadow: '0 0 8px var(--accent-cyan)'
        }}></span>
        <h3 style={{
          fontSize: '13px',
          fontWeight: 700,
          letterSpacing: '0.06em',
          textTransform: 'uppercase',
          color: 'var(--text-primary)',
          margin: 0
        }}>
          {title}
        </h3>
        {subtitle && (
          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            // {subtitle}
          </span>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        {badge}
        {action}
      </div>
    </div>
  );
}
