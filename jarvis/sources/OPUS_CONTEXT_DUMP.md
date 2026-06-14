# OPUS CONTEXT DUMP — Mr. Ripley / El Niño Project
## Teljes projekt-kontextus dashboard generáláshoz

> Ez a dokumentum egy ~1 órás Claude Cowork session teljes kontextusát tartalmazza.
> A feladatod: készíts egy komplex, vizuálisan gazdag HTML dashboardot a projekt aktuális állapotáról.
> A referencia stílus: pixel-art / sci-fi operations center (lásd a user által küldött képet).

---

# 1. A RENDSZER — MI EZ?

## Mr. Ripley
**Gold-first, fail-closed, snapshot-based döntéstámogató rendszer.**

- Layer 2 (Truth Layer): **operatív** — naponta gyűjt makro adatokat, quality gate-en átment snapshot-ot publikál
- Layer 3 (El Niño): **épül** — a döntési motor, ami a snapshot alapján gold (GLD ETF) kereskedési döntést hoz
- Execution: **tiltott** — automatikus kereskedés nincs, minden döntés paper trading + emberi oversight

**Alapelvek:**
- Determinisztikus: ugyanaz a snapshot → bit-azonos döntés
- Fail-closed: helytelen output helyett inkább nincs output
- Snapshot-driven: Layer 3 CSAK publishált snapshotból olvas, raw adatból soha
- LLM = analyst/auditor, NOT decision engine
- Governance-before-autonomy: minden autonómia növelés emberi jóváhagyás után

---

# 2. ARCHITEKTÚRA — RÉTEGMODELL

```
Layer 2 — Truth Layer (Mr. Ripley repó, C:\Code\Mr-Ripley)
    │  Napi EOD makro snapshot: gold, USD, rates, volatility, macro indicators
    │  Quality gate: 16/16 Tier-1 series PASS, freshness check
    │  Publikál: immutable snapshot_id (SHA-256 hash), archived JSON
    ▼
Layer 3 — El Niño (el_nino repó, C:\Code\el_nino)
    │
    ├─ MOD-003 Snapshot Consumer     → beolvassa a snapshot-ot, fail-closed
    ├─ MOD-004 Feature Builder       → 14 macro feature számítása
    ├─ MOD-005 Regime Classifier     → 11 rezsim + NEUTRAL + INDETERMINATE
    ├─ MOD-006 Gold Decision Builder → direction (LONG/FLAT/AVOID/WATCH) + confidence
    ├─ MOD-007 Paper Trading Runtime → ADMIT / HOLD / REJECT verdikt
    │
    ▼ [KÖVETKEZŐ: E2b — Alpaca Execution Adapter, még nem épül]
    
Layer 4 — Execution (tervezett, NEM ÉPÜL MÉG)
    │  Alpaca Paper API → GLD ETF vásárlás/eladás virtuális pénzzel
    │  Offline sim → determinisztikus replay
```

---

# 3. AKTUÁLIS ÁLLAPOT (2026-06-11)

## Mi van kész

| Modul | ID | Leírás | Audit Score |
|-------|----|--------|-------------|
| Snapshot Consumer | MOD-003 | Layer 2 snapshot beolvasás | — |
| Feature Builder | MOD-004 | 14 macro feature | — |
| Regime Classifier | MOD-005 | 11 rezsim determinisztikusan | **97/100** |
| Gold Decision Builder | MOD-006 | direction + confidence + packet_id | **94/100** |
| Paper Trading Runtime | MOD-007 | ADMIT/HOLD/REJECT admission gate | **97/100** |
| Risk Guardrail Engine | MOD-001 | Predikátum-alapú guardrail | — |
| **Teljes tesztcsomag** | — | 853 teszt, mind zöld | ✅ |

## Corpus státusz
- **DEBT-01 JAVÍTVA** (2026-06-11): snapshot_publisher NameError kijavítva
- **Napi automatikus task**: `MrRipley-Layer2-DailyEOD`, 23:00, Windows Scheduled Task
- **Valós snapshotok**: 2 db (2026-05-01 és 2026-06-11)
- **Forward accumulation**: indul 2026-06-11-től, naponta +1

## Valós pipeline eredmény
Az egyetlen éles snapshot eredménye a teljes L3 láncon:
`RESTRICTIVE_RATES → direction: AVOID → Paper Runtime: ADMIT`

---

