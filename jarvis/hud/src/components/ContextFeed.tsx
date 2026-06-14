import type { Answer } from "../data/types";

// ContextFeed — the query-router panel: the matched node, its evidence-class, the source, and the
// related threads (click to pull). Mirrors the Stage-2 console's CONTEXT FEED.
export function ContextFeed({ answer, onRelated }: { answer: Answer | null; onRelated: (q: string) => void }) {
  return (
    <div className="panel">
      <div className="ph">
        <span className="pt">CONTEXT FEED</span>
        <span className="tag c">QUERY ROUTER</span>
      </div>
      {!answer ? (
        <div className="gv-empty">
          Ask something and I'll show which node matched, its evidence-class, the source — and related
          threads worth pulling.
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
            <>
              <div className="lblm">RELATED THREADS</div>
              <div className="rel">
                {answer.related.map((r) => (
                  <span key={r} className="relc" onClick={() => onRelated(r)}>{r}</span>
                ))}
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
}
