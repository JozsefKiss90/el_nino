import type { Answer } from "../../data/types";

// ContextFeed — the QUERY ROUTER panel (TARGET lines 536-539). Answer-driven: shows which node
// matched, its evidence-class, the source, and related threads worth pulling (click to ask).
export function ContextFeed({ answer, onRelated }: { answer: Answer | null; onRelated: (q: string) => void }) {
  return (
    <div className="panel">
      <div className="ph"><span className="pt">CONTEXT FEED</span><span className="tag c">QUERY ROUTER</span></div>
      {!answer ? (
        <div className="ctx-empty">
          Ask something and I'll show which node matched, how confident the match was, the data source — and
          related threads worth pulling. This is where the conversation gets its arc.
        </div>
      ) : (
        <>
          <div className="ctx-topic">{answer.title}</div>
          <div className="ctx-meta">
            <span className={`tag ${answer.confClass}`}>
              {answer.matched ? "EVIDENCE" : "MATCH"}: {answer.evidenceClass}
            </span>
            <span className="tag c">{answer.source}</span>
          </div>
          {answer.related.length > 0 && (
            <div className="rel">
              {answer.related.map((r) => (
                <span key={r} className="relc" onClick={() => onRelated(r)}>{r}</span>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
