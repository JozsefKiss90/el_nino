r"""alpaca_paper_e2e_probe.py - live-readiness probe for el_nino's Alpaca PAPER adapter (ADR-014).

Captures the empirical B-flags + live order-lifecycle facts that ADR-014 requires to close before any
live paper run, and the real live GLD mark that the Blocker-1 fix reads. stdlib-only (no third-party
deps; the reconcile poll replaces the out-of-scope trade_updates WebSocket). PAPER ONLY. Credentials
come from the environment (KA-008) - never hard-coded, never committed.

  WHAT IT CONFIRMS
    B1  client_order_id        accepted length/charset; a duplicate -> HTTP 422 (the dedup el_nino relies on)
    B2  GLD fractionable       GET /v2/assets/GLD -> `fractionable` (true => notional order; false => int shares)
    B3  settled-cash field     GET /v2/account   -> the literal `cash` field (+ `multiplier`); NEVER *_buying_power
    MARK real GLD mark         GET data.alpaca.markets/v2/stocks/GLD/{trades,quotes}/latest (the Blocker-1 read)
    LIFE order lifecycle       async accept (not 'filled' on POST); positions exclude un-filled; status filtering;
                               market+day fill via REST poll

  HOW TO RUN  (PowerShell, paper creds in the environment)
    $env:ALPACA_API_KEY_ID="<paper key>"
    $env:ALPACA_API_SECRET_KEY="<paper secret>"
    # read-only by default (account / assets / market data / positions-orders shapes -> B2, B3, MARK):
    .venv\Scripts\python.exe scripts\alpaca_paper_e2e_probe.py
    # opt in to the ORDER test (B1 + the async-fill lifecycle); submits ONE 1-share GLD market+day paper
    # order, observes the async accept + fill, then closes the position so it leaves no residue:
    .venv\Scripts\python.exe scripts\alpaca_paper_e2e_probe.py --submit-order

Paste the SUMMARY block back so the documented-assumption constants can be marked verified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse

PAPER_HOST = "paper-api.alpaca.markets"
TRADE_BASE = f"https://{PAPER_HOST}"
DATA_BASE = "https://data.alpaca.markets"
SYMBOL = "GLD"
TIMEOUT = 10.0
FILL_DEADLINE = 30.0

KEY = os.environ.get("ALPACA_API_KEY_ID")
SECRET = os.environ.get("ALPACA_API_SECRET_KEY")
HEADERS = {
    "APCA-API-KEY-ID": KEY or "",
    "APCA-API-SECRET-KEY": SECRET or "",
    "content-type": "application/json",
    "accept": "application/json",
}

# Mirrors el_nino's documented-assumption constants (execution/live_adapter.py) so a mismatch is loud.
COID_MAXLEN = 48
SETTLED_CASH_FIELD = "cash"


def _req(method: str, url: str, body: dict | None = None) -> tuple[int, dict]:
    """One JSON request; returns (status, parsed-body). HTTPError bodies are captured (never discarded)."""
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, {"_raw": raw}
    except urllib.error.URLError as exc:
        return 0, {"_error": str(exc)}


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" - {detail}" if detail else ""))
    return ok


def _make_coid() -> str:
    """A unique 48-char client_order_id in el_nino's shape (eln-<side>-<hex>), at the B1 length budget."""
    seed = f"probe|{time.time()}".encode("utf-8")
    digest = hashlib.sha256(seed).hexdigest()
    return (f"eln-buy-{digest}")[:COID_MAXLEN]


