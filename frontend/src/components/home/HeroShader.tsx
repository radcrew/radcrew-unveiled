import { useEffect, useRef } from "react";
import { useReducedMotion } from "framer-motion";

/**
 * The drifting warm field behind the hero headline.
 *
 * Written against raw WebGL rather than a scene library: this is one full-screen
 * triangle with one fragment shader, and `three` would add several hundred
 * kilobytes to the landing bundle to draw it.
 *
 * It layers *over* the CSS radial gradient in `Hero` rather than replacing it.
 * That gradient is the fallback, and it is the reason every failure path here is
 * a bare `return`: no WebGL context, a driver that will not link the program, a
 * canvas that never mounts. The section still gets its warm bloom, just without
 * the drift.
 */

const VERTEX_SOURCE = `
attribute vec2 a_position;

void main() {
  gl_Position = vec4(a_position, 0.0, 1.0);
}
`;

const FRAGMENT_SOURCE = `
#ifdef GL_FRAGMENT_PRECISION_HIGH
precision highp float;
#else
precision mediump float;
#endif

uniform vec2 u_resolution;
uniform float u_time;

float hash(vec2 p) {
  return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
}

float noise(vec2 p) {
  vec2 i = floor(p);
  vec2 f = fract(p);
  vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(
    mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x),
    mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x),
    u.y
  );
}

float fbm(vec2 p) {
  float total = 0.0;
  float amplitude = 0.5;
  for (int i = 0; i < 4; i++) {
    total += noise(p) * amplitude;
    p *= 2.02;
    amplitude *= 0.5;
  }
  return total;
}

void main() {
  vec2 uv = gl_FragCoord.xy / u_resolution;
  float aspect = u_resolution.x / u_resolution.y;

  // Corrected for aspect so the field does not stretch on wide viewports.
  vec2 p = vec2(uv.x * aspect, uv.y);

  float t = u_time * 0.13;

  // Domain warp: the field is sampled through an offset of itself. Without it
  // four octaves of value noise slide past as a flat texture; with it the field
  // folds into itself and reads as something moving in depth.
  vec2 warp = vec2(fbm(p * 1.6 + t), fbm(p * 1.6 + vec2(4.3, 1.9) - t));

  // The warp is the only thing that moved at first, and a change in the warp
  // reaches the output heavily damped, so the field crawled. The direct drift
  // is what actually makes the motion legible.
  float field = fbm(p * 1.9 + warp * 1.4 + vec2(0.0, t * 0.5));

  // Anchored on the same point as the CSS gradient underneath (12% from the
  // left, 28% from the top, and gl_FragCoord counts up from the bottom), so the
  // two layers read as one light source rather than two.
  vec2 anchor = vec2(0.12 * aspect, 0.72);
  float falloff = 1.0 - smoothstep(0.0, 1.25, distance(p, anchor));

  vec3 ember = vec3(0.55, 0.30, 0.12);
  vec3 gold = vec3(0.82, 0.62, 0.28);
  vec3 color = mix(ember, gold, smoothstep(0.35, 0.85, field));

  // The ceiling here is the contrast budget rather than taste. Measured per
  // element against the hero's own type, this alpha leaves every one of them
  // above its WCAG threshold: the tightest is the 20px paragraph at 5.35:1
  // against the 4.5:1 it needs, down from 6.56:1 with no bloom at all. The
  // brightest pixel the field can produce is hotter than that, but it falls in
  // the empty upper left where no text sits. Raising this spends that margin.
  float alpha = smoothstep(0.28, 0.78, field) * falloff * 0.40;

  gl_FragColor = vec4(color, alpha);
}
`;

/**
 * The field is smooth, so it survives being rendered at half resolution and
 * upscaled, which quarters the fragment count. The DPR cap does the same job on
 * phones, where 3x would otherwise be drawn and thrown away.
 */
const RENDER_SCALE = 0.5;
const MAX_DPR = 1.5;

export const HeroShader = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const reduced = useReducedMotion();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const gl = canvas.getContext("webgl", {
      // Straight (not premultiplied) alpha, so the browser composites this over
      // the CSS gradient and the section's dark ground beneath it.
      alpha: true,
      premultipliedAlpha: false,
      antialias: false,
      depth: false,
      stencil: false,
      powerPreference: "low-power",
    });
    if (!gl) return;

    const program = gl.createProgram();
    const vertexShader = gl.createShader(gl.VERTEX_SHADER);
    const fragmentShader = gl.createShader(gl.FRAGMENT_SHADER);
    if (!program || !vertexShader || !fragmentShader) return;

    gl.shaderSource(vertexShader, VERTEX_SOURCE);
    gl.compileShader(vertexShader);
    gl.shaderSource(fragmentShader, FRAGMENT_SOURCE);
    gl.compileShader(fragmentShader);
    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);

    // A compile failure in either stage surfaces here as a link failure, so this
    // single check is the whole guard.
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) return;
    gl.useProgram(program);

    // One oversized triangle rather than two triangles for a quad: it covers the
    // clip volume with three vertices and no seam down the diagonal.
    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    const position = gl.getAttribLocation(program, "a_position");
    gl.enableVertexAttribArray(position);
    gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);

    const resolutionLocation = gl.getUniformLocation(program, "u_resolution");
    const timeLocation = gl.getUniformLocation(program, "u_time");

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, MAX_DPR);
      const width = Math.max(1, Math.round(canvas.clientWidth * dpr * RENDER_SCALE));
      const height = Math.max(1, Math.round(canvas.clientHeight * dpr * RENDER_SCALE));
      if (canvas.width === width && canvas.height === height) return;
      canvas.width = width;
      canvas.height = height;
      gl.viewport(0, 0, width, height);
      gl.uniform2f(resolutionLocation, width, height);
    };

    const draw = (seconds: number) => {
      resize();
      gl.uniform1f(timeLocation, seconds);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    };

    let frame = 0;
    let clock = 0;
    let last = 0;

    const loop = (now: number) => {
      // Accumulated rather than derived from a start timestamp, so a pause adds
      // nothing to the clock and the field resumes where it stopped instead of
      // jumping forward by the time the tab spent hidden.
      clock += (now - last) / 1000;
      last = now;
      draw(clock);
      frame = requestAnimationFrame(loop);
    };

    const start = () => {
      if (frame) return;
      last = performance.now();
      frame = requestAnimationFrame(loop);
    };

    const stop = () => {
      cancelAnimationFrame(frame);
      frame = 0;
    };

    const handleVisibility = () => {
      if (document.hidden) stop();
      else start();
    };

    // Under reduced motion the field is still drawn, just never advanced: the
    // shape and warmth are the design, the drift is the animation.
    const handleResize = () => draw(clock);

    if (reduced) {
      draw(0);
      window.addEventListener("resize", handleResize);
    } else {
      start();
      document.addEventListener("visibilitychange", handleVisibility);
    }

    return () => {
      stop();
      window.removeEventListener("resize", handleResize);
      document.removeEventListener("visibilitychange", handleVisibility);
      gl.deleteBuffer(buffer);
      gl.deleteProgram(program);
      gl.deleteShader(vertexShader);
      gl.deleteShader(fragmentShader);
      // Frees the drawing buffer immediately instead of waiting for the GC to
      // collect the canvas, which matters because route changes unmount this.
      gl.getExtension("WEBGL_lose_context")?.loseContext();
    };
  }, [reduced]);

  return <canvas ref={canvasRef} className="absolute inset-0 block h-full w-full" />;
};
