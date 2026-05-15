# Wiki Index

Last updated: 2026-05-15

## Systems

| Page | Summary |
|------|---------|
| [[Architecture Overview]] | Root node — high-level ecosystem map with all subsystem connections |
| [[Trading Engine Pipeline]] | End-to-end lifecycle: research → signal → validation → execution → journal → evaluation → refinement |
| [[Three-Layer Trading System]] | Screener / strategy engine / execution engine decomposition |
| [[Claude-Assisted Trading Stack]] | Complete tooling ecosystem map (Claude, Alpaca, TradingView, etc.) |
| [[LLM Failure Modes in Trading]] | 12 failure modes: hallucination, overfitting, stale context, eager agent, etc. |
| [[Syndicate Squad Architecture]] | Wallet-native supervisor system for agent teams with treasury constraints |

## Concepts

| Page | Summary |
|------|---------|
| [[VWAP]] | Volume Weighted Average Price — institutional intraday trend benchmark |
| [[EMA Crossover]] | Exponential Moving Average crossover for momentum confirmation (9/21) |
| [[Relative Volume Filter]] | Conviction filter requiring volume >= 1.5x average |
| [[Options Trading]] | Calls, puts, premiums, strike prices, expiration — foundational derivatives concept |

## Strategies

| Page | Summary |
|------|---------|
| [[VWAP Crossover Strategy]] | Multi-indicator strategy: VWAP + EMA + RVOL. Claude-designed. |
| [[Signal Confirmation]] | Pattern requiring multiple independent indicators to agree before trading |
| [[Paper Trading]] | Simulated execution for strategy validation before live deployment |
| [[Wheel Strategy]] | Cyclical options income strategy: sell puts -> assignment -> sell calls -> repeat |
| [[Copy Trading Strategy]] | Replicate trades from politicians/whales using congressional filing data |

## Execution

| Page | Summary |
|------|---------|
| [[Position Sizing]] | Per-trade capital allocation based on equity and risk parameters |
| [[Stop-Loss Systems]] | Fixed, trailing, and time-based automatic exit mechanisms |

## Memory

| Page | Summary |
|------|---------|
| [[Agent Memory Architecture]] | File-based persistent memory for stateless agent invocations |
| [[Context Budget Engineering]] | Token management — "treat tokens like money" |

## Risk

| Page | Summary |
|------|---------|
| [[Autonomous Trading Risk Model]] | Comprehensive risk taxonomy: market, execution, system, AI-specific, governance |
| [[Guardrail Architecture]] | Hard constraints preventing dangerous agent actions |

## Backtesting

| Page | Summary |
|------|---------|
| [[Walk-Forward Optimization]] | In-sample / out-of-sample validation — defense against overfitting |
| [[Overfitting Detection]] | Detecting when strategies memorize history vs. learn patterns |
| [[Backtesting Methodology]] | Protocol for evaluating strategies on historical data |

## Agents

| Page | Summary |
|------|---------|
| [[Supervisor Decision Engine]] | Scores upgrades, allocates treasury, incorporates paper trading evidence |
| [[Multi-Agent Orchestration]] | Coordination of specialized agents: supervisor-worker, sequential routines |
| [[Stateless Agent Recovery]] | How stateless agents reconstruct context from files on each invocation |
| [[Agent Self-Verification]] | Agent validates its own outputs before execution (Opus 4.6) |

## Infrastructure

| Page | Summary |
|------|---------|
| [[Claude Code]] | AI coding agent — primary runtime for building and executing trading systems |
| [[Claude Routines]] | Scheduled autonomous execution with cron scheduling (5 daily routines) |
| [[Claude Co-work]] | Agentic AI with computer use, file access, scheduled tasks |
| [[Railway Deployment]] | Cloud hosting for 24/7 bot operation |

## Integrations

| Page | Summary |
|------|---------|
| [[Alpaca API]] | Commission-free US equities brokerage with paper + live trading API |
| [[TradingView Integration]] | Chart reading, signals, Pine Script, webhook/MCP connection |
| [[Exchange API Integration]] | Crypto exchange APIs (BitGet, Blofin) with 3-factor auth |
| [[Perplexity API]] | AI-powered web research for pre-market analysis |
| [[MCP Architecture]] | Model Context Protocol — standardized tool connectors |
| [[Webhook Architecture]] | HTTP callback pattern for TradingView → Claude → Exchange signals |
| [[Capital Trades Integration]] | Politician/whale stock trade tracking service via MCP |

## Security

| Page | Summary |
|------|---------|
| [[API Credential Isolation]] | Environment-only credential storage, withdrawal disabled |
| [[Environment Variable Management]] | Secure credential storage across deployment contexts |

## Governance

| Page | Summary |
|------|---------|
| [[Trade Logging]] | Mandatory trade journaling for compliance, evaluation, and learning |
| [[Treasury Policy System]] | Budget constraints for Syndicate Squad upgrade spending |
| [[Metadata Migration Plan]] | 3-phase frontmatter rollout: schema, observability, MCP readiness |

## Workflows

| Page | Summary |
|------|---------|
| [[Office Action Loop]] | Syndicate Squad intervention state machine |

## Research

| Page | Summary |
|------|---------|
| [[Research Ingestion Workflow]] | Standardized process for incorporating new source material |

## Sources

| Page | Raw Document | Type |
|------|-------------|------|
| [[SRC - LLM Wiki Methodology]] | `llm-wiki.md` | Methodology |
| [[SRC - Claude Stock Trader]] | `raw/claude_stock_trader.md` | YouTube transcript |
| [[SRC - Claude Opus Trader]] | `raw/claude_opus_trader.md` | YouTube transcript |
| [[SRC - Claude TradingView Integration]] | `raw/claude_tradingview.md` | YouTube transcript |
| [[SRC - Claude Cowork Trader]] | `raw/claude_cowork_trader.md` | YouTube transcript |
| [[SRC - Claude for Financial Services]] | `raw/Claude for Financial Services.md` | Anthropic announcement |
| [[SRC - OWS Dev Squad]] | `raw/ows-dev-squad.md` | Architecture document |
| [[SRC - Build Spec]] | `raw/build-spec.md` | Product requirements |
| [[SRC - Claude Alpaca Trader]] | `raw/calude_alpaca_trader.md` | YouTube transcript |

## Statistics

- **Total pages**: 48 (canonical) + 9 (source) + 2 (index/log) = 59 files
- **Total wikilinks**: ~852
- **Link density**: ~14.4 links/page
- **Source documents**: 9
- **Domains covered**: 14 (systems, concepts, strategies, execution, memory, risk, backtesting, agents, infrastructure, integrations, security, governance, workflows, research)
- **Empty domains**: market_structure, evaluation, patterns (awaiting future ingestion)
- **Frontmatter coverage**: 0% (migration plan approved, Phase 1 pending)
- **Initial build date**: 2026-05-09
- **Last ingestion**: 2026-05-15 (Claude Alpaca Trader)
