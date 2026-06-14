import { useCallback, useRef } from "react";

// useSpeech — the browser Web Speech path (Chrome/Edge). It is the always-available voice
// fallback; the Whisper/Piper bridge (useVoiceBridge, Stage 5) takes precedence when up.

interface SpeechApi {
  supported: boolean;
  speak: (text: string, onState?: (s: "speak" | "idle") => void) => void;
  cancel: () => void;
  listen: (onResult: (text: string) => void, onState?: (s: "listen" | "idle") => void) => void;
  stopListening: () => void;
}

type RecognitionLike = {
  lang: string;
  interimResults: boolean;
  onresult: ((e: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
};

export function useSpeech(): SpeechApi {
  const recRef = useRef<RecognitionLike | null>(null);

  const supported =
    typeof window !== "undefined" &&
    "speechSynthesis" in window &&
    ("SpeechRecognition" in window || "webkitSpeechRecognition" in window);

  const speak = useCallback((text: string, onState?: (s: "speak" | "idle") => void) => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
    const clean = text.replace(/\[[A-Z]+-\d+[^\]]*\]/g, "").replace(/[·•▶✔⛔◐□◇═◈]/g, " ");
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(clean);
    u.onstart = () => onState?.("speak");
    u.onend = () => onState?.("idle");
    u.onerror = () => onState?.("idle");
    window.speechSynthesis.speak(u);
  }, []);

  const cancel = useCallback(() => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) window.speechSynthesis.cancel();
  }, []);

  const listen = useCallback(
    (onResult: (text: string) => void, onState?: (s: "listen" | "idle") => void) => {
      const w = window as unknown as { SpeechRecognition?: new () => RecognitionLike; webkitSpeechRecognition?: new () => RecognitionLike };
      const Ctor = w.SpeechRecognition || w.webkitSpeechRecognition;
      if (!Ctor) return;
      const rec = new Ctor();
      recRef.current = rec;
      rec.lang = "en-US";
      rec.interimResults = false;
      rec.onresult = (e) => {
        const t = e.results?.[0]?.[0]?.transcript ?? "";
        if (t.trim()) onResult(t.trim());
      };
      rec.onend = () => onState?.("idle");
      onState?.("listen");
      rec.start();
    },
    [],
  );

  const stopListening = useCallback(() => {
    try {
      recRef.current?.stop();
    } catch {
      /* ignore */
    }
  }, []);

  return { supported, speak, cancel, listen, stopListening };
}
