Trading Application — Full Concept Audit + Alpaca Integration Verification

Subject: el_nino (branch JARVIS), audited against the real codebase, not assumptions

▎ Method note. I did not fill in the template's [...] placeholders from imagination — I read the actual code and governance, then ran a 27-agent workflow across all 10 template subsections + 6 concept dimensions (117 checks), and adversarially re-verified every claimed defect and high-severity FAIL (18 verifications) to separate real bugs from documented, governed scope boundaries. Where the verification overruled the first-pass auditor, the correcpears below.

The adversarial pass is doing exactly its job — collapsing over-stated "defects" into governed scope-gaps while confirming the genuine ones. Let me read the remaining verifications.

  Read 1 file

I have the complete verified picture. Let me pull the per-dimension narratives plus all blockers/warnings to ground Part 1 prose and Part 3 verdict.

  Read 1 file, ran 1 shell command

I have the complete, adversarially-verified picture. Let me clean up the scratch files I created, then deliver the consolidated report.

  Ran 1 shell command

Trading Application — Full Concept Audit + Alpaca Integration Verification

Subject: el_nino (branch JARVIS), audited against the real codebase, not assumptions

▎ Method note. I did not fill in the template's [...] placeholders from imaginatind governance, then ran a 27-agent workflow across all 10 template subsections + 6 concept dimensions (117 checks), and adversarially re-verified every claimed defect and high-severity FAIL (18 verifications) to separate real bugs from documented, governed scope boundaries. Where the verification overruled the first-pass auditor, the corrected classification is what appears below.

---
Executive verdict (read this first)

el_nino is not the application the template assumes. It is an autonomous, governance-first, single-instrument (GLD), paper-only, long-or-flat research/validation harness. Market "truth" is
consumed as point-in-time snapshots from a separate repo (Mr-Ripley) — it does no The entire Alpaca surface is two stdlib-only (urllib, no SDK) REST plugs, bothdefault-OFF, fail-closed, non-replayable, and refusing any non-paper host at the credential boundary: a POST /v2/orders market-BUY (alpaca_adapter.py) and a GET /v2/calendar gate (alpaca_clock_feed.py). The order adapter is built-but-dormant — the decision layer emits no LONG until calibration lands (ADR-012 DEFER), so it never actually fills today.

┌─────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                         │                                        Verdict                                                                     │
├─────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Is the concept sound?                   │ Yes. For what it is — a deterministicsion/execution harness — the architecture is unusually disciplined (pure core │
│                                         │  + hexagonal port, zero runtime deps, ~1050 tests, snapshot-driven determinism).                                                                │
├─────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Will it integrate fully & reliably with │ No — and the team already knows it. The v0 live adapter is not operable for live paper trading: it expects a synchronous fill, has no           │
│  Alpaca as written?                     │ reconcile, no error typing, no client                                                                              │
├─────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Are those gaps reckless?                │ No. Almost every gap is enumerated and owned by ADR-014 (status: draft / not-started) as deliberate, HARD-PAUSED v1 work behind the ADR-013 ops │
│                                         │  gate. They are governed boundaries,                                                                               │
├─────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Net                                     │ Concept: PASS. Live-Alpaca readiness: Yes-with-fixes — and the fixes are already scoped. Today's running system is correct because the live     │
│                                         │ path is dormant.                                                                                                                                │
└─────────────────────────────────────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

The single thing that is a genuine bug, not a deferral: the GLD-vs-gold-spot pricng else high-severity is a governed scope-gap on a dormant path.

---
PART 1 — General trading-application audit

1. Concept Overview

- Core idea / value: A closed-loop, evidence-gated pipeline — snapshot → features → regime → supervisor decision → gold decision packet → paper-runtime admission → GATE-001 risk guard → execution (src/orchestration/engine.py:48-110). The unit of value is replayable, direction-accuracy evidence on gold (GLD), not P&L. It explicitly does not make money and is not meant to —
live money is "structurally blocked, out of scope" (ADR-014:132-133).
- Audience: a single operator/developer (the author), via an ops/ Textual TUI. Not a multi-user product.
- Key assumptions (explicit & internally consistent): GLD as the gold instrument;unt, long-or-flat semantics; snapshot-driven determinism ("same snapshot in →bit-identical decision out").

2. Technical Feasibility — strong

