---
type: concept
domain: concepts
created: 2026-05-15
updated: 2026-05-15
status: active
aliases: [Options, Derivatives Trading]
confidence: single-source
tags: [concept]
---

# Options Trading

## Definition

Financial derivatives contracts giving the holder the right — but not the obligation — to buy or sell an underlying asset at a specified price (strike price) before a specified date (expiration). Two types: call options (right to buy) and put options (right to sell).

## Purpose

Extends the trading ecosystem beyond equities-only execution into derivatives-based income generation and risk management. Enables strategies like the [[Wheel Strategy]] that collect premiums regardless of market direction.

## Architecture Role

Expands the asset class coverage in [[Trading Engine Pipeline]]. Options-based strategies represent an alternative to indicator-based momentum/trend strategies (see [[Signal Confirmation]]). Requires explicit enablement in [[Guardrail Architecture]] — some configurations prohibit options entirely.

## Core Concepts

### Call Option

Right to **buy** a stock at a locked-in price before expiration.

> Analogy: "Putting a deposit on an apartment. You pay $500 to lock in the rent for $2,000 for 30 days. If the rent price jumps to $2,500, you got a deal. If not, you lost the $500 deposit."

Example: Apple at $200, buy a call with $210 strike. If Apple reaches $230 before expiration, buy at $210, pocket $20/share difference. If Apple stays below $210, contract expires, lose the premium paid.

Source: [[SRC - Claude Alpaca Trader]]

### Put Option

Right to **sell** a stock at a locked-in price before expiration. Functions as insurance against price drops.

Example: Own Apple at $200, buy a put with $190 strike. If Apple drops to $170, sell at $190 instead of $170. The put protected against the drop.

Source: [[SRC - Claude Alpaca Trader]]

### Premium

The price paid (by buyer) or received (by seller) for the option contract. This is the "insurance payment."

> "Someone pays you for a contract and most of the time that contract expires without anything happening and you keep the money."

Source: [[SRC - Claude Alpaca Trader]]

### Strike Price

The locked-in buy/sell price specified in the contract. Determines the threshold at which the option becomes profitable.

### Expiration

The date by which the option must be exercised or it expires worthless. Typical range for income strategies: 2-4 weeks out.

Source: [[SRC - Claude Alpaca Trader]]

## Selling Options (Income Generation)

The source demonstrates selling options as the primary approach — acting as "the insurance company" rather than buying insurance:

- Collect premiums upfront
- Most contracts expire without anything happening
- Seller keeps the premium when contract expires worthless
- "Insurance companies make billions doing this — they collect premiums from millions of people and pay out on a small percentage of claims. The math works in their favor over time."

This is the foundation of the [[Wheel Strategy]]: sell puts to enter, sell calls on owned shares, collect premium at every stage.

Source: [[SRC - Claude Alpaca Trader]]

## Insurance Analogy

| Insurance | Options |
|-----------|---------|
| Monthly premium payment | Option premium |
| Right to file a claim | Right to buy/sell at strike |
| Policy expiration date | Contract expiration |
| Nothing happens → insurer keeps money | Stock doesn't hit strike → seller keeps premium |

Source: [[SRC - Claude Alpaca Trader]]

## Inputs

- Underlying stock price
- Strike price selection
- Expiration date selection
- Premium amount (market-determined)
- Account cash balance (for cash-secured puts)
- Existing share positions (for covered calls)

## Outputs

- Premium income (for sellers)
- Hedged position (for buyers)
- Assignment/exercise events (forced buy/sell at strike)

## Dependencies

- [[Alpaca API]] — options-enabled brokerage account
- [[Position Sizing]] — cash requirements for selling puts, share requirements for selling calls
- [[Guardrail Architecture]] — options permission must be explicitly enabled in strategy config
- [[Trading Engine Pipeline]] — options trades follow the same execution lifecycle

## Failure Modes

- **Assignment risk**: Forced to buy/sell shares at strike when unfavorable
- **Unlimited loss on naked calls**: Selling calls without owning shares exposes to unlimited upside risk (not used in Wheel Strategy — always covered)
- **Premium decay (theta)**: Options lose value as expiration approaches — beneficial for sellers
- **Early assignment**: Rare but possible; disrupts planned cycle timing
- **Liquidity risk**: Illiquid options have wide bid-ask spreads, increasing execution cost
- **Brokerage approval**: Options trading requires specific approval levels from brokerage

## Tradeoffs

| Decision | Tradeoff |
|----------|----------|
| Selling vs. buying options | Consistent income vs. capped profit potential |
| Short expiration (1-2 weeks) | Higher annualized return vs. more management overhead |
| Close-to-money strikes | Higher premium vs. higher assignment probability |
| Far-from-money strikes | Lower premium vs. lower assignment probability |

## Related Concepts

- [[Wheel Strategy]]
- [[Guardrail Architecture]]
- [[Autonomous Trading Risk Model]]
- [[Position Sizing]]
- [[Stop-Loss Systems]]
- [[Trading Engine Pipeline]]
- [[Alpaca API]]

## Implementation Notes

The source demonstrates selling-side strategies exclusively (cash-secured puts, covered calls). No speculative option buying is demonstrated. All options activity occurs within the [[Wheel Strategy]] framework where assignment is planned and welcome.

## Open Questions

- Brokerage options approval level requirements for automated trading?
- Greeks monitoring (delta, theta, gamma, vega) for position management?
- Implied volatility analysis for optimal strike/expiration selection?
- Integration with technical analysis for entry timing on puts?

## Future Extensions

- Greeks-aware position management
- Implied volatility rank filtering for premium optimization
- Multi-stock wheel portfolio management
- Options-based hedging for existing equity positions

## Source References

- Source: [[SRC - Claude Alpaca Trader]] — options fundamentals, insurance analogy, calls/puts/premiums/strike/expiration, selling options as income generation
