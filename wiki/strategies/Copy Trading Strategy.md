# Copy Trading Strategy

## Definition

Strategy archetype that systematically tracks and replicates trades from institutional traders, hedge funds, or politicians with demonstrated market-beating performance. Signal generation comes from filing disclosure data rather than technical indicators.

## Purpose

Eliminates the need for independent signal generation by leveraging trades from actors with superior information access. Replaces indicator-based [[Signal Confirmation]] with filing-based signal sourcing.

> "The biggest traders and the best traders in the world don't trade on gut feelings — they trade on information."

Source: [[SRC - Claude Alpaca Trader]]

## Architecture Role

Alternative signal source within [[Trading Engine Pipeline]] Stage 2 (Signal Generation). Instead of generating signals from technical analysis ([[VWAP]], [[EMA Crossover]], etc.), signals come from tracking public filings of informed traders. The rest of the pipeline (validation, execution, journaling, evaluation) remains unchanged.

## Signal Sources

### US Politicians (Congress)

Primary source demonstrated. Members of Congress are required by law (STOCK Act) to report stock trades publicly.

> "Many of them consistently beat the market. They sit on committees, they regulate entire industries, they get briefed on policy changes before the public."

Data accessed via [[Capital Trades Integration]].

### Other Smart Money Sources

| Source | Filing Type | Frequency | Delay |
|--------|-----------|-----------|-------|
| US Politicians | STOCK Act | Per-trade | Up to 45 days |
| Hedge Fund Managers | 13F | Quarterly | 45 days |
| Corporate Insiders | Form 4 | Per-trade | 2 business days |

Source: [[SRC - Claude Alpaca Trader]] [inferred — source focuses on politicians; hedge fund/insider sources are standard industry knowledge]

## Target Selection

Claude algorithmically selects which politician to copy based on:
- **Trading activity frequency** — must be actively trading
- **Recent success rate** — demonstrated market-beating returns
- **Committee assignments** — relevant oversight positions

> "It chose Michael McCaul... he is very active right now and he's the top trader."

Source: [[SRC - Claude Alpaca Trader]]

## Replication Logic

1. Claude queries [[Capital Trades Integration]] via MCP on schedule
2. Filters for target politician's new filings
3. When new buy detected → place matching buy via [[Alpaca API]]
4. When new sell detected → place matching sell
5. Position sizes scaled to account balance (not matching dollar amounts)

## Latency Analysis

Congressional disclosure delay can be up to 45 days. Despite this, the edge persists:

> "Congress can buy like 2 years out or something like that, so they don't do day trading. That's why even if we're a little late because we know about it later, we can still make those gains."

This is a position trading strategy — holding periods measured in months, not days. Late entry by weeks still captures the majority of the move.

Source: [[SRC - Claude Alpaca Trader]]

## Strategy Isolation

Uses a separate Alpaca paper trading account ("Son account") to track copy trading performance independently from other strategies. This enables clean performance comparison vs. benchmark.

Source: [[SRC - Claude Alpaca Trader]]

## Scheduling

Claude Routines check for new filings daily. The schedule is created conversationally:

> "Set up your cron jobs and your schedules so you're always looking and using Capital Trades to see what they're up to and copy those trades."

See [[Claude Routines]].

Source: [[SRC - Claude Alpaca Trader]]

## Performance Evidence

Backtested 1-year performance on $50K starting capital:

| Strategy | End Balance | Return | vs. S&P |
|----------|------------|--------|---------|
| Copy Trading (McCaul) | $59,650 | +19.3% | 2.2x |
| S&P 500 Buy & Hold | $57,000 | +14.0% | 1.0x |

`[backtested, not live-traded]`

Source: [[SRC - Claude Alpaca Trader]]

## Inputs

- [[Capital Trades Integration]] data feed (via MCP)
- Alpaca account credentials (paper or live)
- Target politician selection criteria
- Account balance for position scaling

## Outputs

- Replicated trades matching target's filings
- Performance tracking vs. S&P 500 benchmark
- Trade log entries for each replicated position

## Dependencies

- [[Capital Trades Integration]] — data source
- [[Alpaca API]] — execution venue
- [[Claude Routines]] — scheduled polling
- [[Paper Trading]] — validation before live deployment
- [[MCP Architecture]] — data connection protocol
- [[Trade Logging]] — compliance and tracking

## Failure Modes

- **Politician stops trading**: Target becomes inactive, no signals generated
- **Disclosure delay exceeds holding period**: Rare short-term trades where late entry negates edge
- **Data service downtime**: No filings available, missed replication window
- **Regulatory change**: STOCK Act amendments could alter disclosure requirements
- **Herding effect**: If too many copiers replicate the same politician, the edge may diminish
- **Politician trades in non-replicable assets**: Options, private placements, or assets not available on Alpaca

## Tradeoffs

| Decision | Tradeoff |
|----------|----------|
| Single politician | Concentrated signal vs. single point of failure |
| Daily polling | Balance freshness vs. API load |
| Full replication | Simple execution vs. no independent analysis |
| Position scaling | Account-proportional vs. exact dollar matching |

## Related Concepts

- [[Signal Confirmation]] — alternative signal generation approach (indicator-based)
- [[Capital Trades Integration]] — data source
- [[Trading Engine Pipeline]] — execution lifecycle
- [[Guardrail Architecture]] — risk constraints apply to replicated trades
- [[Autonomous Trading Risk Model]] — information asymmetry risk
- [[Paper Trading]] — required validation stage
- [[Claude Routines]] — scheduling infrastructure

## Open Questions

- Optimal number of politicians to diversify across?
- Should Claude weight position sizes by politician confidence level?
- How to handle conflicting signals from different politicians?
- Portfolio-level risk management across multiple copy targets?
- How to detect when a politician's edge has degraded?

## Future Extensions

- Multi-politician portfolio with confidence-weighted sizing
- Sector filtering based on committee assignments
- Automatic target rotation based on rolling performance
- Integration with 13F data for hedge fund copy trading
- Correlation analysis between politician trades and subsequent stock moves

## Source References

- Source: [[SRC - Claude Alpaca Trader]] — copy trading strategy, Capital Trades service, politician selection, 2.2x S&P performance, strategy isolation via separate accounts
