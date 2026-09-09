import React, { useState } from 'react';

export default function ForecastChart({ forecast, scenarioConfig, selectedScenario }) {
  const [hoveredIdx, setHoveredIdx] = useState(null);
  if (!forecast?.slots || !forecast?.expected_arrivals) return null;

  const slots = forecast.slots;
  const arrivals = forecast.expected_arrivals;
  const totals = slots.map((_, i) => Object.keys(arrivals).reduce((sum, qKey) => sum + (arrivals[qKey]?.[i] || 0), 0));
  const maxVal = Math.max(...totals, 25);
  const width = 880, height = 240, padLeft = 46, padRight = 24, padTop = 32, padBottom = 38;
  const chartWidth = width - padLeft - padRight, chartHeight = height - padTop - padBottom, slotW = chartWidth / slots.length;
  const queues = scenarioConfig?.queues || [];
  const baselineCapacity = queues.length > 0 ? queues.reduce((sum, q) => {
    const estStaff = q.queue_id === 'teller' ? 4 : (q.queue_id === 'loans' ? 3 : 3);
    return sum + ((15 / (q.avg_service_time_minutes || 5)) * estStaff);
  }, 0) : 0;
  const capacityY = baselineCapacity > 0 ? padTop + chartHeight * (1 - Math.min(0.95, Math.max(0.05, baselineCapacity / maxVal))) : padTop + chartHeight * 0.4;
  const surgeStartIdx = slots.indexOf('11:00'), surgeEndIdx = slots.indexOf('13:30');
  const isSurge = selectedScenario === 'surge';

  return (
    <div className="forecast-chart-svg-container">
      {isSurge && surgeStartIdx !== -1 && surgeEndIdx !== -1 && <div className="forecast-warning-banner">⚠ SURGE PERIOD — ELEVATED CUSTOMER INFLOW · 11:00–13:30</div>}
      <svg viewBox={`0 0 ${width} ${height}`} className="forecast-svg" onMouseLeave={() => setHoveredIdx(null)}>
        <defs>
          <linearGradient id="primaryBarGrad" x1="0%" y1="0%" x2="0%" y2="100%"><stop offset="0%" stopColor="#18181B" stopOpacity="0.95" /><stop offset="100%" stopColor="#27272A" stopOpacity="0.85" /></linearGradient>
          <linearGradient id="surgeBarGrad" x1="0%" y1="0%" x2="0%" y2="100%"><stop offset="0%" stopColor="#EF4444" stopOpacity="1" /><stop offset="100%" stopColor="#F59E0B" stopOpacity="0.9" /></linearGradient>
          <linearGradient id="surgeBackdrop" x1="0%" y1="0%" x2="0%" y2="100%"><stop offset="0%" stopColor="rgba(239, 68, 68, 0.08)" /><stop offset="100%" stopColor="rgba(245, 158, 11, 0.02)" /></linearGradient>
        </defs>
        {[0, 0.25, 0.5, 0.75, 1].map((pct, i) => { const y = padTop + chartHeight * (1 - pct); const val = Math.round(maxVal * pct); return <g key={i}><line x1={padLeft} y1={y} x2={width - padRight} y2={y} stroke="#E5E7EB" strokeDasharray={pct === 0 ? 'none' : '3,3'} /><text x={padLeft - 10} y={y + 4} textAnchor="end" fontSize="10" fontFamily="var(--font-mono)" fill="#6B7280">{val}</text></g>; })}
        {isSurge && surgeStartIdx !== -1 && surgeEndIdx !== -1 && <rect x={padLeft + surgeStartIdx * slotW} y={padTop} width={(surgeEndIdx - surgeStartIdx) * slotW} height={chartHeight} fill="url(#surgeBackdrop)" stroke="#EF4444" strokeWidth="1.5" strokeDasharray="4,4" />}
        <line x1={padLeft} y1={capacityY} x2={width - padRight} y2={capacityY} stroke="#F59E0B" strokeWidth="1.5" strokeDasharray="4,4" />
        <text x={width - padRight - 6} y={capacityY - 6} textAnchor="end" fontSize="9.5" fill="#D97706" fontFamily="var(--font-mono)" fontWeight="600">BASELINE SERVICE CAPACITY {baselineCapacity > 0 ? `(~${Math.round(baselineCapacity)} / SLOT)` : ''}</text>
        {slots.map((slot, i) => { const x = padLeft + i * slotW, barW = Math.max(4, slotW - 4), totalArrivals = totals[i], barH = Math.max(3, (totalArrivals / maxVal) * chartHeight), y = padTop + chartHeight - barH; const inSurge = isSurge && i >= surgeStartIdx && i < surgeEndIdx, isHovered = hoveredIdx === i; return <g key={slot} onMouseEnter={() => setHoveredIdx(i)} style={{ cursor: 'pointer' }}><rect x={x - 1} y={padTop} width={slotW} height={chartHeight} fill={isHovered ? 'rgba(0, 0, 0, 0.04)' : 'transparent'} /><rect x={x + 2} y={y} width={barW} height={barH} rx="4" ry="4" fill={inSurge ? 'url(#surgeBarGrad)' : 'url(#primaryBarGrad)'} stroke={isHovered ? '#18181B' : 'none'} strokeWidth={isHovered ? '1.5' : '0'} />{i % 4 === 0 && <text x={x + barW / 2} y={padTop + chartHeight + 18} textAnchor="middle" fontSize="9.5" fontFamily="var(--font-mono)" fill={isHovered ? '#111827' : '#6B7280'} fontWeight={isHovered ? '700' : '500'}>{slot}</text>}</g>; })}
      </svg>
      {hoveredIdx !== null && <div className="forecast-chart-tooltip font-mono"><div className="tooltip-slot-header">TIME SLOT: <span className="cyan">{slots[hoveredIdx]}</span></div><div className="tooltip-breakdown-list">{Object.keys(arrivals).map(qKey => <div key={qKey} className="tooltip-item"><span className="tooltip-qname">{qKey.toUpperCase()}:</span><span className="tooltip-count font-mono">{arrivals[qKey]?.[hoveredIdx] || 0}</span></div>)}<div className="tooltip-total-row"><span>TOTAL INFLOW:</span><span className="cyan bold">{totals[hoveredIdx]}</span></div></div></div>}
    </div>
  );
}
