# El Niño — Epoch E2b: Alpaca PAPER Execution Adapter
## Roadmap / ADR-011 nyersanyag (human-read — NEM önvezérlő automatizálás, NEM kódgenerálás)

Ez a dokumentum egy ember által olvasandó útiterv és az ADR-011 nyersanyaga. Nem futtatható automatizálás, és nem kódgenerálási feladat. Minden lépés megnevezi a saját emberi ellenőrzőpontját. A cél, hogy a *mi* nyolc komponensünket pontosítsa — nem egy generikus bot leírása.

> **Validációs státusz.** A terv keresztellenőrizve a docs.alpaca.markets aktuális dokumentációja ellen. A validáció nem talált kemény falat — minden alapmechanika támogatott. Négy finomítás és egy szabály-megfelelési pont beépítve (lentebb jelölve); a korábbi EOD-queue `[FLAG]` megerősítve és lezárva. Két `[FLAG]` (client_order_id hossz, GLD fractionable) és egy dashboard-megerősítés (cash vs. margin) marad nyitva kód előtt.

---

## Feltételezések (előre rögzítve)

1. **Cash account.** A paper-számla készpénz-számlaként működik; semmilyen margin/short képesség nincs használatban. **Megjegyzés:** a paper-számla alapból margin-konfigurációval indul (jellemzően 4x vételerő) — ezt vagy cash-számlára állítjuk, vagy az adapter hard-cap-eli (lásd 4. lépés).
2. **GLD az arany instrumentuma.** A `GOLD` asset_id a GLD ETF-re képződik le; az olaj és minden második eszköz a horizonton túl van.
3. **EOD-vezérelt döntés.** A DecisionPacket a zárás után, piaci időn kívül keletkezik — a végrehajtás a **következő reguláris ülés elejére** sorba állítva történik (megerősítve, lásd lent és 5. lépés). Ez nem a nyitó-aukciós ár.
4. **Bináris méret.** A döntés LONG/FLAT; nincs konfidencia-skálázott méretezés. A teljes méret előre regisztrált, determinisztikus fix-notional, a cash-egyenleghez kötve.
5. **A számok igazolatlanok, amíg nem citáltak.** Az Alpaca-specifikumokat a dokumentáció igazolja; ahol nem találtam egyértelmű forrást, az `[FLAG]` jelzéssel szerepel, és emberi megerősítés nélkül nem épül rá kód.

---

## Irányadó alkotmány (soha nem felülírható)

- **Gold-first, fail-closed, snapshot-driven.** Ugyanaz a snapshot be → bit-azonos döntés ki. Egy kimenet sem jobb a rossz kimenetnél.
- **Long-or-flat KIZÁRÓLAG** (LONG/FLAT/AVOID/WATCH). Nincs short, **nincs margin** — csak cash-account szemantika. Nincs konfidencia-skálázott méret (bináris).
- **PAPER kizárólag:** a cél a `paper-api.alpaca.markets`, virtuális pénzzel. Az éles, valódi pénzes végrehajtás a Phase D — strukturálisan blokkolt, hatókörön kívül.
- **Governance before autonomy:** kapuzott, nem önvezérlő. Az ADR-011 Accepted státuszú kell legyen bármilyen kód előtt. Minden lépés megnevezi az emberi ellenőrzőpontját.
- **Zapier tilos a magban** (nem-determinisztikus). Az Alpaca természetes-nyelvű MCP szervere ugyanezen okból szintén a magon kívül van.
- **Minden fill-record a kormányzó `snapshot_id`-ra hivatkozik;** az írások megváltoztathatatlanok (`INSERT OR IGNORE`), soha nem `UPDATE`.
- **La Niña a mi determinisztikus értékelőnkben,** nem bróker-oldali feltételes ordereken keresztül.

---

## Alpaca-igazolás a docs.alpaca.markets ellen

A következőket a hivatalos dokumentáció **megerősíti**. Ahol nem találtam egyértelmű forrást, ott `[FLAG]` jelzi, hogy emberi megerősítés vagy empirikus teszt kell — kitalált végpont/mező/limit nincs.

