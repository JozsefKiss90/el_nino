import { useEffect, useRef } from "react";

// MatrixRain — the #fxRain digital-rain canvas behind the HUD, ported verbatim from the TARGET
// (jarvis/frontend/EL NINO JARVIS Cyberpunk.html, the second <script>). Fixed full-screen; its
// opacity / blend / z-index are set in theme.css (#fxRain), so it sits behind .wrap. Honors
// prefers-reduced-motion (single static wash, no interval).
export function MatrixRain() {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const c = ref.current;
    if (!c) return;
    const x = c.getContext("2d");
    if (!x) return;

    const fs = 16;
    let cols = 0;
    let drops: number[] = [];
    const glyphs = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホ0123456789=+*<>/[]{}$#%";

    const resize = () => {
      c.width = window.innerWidth;
      c.height = window.innerHeight;
      cols = Math.ceil(c.width / fs);
      drops = [];
      for (let i = 0; i < cols; i++) drops[i] = Math.floor(Math.random() * -60);
    };
    resize();
    window.addEventListener("resize", resize);

    const reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const frame = () => {
      x.fillStyle = "rgba(5,3,16,0.09)";
      x.fillRect(0, 0, c.width, c.height);
      x.font = `${fs}px 'Share Tech Mono', monospace`;
      x.textBaseline = "top";
      for (let i = 0; i < cols; i++) {
        const ch = glyphs.charAt(Math.floor(Math.random() * glyphs.length));
        const y = drops[i] * fs;
        x.fillStyle = "rgba(190,255,225,0.92)";
        x.fillText(ch, i * fs, y);
        x.fillStyle = "rgba(25,240,160,0.55)";
        x.fillText(ch, i * fs, y - fs);
        if (y > c.height && Math.random() > 0.975) drops[i] = 0;
        drops[i]++;
      }
    };

    let id: number | undefined;
    if (!reduce) {
      id = window.setInterval(frame, 58);
    } else {
      x.fillStyle = "rgba(5,3,16,0.5)";
      x.fillRect(0, 0, c.width, c.height);
    }

    return () => {
      window.removeEventListener("resize", resize);
      if (id !== undefined) window.clearInterval(id);
    };
  }, []);

  return <canvas id="fxRain" aria-hidden="true" ref={ref} />;
}