# 4. EPOCH ROADMAP

| Epoch | Neve | Státusz |
|-------|------|---------|
| **E1** | DEBT-01 Fix (snapshot publisher) | ✅ **KÉSZ** |
| **E2a** | Paper Runtime / Admission Gate (MOD-007) | ✅ **KÉSZ** (97/100) |
| **E2b** | Alpaca Execution Adapter + fills + scorecard | ❌ **KÖVETKEZŐ** |
| **E3** | Empirikus kalibráció (corpus accumulation) | ⏳ **FOLYAMATBAN** — naptár-korlátozott |
| **E4** | Supervisor Engine (El Niño LLM réteg) | ❌ |
| **E5** | Policy Evolution (Human-Approved Learning) | ❌ |
| **E6** | La Niña — intraday protection (feltételes) | ❌ — E3 gap mérés dönti el |

### Szekvencia
```
[E1] ✅ → [E2a] ✅ → [E2b] ← KÖVETKEZŐ
                              ↓
                         [E3] ⏳ (corpus)
                              ↓
                         [E4] Supervisor
                              ↓
                         [E5] Policy Evolution
                              ↓
                   [E6] La Niña (ha E3 material gap)
                              ↓
                    [Phase D] Live Execution Gate
```

**Kritikus elv:** A naptári idő (corpus gyűjtés) a bottleneck, nem az engineering idő.

---

# 5. AZ EL NIÑO REPÓ STRUKTÚRÁJA

```
C:\Code\el_nino\
├── src/
│   ├── snapshot/snapshot_consumer/   ← MOD-003
│   ├── features/feature_builder/     ← MOD-004
│   ├── regime/regime_classifier/     ← MOD-005
│   ├── gold/
│   │   ├── decision_builder/         ← MOD-006
│   │   └── paper_runtime/            ← MOD-007
│   ├── risk/guardrail_engine/        ← MOD-001
│   └── supervisor/decision_engine/   ← MOD-002 (treasury branch, nem gold)
├── tests/                            ← 853 teszt
├── dev_graph/                        ← Obsidian knowledge graph (~140 node, ~920 él)
├── wiki/                             ← Tudásbázis (57 oldal)
├── benchmarks/                       ← Gold + Regime + Paper Runtime benchmarkok
├── EPOCH_B_CORPUS_RUNBOOK.md         ← Corpus accumulation playbook
├── GOLD_DECISIONPACKET_V0_FINAL_AUDIT.md  ← MOD-006 audit
├── PAPER_TRADING_RUNTIME_FINAL_AUDIT.md   ← MOD-007 audit
└── slice2 fit assessment and roadmap.md   ← Tervező doc (Slice 2 = MOD-007)
```

**dev_graph governance:** Minden architekturális döntés ADR-ban (Architecture Decision Record) rögzítve. ADR-001–ADR-009 chain. Neo4j + PostgreSQL + Obsidian triple substrate.

---

# 6. A 12 SARKALLATOS PONT (egyeztetett kérdések, visszatérésre vár)

## La Niña / Monitor

**1. 4 mechanikus trigger**
Minden trigger előre definiálja a küszöböt ÉS a reflexet: ártrigger, volatilitás-spike, sebesség/velocity, adatkiesés. Semmi sem dől el a pillanatban.

**2. Alert-only vs. automatikus reflex**
Governance-before-autonomy: papíron alert-only indul, automatikus reflex csak bizonyíték után.

**3. Monitor és determinizmus**
Minden monitor-esemény be van logolva a Trade Loggerbe, mint egy fill. A monitor csak az Alpaca paper backenden él (offline szimban nincs intraday).

**4. Triggerek jelenleg nem hangolhatók**
Küszöbök találgatások backtest/paper adat nélkül. La Niña marad egy spec a fiókban, amíg nincs adat.

## Backtest és paper trading

**5. Backtest felbontási probléma**
Napi EOD adattal a monitort nem lehet visszajátszani. Két út: (a) daily high/low közelítés, (b) valódi intraday hourly bars.

**6. Különböző szerepek**
Backtest: "kell-e egyáltalán a monitor?" — Paper trading: "működik-e?"

**7. Helyes sorrend**
High/low rés mérés → ha material: intraday adat + contingency replay → alert-only paper → automatikus reflex.

## Adatgyűjtés és tanulás