- Stack is verified, not just claimed: pyproject.toml dependencies = [] is real — only stdlib + intra-package imports; both Alpaca plugs are raw urllib(alpaca_adapter.py:26-31). Frozen dataclasses throughout.
- Determinism + hexagonal design is the standout property: a pure execute() core that never imports src/risk or does IO; the INT-011 ExecutionPort with the deterministic SimulatedBrokerAdapter as the wired default; the live plug fenced via replayable=False and never re-exported. State is an explicit value with SHA-256 state_hash() chaining.
- Scalability is correctly a non-concern (single instrument, single user, daily bt over-built.
- Maturity: ~1050 tests (verified by collection; the roadmap's "853" is stale).
- Maintainability frictions (low): root project_structure.md is stale and describlayer_3_wiki); the primary E2b roadmap is in Hungarian (bus-factor) — bothmitigated by the English ADR-014 + dev_graph/index.md.

3. Regulatory Compliance — sound posture, correctly scoped

- For what it is today — paper-only, virtual-money, single-operator, no custody, e classic surface (KYC/AML, BD/RIA registration, custody 15c3-3, SIPC,CAT/blue-sheet, GDPR/CCPA, 1099) is genuinely N-A, and in each case the absence is either constitutionally governed or sits with the broker of record.
- Live-money is blocked in depth and the block is governed: ADR-014 §2 + ADR-013 §5 (Non-Goal) + the parsed-hostname-equality credential boundary in code. Crossing to real money needs new code and new governance — the correct gate.
- Recordkeeping/audit trail is pre-seeded (append-only immutable ledgers, snapshot-id provenance, append-only ops audit) — it builds the controls a live system would need before being allowed
to go live.
- Honest gaps (documentary, not substantive): the GDPR/CCPA "N-A" is reasoned but not recorded — add a one-line governance note. And future-scope triggers (managing others' money, or
distributing as an advisory product) would create RIA/BD registration + retentionone implicated today, but worth an explicit ADR gate before any such evolution.

4. User Experience (operator surface) — mature, safety-first, honest

- The authoritative surface is the ops/ TUI (ops/app.py over ops/core.py), governb HUD is a separate read-only knowledge console, explicitly not the tradingsurface.
- Confirmation on irreversible actions is exemplary: the four gated-live actions sit behind a blocking ConfirmModal and the modal is not trusted as the guarantee — each action re-enforces the paper-host precondition server-side and refuses (executed=False) when the plug is. Cancel writes no audit entry.
- Fail-closed feedback (crash-proof worker dispatch; loaders degrade to an error field, never crash), honest trust signals (six-guard PASS/FAIL with reasons, realized P&L, fill/no-fill labels, policy fingerprints, always-on PAPER-ONLY badge), and a proven no-secret-leak invariant (redact(), test_core.py:281-300).
- Gaps (low): artefact drill-down is unimplemented (governed as non-normative in ADR-013 — operator falls back to raw JSON); no in-app ? help overlay; JARVIS HUD ops panels are hard-coded editorial values ("VERDICT: ADMIT", "853 TESTS") that should stay visibly badged as static narrative so they're never mistaken for live status. Accessibility/mobile is N-A (local terminal
app).

5. Risk Management — strong internal spine

- Fail-closed everywhere: missing/non-paper creds → client=None → raise, never syructurally impossible without an approved guard (models.py:303-305).
- Double-layered idempotency: source_snapshot_id once-ever guard short-circuits execute() before any order, reinforced by ledger ADMIT-dedup; crash-consistency is ordered portfolio-first so a
re-run can re-admit but never double-fill.
- GATE-001 hard limits (position size, daily-loss cap, max trades, max positions, withdrawal-disabled) run as a short-circuit conjunction before execution, with fail-closed env config; PRED-008 cooldown is timed by snapshot as_of, never wall-clock.
- Operational gaps: no operator kill switch (halt is read-only on the dashboard; y one-shot gated model + default-OFF adapter); halt/degraded is calendar-based,not a real-time feed (an intraday halt isn't detected — acceptable for a daily pipeline, note for any future intraday work).

6. Audit Readiness — excellent

- Immutability & tamper-evidence: frozen dataclasses; SHA-256 over canonical JSONn each record to the prior state_hash; atomic temp+os.replace persistence;append-only audit log with full-surface credential redaction; end-to-end lineage (source_snapshot_id → source_record_id/source_packet_id).
- Gaps (low): audit timestamps truncate to whole seconds with no monotonic seq (v3 §7 — append-order preserves ordering; no fix needed); AuditEntry has noactor/who field — defensible for a single operator but the one ungoverned audit gap (record the rationale or add the field). Broker-level traceability gap: no alpaca_order_id/raw_payload persisted (governed — ADR-014 §6 additive fields).

---
PART 2 — Alpaca integration verification

Status legend: PASS · FAIL · UNKNOWN · N-A (not applicable to this snapshot-driven, paper-only, single-instrument architecture). Category in parentheses: (defect) = real bug in code as written · (governed) = deliberately deferred with a citable ADR · (ungoverned) = absent and not covered by any decision.

2.1 Authentication & environment — the strongest part of the codebase

┌────────────────────────────┬──────────────┬───────────────────────────────────────────────────────────────────────────┬──────────────────────────────────────┐
│           Check            │    Status    │                                                Evidence                                                │             Fix if FAIL              │
├────────────────────────────┼──────────────┼───────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────┤
│ Keys from env/secret       │              │ os.environ.get('ALPACA_API_KEY_ID'/'ALPACA_API_SECRET_KEY') only (alpaca_adapter.py:165-166,           │                                      │
│ store, never hard-coded    │ PASS         │ alpaca_clock_feed.py:143-144); repo-wide grep finds zero real key literals; .gitignore:24-28 excludes  │ —                                    │
│                            │              │ .secrets; ops/proc.py:48-63 value-r                                       │                                      │
├────────────────────────────┼──────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────┤
│ Correct base URLs          │ PASS         │ Only paper host in code (_DEFAULT_Bpaca.markets'); no live/data host      │ —                                    │
│                            │              │ anywhere in src/                                                                                       │                                      │
├────────────────────────────┼──────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────┤
│ APCA-API-KEY-ID +          │              │ Exact spelling on both single-reque:133-147,                              │                                      │
│ APCA-API-SECRET-KEY on     │ PASS         │ alpaca_clock_feed.py:123-129)                                                                          │ —                                    │
│ every call                 │              │                                                                                                        │                                      │
├────────────────────────────┼──────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────┤
│                            │ FAIL         │                                                                                                        │ Add a GET /v2/account smoke-check    │
│ GET /v2/account → 200      │ (governed,   │ Never called; deferred to ADR-014 §uth smoke), HARD-PAUSED                │ inside the quarantined live plug on  │
│                            │ low)         │                                                                                                        │ enable; do not enable paper          │
│                            │              │                                                                           │ accumulation without it              │
└────────────────────────────┴──────────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────┴──────────────────────────────────────┘

