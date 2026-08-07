/**
 * Film grain for the dark sections. A flat dark field reads as cheap; a little
 * tooth makes it read as printed. Static SVG noise rather than a canvas, so it
 * costs nothing per frame and needs no reduced-motion handling.
 *
 * Shared so every dark surface (Hero, Spotlight, Testimonial, Footer) carries
 * the same texture and they read as one system rather than four dark boxes.
 */
const NOISE =
  "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")";

export const Grain = ({ className = "" }: { className?: string }) => (
  <div
    aria-hidden="true"
    className={`pointer-events-none absolute inset-0 opacity-[0.13] mix-blend-overlay ${className}`}
    style={{ backgroundImage: NOISE }}
  />
);