**8. Gyűjtés ≠ automatikus tanulás**
Gyűjtés most (olcsó), tanulás automatizálása vár amíg zárt kereskedések vannak.

**9. Unified scorecard schema**
Backtest és paper trading azonos formátumot emittál — ez az előfeltétele minden összehasonlításnak.

**10. Zapier**
A core-ban nem megfelelő. Periférián OK: push értesítés, Google Sheet sor.

**11. Human-Approved Policy Evolution**
Megfigyelés + javaslat automatikus; aktiválás emberi jóváhagyás. Háromállapotú kapu: Accept → ADR | Reject → Failure Library | Return for refinement. Kötelező ellenérvek a javaslatban.

## Look-ahead bias

**12. §5.3 kiterjesztés**
Két csapda a CPI példán túl: (a) megjelenési vs. vonatkozási dátum (FRED `vintage_date`), (b) revideált/vintage adatok (FRED `revision_seq=0` historikus futáshoz).

---

# 7. LA NIÑA ARCHITEKTÚRA (specifikáció, nem build order)

## Mi ez
Az EOD (napi) döntési réteg mellé egy intraday védőréteg. Csak akkor épül, ha E3 megmutatja, hogy az intraday rés materially nagyobb mint amit a sima stop elfog.

## 3 réteg

**Step 1 — Dual-Level Truth:**
- EOD macro snapshot (változatlan, naponta)
- IMS (Intraday Market-State Snapshot): hourly, frozen schema, `ims_id`, `parent_snapshot_id`
- IMS tartalom: gold spot, realized vol, VIX, DXY, yields
- IMS SOHA nem írja felül az EOD snapshot-ot

**Step 2 — Standing Orders / Contingency Table:**
Az EOD DecisionPacket tartalmaz egy 24 órás contingency table-t:
```
if intraday_drawdown > X%     → reduce 50%
if realized_vol > Y           → full exit
if IMS stale (> 2 hours)      → freeze + alert
if price reaches Z            → execute EOD-authorized entry
```
Contingency Evaluator: determinisztikus kód (NEM LLM), hourly fut, csak pre-authorized akciókat hajt végre.

**Step 3 — One-Way Valve:**
Intraday authority CSAK risk-reducing irányban: reduce, exit, tighten, freeze.
Új irány, size növelés, rezsim átsorolás → CSAK EOD.

## Governance
3 új guard field a DecisionPacket formális §16.1 amendmentként:
- `ims_freshness_ok`
- `action_budget_ok`
- `cooldown_ok`

**Deploy sorrend:** Alert-only először → paper evidence → automatikus reflex.

**Metafora:** Ha El Niño a meleg, lassú, irányadó réteg, La Niña a hideg, gyors, csak védő ellenfázis. Direction daily, protection continuously, discretion intraday never.

---

# 8. SCORECARD SÉMA (E2b-ben kell megépíteni)

| Field | Típus | Cél |
|-------|-------|-----|
| `decision_id` | string | DecisionPacket horgony |
| `snapshot_id` | string | Layer 2 truth horgony |
| `snapshot_clock_ts` | datetime | Point-in-time |
| `regime_class` | enum | Rezsim a döntéskor |
| `confidence` | float | Konfidencia a döntéskor |
| `direction` | enum | LONG/FLAT/AVOID/WATCH |
| `fill_price` | float/null | Tényleges fill |
| `expected_price` | float/null | Mid-price döntéskor |
| `slippage` | float/null | fill - expected |
| `outcome_pnl` | float/null | Realizált P&L zárásnál |
| `max_drawdown_intraday` | float/null | Legrosszabb intraday DD |
| `hold_duration_hours` | float/null | Tartási idő |
| `close_reason` | enum | eod_decision / contingency / stop / manual |
| `backend` | enum | offline_sim / alpaca_paper |
| `supervisor_verdict` | enum | PASS / SOFT_SHRINK / HARD_VETO / STUB |
| `guard_flags` | object | Minden guard értéke döntéskor |

**Kulcskövetelmény:** offline_sim és alpaca_paper AZONOS sémát emittálnak. Csak backend és fill_price tér el.

---

# 9. HUMAN-APPROVED POLICY EVOLUTION (E5)

## Policy Proposal kötelező tartalma
1. **Mit változtat** — konkrétan, nem általánosan
2. **Bizonyítékalap** — hány trade, melyik rezsim, expected vs actual delta
3. **Várható hatás** — kvantifikálva ahol lehet
4. **Ellenérvek (kötelező!)** — miért lehet téves; kis minta, rezsim-specificitás, alternatív magyarázat

