# El Niño — Operations Control Plane

**User manual for the terminal operator console.**

A local, terminal-based operations console (a [Textual](https://textual.textualize.io/) TUI) that lets
you **observe** the El Niño Layer-3 paper-trading pipeline at runtime and **trigger operator actions** in
three safety tiers — up to gated live (paper) actions — behind explicit in-console confirmation, an
append-only audit log, and the same fail-closed boundaries the rest of the system enforces.

Governed by **ADR-013 — Operations Control Plane** (`dev_graph/decisions/ADR - Operations Control
Plane.md`, status: active). It is the sibling of the JARVIS graph console (ADR-010), **not** the same
thing: JARVIS reads the engineering dev_graph; this console reads the **runtime**.

---

## 1. Safety model — read this first

The console **reuses governed functions** and reimplements no safety, paper-only, or gate logic. The
invariants it honours:

- **Local-only.** A terminal app you run yourself. No network listener, no port, no web surface.
- **Paper-only. No live-money path, ever.** Live actions use the Alpaca **paper** plug only; every
  execution record asserts `paper_only`; withdrawals are always disabled.
- **Secrets never displayed.** Credentials live in your environment / a git-ignored `.secrets` file. The
  console only shows *derived* status (`dormant` / `creds-present`) — never a key.
- **Every mutating/live action is audited** (append-only) and, for gated actions, **confirmed** and
  gated by a **server-side precondition** that fail-closes.
- **Read-only by default.** The lowest tier only reads artefacts; you opt into actions explicitly.

Three action tiers:

| Tier | Confirm? | Audit? | Examples |
|------|----------|--------|----------|
| **1 — Read-only** | n/a | n/a | every pane / view |
| **2 — Safe** | no | yes | run chain (simulator), re-run calibration, re-sync Neo4j |
| **3 — Gated-live** | **yes (modal)** | yes | live Alpaca-paper run, register/unregister schedule, calibration bump |

---

## 2. Install

The console's libraries (Textual, Rich) are an **optional** dependency group, so the trading engine
stays dependency-free. Install the extra once:

```bash
pip install -e ".[ops]"
```

That exposes the `ops` package and the `src/` engine packages, so you can launch directly. (If you have
not installed the editable package, you can still run it with the engine on the path:
`PYTHONPATH=src python -m ops.app` — it only needs `textual` + `rich` available.)

Requires Python ≥ 3.10.

---

## 3. Launch

```bash
python -m ops.app          # the interactive TUI
python -m ops.app --once   # a one-shot, headless text dump (no TTY needed) and exit
```

Use `--once` for a quick glance, for piping into a log, or in an environment without an interactive
terminal. Quit the interactive TUI with **`q`**.

---

## 4. Screen layout

```
┌ El Nino - Operations Control Plane ───────────────────────── clock ┐
│  PAPER-ONLY   health=...  ledger=N  verdict=...  positions=N  calib=...   <- status bar
├────────────────────────────────────────────────────────────────────┤
│ [Overview] Gates Calibration Artefacts Processes Plugs Log           <- tabs
│                                                                      │
│   ...the selected tab's content...                                   │
│                                                                      │
├────────────────────────────────────────────────────────────────────┤
│  r Refresh  c Run chain  k Re-run calib  s Re-sync graph  a Alpaca…  <- footer (key bindings)
└────────────────────────────────────────────────────────────────────┘
```

- **Status bar** — overall pipeline health (`ok` / `degraded` / `no-state` / `error`), the always-on
  `PAPER-ONLY` badge, ledger entry count, the last verdict, open positions, and the calibration verdict.
- **Tabs** — switch with the **mouse** (click a tab), or focus the tab bar with **`Tab`** and use
  **←/→**.
- **Footer** — the live key bindings.

The view **auto-refreshes every 5 seconds**; press **`r`** to refresh immediately. (The Windows
scheduled-task lookup only runs on launch and on manual `r`, so the periodic refresh stays cheap.)

---

## 5. The tabs

### Overview
- **Pipeline** headline (health, ledger count, latest verdict, open positions).
- **Latest-decision preview** — a *pure* projection of "what running the latest banked snapshot now would
  produce": regime, direction, verdict (ADMIT / HOLD / REJECT), the full **six-guard block** (each
  guard's pass/fail + reason), and fill-or-no-fill. This computes nothing into your state — it never
  persists and never touches the network or a live feed.
- **Policy versions** — the active runtime / execution / fill-model versions + fingerprints.

### Gates
- **ADR-011** execution Creation Gates (a–f) — the governance board, all closed.
- **ADR-012** calibration readiness (G0–G3) — **advisory** proxies the console derives from the committed
  golden (corpus size, regime/direction diversity, realized labels). These are advisory only; the
  authoritative gate and any version bump are human-review-required.

### Calibration
Readiness detail: committed N vs the G0 floor (60), the regime/direction distributions, realized-label
count, the active decision versions, the discrete **`eligible`** verdict, and the per-gate pass/fail. The
console **never bumps a `*_version`**.

### Artefacts
Status + summary of the artefacts the pipeline reads/writes: the runtime **ledger**, the **portfolio**
state, the captured **operational** input, and the **calibration golden** (counts, hashes, exists/absent).

### Processes
- **daily-chain-task** — whether the `ElNino-Chain-DailyRun` Windows scheduled task is registered, and its
  last/next run + result (queried on launch / manual refresh).
- **producer-freshness** — the latest snapshot banked by the Mr-Ripley Layer-2 producer (a separate repo),
  with its bank time.
- **neo4j-sync** — availability of the re-sync script (the last-sync time is not tracked).

### Plugs
The live-plug status, derived **without ever reading a key**:
- `dormant` — fail-closed (no paper creds present, or a non-paper base URL).
- `creds-present` — paper credentials + the paper host are present, so the live plug *could* be used.

### Log
The **append-only audit log** (every console action) on top, then the **daily-run logs**. After you
trigger any action its result appears here, and the persisted entry shows in the audit section.

---

## 6. Keyboard reference

| Key | Tier | Action |
|-----|------|--------|
| `r` | — | Refresh now (also re-queries the scheduled task) |
| `c` | 2 safe | **Run chain now** on the deterministic simulator, latest snapshot |
| `k` | 2 safe | **Re-run calibration readiness** (the MOD-009 labeler) |
| `s` | 2 safe | **Re-sync Neo4j** (`sync_to_neo4j.py --clear`) |
| `a` | 3 gated | **Run chain via the live Alpaca paper adapter** (confirm modal) |
| `g` | 3 gated | **Register** the daily scheduled task (confirm modal) |
| `u` | 3 gated | **Unregister** the daily scheduled task (confirm modal) |
| `b` | 3 gated | **Commit a calibration bump** (confirm modal; DEFERs unless the gate passes) |
| `q` | — | Quit |

**Confirm modal** (gated actions): **`y`** confirm · **`n`** or **`Esc`** cancel.

---

## 7. The action tiers in detail

### Tier 2 — safe (no confirm, audited)
Pressing the key runs the action immediately, switches you to the **Log** tab, and writes one audit
entry. The safety is structural, not a prompt:

- **`c` Run chain now** — runs the latest banked snapshot through the full chain on the
  deterministic `SimulatedBrokerAdapter` + the credential-free market calendar. There is no way to reach
  a live broker from this action. It writes the canonical ledger + portfolio (idempotent on the
  snapshot id, so a re-run will not double-fill). Use this to populate state from a `no-state` console.
- **`k` Re-run calibration readiness** — re-runs the read-only forward-return labeler and re-reads the
  readiness. It is measurement-only and **never bumps a `*_version`**.
- **`s` Re-sync Neo4j** — re-projects the canonical dev_graph markdown into Neo4j (idempotent). Requires
  `NEO4J_PASSWORD` and the DB up; a failure is surfaced in the Log pane, never raised.

### Tier 3 — gated-live (confirm + audit + server-side precondition)
Pressing the key opens a **confirm modal** that shows the action and its current precondition. On `y` the
action runs in the background and reports to the Log pane; on `n`/`Esc` nothing happens and nothing is
audited.

- **`a` Run chain via live Alpaca paper** — routes *this one run's* execution through the live Alpaca
  **paper** adapter. **Precondition:** the plug must be `creds-present` (paper creds + paper host); if it
  is `dormant`, the action **REFUSES** and places no order. Paper-only / virtual money always.
  (Built-but-dormant: until calibration emits a LONG there is nothing to fill, so today this is a safe
  no-fill live round-trip.)
- **`g` / `u` Register / Unregister the daily schedule** — reuse the existing
  `scripts/register_daily_chain_task.ps1` / `Unregister-ScheduledTask` for the `ElNino-Chain-DailyRun`
  task (deterministic simulator + calendar feed). Reversible.
- **`b` Commit a calibration bump** — checks the ADR-012 gate and returns **DEFER** unless it passes
  (it does not, with the current corpus). A bump is a human-review-required config-version amendment;
  the console can **never** force one and never mutates a `*_version`.

---

## 8. The audit log

Every Tier-2 and Tier-3 action appends one line to:

```
runtime/ops/audit_log.jsonl
```

Each entry is an ASCII JSON line:

```json
{"action":"run-chain-now","args_summary":"port=simulated feed=calendar ...","ok":true,"result":"verdict=ADMIT direction=AVOID regime=RESTRICTIVE_RATES no-fill","timestamp":"2026-06-18T12:00:00Z"}
```

It records *timestamp, action, args-summary, result, ok*. It contains **no credential value** (the whole
surface is secret-redacted). It is an operational journal of console actions — not a second source of
truth for pipeline state. The most recent entries are shown in the **Log** tab.

---

## 9. Credentials & prerequisites for live actions

Credentials live in your **environment** or a **git-ignored `.secrets`** file — never in the repo, a
config, or any console view.

- **Alpaca paper plug (`a`)** turns from `dormant` to `creds-present` only when:
  - `ALPACA_API_KEY_ID` and `ALPACA_API_SECRET_KEY` are set, **and**
  - `ALPACA_PAPER_BASE_URL` (optional; defaults to the Alpaca paper host) parses to exactly the paper
    host over https. Any non-paper URL is refused (fail-closed).
- **Neo4j re-sync (`s`)** needs `NEO4J_PASSWORD` and the database reachable (bolt on `127.0.0.1:7687`;
  use `127.0.0.1`, not `localhost`, on this Windows + Docker setup).
- **Schedule register/unregister (`g`/`u`)** run PowerShell scheduled-task cmdlets — no credentials.

---

## 10. What it reads (paths)

By default the console reads/writes the same paths the orchestration runtime uses (repo-root relative
unless noted):

| What | Path |
|------|------|
| Runtime ledger | `runtime/chain/runtime_ledger.json` |
| Portfolio state | `runtime/chain/portfolio_state.json` |
| Operational capture | `runtime/chain/operational_capture.json` |
| el_nino snapshot pointer | `snapshot_sources/latest_snapshot.json` |
| Producer snapshots (separate repo) | `C:\Code\Mr-Ripley\runtime\snapshots` |
| Calibration golden | `benchmarks/calibration/artifacts/forward_return_labels.json` |
| Daily-run logs | `runtime/logs/daily_chain_run_*.log` |
| Audit log | `runtime/ops/audit_log.jsonl` |

Missing artefacts are handled gracefully (shown as `absent` / `no-state`, never a crash). The paths are
defaults defined by `ops.core.OpsPaths`; to point at a different layout you currently construct an
`OpsPaths` in code (there is no CLI path override yet).

---

## 11. Troubleshooting

| You see | Meaning / what to do |
|---------|----------------------|
| `health=no-state`, `ledger=0` | No chain has been run into `runtime/chain/` yet. Press **`c`** to run the latest snapshot on the simulator. |
| Plugs `dormant` | No Alpaca paper credentials present (or a non-paper URL). Set creds in env/`.secrets` to enable the gated `a` run. |
| Calibration `DEFER` | Expected with the current monochromatic corpus — the gate has not passed; the console will not bump. |
| `a` says `REFUSED (fail-closed)` | The Alpaca plug is dormant — the action placed no order. Provide paper creds + paper host. |
| `s` fails in the Log | Neo4j is down or `NEO4J_PASSWORD` is unset. Start the DB / set the env var. |
| `daily-chain-task: not-registered` | The recurring task is not installed. Press **`g`** (gated) to register it, or run the script yourself. |
| A pane shows an `error` field | A loader hit a malformed/locked artefact; the console fail-closed and surfaced it rather than crashing. |

---

## 12. What it will NOT do (the boundary)

- It will **never** place a live-money order or reach a non-paper venue.
- It will **never** display a credential.
- It will **never** force a calibration bump or mutate a `*_version`.
- It opens **no network listener** and depends on no web stack.
- It changes no `src/` decision logic, contract, or version — it only reads artefacts and calls the
  existing governed functions.

---

## 13. Reference

| File | Role |
|------|------|
| `ops/core.py` | Headless governed read-model (no Textual); `assemble_dashboard()`, `OpsPaths`, view models |
| `ops/app.py` | The Textual TUI (`OpsConsole`, `ConfirmModal`) + the `--once` headless dump |
| `ops/actions.py` | Tier-2 safe actions + the `SAFE_ACTIONS` registry |
| `ops/gated.py` | Tier-3 gated-live actions + `GATED_ACTIONS` + `precondition_line` |
| `ops/audit.py` | The append-only audit log |
| `ops/proc.py` | Shared subprocess runner + secret-redaction helper |

- **Governance:** `dev_graph/decisions/ADR - Operations Control Plane.md` (ADR-013).
- **dev_graph nodes:** module `Operations Control Plane` (MOD-011), observability
  `Operations Control Plane Console` (OBS-002), plus the `ops/` file/test nodes.

> Paper-only. Local-only. Secrets never shown. Read-only before actions, with every mutation confirmed,
> audited, and gated by a fail-closed precondition.