def read_only_checks(summary: dict) -> bool:
    ok = True

    print("\n[1] AUTH + ACCOUNT (B3: the settled-cash field + multiplier)")
    st, acct = _req("GET", f"{TRADE_BASE}/v2/account")
    ok &= check("GET /v2/account", st == 200, f"HTTP {st}")
    if st == 200:
        ok &= check(
            "status ACTIVE and not blocked",
            acct.get("status") == "ACTIVE" and not acct.get("trading_blocked")
            and not acct.get("account_blocked"),
            f"status={acct.get('status')} trading_blocked={acct.get('trading_blocked')} "
            f"account_blocked={acct.get('account_blocked')}",
        )
        has_cash = SETTLED_CASH_FIELD in acct
        ok &= check(
            f"settled-cash field {SETTLED_CASH_FIELD!r} present (B3)", has_cash,
            f"{SETTLED_CASH_FIELD}={acct.get(SETTLED_CASH_FIELD)} multiplier={acct.get('multiplier')}",
        )
        # Show the full cash/buying-power surface so the operator can confirm `cash` == settled cash and
        # that el_nino is right to bind the cap to it (never any *_buying_power).
        for field in (
            "cash", "multiplier", "buying_power", "regt_buying_power", "daytrading_buying_power",
            "non_marginable_buying_power", "cash_withdrawable", "pattern_day_trader", "currency",
        ):
            print(f"        account.{field} = {acct.get(field)}")
        summary["B3_settled_cash_field"] = SETTLED_CASH_FIELD if has_cash else "MISSING - INVESTIGATE"
        summary["B3_cash_value"] = acct.get(SETTLED_CASH_FIELD)
        summary["B3_multiplier"] = acct.get("multiplier")

    print("\n[2] ASSET (B2: GLD fractionable)")
    st, asset = _req("GET", f"{TRADE_BASE}/v2/assets/{SYMBOL}")
    ok &= check(f"GET /v2/assets/{SYMBOL}", st == 200, f"HTTP {st}")
    if st == 200:
        frac = asset.get("fractionable")
        ok &= check("`fractionable` field present (B2)", "fractionable" in asset, f"fractionable={frac}")
        for field in ("tradable", "fractionable", "shortable", "marginable", "min_order_size",
                      "min_trade_increment", "status"):
            print(f"        asset.{field} = {asset.get(field)}")
        summary["B2_GLD_fractionable"] = frac

    print("\n[3] MARKET DATA (MARK: the REAL live GLD share mark - the Blocker-1 read)")
    st, trade = _req("GET", f"{DATA_BASE}/v2/stocks/{SYMBOL}/trades/latest")
    t = trade.get("trade", {}) if st == 200 else {}
    ok &= check(
        "GET /v2/stocks/GLD/trades/latest -> trade.p / trade.t", st == 200 and "p" in t,
        f"trade.p={t.get('p')} trade.t={t.get('t')}",
    )
    summary["MARK_trade_p"] = t.get("p")
    summary["MARK_trade_t"] = t.get("t")
    st, quote = _req("GET", f"{DATA_BASE}/v2/stocks/{SYMBOL}/quotes/latest")
    q = quote.get("quote", {}) if st == 200 else {}
    check(
        "GET /v2/stocks/GLD/quotes/latest -> quote.ap / quote.bp", st == 200 and "ap" in q,
        f"quote.ap={q.get('ap')} quote.bp={q.get('bp')}",
    )

    print("\n[4] POSITIONS + ORDERS shape (LIFE: positions exclude un-filled; status filtering)")
    st, positions = _req("GET", f"{TRADE_BASE}/v2/positions")
    check("GET /v2/positions", st == 200, f"HTTP {st} count={len(positions) if isinstance(positions, list) else '?'}")
    if isinstance(positions, list):
        gld = next((p for p in positions if p.get("symbol") == SYMBOL), None)
        print(f"        GLD position currently held: {bool(gld)}"
              + (f" qty={gld.get('qty')} avg_entry={gld.get('avg_entry_price')}" if gld else ""))
    st, openorders = _req("GET", f"{TRADE_BASE}/v2/orders?status=open")
    check("GET /v2/orders?status=open (status filtering)", st == 200,
          f"HTTP {st} open={len(openorders) if isinstance(openorders, list) else '?'}")
    return ok


