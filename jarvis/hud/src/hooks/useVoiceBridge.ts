import { useCallback, useEffect, useState } from "react";
import { API_BASE } from "../data/api";

// useVoiceBridge — client for the local Whisper/Piper voice router folded into the bridge
// (Stage 5: GET /voice/health, POST /voice/stt, POST /voice/tts). Until that backend exists the
// hook simply reports offline and the UI falls back to useSpeech (Web Speech).

interface VoiceBridge {
  online: boolean;
  stt: (audio: Blob) => Promise<string | null>;
  tts: (text: string) => Promise<Blob | null>;
}

export function useVoiceBridge(): VoiceBridge {
  const [online, setOnline] = useState(false);

  useEffect(() => {
    let alive = true;
    fetch(`${API_BASE}/voice/health`, { cache: "no-store" })
      .then((r) => (r.ok ? r.json() : null))
      .then((j) => {
        if (alive) setOnline(!!(j && j.ok));
      })
      .catch(() => {
        if (alive) setOnline(false);
      });
    return () => {
      alive = false;
    };
  }, []);

  const stt = useCallback(async (audio: Blob): Promise<string | null> => {
    try {
      const fd = new FormData();
      fd.append("audio", audio, "clip.webm");
      const r = await fetch(`${API_BASE}/voice/stt`, { method: "POST", body: fd });
      if (!r.ok) return null;
      const j = (await r.json()) as { text?: string };
      return j.text ?? null;
    } catch {
      return null;
    }
  }, []);

  const tts = useCallback(async (text: string): Promise<Blob | null> => {
    try {
      const r = await fetch(`${API_BASE}/voice/tts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      if (!r.ok) return null;
      return await r.blob();
    } catch {
      return null;
    }
  }, []);

  return { online, stt, tts };
}
