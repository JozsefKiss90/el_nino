# Epoch (b) — Real-Corpus Accumulation Runbook

**Status:** operational since 2026-06-11. **Scope:** corpus accumulation only (no calibration).
**Owner repos:** producer = `C:\Code\Mr-Ripley` (Layer-2 Truth); consumer/governance = `C:\Code\el_nino` (Layer-3 + dev_graph).

This runbook documents how one immutable, SCHEMA-001-conformant snapshot is produced and banked
per day so the real corpus accumulates forward. It is the calendar-bound prerequisite for epoch (b)
*calibration*, which is a later, separately-governed step gated on N real snapshots existing.

---

## 1. Architecture (where things live)

| Concern | Location |
|---|---|
| Layer-2 producer (runnable) | `C:\Code\Mr-Ripley\layer2\adapters\snapshot_publisher.py` |
| Truth DB (system of record) | `C:\Code\Mr-Ripley\layer2_truth.db` |
| Ingestion adapters | `C:\Code\Mr-Ripley\layer2\adapters\{gold,move,spy,gld_holdings,fred_loader}_adapter.py` |
| Pipeline orchestrator | `C:\Code\Mr-Ripley\scripts\run_layer2_pipeline.py` (adapters → quality gate → publish) |
| **Daily EOD job (new)** | `C:\Code\Mr-Ripley\scripts\daily_eod_snapshot.ps1` |
| **Task registrar (new)** | `C:\Code\Mr-Ripley\scripts\register_daily_task.ps1` |
| Layer-3 consumer chain | `C:\Code\el_nino\src\` (`consume → build_features → classify → build_decision → evaluate`) |
| Vendored producer copy | `C:\Code\el_nino\snapshot_sources\snapshot_publisher.py` — **read-only reference, NOT runnable** |

> **Two-copy caveat (root cause of the historical DEBT-01 confusion):** the el_nino
> `snapshot_sources/` copy cannot import `layer2` and is a *reference snapshot only*. The
> 2026-06-08 DEBT-01 fix was applied to that dead copy; the live producer still NameError-ed until
> 2026-06-11. **Always fix and run the producer in Mr-Ripley.** Do not run the el_nino copy.

---

## 2. The corpus — two immutable, content-id-keyed sinks

Every banked snapshot is identified by its deterministic `snapshot_id` (SHA-256 over
`clock_ts + engine_version + config_version + sorted series values`). Both sinks are append-only:

1. **`layer2_truth.db`** → `snapshots` + `snapshot_values` tables. `snapshot_id` is the primary key
   and writes use `INSERT OR IGNORE`. The publisher additionally dedups by
   `(clock_ts, engine_version, config_version)` — so there is **exactly one snapshot per day**, and
   a same-day re-run is a logged no-op. History is never overwritten.
2. **`C:\Code\Mr-Ripley\runtime\snapshots\snapshot_<clock_date>__<id8>.json`** → a per-day immutable
   JSON copy of the published `latest_snapshot.json`. The archive step skips if the file already
   exists. `latest_snapshot.json` itself is the *latest pointer* (overwritten each run), **not** the
   archive.

Conformance (consumable) test, enforced by the consumer and the archive step:
`verdict == "PASS" AND guards.snapshot_ok AND NOT forced AND NOT dry_run`.

---

## 3. Automated daily run (the scheduled task)

- **Task name:** `MrRipley-Layer2-DailyEOD`  •  **Trigger:** daily at **23:00 local** (≈21:00 UTC,
  after the US cash close + FRED daily update; the publisher clock cut is 22:00 UTC).
- **Action:** `powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Code\Mr-Ripley\scripts\daily_eod_snapshot.ps1`
- `-StartWhenAvailable` reruns a missed day when the machine next wakes, so an offline night is not
  silently lost (the calendar-bound day is still recovered as long as the data is within threshold).
- The wrapper injects `L2_ENGINE_VERSION=gold-v3.3.0` into the process env (the repo `.env` line is an
  inert comment — nothing loads dotenv on the pipeline path), runs the pipeline, then archives.

**(Re)register / verify / remove:**
```powershell
# register or refresh
& C:\Code\Mr-Ripley\scripts\register_daily_task.ps1
# inspect
Get-ScheduledTaskInfo -TaskName 'MrRipley-Layer2-DailyEOD'
# remove
Unregister-ScheduledTask -TaskName 'MrRipley-Layer2-DailyEOD' -Confirm:$false
```

> The task runs as the current user, so it fires only while you are logged on. To run whether or not
> logged on, re-register with a stored credential (`-User`/`-Password`) or as `SYSTEM` (requires
> elevation) — and ensure `.secrets\fred_api_key.txt` is readable by that principal.

---

## 4. Manual operation

```powershell
# Full daily job by hand (same as the scheduled task)
& C:\Code\Mr-Ripley\scripts\daily_eod_snapshot.ps1