**Megerősítve — API és orderek:**

- **Base URL-ek.** Paper: `https://paper-api.alpaca.markets`. Élő: `https://api.alpaca.markets`. Külön domain, külön kulcs; a live hitelesítő adatok a paper API-n nem használhatók, és fordítva.
- **Auth headerek.** `APCA-API-KEY-ID` és `APCA-API-SECRET-KEY` minden hívásnál.
- **Order beküldés.** `POST /v2/orders` (JSON body). Listázás: `GET /v2/orders` (max. 500/hívás). Egyedi: `GET /v2/orders/{order_id}`, `GET /v2/orders:by_client_order_id`.
- **`client_order_id`.** Auto-generált, ha nincs megadva; visszaadva az objektumban. Duplikált `client_order_id` egy **aktív** orderre → **HTTP 422**. **Ez a mi idempotencia-védelmünk.**
- **Reconcile-olvasás.** `GET /v2/positions` (összes), `GET /v2/positions/{symbol}`; zárás `DELETE /v2/positions/{symbol}`.
- **Fill-mezők.** `filled_qty`, `filled_avg_price`, `submitted_at`, `filled_at`, `status`, `side`, `symbol`, `notional`/`qty`, `commission`.
- **Status enum.** `new`/`accepted` → `partially_filled` → `filled`; továbbá `done_for_day`, `canceled`, `expired`, `rejected`, valamint piaci időn kívül gyakori `accepted`/`pending_new` (sorba állítva, még nem teljesült).
- **Market order.** Stop/limit ár nem adható meg → különben HTTP 422.
- **Tört részvény / notional.** Market + `time_in_force=day` esetén; `qty` **vagy** `notional` (mindkettő → HTTP 400); 9 tizedesjegyig. A `notional` csak market + day esetén. **Ez teszi a fix-notional méretezést kivitelezhetővé.**

**Megerősítve — paper-szimuláció és időzítés (a validáció kulcspontjai):**

- **EOD-queue (a korábbi `[FLAG]` lezárva).** A zárás után beadott `day` order a következő kereskedési napra sorba kerül; a piaci időn kívüli hívásokat az Alpaca elfogadja és a következő elérhető időpontban a piacra irányítja, de **csak a következő ülésben teljesül**. → A sima market + day a helyes út az „act at next open"-höz.
- **Nyitó-aukció vs. tört részvény — kizárják egymást.** A nyitó auKción teljesülő order a TIF=OPG (market-on-open), amit 7:00 PM után, 9:28 AM előtt kell beadni — **de az OPG csak egész részvényre megy, notional/fractional méretre nem.** Mivel fix-notional méretezünk, **OPG nem használható**; marad a market+day queue → következő ülés eleje, normál routinggal (nem auKciós ár).
- **Paper-fill fidelitás.** Az éles orderek valós likviditás ellen teljesülnek; a paper orderek szimulációs modellel, a valós idejű NBBO ellen. A rendelési mennyiséget a paper **nem** veti össze az NBBO likviditással — vagyis irreálisan nagy orderre is kaphatsz teljes fillt. → **A „csúszás a méret függvényében" metrika paper alatt értelmetlen**, a csúszás idealizált. Egy dolog valósan szimulálódik: a teljesülő orderek **10%-ában véletlen méretű részleges fill** — tehát a partial-fill kezelésünk lefut.
- **PDT és osztalék.** A paper szimulálja a Pattern Day Trader ellenőrzést (5 munkanapon belüli 4. day trade elutasul <25k nettó vagyonnál); osztalékot **nem** szimulál.

**Megjelölve (emberi megerősítés / empirikus teszt kell, kód előtt):**

