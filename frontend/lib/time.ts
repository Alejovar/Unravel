/**
 * Many sources only publish the date in their metadata (no clock time), and
 * the backend date parser fills the missing time with midnight UTC.
 * Converted to the browser's local timezone, that fabricated midnight shows
 * up as a "real" but bogus time (e.g. 18:00 in Mexico) — and because it
 * happens for many articles, almost all of them end up displaying the same
 * time. We treat exact UTC midnight as "unknown time" instead of rendering
 * it as if it were precise.
 */
export function hasKnownTime(iso: string | null): boolean {
  if (!iso) return false;
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return false;
  return !(d.getUTCHours() === 0 && d.getUTCMinutes() === 0 && d.getUTCSeconds() === 0);
}