def order_check(summary: dict) -> bool:
    """Submit ONE 1-share GLD market+day paper order: B1 (coid len + 422 dedup) + async-fill lifecycle.

    Closes the position at the end so the probe leaves no residue. ONLY runs under --submit-order.
    """
    ok = True
    coid = _make_coid()
    print(f"\n[5] SUBMIT (B1: client_order_id len={len(coid)} <= {COID_MAXLEN}; LIFE: async accept)")
    print(f"        client_order_id = {coid!r}")
    body = {"symbol": SYMBOL, "qty": 1, "side": "buy", "type": "market", "time_in_force": "day",
            "client_order_id": coid}
    st, order = _req("POST", f"{TRADE_BASE}/v2/orders", body)
    ok &= check("POST /v2/orders accepted (B1 length OK)", st in (200, 201),
                f"HTTP {st} status={order.get('status')} msg={order.get('message', '')}")
    if st not in (200, 201):
        summary["B1_coid_len_accepted"] = f"REJECTED at len {len(coid)} (HTTP {st})"
        return False
    summary["B1_coid_len_accepted"] = f"len {len(coid)} accepted"
    order_id = order.get("id")
    submit_status = order.get("status")
    check("submit status is ASYNC (accepted/new/pending_new), NOT 'filled'",
          submit_status in {"accepted", "new", "pending_new"}, f"status={submit_status}")
    summary["LIFE_submit_status"] = submit_status

    print("\n[6] DUPLICATE client_order_id -> HTTP 422 (B1: the idempotent dedup el_nino relies on)")
    st_dup, dup = _req("POST", f"{TRADE_BASE}/v2/orders", body)
    is_422 = st_dup == 422
    check("re-submit same client_order_id -> 422", is_422, f"HTTP {st_dup} body={json.dumps(dup)[:160]}")
    summary["B1_duplicate_status"] = st_dup
    summary["B1_duplicate_body"] = json.dumps(dup)[:240]

    print("\n[7] FILL via REST poll (LIFE: async fill resolved from the order read)")
    filled = None
    deadline = time.time() + FILL_DEADLINE
    while time.time() < deadline:
        st_o, o = _req("GET", f"{TRADE_BASE}/v2/orders/{order_id}")
        if st_o == 200 and o.get("status") == "filled":
            filled = o
            break
        time.sleep(2)
    check("order filled (resolved from GET /v2/orders/{id})", bool(filled),
          (f"filled_qty={filled.get('filled_qty')} filled_avg_price={filled.get('filled_avg_price')}"
           if filled else "no fill within deadline (market may be closed - order is QUEUED to next open)"))
    if filled:
        summary["LIFE_fill_avg_price"] = filled.get("filled_avg_price")
        summary["LIFE_fill_qty"] = filled.get("filled_qty")
        st_p, positions = _req("GET", f"{TRADE_BASE}/v2/positions")
        held = isinstance(positions, list) and any(p.get("symbol") == SYMBOL for p in positions)
        check("GET /v2/positions now reflects the filled order (positions exclude un-filled)", held)
    else:
        summary["LIFE_fill"] = "not filled within deadline (queued to next open)"

    print("\n[8] CLEANUP (leave no residue: cancel open orders + close the GLD position)")
    _req("DELETE", f"{TRADE_BASE}/v2/orders/{order_id}")  # cancel if still open (no-op if filled/gone)
    st_c, _ = _req("DELETE", f"{TRADE_BASE}/v2/positions/{SYMBOL}")
    check("position closed / nothing left open", st_c in (200, 207, 404), f"HTTP {st_c}")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description="el_nino Alpaca PAPER live-readiness probe (ADR-014).")
    parser.add_argument("--submit-order", action="store_true",
                        help="opt in to the order test (B1 + async-fill lifecycle); submits 1 GLD share, "
                             "then closes it. Default OFF (read-only checks only).")
    args = parser.parse_args()

    if not KEY or not SECRET:
        check("creds present", False, "set ALPACA_API_KEY_ID / ALPACA_API_SECRET_KEY (paper) in the env")
        return 1
    # Paper-only boundary - parsed-hostname equality (mirrors execution.alpaca_adapter._is_paper_base_url).
    if urlparse(TRADE_BASE).scheme != "https" or urlparse(TRADE_BASE).hostname != PAPER_HOST:
        check("paper-only host", False, f"refusing non-paper host {TRADE_BASE}")
        return 1
    print(f"el_nino Alpaca PAPER probe -> {TRADE_BASE} (paper money) + {DATA_BASE} (market data, read-only)")

    summary: dict = {}
    ok = read_only_checks(summary)
    if args.submit_order:
        ok = order_check(summary) and ok
    else:
        print("\n[5-8] ORDER test SKIPPED (read-only). Re-run with --submit-order to capture B1 + the "
              "async-fill lifecycle.")

    print("\n" + "=" * 78)
    print("SUMMARY (paste this back; values marked here become the verified constants)")
    print("=" * 78)
    for k, v in summary.items():
        print(f"  {k:24} = {v}")
    print("\n  el_nino assumptions to confirm against the above:")
    print(f"    _COID_MAXLEN       = {COID_MAXLEN}   (B1: the submitted coid len must be accepted)")
    print(f"    _SETTLED_CASH_FIELD = {SETTLED_CASH_FIELD!r}  (B3: must be present on /v2/account)")
    print("    mark fields         = trade.p / trade.t  (Blocker-1 live GLD mark read)")
    print("=" * 78)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