- `[FLAG]` **`client_order_id` pontos hossz- és karakterkészlet-korlátja.** Az egyediség-ablak megerősített, de a max. hossz nem. A kulcsunk `hash(snapshot_id + asset_id + intended_action)`; egy SHA-256 hex 64 karakter — ha van pl. 48 karakteres plafon, rövidített digest kell. Megerősítendő a Create Order referencián vagy empirikusan.
- `[FLAG]` **GLD `fractionable` státusza.** Futásidőben a `GET /v2/assets/GLD` válaszában a `fractionable: true` mező ellenőrzendő — nem feltételezni. Ha hamis, egész részvényes méretezésre kell váltani.
- `[FLAG]` **Cash vs. margin alapértelmezés.** A paper-számla alapból margin (jellemzően 4x vételerő). A cash-account elv betartásához cash paper-számla, vagy `notional ≤ available_cash` hard-cap. A pontos alapértelmezett vételerő a dashboardon megerősítendő.

---

## A nyolc komponens — akció-lépések függőségi sorrendben

Minden lépés: **cél · kulcslépések · függőség · emberi ellenőrzőpont · várt kimenet.**

### 1. lépés — ADR-011 megírása és elfogadása

- **Cél:** rögzíteni az adapter határait, garanciáit és kifejezett hatókör-kizárásait, mielőtt bármilyen kód készül.
- **Kulcslépések:** Status/Context/Decision/Out-of-scope/Consequences kitöltése a lenti vázzal; a 2–8. lépés tartalma adja a Decision/Consequences anyagát; a validáció megállapításai mint elfogadott döntések, a maradék `[FLAG]`-ek mint döntés-előfeltételek.
- **Függőség:** ez a gyökér — semmi sem előzi meg.
- **Emberi ellenőrzőpont:** te elfogadod (Proposed → Accepted). Amíg nem Accepted, nincs kódolás.
- **Várt kimenet:** egy verziózott, hivatkozható ADR, ami a teljes E2b-t kormányozza.

```
# ADR-011: Alpaca Paper Execution Adapter
## Status        Proposed → Accepted (dátum)
## Context        L3 verdikt kész; nincs valós végrehajtási visszacsatolás.
## Decision       Alpaca paper; reconcile-then-act; determinisztikus
                  client_order_id; fix-notional cash-cap-pel; market+day
                  queue-to-next-open; GLD-alapú csúszás-referencia; fail-closed.
## Out of scope   Élő pénz (Phase D); short; margin; olaj; konfidencia-skálázás;
                  Zapier; Alpaca NL MCP; bróker-oldali conditional orderek; OPG.
## Consequences   Biztonságos izolált paper-fokozat; az élő strukturálisan blokkolt.
                  Paper alatt a csúszás-metrikák idealizáltak (lásd 8. lépés).
```

### 2. lépés — Execution Adapter

- **Cél:** a publikált DecisionPacketet determinisztikusan order-akcióvá fordítani.
- **Kulcslépések:** **reconcile-then-act** — előbb `GET /v2/positions`, a célállapothoz mért deltára cselekedni. LONG → cél a teljes méret; FLAT → cél nulla; AVOID/WATCH → **nincs order, de NO_ACTION rekord**. Determinisztikus `client_order_id = hash(snapshot_id + asset_id + intended_action)` (a `[FLAG]` hosszkorlát tisztázása után véglegesítve). Market order, `time_in_force=day`. Beküldés után szinkron poll a `filled`/`rejected` állapotig — a sorba állított, még nem teljesült (`accepted`/`pending_new`) állapot **nem** hiba (lásd 5. lépés).
- **Függőség:** elfogadott ADR-011 (1); a `client_order_id`-korlát igazolása.
- **Emberi ellenőrzőpont:** dry-run review — a delta-számítás és a `client_order_id`-képzés átnézése valós order beküldése előtt.
- **Várt kimenet:** egy adapter, ami célállapotba mozdít, nem „vakon vesz", és idempotens újraindításra.

### 3. lépés — Fill-record perzisztencia

