export function stringToColor(str) {
  if (!str) return 'var(--surface-dim)';
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  // Generate HSL: hue based on hash, 60% saturation, 45% lightness (so white text is readable)
  const h = Math.abs(hash) % 360;
  return `hsl(${h}, 60%, 45%)`;
}
