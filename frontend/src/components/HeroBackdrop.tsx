import { useEffect, useRef } from "react";

const GOLD = "201, 169, 110";
const INK = "24, 22, 20";
const LINE_HEIGHT = 18;

type Line = { x: number; y: number; w: number; alpha: number; gold: boolean };

/**
 * Indented line-lengths: the silhouette of a source file seen from far enough
 * away that the characters are gone and only the shape of the code is left.
 *
 * Chosen over the particle field it replaced because it says something true
 * about the subject, and over a commit grid because that swamped the figures
 * beside it. The hairline vocabulary matches the rules already used in the
 * Spotlight, Process and Journal sections.
 */
function buildStrata(width: number, height: number): Line[] {
  const lines: Line[] = [];
  // Sits in the open band between the headline and the figures, so the lines
  // never run underneath either.
  const columnX = width * 0.42;
  let y = -LINE_HEIGHT * 4;
  let depth = 0;

  while (y < height + LINE_HEIGHT * 4) {
    // A blank line between blocks, the way real code breathes between functions.
    if (Math.random() < 0.12) {
      y += LINE_HEIGHT;
      depth = 0;
      continue;
    }
    if (Math.random() < 0.28) depth = Math.min(depth + 1, 3);
    else if (Math.random() < 0.22) depth = Math.max(depth - 1, 0);

    const indent = depth * 22;
    lines.push({
      x: columnX + indent,
      y,
      w: 36 + Math.random() * (width * 0.22 - indent),
      alpha: 0.07 + Math.random() * 0.09,
      gold: Math.random() < 0.1,
    });
    y += LINE_HEIGHT;
  }
  return lines;
}

export default function HeroBackdrop() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let animationId: number | null = null;
    let lines: Line[] = [];
    let elapsed = 0;

    function resize() {
      if (!canvas) return;
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    }

    function init() {
      if (!canvas) return;
      lines = buildStrata(canvas.width, canvas.height);
    }

    function draw() {
      if (!canvas || !ctx) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const span = canvas.height + LINE_HEIGHT * 4;

      for (const line of lines) {
        // Drifts upward like a file scrolling past, wrapping back in at the bottom.
        const y = (((line.y - elapsed * 0.18) % span) + span) % span - LINE_HEIGHT * 2;
        ctx.beginPath();
        ctx.moveTo(line.x, y);
        ctx.lineTo(line.x + line.w, y);
        ctx.strokeStyle = line.gold ? `rgba(${GOLD}, ${line.alpha * 2.6})` : `rgba(${INK}, ${line.alpha})`;
        ctx.lineWidth = 3;
        ctx.lineCap = "round";
        ctx.stroke();
      }
    }

    function tick() {
      elapsed += 1;
      draw();
      animationId = requestAnimationFrame(tick);
    }

    function start() {
      if (animationId !== null || reducedMotion) return;
      animationId = requestAnimationFrame(tick);
    }

    function stop() {
      if (animationId === null) return;
      cancelAnimationFrame(animationId);
      animationId = null;
    }

    resize();
    init();
    draw();
    start();

    const resizeObserver = new ResizeObserver(() => {
      resize();
      init();
      draw();
    });
    resizeObserver.observe(canvas);

    // Stop drawing once the hero scrolls out of view.
    const intersectionObserver = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) start();
      else stop();
    });
    intersectionObserver.observe(canvas);

    return () => {
      stop();
      resizeObserver.disconnect();
      intersectionObserver.disconnect();
    };
  }, []);

  return (
    <canvas ref={canvasRef} aria-hidden="true" className="absolute inset-0 h-full w-full" style={{ display: "block" }} />
  );
}
