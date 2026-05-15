# Glossary

Canonical term definitions for the wiki. Each term links to its full canonical page where applicable.

---

**ATR** — Average True Range. Volatility measure used in stock screening. Measures the average range between high and low prices over a period.

**Alpaca** — Commission-free brokerage with trading API for US equities. See [[Alpaca API]].

**Backtest** — Simulating strategy execution on historical data. See [[Backtesting Methodology]].

**Call Option** — Contract giving the right to buy a stock at a locked-in price before expiration. See [[Options Trading]].

**Capital Trades** — Service tracking US congressional stock trading filings. See [[Capital Trades Integration]].

**Cash-Secured Put (CSP)** — Selling a put option while holding enough cash to buy the shares if assigned. Stage 1 of [[Wheel Strategy]].

**Copy Trading** — Strategy of replicating trades from informed actors (politicians, whales). See [[Copy Trading Strategy]].

**Covered Call (CC)** — Selling a call option on shares you already own. Stage 2 of [[Wheel Strategy]].

**Claude Code** — Anthropic's AI coding agent for building and running trading systems. See [[Claude Code]].

**Claude Co-work** — Anthropic's agentic AI with computer use and scheduling. See [[Claude Co-work]].

**Context Budget** — The token allocation for an LLM agent invocation. See [[Context Budget Engineering]].

**Context Rot** — Degradation of reasoning quality when context window is heavily loaded. See [[LLM Failure Modes in Trading]].

**Cron** — Time-based scheduler for recurring tasks. Used by [[Claude Routines]].

**EMA** — Exponential Moving Average. Trend-following indicator weighting recent prices more heavily. See [[EMA Crossover]].

**Guardrails** — Hard constraints preventing dangerous agent actions. See [[Guardrail Architecture]].

**Ladder Buying** — Placing buy orders at progressively lower price levels to average down. See [[Position Sizing]].

**MCP** — Model Context Protocol. Standardized AI-tool integration protocol. See [[MCP Architecture]].

**Options** — Financial derivatives contracts giving the right to buy/sell at a specified price. See [[Options Trading]].

**Overfitting** — Strategy memorizing historical data rather than learning general rules. See [[Overfitting Detection]].

**Paper Trading** — Simulated trading with virtual capital. See [[Paper Trading]].

**Premium** — The price paid or received for an options contract. See [[Options Trading]].

**Pine Script** — TradingView's scripting language for custom indicators and strategies.

**Position Sizing** — Determining how much capital to allocate per trade. See [[Position Sizing]].

**Routine** — A scheduled Claude Code invocation. See [[Claude Routines]].

**RSI** — Relative Strength Index. Momentum oscillator measuring speed and magnitude of price changes. Oversold below 30, overbought above 70.

**R:R** — Risk-Reward Ratio. Average winning trade size divided by average losing trade size. Target: >= 1:2.

**Slippage** — Difference between expected and actual execution price.

**Smart Money** — Capital deployed by actors with superior information access (whales, politicians). See [[Copy Trading Strategy]].

**Stop-Loss** — Automatic exit when price moves against position. See [[Stop-Loss Systems]].

**Strike Price** — The locked-in buy/sell price in an options contract. See [[Options Trading]].

**VWAP** — Volume Weighted Average Price. Institutional intraday benchmark. See [[VWAP]].

**Walk-Forward** — Validation method splitting data into training and testing windows. See [[Walk-Forward Optimization]].

**Webhook** — HTTP callback for event-driven communication. See [[Webhook Architecture]].

**Wheel Strategy** — Cyclical income strategy rotating through selling puts and covered calls. See [[Wheel Strategy]].

**Win Rate** — Percentage of trades that are profitable. Healthy range: 45-60% with good R:R.

**x402** — Pay-per-call payment protocol using USDC micropayments. Used in [[Syndicate Squad Architecture]].

**XMTP** — Messaging protocol for structured inter-agent communication. Used in [[Syndicate Squad Architecture]].