Ellenérvek nélküli javaslat = advocacy, nem evidence.

## Háromállapotú kapu
- **Accept** → verzionált policy change, ADR entry, dátum + aláírás
- **Reject** → Failure Library, indoklással; rendszer nem javasolja újra ugyanezt
- **Return** → konkrét kérdés visszaküldve (pl. "gyűjts még 20 trade-et high-vol rezsimben")

---

# 10. VONATKOZÓ FÁJLOK

| Fájl | Helye | Tartalom |
|------|-------|---------|
| `el_nino_project_plan_v1.md` | `C:\Users\User\Claude\Projects\EL Nino\` | Master terv (5 rész + epoch roadmap) |
| `sarkallatos_pontok.md` | `C:\Users\User\Claude\Projects\EL Nino\` | 12 egyeztetett kulcspont |
| `EPOCH_B_CORPUS_RUNBOOK.md` | `C:\Code\el_nino\` | Corpus accumulation playbook |
| `PAPER_TRADING_RUNTIME_FINAL_AUDIT.md` | `C:\Code\el_nino\` | MOD-007 97/100 audit |
| `GOLD_DECISIONPACKET_V0_FINAL_AUDIT.md` | `C:\Code\el_nino\` | MOD-006 94/100 audit |
| `slice2 fit assessment and roadmap.md` | `C:\Code\el_nino\` | Slice 2 tervező doc |

---

# 11. A DASHBOARD FELADAT

## Mit kell elkészíteni
Egy **önállóan megnyitható HTML dashboard** a projekt teljes aktuális állapotáról.

## Referencia stílus
A user egy pixel-art / sci-fi operations center stílusú dashboardot mutatott (sötét háttér, neon zöld/kék/sárga colorok, több panel, élő metrikák érzetét keltő design). Hasonló mélységű és vizuális gazdagságú dashboardot kér.

## Kötelező panelek / szekciók

**1. Pipeline Status**
Az L3 pipeline 5 stádiuma vizuálisan:
`Snapshot Consumer → Feature Builder → Regime Classifier → Gold Decision Builder → Paper Runtime`
Minden modulnál: státusz (✅ kész), audit score, tesztszám.

**2. Corpus & Truth Layer**
- Valós snapshotok száma: 2 (2026-05-01, 2026-06-11)
- Forward accumulation: naponta +1
- Következő várható snapshot: ma este 23:00
- DEBT-01 státusz: FIXED

**3. Epoch Roadmap**
Vizuális progress bar vagy timeline:
E1 ✅ → E2a ✅ → E2b ⬜ → E3 ⏳ → E4 ⬜ → E5 ⬜ → E6 ⬜ (conditional)

**4. Live Pipeline Result**
Az egyetlen éles snapshot eredménye:
`Snapshot: RESTRICTIVE_RATES | Confidence: 0.397 | Direction: AVOID | Admission: ADMIT`

**5. Next Actions**
- E2b: Alpaca Execution Adapter tervezése (ADR-010 kell előbb)
- Corpus accumulation: ~N nap múlva elegendő kalibráció E3-hoz
- La Niña: spec a fiókban, E3 gap mérés dönti el

**6. 12 Sarkallatos Pont** (visszatérésre váró kérdések)
Kompakt lista, kategóriák szerint: La Niña / Monitor (1-4), Backtest (5-7), Tanulás (8-11), Look-ahead bias (12).

**7. Architecture Diagram**
Egyszerű flow: Layer 2 → L3 pipeline modulok → Paper Runtime → [jövő: Alpaca fill]

**8. Audit Scoreboard**
MOD-005: 97/100 | MOD-006: 94/100 | MOD-007: 97/100 | Tests: 853 green

## Stílus irányelvek
- Sötét háttér (fekete / sötét navy)
- Neon accent colorok: zöld (kész), sárga (folyamatban), piros (nem kész / blocker), kék (info)
- Pixel-art / monospace font érzetű
- Több panel / card layout
- Nem kell interaktívnak lennie — statikus, de vizuálisan gazdag
- Önálló HTML fájl, CSS és JS inline

## Output
Mentsd el `el_nino_dashboard.html` névvel. A user meg fogja nyitni böngészőben.
