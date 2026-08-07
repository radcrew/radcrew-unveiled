import type { Variants } from "framer-motion";

/** The house easing: quick off the mark, long settle. */
const EASE: [number, number, number, number] = [0.16, 1, 0.3, 1];

/**
 * The section variants, and the roles they are assigned to. Before these
 * existed every section entered with `fadeIn`, so nine of them in a row read as
 * one gesture repeated rather than a page with any rhythm to it.
 *
 * - `maskWipe` for the serif section headings.
 * - `staggerContainer` + `riseIn` for grids and lists.
 * - `fadeIn` for everything else, which is still most of it.
 */

export const fadeIn: Variants = {
  hidden: { opacity: 0, y: 30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.8, ease: EASE },
  },
};

export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.2 },
  },
};

/**
 * Uncovers a heading left to right instead of sliding it in, so a section's
 * entrance has a different shape from the content stacked underneath it. The
 * opacity is animated alongside the clip so the heading does not appear as a
 * hard edge on the first frame.
 */
export const maskWipe: Variants = {
  hidden: { opacity: 0, clipPath: "inset(0 100% 0 0)" },
  visible: {
    opacity: 1,
    clipPath: "inset(0 0% 0 0)",
    transition: { duration: 0.9, ease: EASE },
  },
};

/**
 * For items staggered under `staggerContainer`. Travels less than `fadeIn` and
 * carries a slight scale, so a run of six or eight reads as one group arriving
 * rather than as that many separate entrances.
 */
export const riseIn: Variants = {
  hidden: { opacity: 0, y: 16, scale: 0.98 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { duration: 0.55, ease: EASE },
  },
};
