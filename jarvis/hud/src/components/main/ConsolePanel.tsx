import { useEffect, useRef, useState } from "react";
import type { Citation } from "../../data/types";

// ConsolePanel — the EL NIÑO CONSOLE, re-skinned to the TARGET (lines 514-531) but kept as the
// graph-grounded console: answers come from the dev_graph router / GraphRAG uplink, each cited and
// fail-closed (ADR-010). The .clog ◈/› terminal styling is the TARGET's; the hints/placeholder are
// graph queries so the console actually answers them (a deliberate fold over the vanilla KB topics).
export interface Message {
  role: "u" | "j";
  text: string;
  citations?: Citation[];
}

const HINTS = [
  "what depends on the Gold Decision Builder?",
  "what tests cover the Feature Builder?",
  "what does ADR-010 decide?",
  "Paper Runtime API",
  "Guardrail Engine",
  "ADR-009",
];

interface Props {
  messages: Message[];
  onSubmit: (q: string) => void;
  onCite: (id: string) => void;
  onMic: () => void;
  micActive: boolean;
  voiceOn: boolean;
  onToggleVoice: () => void;
}

export function ConsolePanel({ messages, onSubmit, onCite, onMic, micActive, voiceOn, onToggleVoice }: Props) {
  const [val, setVal] = useState("");
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = logRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages]);

  const submit = () => {
    const q = val.trim();
    if (!q) return;
    setVal("");
    onSubmit(q);
  };

  return (
    <div className="console">
      <div className="ph">
        <span className="pt">EL NIÑO CONSOLE — TALK TO THE SYSTEM</span>
        <span className="tag g">VOICE · GRAPH-GROUNDED · CITED</span>
      </div>
      <div className="clog" ref={logRef}>
        {messages.map((m, i) => (
          <div key={i} className={m.role}>
            {m.text}
            {m.role === "j" && m.citations && m.citations.length > 0 && (
              <div className="rel" style={{ marginTop: 6 }}>
                {m.citations.map((c) => (
                  <span key={c.id} className="relc" title={`evidence: ${c.confidence}`} onClick={() => onCite(c.id)}>
                    {c.id}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
      <div className="cin">
        <input
          value={val}
          onChange={(e) => setVal(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          type="text"
          placeholder='e.g. "what depends on the Gold Decision Builder?" · "what does ADR-010 decide?"'
          autoComplete="off"
        />
        <button className="cbtn" onClick={submit}>SEND</button>
        <button className={`cbtn mic${micActive ? " live" : ""}`} title="Voice input — tap and speak (Chrome / Edge)" onClick={onMic}>🎙</button>
        <button className={`cbtn mic${voiceOn ? "" : " mute"}`} title="Spoken replies on / off" onClick={onToggleVoice}>🔊</button>
      </div>
      <div className="hints">
        {HINTS.map((h) => (
          <span key={h} className="hint" onClick={() => onSubmit(h)}>{h}</span>
        ))}
      </div>
    </div>
  );
}
