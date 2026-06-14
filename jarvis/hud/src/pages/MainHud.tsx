import { useCallback, useEffect, useRef, useState } from "react";
import { Caption } from "../components/Caption";
import { ConnectorArray } from "../components/ConnectorArray";
import { Console, type Message } from "../components/Console";
import { ContextFeed } from "../components/ContextFeed";
import { GraphView } from "../components/GraphView";
import { OperatorPanel } from "../components/OperatorPanel";
import { Reactor } from "../components/Reactor";
import type { Answer, Citation } from "../data/types";
import { useClaudeUplink } from "../hooks/useClaudeUplink";
import type { GraphHook } from "../hooks/useGraph";
import { useReactorState } from "../hooks/useReactorState";
import { useSpeech } from "../hooks/useSpeech";
import { useVoiceBridge } from "../hooks/useVoiceBridge";

const WELCOME: Message = {
  role: "j",
  text:
    "El Niño interface online. I answer from the live dev_graph — every structural claim cites its " +
    "canonical_id and evidence-class, and the matched node + neighborhood render in the DEV_GRAPH VIEW. " +
    'Try "what depends on the Gold Decision Builder?" or "what does ADR-010 decide?".',
};

export function MainHud({ graph, pendingQuery, onConsumed }: { graph: GraphHook; pendingQuery: string | null; onConsumed: () => void }) {
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

  // consume a cross-page query (a graph node / flow stage clicked on another tab)
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
    <div className="grid3">
      <div className="col">
        <div className="panel core">
          <div className="ph"><span className="pt">REACTOR CORE</span><span className="tag c">VOICE</span></div>
          <div className="core">
            <Reactor state={reactor.state} onTap={onMic} />
            <Caption state={reactor.state} text="" />
          </div>
        </div>
        <OperatorPanel />
      </div>

      <div className="col">
        <div className="panel">
          <Console
            messages={messages}
            onSubmit={submit}
            onCite={(id) => submit(id)}
            onMic={onMic}
            micActive={reactor.state === "listen"}
            voiceOn={voiceOn}
            onToggleVoice={() => setVoiceOn((v) => !v)}
          />
        </div>
      </div>

      <div className="col">
        <ContextFeed answer={answer} onRelated={submit} />
        <div className="panel gv-wrap">
          <div className="ph">
            <span className="pt">DEV_GRAPH VIEW</span>
            <span className={`tag ${graph.source === "live" ? "g" : "a"}`}>
              {graph.source === "live" ? "● LIVE BRIDGE" : graph.source === "offline" ? "◐ OFFLINE graph.json" : "✕ NO GRAPH"}
            </span>
          </div>
          {answer && answer.subgraph.nodes.length > 0 ? (
            <GraphView graph={answer.subgraph} focus={answer.focus} onNodeClick={(_, name) => submit(name)} />
          ) : (
            <div className="gv-empty">Ask a structural question and the matched node + neighborhood render here. Click a node to expand it.</div>
          )}
        </div>
        <ConnectorArray
          source={graph.source}
          health={graph.health}
          nodeCount={graph.nodeCount}
          voiceBridgeOnline={voiceBridge.online}
          uplinkAvailable={uplink.available}
        />
      </div>
    </div>
  );
}
