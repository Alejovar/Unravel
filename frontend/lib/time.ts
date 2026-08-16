/**
 * Muchas fuentes solo publican la fecha en sus metadatos (sin hora), y el
 * parser de fechas del backend completa la hora faltante con medianoche
 * UTC. Convertida a la zona horaria local del navegador, esa medianoche
 * fabricada aparece como una hora "real" pero falsa (ej. 18:00 en México)
 * — y como pasa con muchos artículos, casi todos terminan mostrando la
 * misma hora. Tratamos la medianoche UTC exacta como "hora desconocida"
 * en vez de mostrarla como si fuera precisa.
 */
export function hasKnownTime(iso: string | null): boolean {
  if (!iso) return false;
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return false;
  return !(d.getUTCHours() === 0 && d.getUTCMinutes() === 0 && d.getUTCSeconds() === 0);
}
