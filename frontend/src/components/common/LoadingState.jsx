import React from 'react';

export default function LoadingState({ message = 'PROCESSING TELEMETRY...', height = '140px' }) {
  return (
    <div style={{
      height,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '12px',
      background: 'rgba(0, 0, 0, 0.2)',
      borderRadius: 'var(--radius-sm)',
      border: '1px dashed rgba(0, 240, 255, 0.2)',
      padding: '24px'
    }}>
      <div style={{
        width: '160px',
        height: '4px',
        background: 'rgba(0, 240, 255, 0.15)',
        borderRadius: '2px',
        overflow: 'hidden',
        position: 'relative'
      }}>
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          bottom: 0,
          width: '50px',
          background: 'var(--accent-cyan)',
          boxShadow: '0 0 10px var(--accent-cyan)',
          animation: 'scanner-swipe 1.2s infinite ease-in-out'
        }}></div>
      </div>
      <span className="text-micro" style={{ color: 'var(--accent-cyan)' }}>
        {message}
      </span>
    </div>
  );
}
