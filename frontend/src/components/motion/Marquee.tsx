import { useRef, type PointerEvent, type ReactNode } from "react";
import { motion, useAnimationFrame, useMotionValue, useReducedMotion, useSpring, useTransform } from "framer-motion";

type MarqueeProps = {
  children: ReactNode;
  /** Seconds for one full pass. Higher is slower. */
  duration?: number;
  reverse?: boolean;
  className?: string;
};

/** Degrees of lean at full fling. Past this the wordmarks stop being readable. */
const SKEW_LIMIT = 7;
/** Degrees of lean per percent-per-second of travel. */
const SKEW_PER_UNIT = 0.08;
/** Time constant of the post-release slowdown. */
const FLING_DECAY_MS = 260;
/** Percent of track width per second. A hard flick can otherwise blur the row. */
const MAX_FLING = 220;

const clamp = (min: number, max: number, value: number) => Math.min(max, Math.max(min, value));

/**
 * Keeps the track's offset inside one copy's width. The second copy occupies the
 * other half, so any offset in [-50, 0] shows a continuous row and the wrap is
 * invisible however far the strip has been dragged.
 */
const wrap = (min: number, max: number, value: number) => {
  const range = max - min;
  return ((((value - min) % range) + range) % range) + min;
};

/**
 * The moving variant: drifts on its own, can be grabbed and flung, and leans in
 * the direction of travel by an amount proportional to its speed.
 *
 * The offset is held as a plain motion value advanced per frame rather than as a
 * declarative `animate` keyframe, because a keyframed animation owns `x` and a
 * drag cannot write to it without the two fighting over the same transform.
 */
const DriftingRow = ({ children, duration = 40, reverse = false, className }: MarqueeProps) => {
  const trackRef = useRef<HTMLDivElement>(null);
  const drag = useRef({ active: false, lastX: 0, lastTime: 0, velocity: 0 });

  const baseX = useMotionValue(0);
  const x = useTransform(baseX, (value) => `${wrap(-50, 0, value)}%`);
  const skewTarget = useMotionValue(0);
  // Sprung, so the lean settles rather than snapping back the instant a fling
  // decays, which is what makes it read as weight rather than as a glitch.
  const skewX = useSpring(skewTarget, { stiffness: 180, damping: 26, mass: 0.4 });

  const driftPerSecond = (reverse ? 1 : -1) * (50 / duration);

  useAnimationFrame((_, delta) => {
    const state = drag.current;

    if (state.active) {
      // Pointer movement is writing `baseX` directly; the frame loop only
      // mirrors the speed into the lean.
      skewTarget.set(clamp(-SKEW_LIMIT, SKEW_LIMIT, state.velocity * SKEW_PER_UNIT));
      return;
    }

    state.velocity *= Math.exp(-delta / FLING_DECAY_MS);
    if (Math.abs(state.velocity) < 0.5) state.velocity = 0;

    const perSecond = driftPerSecond + state.velocity;
    // Capped so a tab returning from the background advances by one frame
    // rather than by the whole time it spent hidden.
    baseX.set(baseX.get() + perSecond * (Math.min(delta, 64) / 1000));
    skewTarget.set(clamp(-SKEW_LIMIT, SKEW_LIMIT, perSecond * SKEW_PER_UNIT));
  });

  const handlePointerDown = (event: PointerEvent<HTMLDivElement>) => {
    event.currentTarget.setPointerCapture(event.pointerId);
    drag.current = { active: true, lastX: event.clientX, lastTime: event.timeStamp, velocity: 0 };
  };

  const handlePointerMove = (event: PointerEvent<HTMLDivElement>) => {
    const state = drag.current;
    const track = trackRef.current;
    if (!state.active || !track) return;

    // `translateX` percentages resolve against the element's own width, so the
    // pixel delta is converted against the track rather than the viewport.
    const movedPercent = ((event.clientX - state.lastX) / track.offsetWidth) * 100;
    const elapsed = Math.max(1, event.timeStamp - state.lastTime);

    baseX.set(baseX.get() + movedPercent);
    state.velocity = (movedPercent / elapsed) * 1000;
    state.lastX = event.clientX;
    state.lastTime = event.timeStamp;
  };

  const handlePointerUp = (event: PointerEvent<HTMLDivElement>) => {
    const state = drag.current;
    if (!state.active) return;
    state.active = false;
    state.velocity = clamp(-MAX_FLING, MAX_FLING, state.velocity);
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
  };

  return (
    <div
      className={`cursor-grab select-none overflow-hidden active:cursor-grabbing ${className ?? ""}`}
      // `pan-y` and not `none`: the strip claims horizontal gestures, but a
      // vertical swipe that starts on it must still scroll the page.
      style={{ touchAction: "pan-y" }}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      onPointerCancel={handlePointerUp}
    >
      <motion.div ref={trackRef} className="flex w-max items-center" style={{ x, skewX }}>
        <div className="flex shrink-0 items-center">{children}</div>
        <div className="flex shrink-0 items-center" aria-hidden="true">
          {children}
        </div>
      </motion.div>
    </div>
  );
};

/**
 * Continuous horizontal scroll. `children` is rendered twice and the track is
 * offset by at most half its width, so the second copy lands where the first
 * started and the loop has no visible seam.
 *
 * Under `prefers-reduced-motion` a single static copy is rendered in a
 * horizontally scrollable row, so the content stays reachable without motion.
 */
export const Marquee = ({ children, duration = 40, reverse = false, className }: MarqueeProps) => {
  const reduced = useReducedMotion();

  if (reduced) {
    return (
      <div className={`overflow-x-auto ${className ?? ""}`}>
        <div className="flex w-max items-center">{children}</div>
      </div>
    );
  }

  return (
    <DriftingRow duration={duration} reverse={reverse} className={className}>
      {children}
    </DriftingRow>
  );
};