2.2 Account state & permissions

┌─────────────────────────────────────┬────────────────┬──────────────────────────────────────────────────────────────┬───────────────────────────────────────┐
│                Check                │     Status     │                                         Evidence                                          │              Fix if FAIL              │
├─────────────────────────────────────┼────────────────┼───────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────┤
│ status=ACTIVE,                      │ FAIL           │                                                                                           │ Add status=='ACTIVE' &&               │
│ account_blocked/trading_blocked     │ (ungoverned,   │ No status gate read or ncount would only fail at the order   │ !trading_blocked to the v1 startup    │
│ false                               │ low)           │ boundary                                                                                  │ reconcile and record it in ADR-014 to │
│                                     │                │                                                              │  make it governed                     │
├─────────────────────────────────────┼────────────────┼───────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────┤
│                                     │ FAIL           │ Guard validates against 00 (config.py:79 → runtime.py:98 →   │ Implement cash-cap via GET            │
│ buying_power/cash/equity parsed     │ (governed,     │ predicates.py:18); no live read. Verified: threading a live account read into the shared  │ /v2/account inside the plug (ADR-014  │
│                                     │ low)           │ build_guard_request would contaminate the determinism/replay key (paper_equity folds into │ §6), never in the deterministic guard │
│                                     │                │  fingerprint()), so the e plug only                          │  input                                │
├─────────────────────────────────────┼────────────────┼───────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────┤
│                                     │ FAIL           │                                                                                           │ N-A until margin/short is ever in     │
│ pattern_day_trader read/handled     │ (governed,     │ Moot under cash-account + long-or-flat semantics (ADR-014 §2)                             │ scope                                 │
│                                     │ low)           │                                                                                           │                                       │
├─────────────────────────────────────┼────────────────┼──────────────────────────────────────────────────────────────┼───────────────────────────────────────┤
│                                     │ FAIL           │                                                                                           │                                       │
│ Entitlements for asset classes used │ (governed,     │ Single instrument, cash,                                     │ Covered by the auth smoke-check above │
│                                     │ low)           │                                                                                           │                                       │
└─────────────────────────────────────┴────────────────┴──────────────────────────────────────────────────────────────┴───────────────────────────────────────┘

2.3 Market data

┌──────────────────────────────────────────────────┬─────────────────┬───────────────────────────────────────────────────────────────────────────────────┬─────────────────────────────────┐
│                      Check                       │     Status      │                                     Evidence                                      │           Fix if FAIL           │
├──────────────────────────────────────────────────┼─────────────────┼───────────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────┤
│ Latest quote / historical bars / IEX-vs-SIP /    │ N-A             │ el_nino co-001), not Alpaca data; no                 │ — (architectural, by ADR-011    │
│ crypto-options                                   │                 │ data.alpaca.markets, /v2/stocks, iex, sip in src/                                 │ determinism)                    │
├──────────────────────────────────────────────────┼─────────────────┼──────────────────────────────────────────────────────┼─────────────────────────────────┤
│ Missing/halted/non-tradable handled gracefully   │ PASS (partial)  │ Operational feed fail-closes to closed() on any fault                             │ —                               │
├──────────────────────────────────────────────────┼─────────────────┼──────────────────────────────────────────────────────┼─────────────────────────────────┤
│ Price-reference correctness                      │ FAIL (defect,   │ The one real bug. See 2.8 / blocker #1                                            │ Fix per ADR-014 §5              │
│                                                  │ high)           │                                                                                   │                                 │
└──────────────────────────────────────────────────┴─────────────────┴──────────────────────────────────────────────────────┴─────────────────────────────────┘