# Just the pipeline (adapters → gate → publish)
cd C:\Code\Mr-Ripley; $env:L2_ENGINE_VERSION='gold-v3.3.0'
& .\venv\Scripts\python.exe scripts\run_layer2_pipeline.py

# Preview only — no DB/JSON writes
& .\venv\Scripts\python.exe layer2\adapters\snapshot_publisher.py --dry-run

# List banked snapshots in the DB
& .\venv\Scripts\python.exe layer2\adapters\snapshot_publisher.py --list

# One-time wider catch-up after an outage (real FRED/Yahoo history; gold kept short to avoid
# fabricating spot for past days):
& .\venv\Scripts\python.exe layer2\run_backfill.py --only fred move spy gld --start-date <YYYY-MM-DD> --end-date <today>
& .\venv\Scripts\python.exe layer2\run_backfill.py --only gold
```

---

## 5. Verify a snapshot flows through the el_nino Layer-3 chain

```powershell
cd C:\Code\el_nino; $env:PYTHONPATH='C:\Code\el_nino\src'
& .\.venv\Scripts\python.exe -m pytest tests/gold/test_e2e_pipeline.py -q   # pinned golden chain
```
For an ad-hoc snapshot, run `consume → build_features → classify → build_decision → evaluate` over the
JSON path; `consume()` fail-closes unless the snapshot is consumable, and `snap.id_matches`
re-derives the `snapshot_id` (recompute_id-stable). The 2026-06-11 snapshot was verified end-to-end:
`RESTRICTIVE_RATES → AVOID`, `packet_id gold-v0:3691a5a776f1d7ef`, runtime `ADMIT`, deterministic
replay, `duplicate_ok` once-ever (2nd presentation → `REJECT`).

---

## 6. Point-in-time & data-quality notes

- **Fail-closed is correct, not a bug.** If any Tier-1 series is stale (> 3 days; DTWEXBGS > 10 days)
  or missing at the clock boundary, the gate FAILs and **no** snapshot is banked that day. That is a
  faithful refusal — fix the data, do not force.
- **DTWEXBGS** (Broad USD index) publishes weekly with a multi-day lag; it is the most likely single
  blocker. The daily 5-day adapter top-up captures each weekly print while it is still in-window; the
  10-day threshold tolerates the lag. Watch it after any multi-day outage.
- **Gold** live source (gold-api.com) returns *current spot* and assigns it to recent dates; only the
  latest (today) value is authoritative. Real gold history comes from the stooq JSON bulk load, not
  the daily job. The daily job therefore keeps the gold window short.
- **Revisions** are not yet tracked (`revision_seq = 0` throughout); FRED daily series are effectively
  non-revised. Revision-aware PIT is a Layer-2 maturation item for the calibration epoch, not this one.
- **Do not back-bank history with the same PIT integrity as forward days** — data fetched now for a
  past date is not what was known on that date. Forward accumulation from 2026-06-11 is the clean
  corpus; the ~40 lost days (2026-05-02 … 2026-06-10, while the producer was broken) are not
  reconstructed as snapshots by design.

---

## 7. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `NameError: H_get_engine_version` | running an unpatched producer copy | use `Mr-Ripley\layer2\adapters\snapshot_publisher.py` (fixed 2026-06-11); never run the el_nino vendored copy |
| `L2_ENGINE_VERSION is not set` → exit 1 | env var not in process | the wrapper sets it; for manual runs `$env:L2_ENGINE_VERSION='gold-v3.3.0'` |
| Gate FAIL, all Tier-1 stale | adapters haven't run for days | run the catch-up backfill (§4), then the pipeline |
| Gate FAIL, only DTWEXBGS stale | weekly print not yet captured/published | widen the FRED window (`--start-date`), or wait for FRED |
| FRED loader can't find key | `.secrets\fred_api_key.txt` missing/unreadable | restore the key file (or set `L2_FRED_KEY_PATH`) |
| Task never runs | machine off / not logged on at 23:00 | `-StartWhenAvailable` recovers on next wake; or re-register to run as SYSTEM |

---

## 8. Provenance — corpus as of 2026-06-11

| snapshot_id | clock_ts | verdict | Tier-1 | series |
|---|---|---|---|---|
| `952cc83a…afaef` | 2026-05-01T22:00Z | PASS | 16/16 | 21 |
| `05c8369d…7184d` | 2026-06-11T22:00Z | PASS | 16/16 | 21 |

Forward accumulation continues nightly via `MrRipley-Layer2-DailyEOD`.
