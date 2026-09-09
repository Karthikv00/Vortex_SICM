import React from 'react';

export default function StatusBadge({ status, label, pulsing = false }) {
  const norm = (status || 'normal').toLowerCase();
  
  let type = 'normal';
  let dotColor = 'green';
  
  if (norm.includes('overload') || norm.includes('critical') || norm === 'red') {
    type = 'overloaded';
    dotColor = 'red';
  } else if (norm.includes('warn') || norm === 'amber') {
    type = 'warning';
    dotColor = 'amber';
  } else if (norm.includes('opt') || norm === 'purple') {
    type = 'purple';
    dotColor = 'cyan';
  } else if (norm.includes('cyan')) {
    type = 'cyan';
    dotColor = 'cyan';
  }

  const displayLabel = label || status;

  return (
    <span className={`status-badge ${type}`}>
      <span className={`status-dot ${dotColor} ${pulsing ? 'pulsing' : ''}`}></span>
      <span>{displayLabel}</span>
    </span>
  );
}