2.4 Clock, calendar & assets

┌───────────────────────────────────────────┬──────────────────┬─────────────────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────┐
│                   Check                   │      Status      │                                    Evidence                                     │               Fix if FAIL               │
├───────────────────────────────────────────┼──────────────────┼─────────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────┤
│ GET /v2/clock gates orders to hours       │ N-A (governed)   │ Correctly uses / read — required for as-of replay  │ —                                       │
├───────────────────────────────────────────┼──────────────────┼─────────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────┤
│ GET /v2/calendar honored (holidays)       │ PASS             │ Open iff date ∈ k_feed.py:99-109); weekends,       │ —                                       │
│                                           │                  │ movable feasts, observed shifts all closed; every failure → closed()            │                                         │
├───────────────────────────────────────────┼──────────────────┼────────────────────────────────────────────────────┼─────────────────────────────────────────┤
│                                           │ FAIL             │                                                                                 │ Immaterial at day granularity; document │
│ Early-close / half-days                   │ (ungoverned,     │ trading_days kee discarding session open/close     │  in ADR-014 or model session bounds     │
│                                           │ low)             │                                                                                 │                                         │
├───────────────────────────────────────────┼──────────────────┼─────────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────┤
│ GET /v2/assets/{symbol}                   │ FAIL (governed,  │ No assets read; 42-144)                            │ ADR-014 §6/B2 — add fractionable check  │
│ tradable/fractionable/shortable           │ medium)          │                                                                                 │ before a real qty is submitted          │
└───────────────────────────────────────────┴──────────────────┴─────────────────────────────────────────────────────────────────────────────────┴─────────────────────────────────────────┘

2.5 Order management

Check: Market order fills, status transitions
Status: FAIL (defect/governed, high)
Evidence: BUY works against a stub, but the status gate _FILLED_STATUSES={'filled','FILLED'} (:42,112-113) expects a synchronous fill — real Alpaca market orders return accepted/pending_new and
  fill async, so the live path would raise on essentially every real order. Verif/EXECUTION_UNCERTAIN state machine is deferred v1 (ADR-014 §6); harmless today
  (dormant). Caveat: the naive "accept the POST echo" fix would break fail-closed — resolve fills via a separate GET /v2/positions/GET /v2/orders reconcile, not the synchronous response (and
  note: GET /v2/orders/reconcile is not a real Alpaca endpoint)
