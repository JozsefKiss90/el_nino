# Agent Self-Verification

## Definition

The capacity of an AI agent to verify its own outputs, detect errors in its reasoning, and validate decisions before execution. A key capability of Opus 4.6 for autonomous trading.

## Purpose

Reduces reliance on human oversight by enabling the agent to catch its own mistakes. Critical for autonomous operation where human review is delayed or absent.

## Architecture Role

Quality assurance layer in [[Trading Engine Pipeline]]. Supports [[Guardrail Architecture]] by adding internal validation.

## Self-Verification in Opus 4.6

> "4.7 was built for full throttle agentic work, judgment over ambiguity, and self-verifying outputs."

Source: [[SRC - Claude Opus Trader]]

## Verification Patterns

### Signal Verification
Before executing a trade, verify:
- Indicator values were computed (not estimated)
- All [[Signal Confirmation]] conditions actually met
- Position sizing within [[Guardrail Architecture]] limits
- Market data is fresh (not stale)

### Memory Verification
Before writing memory files, verify:
- Trade log entries are complete and accurate
- Portfolio state reflects actual positions
- No contradictory entries

### Execution Verification
After placing an order, verify:
- Order was accepted by broker/exchange
- Fill price within expected range
- Stop-loss was placed
- Trade was logged

## Inputs

- Agent's proposed action
- Verification criteria (from strategy rules, guardrails)
- System state

## Outputs

- Verified action (proceed) or flagged issue (halt/modify)

## Dependencies

- [[Guardrail Architecture]] — verification criteria
- [[Signal Confirmation]] — signal validation
- [[Trading Engine Pipeline]] — execution context

## Failure Modes

- Agent verifies against wrong criteria
- Self-verification consumes excessive context budget
- False confidence in self-verification → missed errors
- Verification logic itself may contain errors

## Related Concepts

- [[Guardrail Architecture]]
- [[LLM Failure Modes in Trading]]
- [[Signal Confirmation]]
- [[Supervisor Decision Engine]]

## Source References

- Source: [[SRC - Claude Opus Trader]] — Opus 4.6 self-verifying outputs capability
