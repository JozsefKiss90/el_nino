---
type: system
domain: systems
created: 2026-05-09
updated: 2026-05-09
status: active
aliases: [LLM Failure Modes, AI Trading Risks]
confidence: confirmed
tags: [system, risk]
---

# LLM Failure Modes in Trading

## Definition

Comprehensive catalog of ways LLM-based trading systems can fail, with specific focus on failure modes unique to or amplified by AI agent architectures.

## Purpose

Proactive risk identification. Every failure mode maps to a mitigation strategy. This page is the canonical reference for "what can go wrong" beyond standard market risk.

## Architecture Role

Cross-cutting risk layer. Feeds into [[Autonomous Trading Risk Model]], [[Guardrail Architecture]], and [[Agent Self-Verification]].

## Failure Mode Catalog

### 1. Hallucinated Signals

**Description**: LLM generates technical analysis conclusions not supported by actual data. May invent indicator values, misread chart patterns, or fabricate price levels.

**Severity**: Critical
**Probability**: Medium (higher with weaker models, lower with Opus-class)
**Mitigation**:
- Always compute indicators programmatically, never ask the LLM to "estimate" values
- [[Signal Confirmation]] — require multiple independent indicators
- Validate signals against raw API data before execution
- Never trust LLM-generated price targets without verification

### 2. Overfitting

**Description**: Strategy memorizes past patterns instead of learning general rules. Manifests as suspiciously high backtest win rates (>65%) that collapse in live trading.

**Severity**: High
**Probability**: High (especially in first iterations)
**Mitigation**:
- [[Walk-Forward Optimization]] — split data into in-sample/out-of-sample
- Healthy skepticism of backtest results >65% win rate
- Focus on risk-reward ratio (1:2+) over win rate
- Regular out-of-sample validation

**Evidence**: Initial backtest showed 74% win rate → suspiciously high → walk-forward validation reduced to 53% with 1:2.3 risk-reward → "that math is extremely profitable and that's what an actual edge looks like"

Source: [[SRC - Claude Stock Trader]]

### 3. Stale Context

**Description**: Agent acts on outdated information because memory files haven't been updated, market data is cached, or research is from a previous session.

**Severity**: High
**Probability**: Medium
**Mitigation**:
- Timestamp all memory files
- Always fetch fresh market data at routine start
- Validate data freshness before trading decisions
- Clear stale cache on routine wake

### 4. Context Overflow / Budget Exhaustion

**Description**: Agent reads too many files, consuming the token budget before completing its task. Results in truncated analysis, missed information, or incomplete execution.

**Severity**: Medium
**Probability**: Medium (grows with memory file size)
**Mitigation**:
- [[Context Budget Engineering]] — plan token allocation per stage
- Selective file reading (only what's needed for current routine)
- Memory file compaction / rolling windows
- Prioritize structural memory over operational history

### 5. Delayed Execution

**Description**: Time gap between signal generation and order placement. In fast-moving markets, the entry conditions may no longer be valid.

**Severity**: Medium
**Probability**: Medium
**Mitigation**:
- Minimize pipeline stages between signal and execution
- Use limit orders with tight validity windows
- Time-validate signals immediately before execution
- Consider market vs. limit order tradeoffs

### 6. Invalid Assumptions

**Description**: LLM reasons about market behavior using incorrect financial assumptions. May misunderstand market microstructure, confuse asset classes, or apply wrong frameworks.

**Severity**: High
**Probability**: Low-Medium
**Mitigation**:
- Codify strategy rules explicitly (not implied)
- Hard-code risk parameters (don't let LLM negotiate them)
- Separate LLM judgment from mechanical rule execution
- Regular human review of decision reasoning

### 7. Eager Agent Syndrome

**Description**: Without guardrails, LLM agents are biased toward action. They want to trade even when standing aside is optimal.

**Severity**: Medium
**Probability**: High
**Mitigation**:
- Explicit "do nothing" as a valid action
- [[Guardrail Architecture]] — hard limits on trade frequency
- High conviction threshold for entry
- "If you don't give it guardrails it might just start to go off the rails"

Source: [[SRC - Claude Opus Trader]]

### 8. Memory Corruption

**Description**: Inconsistent state in memory files due to interrupted writes, concurrent access, or malformed data.

**Severity**: High
**Probability**: Low
**Mitigation**:
- Sequential routine scheduling (no concurrent runs)
- Atomic file writes
- Git-based versioning for rollback
- Startup validation of memory file integrity

### 9. API Key Exposure

**Description**: Agent accidentally logs, commits, or exposes API credentials in output, files, or git history.

**Severity**: Critical
**Probability**: Low-Medium
**Mitigation**:
- [[API Credential Isolation]] — environment variables only
- Never store keys in `.env` files committed to git
- Disable withdrawal permissions on exchange APIs
- Regular key rotation

**Evidence**: During migration, agent template contained live Alpaca keys in a file that was being committed.

Source: [[SRC - Claude Opus Trader]]

### 10. Strategy Drift

**Description**: Gradual, unintended changes to strategy parameters as the LLM "improves" the system over many iterations without human oversight.

**Severity**: Medium
**Probability**: Medium
**Mitigation**:
- Version-controlled strategy files
- Diff review on strategy changes
- Periodic human review of strategy evolution
- Immutable core guardrail parameters

### 11. Context Window Rot

**Description**: Quality of LLM reasoning degrades when the context window is heavily loaded, even within limits. Early information receives less attention than recent information.

**Severity**: Medium
**Probability**: Medium
**Mitigation**:
- Keep critical information (strategy, guardrails) in CLAUDE.md (always loaded first)
- Fresh context via `/clear` between tasks
- Summarize and condense before context resets
- "Treat tokens like money"

Source: [[SRC - Claude Opus Trader]]

### 12. Benchmark Misinterpretation

**Description**: Confusing "agentic financial analysis" benchmark scores with trading ability. The benchmark tests fundamentals-driven thesis writing, not technical analysis or day trading.

**Severity**: Low
**Probability**: Medium
**Mitigation**:
- Understand what benchmarks actually measure
- Match strategy type to model capabilities
- Don't day trade based on financial analysis benchmarks

Source: [[SRC - Claude Opus Trader]] — "this benchmark rewards models that can digest filings and write coherent fundamentals driven theses... not day trading"

## Dependencies

- [[Autonomous Trading Risk Model]]
- [[Guardrail Architecture]]
- [[Context Budget Engineering]]
- [[Agent Memory Architecture]]

## Related Concepts

- [[Walk-Forward Optimization]]
- [[Overfitting Detection]]
- [[Signal Confirmation]]
- [[Agent Self-Verification]]
- [[Paper Trading]]

## Open Questions

- Can LLM self-detection of hallucinated signals be reliable enough?
- Optimal human-in-the-loop frequency for catching strategy drift?
- How to quantify context window rot impact on trading quality?

## Future Extensions

- Automated failure mode detection and alerting
- LLM confidence calibration for trading decisions
- Ensemble models for cross-validation of signals
- Formal verification of guardrail constraints
- Red-teaming framework for trading agent adversarial testing

## Source References

- Source: [[SRC - Claude Stock Trader]] — overfitting evidence (74% → 53%)
- Source: [[SRC - Claude Opus Trader]] — eager agent, context budget, benchmark misinterpretation, key exposure
- Source: [[SRC - Claude TradingView Integration]] — safety filter blocking, execution validation
- Source: [[SRC - Claude Cowork Trader]] — API security, exchange connection risks