Fix if FAIL: Implement ADR-014 §6 state machine + reconcile inside the plug
────────────────────────────────────────
Check: Limit / stop / stop_limit / trailing
Status: N-A (governed)
Evidence: Non-Goal; exits are evaluator-side, never broker-conditional (ADR-014 §
Fix if FAIL: —
────────────────────────────────────────
Check: Valid TIF
Status: PASS
Evidence: time_in_force='day' (:143); other TIFs N-A
Fix if FAIL: —
────────────────────────────────────────
Check: Bracket / OCO / OTO
Status: N-A (governed)
Evidence: Non-Goal
Fix if FAIL: —
────────────────────────────────────────
Check: Fractional / notional
Status: FAIL (governed, medium)
Evidence: qty=default_size=1.0, no notional/fractionable
Fix if FAIL: ADR-014 §6 fixed-notional + cash-cap
────────────────────────────────────────
Check: Cancel single/all, replace
Status: N-A (governed)
Evidence: Reconcile-superseded design
Fix if FAIL: —
────────────────────────────────────────
Check: qty as JSON number
Status: PASS
Evidence: Verified via Alpaca docs: equities accept a bare numeric qty (qty: 3.65Sizing is fixed whole-size anyway
Fix if FAIL: Optional cosmetic str(qty); verify on a live paper run
────────────────────────────────────────
Check: GET /v2/positions & /v2/orders parse
Status: FAIL (governed, high)
Evidence: No reconcile; port exposes only submit_market_buy
Fix if FAIL: ADR-014 §6 mandatory startup reconcile (refuse on broker≠local)
────────────────────────────────────────
Check: client_order_id for idempotency
Status: FAIL (governed, medium)
Evidence: Internal once-ever via source_snapshot_id only (models.py:201-203) — a ble-submit broker-side
Fix if FAIL: ADR-014 §6 deterministic client_order_id for HTTP-422 dedup, alongside the internal guard
────────────────────────────────────────
Check: Internal once-ever idempotency
Status: PASS
Evidence: PortfolioState.has_execution() short-circuits before the broker call
Fix if FAIL: —

2.6 Real-time streaming (WebSockets)

┌───────────────────────────────────────┬─────────────┬───────────────────────────────────────────────────┬───────────────────────────────────────────────────┐
│                 Check                 │   Status    │                                    Evidence                                    │                    Fix if FAIL                    │
├───────────────────────────────────────┼─────────────┼───────────────────────────────────────────────────┼───────────────────────────────────────────────────┤
│ trade_updates stream / market-data    │ N-A         │ No WebSocket anywhere (grep=0); order result read off the synchronous POST;    │ — (architectural). A stream becomes relevant only │
│ stream / reconnect+backoff            │ (governed)  │ ADR-014 §6 deliberately cncile poll over a stream │  if intraday operation is ever in scope           │
└───────────────────────────────────────┴─────────────┴────────────────────────────────────────────────────────────────────────────────┴───────────────────────────────────────────────────┘

2.7 Rate limits & resilience

┌──────────────────────┬───────────────────────┬─────────────────────────────────────────────────────────────────────────────────────────┬────────────────────────────────────────────────┐
│        Check         │        Status         │                                                            │                  Fix if FAIL                   │
├──────────────────────┼───────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────┼────────────────────────────────────────────────┤
│ Stays within ~200    │ FAIL (ungoverned,     │                                                                                         │ Single-instrument daily volume makes this      │
│ req/min / throttling │ low)                  │ No rate limiter                                            │ near-moot; add a minimal pacer or document why │
│                      │                       │                                                                                         │  unnecessary                                   │
├──────────────────────┼───────────────────────┼────────────────────────────────────────────────────────────┼────────────────────────────────────────────────┤
│ Handles 429 +        │ FAIL (ungoverned,     │ No 429 handling; a 429 leaks as a raw HTTPError. ADR-014 never mentions 429 — genuinely │ Honor Retry-After, no blind resend; add 429 to │
│ Retry-After          │ medium)               │  uncovered                                                 │  the ADR-014 §6 state machine                  │
├──────────────────────┼───────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────┼────────────────────────────────────────────────┤
│ 5xx/network retry +  │ PASS (timeouts) /     │ _HTTP_TIMEOUT_S=10.0 wired into both urlopen calls (good); retry is intentionally       │                                                │
│ timeouts             │ FAIL (retry,          │ absent — ADR-014 §6 chooses "no AIN + halt" +              │ Implement the §6 halt/uncertain path           │
│                      │ governed)             │ deterministic client_order_id before any retry is safe                                  │                                                │
└──────────────────────┴───────────────────────┴─────────────────────────────────────────────────────────────────────────────────────────┴────────────────────────────────────────────────┘

2.8 Error handling & edge cases

Check: Insufficient buying power / rejected orders and wash/forbidden/not-tradable
Status: FAIL (governed, medium — one root cause, not two)
Evidence: submit_market_buy (:141-154) has no try/except, so a 4xx raises a raw urllib.error.HTTPError out of fill→execute→run_once. Verified: this does not break fail-closed (no synthetic
  fill, nothing swallowed, propagates loudly) — it is an exception-TYPE/ergonomicis discarded (:150-154). Deferred v1 (ADR-014 §6 EXECUTION_UNCERTAIN/halt +
  raw_payload; roadmap B17/B18). N-A today (dormant)
Fix if FAIL: Catch HTTPError/URLError, parse the body, route to EXECUTION_UNCERTA§6; add a 4xx test (current suite only stubs status='filled')
────────────────────────────────────────
Check: Partial fills reconciled to intended size
Status: FAIL (governed, medium)
Evidence: filled_qty echoed verbatim; a filled with filled_qty<requested would silently book a smaller position
Fix if FAIL: ADR-014 §6 PARTIAL state + next-reconcile
────────────────────────────────────────
Check: Timestamps treated as UTC; exact decimals
Status: PASS (decimals) / minor/UNKNOWN (clock-feed venue date)
Evidence: Float everywhere but every to_dict() rounds to 6dp for byte-stable hashce). Clock-feed _calendar_date (:62) has no TZ normalization — verified not
  triggered by this system's data (all timestamps are US-afternoon UTC, far from the 00:00–05:00 UTC danger window) and fail-closed (wrong day → closed(), never a bad trade); a TZ fix as
  proposed would break the feed-equivalence test, so it must touch both feeds
Fix if FAIL: Low; add a near-midnight-UTC fixture and normalize both feeds togeth

2.9 Reconciliation & safety

┌───────────────────────────┬─────────────────────────────┬─────────────────────────────────────────┬──────────────────────────────────────────────────────────┐
│           Check           │           Status            │                               Evidence                               │                       Fix if FAIL                        │
├───────────────────────────┼─────────────────────────────┼─────────────────────────────────────────┼──────────────────────────────────────────────────────────┤
│ Startup reconcile local   │ FAIL (governed, high)       │ No GET /v2/positions/GET /v2/account; portfolio folded purely from   │ ADR-014 §6 mandatory startup reconcile + add cash to     │
│ vs Alpaca                 │                             │ the POST echo; Portfo all               │ SCHEMA-015 (version bump)                                │
├───────────────────────────┼─────────────────────────────┼──────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────┤
│ Duplicate-order           │ PASS (internal) / FAIL      │                                         │                                                          │
│ protection via            │ (broker-side, governed)     │ Internal once-ever is solid; no broker-side 422 dedup                │ ADR-014 §6                                               │
│ client_order_id           │                             │                                                                      │                                                          │
├───────────────────────────┼─────────────────────────────┼─────────────────────────────────────────┼──────────────────────────────────────────────────────────┤
│ Kill switch /             │ PASS (position, loss) /     │ GATE-001 limits enforced before execution; no operator halt action   │ Add an audited Tier-2 halt that writes halt=True (the    │
│ max-position / max-loss   │ FAIL (kill switch,          │ exists (halt is read-only)                                           │ feed already honors it), or document one-shot+unregister │
│                           │ ungoverned, low)            │                                                                      │  as the accepted kill mechanism                          │
├───────────────────────────┼─────────────────────────────┼──────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────┤
│ Every request/response id │ PASS (console) / FAIL       │ Console-action audit raw_payload        │ ADR-014 §6 additive fields                               │
│  logged                   │ (broker, governed, low)     │ persisted                                                            │                                                          │
├───────────────────────────┼─────────────────────────────┼─────────────────────────────────────────┼──────────────────────────────────────────────────────────┤
│                           │                             │ The only route to a live order enforces confirm + append-only audit  │                                                          │
│ Gated-live enablement     │ PASS                        │ + server-side paper-h without placing   │ —                                                        │
│                           │                             │ an order (ops/gated.py:84-90)                                        │                                                          │
└───────────────────────────┴─────────────────────────────┴──────────────────────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────┘

2.10 Paper → live cutover

┌──────────────────────────────┬─────────────┬────────────────────────────────────────────────────────────────────────────────────────┬────────────────────────────────────────────────────┐
│            Check             │   Status    │                                        Evidence                                        │                    Fix if FAIL                     │
├──────────────────────────────┼─────────────┼───────────────────────────────────────────────────────────┼────────────────────────────────────────────────────┤
│ Only diff is base URL + keys │ PASS        │ No paper-vs-live branch exists; the one tunable (ALPACA_PAPER_BASE_URL) is hard-gated  │ —                                                  │
│                              │             │ to the paper host                                         │                                                    │
├──────────────────────────────┼─────────────┼────────────────────────────────────────────────────────────────────────────────────────┼────────────────────────────────────────────────────┤
│ Live keys separate / never   │             │ _is_paper_base_url parsed-hostnamest + sub/super-domain + │                                                    │
│ committed / structurally     │ PASS        │  query/fragment spoofs + http:// (test_alpaca_adapter.py:129-148); no live endpoint is │ —                                                  │
│ blocked                      │             │  constructible                                                                         │                                                    │
├──────────────────────────────┼─────────────┼───────────────────────────────────────────────────────────┼────────────────────────────────────────────────────┤
│ Canary plan for first live   │ FAIL        │                                                                                        │ Author a dedicated Phase-D ADR only after KA-010   │
│ trades                       │ (governed)  │ Correctly absent — live is "structurally blocked, Phase D" (ADR-014:132)               │ paper-validation + ADR-012 calibration lift +      │
│                              │             │                                                                                        │ ADR-014 v1 acceptance                              │
└──────────────────────────────┴─────────────┴────────────────────────────────────────────────────────────────────────────────────────┴────────────────────────────────────────────────────┘

---
PART 3 — Recommendations & verdict

1. Overall verdict

Concept: sound (PASS). Alpaca integration: Yes-with-fixes. The system is correct and safe as it runs today because the live path is dormant and the credential/determinism/fail-closed spine is
genuinely excellent. It is not yet live-paper-capable, but the gap between "v0 ster" is already mapped, owned, and HARD-PAUSED by ADR-014 — this is governanceworking as intended, not negligence.

2. 🔴 Red flags / blockers (must fix before any paper accumulation goes live)

1. GLD-vs-gold-spot price reference — the one real defect (CONFIRMED). orchestration/engine.py:45,95 forwards gold_price (= gold_price_proxy = 4624.5 $/oz gold spot) as instrument_price for a
GLD share order (~$300–600/share). Consequences, verified end-to-end:
  - alpaca_adapter.py:117-118 slippage = (GLD_fill − gold_spot)/gold_spot ≈ −9,300 bps (nonsense) — live path only.
  - engine.py:101 → _apply_buy marks avg_cost/unrealized_pnl in $/oz against GLD-units on both the simulator and the live path.
  - Latent only because no LONG fires today (current snapshot → AVOID; ADR-012 DEFER). It misbehaves the instant a LONG fills.
  - Fix (ADR-014 §5): add exec_ref_gld_price re-derived from the snapshot (per the D1 replay discipline, no live read), keep gold_price as decision-context only, make slippage GLD-vs-GLD, bump
execution_policy_version, re-pin BENCH-004/006.
  - Blocked by A8 (also confirmed): the snapshot carries no GLD share/close price (only spot + a holdings-flow proxy gld_holdings_flow_confirm — do not mistake the flow for a price). A Mr-Ripley (Layer-2) ingest extension must land first.
2. No startup reconcile + no live-capable order lifecycle (governed, high). No GET /v2/positions/GET /v2/account; the live order is a blind market BUY folded from the synchronous POST echo, which expects an immediate filled that real Alpaca orders don't return. ADR-014 §6 reconcile-then-act + the QUEUED/PARTIAL/EXECUTION_UNCERTAIN state machine must land (inside the quarantined
plug) before any live enable.

