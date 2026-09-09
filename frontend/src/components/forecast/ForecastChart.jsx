import React, { useState } from 'react';

export default function ForecastChart({ forecast, selectedScenario }) {
  const [hoveredIdx, setHoveredIdx] = useState(null);

  if (!forecast?.slots || !forecast?.expected_arrivals) {
    return null;
  }

  const slots = forecast.slots; // 32 slots (09:00 - 16:45)
  const arrivals = forecast.expected_arrivals;
  
  // Aggregate expected arrivals per slot
  const totals = slots.map((_, i) => {
    let sum = 0;
    Object.keys(arrivals).forEach(qKey => {
      sum += arrivals[qKey]?.[i] || 0;
    });
    return sum;
  });

  const maxVal = Math.max(...totals, 25);

  // SVG Viewport Dimensions
  const width = 880;
  const height = 240;
  const padLeft = 46;
  const padRight = 24;
  const padTop = 32;
  const padBottom = 38;
  const chartWidth = width - padLeft - padRight;
  const chartHeight = height - padTop - padBottom;
  const slotW = chartWidth / slots.length;

  // Surge window indices: 11:00 (slot 8) to 13:30 (slot 18)
  const surgeStartIdx = slots.indexOf("11:00");
  const surgeEndIdx = slots.indexOf("13:30");
  const isSurge = selectedScenario === 'surge';

  return (
    <div className="forecast-chart-svg-container">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="forecast-svg"
        onMouseLeave={() => setHoveredIdx(null)}
      >
        <defs>
          {/* Dark Slate Primary Bar Gradient (matching inspiration image) */}
          <linearGradient id="primaryBarGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#18181B" stopOpacity="0.95" />
            <stop offset="100%" stopColor="#27272A" stopOpacity="0.85" />
          </linearGradient>

          {/* Surge Period Accent Gradient */}
          <linearGradient id="surgeBarGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#EF4444" stopOpacity="1" />
            <stop offset="100%" stopColor="#F59E0B" stopOpacity="0.9" />
          </linearGradient>

          {/* Surge Backdrop Tint */}
          <linearGradient id="surgeBackdrop" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="rgba(239, 68, 68, 0.08)" />
            <stop offset="100%" stopColor="rgba(245, 158, 11, 0.02)" />
          </linearGradient>
        </defs>

        {/* Horizontal Gridlines & Y-Axis Labels */}
        {[0, 0.25, 0.5, 0.75, 1].map((pct, i) => {
          const y = padTop + chartHeight * (1 - pct);
          const val = Math.round(maxVal * pct);
          return (
            <g key={i}>
              <line
                x1={padLeft}
                y1={y}
                x2={width - padRight}
                y2={y}
                stroke="#E5E7EB"
                strokeDasharray={pct === 0 ? 'none' : '3,3'}
              />
              <text
                x={padLeft - 10}
                y={y + 4}
                textAnchor="end"
                fontSize="10"
                fontFamily="var(--font-mono)"
                fill="#6B7280"
              >
                {val}
              </text>
            </g>
          );
        })}

        {/* Surge Window Visual Emphasis (11:00 — 13:30) */}
        {isSurge && surgeStartIdx !== -1 && surgeEndIdx !== -1 && (
          <g>
            <rect
              x={padLeft + surgeStartIdx * slotW}
              y={padTop}
              width={(surgeEndIdx - surgeStartIdx) * slotW}
              height={chartHeight}
              fill="url(#surgeBackdrop)"
              stroke="#EF4444"
              strokeWidth="1.5"
              strokeDasharray="4,4"
            />
            <text
              x={padLeft + surgeStartIdx * slotW + 8}
              y={padTop + 16}
              fill="#DC2626"
              fontSize="10"
              fontFamily="var(--font-mono)"
              fontWeight="700"
              letterSpacing="0.04em"
            >
              ⚠ SURGE PERIOD // ELEVATED INFLOW
            </text>
          </g>
        )}

        {/* Capacity Baseline Line */}
        <line
          x1={padLeft}
          y1={padTop + chartHeight * (1 - (isSurge ? 28 / maxVal : 22 / maxVal))}
          x2={width - padRight}
          y2={padTop + chartHeight * (1 - (isSurge ? 28 / maxVal : 22 / maxVal))}
          stroke="#F59E0B"
          strokeWidth="1.5"
          strokeDasharray="4,4"
        />
        <text
          x={width - padRight - 6}
          y={padTop + chartHeight * (1 - (isSurge ? 28 / maxVal : 22 / maxVal)) - 6}
          textAnchor="end"
          fontSize="9.5"
          fill="#D97706"
          fontFamily="var(--font-mono)"
          fontWeight="600"
        >
          BASELINE SERVICE CAPACITY
        </text>

        {/* Data Bars */}
        {slots.map((slot, i) => {
          const x = padLeft + i * slotW;
          const barW = Math.max(4, slotW - 4);
          const totalArrivals = totals[i];
          const barH = Math.max(3, (totalArrivals / maxVal) * chartHeight);
          const y = padTop + chartHeight - barH;

          // Is this slot inside the surge window?
          const inSurge = isSurge && i >= surgeStartIdx && i < surgeEndIdx;
          const isHovered = hoveredIdx === i;

          return (
            <g
              key={slot}
              onMouseEnter={() => setHoveredIdx(i)}
              style={{ cursor: 'pointer' }}
            >
              {/* Invisible Hover Hitbox */}
              <rect
                x={x - 1}
                y={padTop}
                width={slotW}
                height={chartHeight}
                fill={isHovered ? 'rgba(0, 0, 0, 0.04)' : 'transparent'}
              />

              {/* Bar Fill with rounded top corners */}
              <rect
                x={x + 2}
                y={y}
                width={barW}
                height={barH}
                rx="4"
                ry="4"
                fill={inSurge ? "url(#surgeBarGrad)" : "url(#primaryBarGrad)"}
                stroke={isHovered ? "#18181B" : "none"}
                strokeWidth={isHovered ? "1.5" : "0"}
              />

              {/* X-Axis Time Labels at Every 4th Slot (Hourly) */}
              {i % 4 === 0 && (
                <text
                  x={x + barW / 2}
                  y={padTop + chartHeight + 18}
                  textAnchor="middle"
                  fontSize="9.5"
                  fontFamily="var(--font-mono)"
                  fill={isHovered ? "#111827" : "#6B7280"}
                  fontWeight={isHovered ? "700" : "500"}
                >
                  {slot}
                </text>
              )}
            </g>
          );
        })}
      </svg>

      {/* Interactive Tooltip Inspector */}
      {hoveredIdx !== null && (
        <div className="forecast-chart-tooltip font-mono">
          <div className="tooltip-slot-header">
            TIME SLOT: <span className="cyan">{slots[hoveredIdx]}</span>
          </div>
          <div className="tooltip-breakdown-list">
            {Object.keys(arrivals).map(qKey => (
              <div key={qKey} className="tooltip-item">
                <span className="tooltip-qname">{qKey.toUpperCase()}:</span>
                <span className="tooltip-count font-mono">{arrivals[qKey]?.[hoveredIdx] || 0}</span>
              </div>
            ))}
            <div className="tooltip-total-row">
              <span>TOTAL INFLOW:</span>
              <span className="cyan bold">{totals[hoveredIdx]}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
