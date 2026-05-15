# Capital Trades Integration

## Definition

External data service that aggregates and organizes US congressional stock trading filings, enabling systematic tracking and replication of politician trades. Connected to Claude via [[MCP Architecture]].

## Purpose

Provides the "smart money" signal source for [[Copy Trading Strategy]]. Transforms raw SEC/STOCK Act filings into actionable trade data accessible to Claude as an MCP skill.

## Architecture Role

Data provider in the [[Claude-Assisted Trading Stack]] Data & Research layer. Parallel to [[Perplexity API]] (market research) and [[TradingView Integration]] (technical signals), Capital Trades provides a fundamentally different signal type: institutional/political flow data.

## Connection Method

MCP plug-in. Claude gains Capital Trades as a new "skill" once the MCP server is configured.

> "Think of it like a power outlet — the electricity (the insider information) is running through those walls and we basically plug our Claude into that so we can use it."

The MCP connector enables Claude to query Capital Trades data at any time during scheduled routines or interactive sessions.

Source: [[SRC - Claude Alpaca Trader]]

## Smart Money Concept

"Smart money" refers to capital deployed by actors with superior information access:

- **Whales**: Institutional traders moving millions per trade. "When someone puts $50 million into a stock, they didn't do that off a gut feeling. They have research teams and private data."
- **US Politicians**: Congress members required by law to report stock trades (STOCK Act). "They sit on committees, they regulate entire industries, they get briefed on policy changes before the public."
- **Observable signals**: Massive options orders, unusual volume spikes, congressional filing disclosures.

Source: [[SRC - Claude Alpaca Trader]]

## Data Provided

| Field | Description |
|-------|-------------|
| Politician name | Filing member of Congress |
| Stock ticker | Security traded |
| Trade direction | Buy or sell |
| Trade date | Date of transaction |
| Disclosure date | Date filing became public |
| Dollar range | Approximate transaction value |
| Committee assignments | Relevant oversight committees |

## Latency Considerations

Congressional disclosure delay can be up to 45 days. Why the edge persists despite delay:

> "Trades may be slightly stale but that's the nature of how they disclose. We still get a lot of gains because mostly Congress can buy like 2 years out or something like that, so they don't do day trading."

Long holding periods mean late entry still captures most of the move. This is a position trading signal, not a day trading signal.

Source: [[SRC - Claude Alpaca Trader]]

## Inputs

- MCP server configuration
- Capital Trades service URL
- Query parameters (politician filter, date range, ticker)

## Outputs

- Structured trade data per politician
- Trade history for algorithm-based politician selection
- Performance metrics for copy target evaluation

## Dependencies

- [[MCP Architecture]] — connection protocol
- [[Claude Code]] or [[Claude Routines]] — runtime for data queries
- [[Claude-Assisted Trading Stack]] — component in data layer

## Failure Modes

- Service downtime or API changes
- Stale filing data beyond expected delay window
- Politician changes trading pattern or retires
- MCP connection failure or configuration drift
- Data format changes requiring connector updates
- Regulatory changes to disclosure requirements (STOCK Act amendments)

## Tradeoffs

| Decision | Tradeoff |
|----------|----------|
| Free service | Accessible but potentially limited data depth |
| Single-politician focus | Concentrated signal vs. diversification |
| Daily polling frequency | Balance between freshness and API load |
| MCP vs. web scraping | Structured access vs. broader data but fragile parsing |

## Related Concepts

- [[Copy Trading Strategy]]
- [[MCP Architecture]]
- [[Claude-Assisted Trading Stack]]
- [[Alpaca API]]
- [[Claude Routines]]
- [[Perplexity API]]

## Open Questions

- Rate limits on Capital Trades API?
- Alternative data sources for hedge fund 13F filings?
- Webhook support for real-time filing notifications?
- Historical data depth available through the service?

## Future Extensions

- Multi-source aggregation (Capital Trades + 13F filings + Form 4 insider trades)
- Real-time filing notification via webhook
- Politician performance scoring and automatic target rotation
- Committee-based sector filtering

## Source References

- Source: [[SRC - Claude Alpaca Trader]] — Capital Trades as MCP data source for copy trading, politician selection algorithm, latency analysis