3. 🟡 Warnings (should fix, prioritized)

1. Uncaught HTTPError + discarded reject reason (alpaca_adapter.py:141-154) — wraXECUTION_UNCERTAIN/halt with raw_payload; add a 4xx test (the suite only stubsstatus='filled'). One root cause covers both the insufficient-BP and wash/forbidden findings.
2. No broker-side client_order_id — a lost portfolio file could double-submit; add deterministic client_order_id for 422 dedup alongside the internal guard.
3. Mislabeled "daily" guard inputs (ungoverned, fail-safe): daily_pnl sums all-tiSCHEMA-007/PRED-002 "for the day") and trades_today=next_seq() is the lifetimefill count (blocks forever after 10 fills). Both are dormant today (no realized P&L without a SELL/FLAT exit). Fix needs the snapshot as_of threaded into build_guard_request and an as_of field on ExecutionEntry (SCHEMA-015 change + BENCH re-pin) — mirror the existing snapshot-as_of cooldown predicate to stay replay-safe.
4. No 429/Retry-After handling (genuinely ungoverned) — honor Retry-After, no blie machine.
5. No operator kill switch — add an audited Tier-2 halt (the feed already honors halt=True) or document one-shot+unregister as the accepted mechanism.
6. Hygiene: fix/delete the stale project_structure.md (describes a different reponels badged as static narrative; record the GDPR/CCPA "N-A" rationale ingovernance.

4. ✅ Actionable improvements (sequenced)

1. Unblock the defect: extend Mr-Ripley ingest to carry a GLD close (A8) → impleme fix → re-pin benchmarks.
2. Make the plug live-capable: ADR-014 §6 inside the quarantined adapter — startup reconcile, GET /v2/account cash-cap + auth smoke, fractionable check, client_order_id, QUEUED/PARTIAL/EXECUTION_UNCERTAIN state machine, typed error handling + raw_payload, FLAT→SELL exit.
3. Harden guard inputs (day-scoped daily_pnl/trades_today) and add the broker-traceability fields (alpaca_order_id, raw_payload).
4. Only then author the Phase-D live-money ADR + canary plan (KA-010 + ADR-012 ga
▎ Keep all of step 2–3 inside the default-OFF, non-replayable plug — the verification showed that threading any live broker read into the shared deterministic guard/build_guard_request would
contaminate the replay key and break BENCH-004/006.

5. Minimal end-to-end paper test script

This proves the full path the v0 adapter does not yet exercise — auth → account →hare price the system is missing) → submit → fill via WebSocket trade_updates →close. Run against a paper account only. It deliberately mirrors el_nino's ethos (stdlib REST; the one WebSocket dep is isolated, with a polling fallback).

"""alpaca_paper_e2e_probe.py — live-readiness probe for el_nino's Alpaca paper pa
Proves: auth -> account -> market data (GLD share price) -> market BUY -> fill via
trade_updates WebSocket -> close. PAPER ONLY. Creds from env (KA-008), never hard-coded.

    pip install websocket-client      # only dependency; REST is stdlib
    set ALPACA_API_KEY_ID=...         # PowerShell:  $env:ALPACA_API_KEY_ID="..."
    set ALPACA_API_SECRET_KEY=...
    python alpaca_paper_e2e_probe.py
"""
from __future__ import annotations
import json, os, sys, time, urllib.request, urllib.error
from urllib.parse import urlparse

PAPER_HOST = "paper-api.alpaca.markets"
TRADE_BASE = f"https://{PAPER_HOST}"
DATA_BASE  = "https://data.alpaca.markets"
STREAM_URL = f"wss://{PAPER_HOST}/stream"          # account/trade_updates stream
SYMBOL, QTY, TIMEOUT = "GLD", 1, 10.0

KEY, SECRET = os.environ.get("ALPACA_API_KEY_ID"), os.environ.get("ALPACA_API_SEC
HEADERS = {"APCA-API-KEY-ID": KEY or "", "APCA-API-SECRET-KEY": SECRET or "",
           "content-type": "application/json", "accept": "application/json"}

def _req(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(r, timeout=TIMEOUT) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:                # capture the reject reason (v0 discards this)
        return e.code, json.loads(e.read().decode() or "{}")

def check(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}{(' — ' + detail) if detail else ''}")
    return ok

def main() -> int:
    if not KEY or not SECRET:
        return check("creds present", False, "set ALPACA_API_KEY_ID / ALPACA_API_SECRET_KEY") or 1
    # paper-only boundary — refuse anything but the paper host (mirrors el_nino's guard)
    if urlparse(TRADE_BASE).hostname != PAPER_HOST:
        return check("paper-only host", False) or 1

    print("\n2.1 AUTH + 2.2 ACCOUNT"); st, acct = _req("GET", f"{TRADE_BASE}/v2/a
    if not check("GET /v2/account", st == 200, f"HTTP {st}"): return 1
    check("status ACTIVE & not blocked",
          acct.get("status") == "ACTIVE" and not acct.get("trading_blocked"), acct.get("status",""))
    bp = float(acct.get("buying_power", 0))
    check("buying_power parsed", bp > 0, f"${bp:,.2f}  PDT={acct.get('pattern_day_trader')}")

    print("\n2.3 MARKET DATA (the GLD share price el_nino's snapshot lacks — A8)"
    st, q = _req("GET", f"{DATA_BASE}/v2/stocks/{SYMBOL}/quotes/latest")
    ask = float(q.get("quote", {}).get("ap", 0)) if st == 200 else 0.0
    check(f"latest GLD quote (ask=${ask:.2f})", ask > 0,
          "NOTE: this $/share is the correct fill reference — NOT gold spot $/oz")

    print("\n2.5 SUBMIT (idempotent via client_order_id — the v0 broker-side gap)
    coid = f"probe-{SYMBOL}-{int(time.time())}"
    st, order = _req("POST", f"{TRADE_BASE}/v2/orders",
                     {"symbol": SYMBOL, "qty": QTY, "side": "buy", "type": "market",
                      "time_in_force": "day", "client_order_id": coid})
    if not check("POST /v2/orders accepted", st in (200, 201),
                 f"HTTP {st} status={order.get('status')} reason={order.get('message','')}"):
        return 1
    oid = order["id"]
    check("status is async (accepted/new/pending_new), NOT 'filled'",   # the v0 fail-closed trap
          order.get("status") in {"accepted", "new", "pending_new"}, order.get("status"))

    print("\n2.6 FILL via trade_updates WebSocket")
    filled = await_fill_ws(oid) or await_fill_poll(oid)   # WS first, REST poll fallback
    check("fill confirmed", bool(filled),
          f"avg=${float((filled or {}).get('filled_avg_price') or 0):.2f}" if filled else "no fill")

    print("\n2.9 CLOSE / cancel (reconcile-and-exit the probe leaves no residue)")
    st, _ = _req("DELETE", f"{TRADE_BASE}/v2/positions/{SYMBOL}")
    check("position closed", st in (200, 207, 404), f"HTTP {st}")
    return 0

def await_fill_ws(order_id, deadline=30.0):
    try:
        from websocket import create_connection
    except ImportError:
        print("    (websocket-client not installed — using REST poll fallback)");
    try:
        ws = create_connection(STREAM_URL, timeout=deadline)
        ws.send(json.dumps({"action": "auth", "key": KEY, "secret": SECRET}))
        ws.send(json.dumps({"action": "listen", "data": {"streams": ["trade_updat
        end = time.time() + deadline
        while time.time() < end:
            for msg in _iter(json.loads(ws.recv())):
                if msg.get("stream") == "trade_updates":
                    d = msg.get("data", {})
                    if d.get("event") == "fill" and d.get("order", {}).get("id") == order_id:
                        ws.close(); return d["order"]
        ws.close()
    except Exception as e:
        print(f"    (WS error: {e} — falling back to poll)")
    return None

def await_fill_poll(order_id, deadline=30.0):
    end = time.time() + deadline
    while time.time() < end:
        st, o = _req("GET", f"{TRADE_BASE}/v2/orders/{order_id}")
        if st == 200 and o.get("status") == "filled":
            return o
        time.sleep(2)
    return None

def _iter(x): return x if isinstance(x, list) else [x]

if __name__ == "__main__":
    sys.exit(main())

What it demonstrates (and the v0 adapter does not): reading the real account, fet snapshot is missing (the A8 prerequisite), tolerating the asynchronous orderstatus the v0 status-gate would wrongly raise on, confirming the fill over trade_updates (with a REST-poll fallback), capturing the reject reason, and reconcile-closing the position.

---
Bottom line: the concept is sound and the engineering discipline is high. The integration will work fully with Alpaca once ADR-014's already-scoped v1 work is built — gated, correctly, on fixing the one genuine defect (GLD-vs-gold-spot pricing) and its data prerequisitehave today because the live path is dormant; the risk is entirely about what must close before it is ever switched on.

Files I created during the audit have been cleaned up; no changes were made to the codebase.