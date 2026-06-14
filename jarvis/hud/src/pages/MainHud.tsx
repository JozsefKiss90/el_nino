import { useCallback, useEffect, useRef, useState } from "react";
import { ConnectorArray } from "../components/main/ConnectorArray";
import { ConsolePanel, type Message } from "../components/main/ConsolePanel";
import { ContextFeed } from "../components/main/ContextFeed";
import { DecisionCore } from "../components/main/DecisionCore";
import { EpochTrack } from "../components/main/EpochTrack";
import { KnowledgeGraph } from "../components/main/KnowledgeGraph";
import { LiveMarketIntel } from "../components/main/LiveMarketIntel";
import { OperatorPanel } from "../components/main/OperatorPanel";
import { StrategyStrip } from "../components/main/StrategyStrip";
import { SystemVitals } from "../components/main/SystemVitals";
import { TruthCorpus } from "../components/main/TruthCorpus";
import type { Answer, Citation } from "../data/types";
import { useClaudeUplink } from "../hooks/useClaudeUplink";
import type { GraphHook } from "../hooks/useGraph";
import { useReactorState } from "../hooks/useReactorState";
import { useSpeech } from "../hooks/useSpeech";
import { useVoiceBridge } from "../hooks/useVoiceBridge";

// MainHud (#pg-main) — ported 1:1 from the TARGET (jarvis/sources/el_nino_jarvis_interface (6).html,
// lines 434-593): the operator/vitals/corpus/knowledge-graph left column, the DECISION CORE (reactor
// + orbits + readouts + console) center, the context/market/connectors/epoch right column, and the
// doctrine strip. The Console + KnowledgeGraph + ContextFeed + ConnectorArray are the live, graph-
// grounded, read-only versions (ADR-010); the orchestration below is preserved from Stage 4.
const WELCOME: Message = {
  role: "j",
  text:
    "El Niño interface online. I answer from the live dev_graph — every structural claim cites its " +
    "canonical_id and evidence-class, and the matched node + neighborhood render in the KNOWLEDGE GRAPH. " +
    'Try "what depends on the Gold Decision Builder?" or "what does ADR-010 decide?".',
};

export function MainHud({
  graph,
  corpus,
  pendingQuery,
  onConsumed,
}: {
  graph: GraphHook;
  corpus: { count: number; day: number };
  pendingQuery: string | null;
  onConsumed: () => void;
}) {
  const [messages, setMessages] = useState<Message[]>([WELCOME]);
  const [answer, setAnswer] = useState<Answer | null>(null);
  const [voiceOn, setVoiceOn] = useState(false);
  const reactor = useReactorState();
  const speech = useSpeech();
  const voiceBridge = useVoiceBridge();
  const uplink = useClaudeUplink();
  const submitRef = useRef<(q: string) => void>(() => {});

  const speak = useCallback(
    (text: string) => {
      if (!voiceOn) return;
      if (voiceBridge.online) {
        voiceBridge.tts(text).then((b) => {
          if (b) {
            const a = new Audio(URL.createObjectURL(b));
            reactor.speak();
            a.onended = () => reactor.idle();
            a.onerror = () => reactor.idle();
            a.play().catch(() => reactor.idle());
          } else {
            speech.speak(text, (s) => (s === "speak" ? reactor.speak() : reactor.idle()));
          }
        });
      } else {
        speech.speak(text, (s) => (s === "speak" ? reactor.speak() : reactor.idle()));
      }
    },
    [voiceOn, voiceBridge, speech, reactor],
  );

  const submit = useCallback(
    async (q: string) => {
      setMessages((m) => [...m, { role: "u", text: q }]);

      // Stage 4: try the GraphRAG /ask uplink first; it returns null on 503 (no API key) or error,
      // in which case we fall back to the offline pure-router answer (Stage 2/3). Read-only either way.
      const up = await uplink.ask(q);
      if (up) {
        const byId = new Map(up.subgraph.nodes.map((n) => [n.id, n] as const));
        const citations: Citation[] = up.citations.map((id) => ({ id, confidence: byId.get(id)?.confidence ?? "" }));
        const related = up.subgraph.nodes.filter((n) => n.id !== up.citations[0]).map((n) => n.name).slice(0, 6);
        const a: Answer = {
          matched: up.citations.length > 0,
          focus: up.citations[0],
          title: "GRAPHRAG · CLAUDE",
          text: up.answer,
          citations,
          evidenceClass: "claude-grounded",
          confClass: "g",
          source: "/ask · Claude over subgraph",
          related,
          subgraph: up.subgraph,
        };
        setMessages((m) => [...m, { role: "j", text: a.text, citations }]);
        setAnswer(a);
        speak(a.text);
        return;
      }

      const a = await graph.ask(q);
      if (a) {
        setMessages((m) => [...m, { role: "j", text: a.text, citations: a.citations }]);
        setAnswer(a);
        speak(a.text);
      } else {
        setMessages((m) => [...m, { role: "j", text: "The graph isn't loaded yet — give it a moment and retry." }]);
      }
    },
    [graph, uplink, speak],
  );
  submitRef.current = submit;

  // consume a cross-page query (a graph node / flow stage / pipeline module clicked on another tab)
  useEffect(() => {
    if (pendingQuery) {
      submitRef.current(pendingQuery);
      onConsumed();
    }
  }, [pendingQuery, onConsumed]);

  const onMic = useCallback(() => {
    if (reactor.state === "listen") {
      speech.stopListening();
      reactor.idle();
      return;
    }
    if (speech.supported) {
      speech.listen((t) => submitRef.current(t), (s) => (s === "listen" ? reactor.listen() : reactor.idle()));
    }
  }, [reactor, speech]);

  // Escape silences
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        speech.cancel();
        speech.stopListening();
        reactor.idle();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [speech, reactor]);

  return (
    <div className="page show" id="pg-main">
      <div className="main">
        {/* LEFT */}
        <div className="col">
          <OperatorPanel />
          <SystemVitals />
          <TruthCorpus corpus={corpus} />
          <KnowledgeGraph answer={answer} onQuery={submit} />
        </div>

        {/* CENTER — REACTOR + CONSOLE */}
        <div className="panel core">
          <div className="ph" style={{ width: "100%" }}>
            <span className="pt">DECISION CORE — LAST FULL L3 RUN · SNAPSHOT 2026-03-15</span>
            <span className="tag g">VERDICT: ADMIT</span>
          </div>
          <DecisionCore reactorState={reactor.state} onReactorTap={onMic} />
          <ConsolePanel
            messages={messages}
            onSubmit={submit}
            onCite={(id) => submit(id)}
            onMic={onMic}
            micActive={reactor.state === "listen"}
            voiceOn={voiceOn}
            onToggleVoice={() => setVoiceOn((v) => !v)}
          />
        </div>

        {/* RIGHT */}
        <div className="col">
          <ContextFeed answer={answer} onRelated={submit} />
          <LiveMarketIntel />
          <ConnectorArray source={graph.source} voiceBridgeOnline={voiceBridge.online} uplinkAvailable={uplink.available} />
          <EpochTrack />
        </div>
      </div>

      <StrategyStrip />
    </div>
  );
}
