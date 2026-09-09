export function formatDuration(minutes) {
  const value = Number(minutes);
  if (!Number.isFinite(value)) return '—';

  const rounded = Math.max(0, Math.round(value * 10) / 10);
  if (rounded < 60) return `${rounded.toFixed(1)} min`;

  const hours = Math.floor(rounded / 60);
  const remaining = Math.round((rounded - hours * 60) * 10) / 10;
  if (remaining === 0) return `${hours} hr`;
  return `${hours} hr ${Number.isInteger(remaining) ? remaining : remaining.toFixed(1)} min`;
}

export function formatDecimal(value, digits = 1) {
  const number = Number(value);
  return Number.isFinite(number) ? number.toFixed(digits) : '—';
}