- **Cél:** minden végrehajtási kimenetet befagyasztani, a `snapshot_id`-hoz horgonyozva.
- **Kulcslépések:** immutable tábla, `INSERT OR IGNORE`, soha `UPDATE`. **Csúszás-referencia javítva:** két külön ár tárolódik — `regime_ref_gold_spot` (a snapshotból, $/uncia, csak a döntési kontextushoz) és `exec_ref_gld_price` (GLD záróár a döntés napján, $/részvény, a csúszás referenciája). A `slippage_bps` az **utóbbira** számolódik — sosem a két különböző instrumentum összevetéséből. Az Alpaca nyers válasza JSON-ként befagyasztva; a NO_ACTION sorok is bekerülnek.
- **Függőség:** adapter (2); GLD záróár forrása (Alpaca market data vagy Yahoo) a döntés idején.
- **Emberi ellenőrzőpont:** az első néhány fill-record kézi átnézése — a `slippage_bps` helyesen GLD-vs-GLD-e.
- **Várt kimenet:** auditálható, visszajátszható végrehajtási napló; a scorecard alapja.

```sql
CREATE TABLE IF NOT EXISTS fill_record (
    fill_id              TEXT PRIMARY KEY,   -- hash(client_order_id)
    snapshot_id          TEXT NOT NULL,      -- a horgony
    client_order_id      TEXT NOT NULL,      -- a determinisztikus dedup-kulcs
    alpaca_order_id      TEXT,
    asset_id             TEXT NOT NULL,      -- GOLD
    symbol               TEXT NOT NULL,      -- GLD
    intended_action      TEXT NOT NULL,      -- BUY / SELL / NO_ACTION
    intended_qty         REAL,               -- a cél-delta (notional vagy share)
    filled_qty           REAL,               -- a TÉNYLEGES teljesülés
    filled_avg_price     REAL,               -- a TÉNYLEGES GLD átlagár
    regime_ref_gold_spot REAL,               -- snapshot arany-spot ($/oz), KONTEXTUS
    exec_ref_gld_price   REAL,               -- GLD záróár a döntés napján ($/share)
    slippage_bps         REAL,               -- (filled_avg_price - exec_ref_gld_price)
                                             --   / exec_ref_gld_price * 10000
    submitted_ts         TEXT NOT NULL,
    filled_ts            TEXT,
    status               TEXT NOT NULL,      -- FILLED/PARTIAL/QUEUED/REJECTED/
                                             -- NO_ACTION/EXECUTION_UNCERTAIN
    backend              TEXT NOT NULL,      -- offline_sim / alpaca_paper
    engine_version       TEXT NOT NULL,
    config_version       TEXT NOT NULL,
    raw_payload          TEXT NOT NULL       -- az Alpaca teljes válasza, fagyasztva
);
```

### 4. lépés — Instrumentum-leképezés és méretezés

- **Cél:** explicit, versionözött leképezés és előre regisztrált, cash-fedezetű determinisztikus méret.
- **Kulcslépések:** konfig `GOLD → GLD`, `fractional: true` (a `[FLAG]` `fractionable`-ellenőrzés után); **fix-notional** méret a `notional` mezőn (market + day). **Cash-cap:** a notional sosem lépi túl a rendelkezésre álló készpénzt — ezzel a margin-szemantika strukturálisan kizárt, akkor is, ha a számla margin-konfigurációjú. **Order-mód:** market + `time_in_force=day` (NEM OPG — az tört méretre nem megy). A méret a konfigból jön, soha nem a döntés pillanatában improvizálva.
- **Függőség:** GLD `fractionable` igazolása; a cash vs. margin alapértelmezés tisztázása; a méretezési érték emberi jóváhagyása.
- **Emberi ellenőrzőpont:** te rögzíted a fix-notional értéket, a cash-cap szabályt és a leképezést — ez döntés, nem mérnöki feladat.
- **Várt kimenet:** versionözött instrument/sizing konfig; eszközfüggetlenül bővíthető.

```yaml
instruments:
  GOLD:
    symbol: GLD
    fractional: true            # csak ha GET /v2/assets/GLD → fractionable=true
sizing:
  mode: fixed_notional          # bináris: LONG → teljes, FLAT → nulla
  notional_usd: 10000           # ELŐRE regisztrált, determinisztikus
  cap_to_available_cash: true   # margin-szemantika strukturálisan kizárva
order:
  type: market
  time_in_force: day            # queue-to-next-open; OPG NEM (fractional kizárja)
```

### 5. lépés — Hibakezelés és fail-closed

