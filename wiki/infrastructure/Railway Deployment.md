# Railway Deployment

## Definition

Cloud hosting platform used to deploy Claude-based trading bots for 24/7 operation. Handles cron job scheduling, environment variable management, and persistent execution without requiring the user's local machine to be running.

## Purpose

Enables continuous autonomous trading when the user's computer is off. The bot runs in the cloud, checks for trades on schedule, and executes independently.

## Architecture Role

Deployment infrastructure in [[Claude-Assisted Trading Stack]]. Alternative to [[Claude Routines]] remote execution for the TradingView-Exchange pipeline.

## Configuration

1. Install Railway CLI
2. Authenticate via browser
3. Deploy trading bot project
4. Configure environment variables (API keys)
5. Set cron schedule (e.g., every 4 hours)

Source: [[SRC - Claude TradingView Integration]]

## Environment Variables

Railway uses its own environment variable system (separate from local `.env`):
- Must add all API keys to Railway env, not just local
- `PAPER_TRADING=true/false` controls mode
- Portfolio and trade size limits configured here

## Inputs

- GitHub repository (bot code)
- Environment variables (API keys, configuration)
- Cron schedule

## Outputs

- Automated trade execution
- Trade logs
- Status reports

## Dependencies

- [[Claude-Assisted Trading Stack]]
- [[Exchange API Integration]] or [[Alpaca API]]
- [[TradingView Integration]] (for webhook-based setups)

## Tradeoffs

| Decision | Tradeoff |
|----------|----------|
| Railway vs. Claude Routines (remote) | Simpler for non-Claude-Code setups vs. tighter Claude integration |
| Cloud vs. local | 24/7 uptime vs. cost and complexity |

## Related Concepts

- [[Claude Routines]] — alternative scheduling mechanism
- [[Claude-Assisted Trading Stack]]
- [[Environment Variable Management]]

## Source References

- Source: [[SRC - Claude TradingView Integration]] — Railway setup, CLI auth, cron configuration, env vars
