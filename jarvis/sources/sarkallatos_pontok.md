# Sarkallatos Pontok — El Niño / La Niña Egyeztetés

Ezek az előző session során egyeztetett kulcspontok, amelyekre később vissza kívánunk térni.

---

## La Niña / Monitor

**1. 4 mechanikus trigger**
Mindegyik előre definiálja a küszöböt ÉS a reflexet: ártrigger, volatilitás-spike, sebesség/velocity, adatkiesés. Semmi sem dől el a pillanatban.

**2. Alert-only vs. automatikus reflex**
Governance-before-autonomy elv: papíron indul alert-only módban, automatikus reflex csak bizonyíték után.

**3. Monitor és determinizmus**
Minden monitor-esemény be van logolva a Trade Loggerbe, mint egy fill. A monitor csak az Alpaca paper backenden él (offline szimban nincs intraday).

**4. Triggerek jelenleg nem hangolhatók**
A küszöbök találgatások backtest/paper adat nélkül. La Niña marad egy spec a fiókban, amíg nincs adat.

---

## Backtest és paper trading

**5. Backtest felbontási probléma**
Napi EOD adattal a monitort nem lehet hűen visszajátszani. Két út:
- (a) daily high/low közelítés — elegendő annak eldöntésére, hogy material-e a rés
- (b) valódi intraday hourly bars — szükséges a volatilitás/sebesség triggerekhez

**6. Különböző szerepek**
Backtest megválaszolja: "kell-e egyáltalán a monitor?" — Paper trading megválaszolja: "működik-e a gyakorlatban?"

**7. Helyes sorrend**
High/low rés mérés először → ha material: intraday adat + contingency visszajátszás → alert-only paper → automatikus reflex.

---

## Adatgyűjtés és tanulás

**8. Gyűjtés ≠ automatikus tanulás**
A gyűjtést most kell felépíteni (olcsó), a tanulás automatizálása marad, amíg zárt kereskedések vannak. Az analízis együtt, manuálisan.

**9. Unified scorecard schema**
Backtest és paper trading azonos formátumot emittál. Ez az előfeltétele minden jövőbeli összehasonlíthatóságnak és Policy Proposalnak.

**10. Zapier**
A core-ban nem megfelelő (nem determinisztikus, nem visszajátszható, fekete doboz). A periférián elfogadható: push értesítés, Google Sheet sor.

**11. Human-Approved Policy Evolution**
A rendszer megfigyel és javaslatot tesz automatikusan; aktiválás emberi jóváhagyást igényel. A Policy Proposalban kötelező az ellenérvek szerepeltetése. Háromállapotú kapu:
- Accept → verzionált ADR
- Reject → Failure Library indoklással
- Return for refinement

Minden kapudöntés naplózva.

---

## Look-ahead bias

**12. §5.3 kiterjesztés még nem alkalmazva**
A CPI-példán túl két finomabb csapda:
- (a) **Megjelenési dátum vs. vonatkozási dátum** — az adat a referencia-időszak szerint van tárolva, nem a kiadás napja szerint
- (b) **Revideált/vintage adatok** — pl. GDP: a backtest az eredetileg publikált értéket kell hogy használja, nem a mai revised értéket; FRED `vintage_date` paraméter; Mr. Ripley `revision_seq=0` historikus futásokhoz

---

*Forrás: El Niño projekt egyeztetés, előző session*