- **Cél:** bizonytalan állapotban inkább ne cselekedj és naplózz, mintsem hibásan tovább menj.
- **Kulcslépések:** timeout / nincs válasz → `EXECUTION_UNCERTAIN` rekord + leállás az adott eszközön (nem vak retry); auth-hiba → leállás; piac zárva → **várt állapot**, az order a következő reguláris ülésre sorba állítva („act at next open" = a következő ülés eleje, normál routing, **nem** auKciós ár); **sorba állított, még nem teljesült order** (`accepted`/`pending_new`) → **nem hiba, nem újraküldendő** — a reconcile a következő futáskor látja a fillt; részleges fill → a `filled_qty` a tényleges, a következő reconcile korrigál (a paper 10%-ban szimulál partialt, tehát ez tényleg lefut); **indításkor kötelező reconcile** bármilyen új akció előtt. **PDT:** az EOD long-or-flat overnight tart pozíciót, így a day-trade számláló >25k tőkénél nem üt be — de a guard ismerje a `rejected` PDT-okot.
- **Függőség:** adapter (2), fill-record (3).
- **Emberi ellenőrzőpont:** a hibataxonómia, az „act at next open" politika és a queued-állapot kezelésének átnézése az ADR-011-ben.
- **Várt kimenet:** öngyógyító, soha nem duplikáló, a sorba állított ordert helyesen kezelő adapter.

### 6. lépés — Scorecard séma

- **Cél:** az első fill ELŐTT rögzíteni a mezőket, hogy az összehasonlítás egységes legyen.
- **Kulcslépések:** per-döntés sorok; round-trip párosítás (egy LONG nyitja, a következő FLAT zárja → realizált P&L, hold time); version-lock (`engine_version` + `config_version`). A csúszás GLD-alapú referenciával (`exec_ref_gld_price`), nem arany-spottal. **Paper-figyelmeztetés a sémában:** a csúszás-mezők paper alatt idealizáltak (NBBO-fill, nincs likviditás-hatás), ezért „live-only" jelölést kapnak az elemzésben (lásd 8. lépés). Aggregátumok: irány-pontosság rezsimenként (ez paper alatt is valid), és — csak élesben — átlagos csúszás, csúszás a méret függvényében.
- **Függőség:** fill-record (3).
- **Emberi ellenőrzőpont:** a mezőlista jóváhagyása az első futás előtt.
- **Várt kimenet:** a finomhangolás motorja — „a rezsim-hívás korrelált-e a price action-nel", a végrehajtási minőség pedig élesre eltéve.

```sql
CREATE TABLE IF NOT EXISTS scorecard (
    snapshot_id          TEXT PRIMARY KEY,
    asset_id             TEXT NOT NULL,
    regime               TEXT,            -- pl. RESTRICTIVE_RATES
    direction            TEXT,            -- LONG/FLAT/AVOID/WATCH
    confidence           REAL,
    verdict              TEXT,            -- ADMIT/...
    regime_ref_gold_spot REAL,            -- arany-spot, döntési kontextus
    exec_ref_gld_price   REAL,            -- GLD záróár, csúszás-referencia
    fill_price           REAL,            -- GLD átlagár; NULL, ha NO_ACTION
    slippage_bps         REAL,            -- GLD-vs-GLD; paper alatt idealizált
    latency_ms           INTEGER,         -- DecisionPacket → fill
    position_qty         REAL,
    entry_ts             TEXT,
    exit_ts              TEXT,            -- amikor egy későbbi FLAT zárja
    hold_duration_sec    INTEGER,
    realized_pnl         REAL,
    backend              TEXT NOT NULL,
    engine_version       TEXT NOT NULL,
    config_version       TEXT NOT NULL
);
```

### 7. lépés — API-kulcs és környezet-elkülönítés

- **Cél:** strukturálisan lehetetlenné tenni az éles csatlakozást Phase D előtt.
- **Kulcslépések:** **hard guard** — az adapter csak akkor indul, ha a `base_url` tartalmazza a `paper-api` szövegrészt, különben nem-nulla exit kóddal leáll; az élő URL a konfig-validációban nem is megengedett a Phase D unlock előtt. Kulcsok `.gitignore`-ban, soha nem commitolva, soha nem logolva (maszkolva), soha nem a snapshot/decision adatban.
- **Függőség:** minden kód előtt — ez a védőfal, nem egy fázis.
- **Emberi ellenőrzőpont:** a guard kódjának átnézése; annak igazolása, hogy paper-kulcsokkal indul.
- **Várt kimenet:** a paper/real money határ Python-hook-kal kikényszerítve (nem viselkedési ígérettel).

```python
def assert_paper_environment(base_url: str) -> None:
    if "paper-api" not in base_url:
        raise SystemExit(
            "FAIL-CLOSED: live execution blocked until Phase D. "
            f"Refusing to start against {base_url}"
        )
```

### 8. lépés — Megfigyelési ablak

- **Cél:** előre rögzíteni, mikor és mi alapján vonsz le következtetést — a confidence theater ellen.
- **Kulcslépések:** két külön kapu. **(a) Vízvezeték-ellenőrzés** (korai, N nap): mennek-e az orderek, sorba állnak-e helyesen, teljesülnek-e a következő nyitáskor, rögzülnek-e a fill-ek, töltődik-e a scorecard, helyesek-e a NO_ACTION sorok, lefut-e a partial-fill kezelés (a paper 10%-ban szimulálja). **(b) Teljesítmény-kapu** (jóval később): **az irány-pontosságra alapozva** — a rezsim-hívás vs. a tényleges GLD price action —, mert ezt a paper valós idejű piaci adattal validálni tudja. A **csúszás-alapú metrikák „live-only" jelölést kapnak**, és paper alatt nem következtetünk belőlük (NBBO-fill, nincs likviditás-hatás). A metrikai küszöböt (túlélés, a null-modellt verő irány-pontosság) a start ELŐTT rögzíted; elég **rezsim-sokféleség** és elég **lezárt round-trip** kell.
- **Függőség:** scorecard (6); a teljes lánc él.
- **Emberi ellenőrzőpont:** a start előtt te írod alá a küszöböket — utólag nem mozdíthatók.
- **Várt kimenet:** előre regisztrált validációs jegyzék; a multi-epoch fegyelem természetes folytatása.

---

## Hatókörön kívül (kifejezetten NEM most)

Olaj / második eszköz; short; margin; konfidencia-skálázott méret; bróker-oldali conditional orderek; OPG/market-on-open; Zapier; Alpaca NL MCP szerver; éles pénzes végrehajtás (Phase D). Mind a gold-paper-eredmények után, saját bizonyíték-alapú kapuikon át.

---

## Pre-launch verifikációs csomag

Mit kell ténylegesen bizonyítani, mielőtt a paper-akkumulációt élesítjük. A verification ledger formátuma: minden tétel egy állítás, egy teszt, egy várt eredmény és egy státusz. **Sorrend:** az A-blokk (Layer 2 adat/snapshot) jön elöl, mert ebből inherit minden — egy rossz snapshotot az adapter hűségesen hajt végre. Az A-blokk nagyrészt **nem függ az adaptertől**, ezért az ADR-011 megírásával párhuzamosan már most futtatható; a B-blokk (execution) az adapter megépülése után. **Kapu:** minden tétel PASS, mielőtt a folyamat elindul.

> A Layer 2 magja már bizonyított (magas 90-es auditpontok, 853 zöld teszt, a márciusi snapshot 5/5 guarddal PASS). Ez a csomag nem a mechanizmust bizonyítja újra, hanem az **élő ritmust**, a **fail-closed tényleges kiváltását**, és a most aktuális **réseket** (GLD-ár, séma-drift).

### A-blokk — Layer 2: adatbeérkeztetés és snapshot

| ID | Mit igazol | Teszt | Várt eredmény | Státusz |
|---|---|---|---|---|
| A1 | Élő ritmus / frissesség | A 23:00 task után 3–5 egymást követő napon keletkezik-e friss snapshot | Minden napra friss snapshot, helyes `clock_ts` — nem csak egyszer futott | PENDING |
| A2 | Forrás-élőség | A 20 series értéke + staleness átnézése; null / megszűnt / ID-váltott series keresése | Minden Tier-1 friss és nem-null; ismert kivételek (megszűnt PPI, SP500 2016) dokumentáltan kezelve | PENDING |
| A3 | Fail-closed Tier-1 blokk | Egy Tier-1 series szándékos elavulttá tétele a küszöb fölé | NINCS publikált snapshot; verdict nem PASS | PENDING |
| A4 | Tier-2 csak figyelmeztet | Egy Tier-2 (CPI/PCE) staleness a küszöb fölé | Snapshot publikálva, warning jelölve, nem blokk | PENDING |
| A5 | Point-in-time / no look-ahead | Egy múltbeli nap futtatása; jövőbeli adat keresése; `revision_seq` | Csak a `clock_ts`-ig elérhető adat szerepel | PENDING |
| A6 | Replay-determinizmus | Ugyanaz a múltbeli nap kétszer lefuttatva | Bit-azonos `snapshot_id` (SHA-256: clock_ts+engine+config) | PENDING |
| A7 | Contract boundary | Strukturális ellenőrzés: a Layer 3 csak publikált snapshotból olvas-e | Raw/latest olvasás tiltva; csak snapshot engedett | PENDING |
| A8 | **GLD-ár a snapshotban** (a csúszás-mező előfeltétele) | A snapshot tartalmaz-e GLD záróárat az `exec_ref_gld_price`-hoz | GLD záróár jelen — **ha nincs, ingest-bővítés kell indítás ELŐTT** | PENDING |
| A9 | Séma-drift (márc-22 vs jún) | A kapu zöldje valódi-e (skill-logika tényleg lefut, nem shell-mode); az adapter a jelenlegi DecisionPacket guard-taxonómiát (6-elem) fogyasztja-e | Valódi zöld, jelenlegi séma — nincs hamis shell-mode PASS | PENDING |

### B-blokk — Execution / adapter

**Előfeltételek (a maradék `[FLAG]`-ek empirikus lezárása):**

| ID | Mit igazol | Teszt | Várt eredmény | Státusz |
|---|---|---|---|---|
| B1 | `client_order_id` hossz | Paper order 64-karakteres SHA-256 hex kulccsal | Elfogadja — vagy hosszhiba → rövidített digest (pl. 32 hex) | PENDING |
| B2 | GLD `fractionable` | `GET /v2/assets/GLD` → `fractionable` mező | `true` — vagy egész részvényes méretezésre váltás | PENDING |
| B3 | Cash vs. margin | `GET /v2/account` → `multiplier`, `cash`, `buying_power` | Ismert; a cash-cap elég, vagy cash-számla kérendő | PENDING |

**Egységtesztek (Alpaca nélkül, determinisztikus):**

| ID | Mit igazol | Teszt | Várt eredmény | Státusz |
|---|---|---|---|---|
| B4 | Reconcile delta-logika | Több kiinduló pozíció → célállapot | már-LONG+LONG → nincs order; FLAT-cél+pozíció → pontos eladás | PENDING |
| B5 | `client_order_id` determinizmus | Ugyanaz a (snapshot_id+asset_id+action) többször | Bit-azonos kulcs minden futáskor | PENDING |
| B6 | Csúszás-képlet (a javított bug) | `slippage_bps` számítás ellenőrzése | GLD-vs-GLD (`exec_ref_gld_price`), nem arany-spot; bázispont-nagyságrend | PENDING |
| B7 | Fill-record immutabilitás | Ugyanaz a `fill_id` kétszer beírva | `INSERT OR IGNORE`: nincs duplikáció, nincs felülírás | PENDING |
| B8 | NO_ACTION útvonal | AVOID/WATCH döntés | Nincs order, DE születik NO_ACTION rekord valid `snapshot_id`-vel | PENDING |
| B9 | Round-trip párosítás | LONG belépő + későbbi FLAT kilépő | Helyes `realized_pnl` és `hold_duration_sec` | PENDING |
| B10 | Környezet-guard (védőfal) | `assert_paper_environment` paper és live URL-lel | Paper elfogad; live → nem-nulla exit (elutasít) | PENDING |

**Integráció (apró notional, paper):**

| ID | Mit igazol | Teszt | Várt eredmény | Státusz |
|---|---|---|---|---|
| B11 | Auth smoke | `GET /v2/account` paper kulccsal | HTTP 200, érvényes számla-adat | PENDING |
| B12 | Egy teljes BUY | Kis notional market+day GLD | Elfogadás, majd `filled_qty`/`filled_avg_price`/`filled_at` kitöltődik | PENDING |
| B13 | Idempotencia 422 (dedup-garancia) | Ugyanaz a `client_order_id` kétszer | A második **HTTP 422** | PENDING |
| B14 | Sell-to-zero | Meglévő pozícióra FLAT | A pozíció nullára megy | PENDING |

**Állapotgép (queued / overnight) — a validáció által feltárt finomság:**

| ID | Mit igazol | Teszt | Várt eredmény | Státusz |
|---|---|---|---|---|
| B15 | Queued-állapot | Zárás után beadott order | `accepted`/`pending_new` (QUEUED) — nem hiba, nem újraküld; a következő nyitáskor teljesül | PENDING |
| B16 | Részleges fill | Elég order, hogy a paper ~10%-os random partialja beessen | `filled_qty` a tényleges (nem feltételezett teljes); a reconcile korrigál | PENDING |

**Fail-closed / biztonság (a legkritikusabbak):**

| ID | Mit igazol | Teszt | Várt eredmény | Státusz |
|---|---|---|---|---|
| B17 | Timeout / elérhetetlen host | Hálózati hiba szimulálása order közben | `EXECUTION_UNCERTAIN` rekord + leállás; NINCS vak retry | PENDING |
| B18 | Auth-hiba | Rossz kulcs (401/403) | Azonnali leállás | PENDING |
| B19 | Startup reconcile diszkrepancia | Szándékos eltérés (Alpaca-pozíció ≠ DB) | A startup reconcile észleli és megtagadja az új akciót | PENDING |

**Determinizmus és teljes főpróba:**

| ID | Mit igazol | Teszt | Várt eredmény | Státusz |
|---|---|---|---|---|
| B20 | Replay (alaptörvény az execution-rétegen) | Ugyanaz a snapshot kétszer a döntés→adapter láncon | Bit-azonos szándékolt akció + ugyanaz a `client_order_id` | PENDING |
| B21 | E2E offline_sim | Teljes lánc Alpaca nélkül: snapshot→döntés→adapter→fill_record→scorecard | Koherens, párosított rekordok végig | PENDING |
| B22 | E2E egy valódi paper order | Egyetlen end-to-end paper kereskedés a teljes láncon | A teljes lánc valós fillel zár, helyes scorecard-sorral | PENDING |

---

## A következő azonnali lépés

**Az ADR-011 megírása és Accepted státuszba emelése.** A fenti váz és a 2–8. lépés tartalma a Decision/Consequences anyaga; a validáció négy megállapítása (GLD-alapú csúszás-referencia, market+day queue az OPG helyett, cash-cap a méretezésben, paper-fill fidelitás → irány-alapú teljesítmény-kapu) mint elfogadott döntés, a két maradék `[FLAG]` (client_order_id hossz, GLD fractionable) plusz a cash/margin dashboard-megerősítés mint nyitott előfeltétel rögzítendő. Amíg az ADR-011 nincs Accepted állapotban, kód nem készül.

**Párhuzamosan már most indítható:** a pre-launch csomag **A-blokkja** (Layer 2 adat/snapshot) nem függ az adaptertől — az élő ritmus (A1), a forrás-élőség (A2) és kiemelten a **GLD-ár jelenléte (A8)** azonnal ellenőrizhető, mert ha A8 elbukik, az egy adatbeérkeztetési bővítés, amit az adapter megépítése előtt érdemes tudni. A **B-blokk** az adapter elkészülte után jön; a paper-akkumuláció élesítése előtt mind az A-, mind a B-blokk PASS kell legyen.
