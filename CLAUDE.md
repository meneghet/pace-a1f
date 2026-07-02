# Progetto: pace nel basket femminile italiano

Scraping + analisi del "pace" (possessi stimati ogni 40') per la Serie A1
femminile 2025/26, da legabasketfemminile.it. Formula da hackastat.eu.

## Pipeline (in ordine)

1. `scripts/lbf_scraper.py` — scarica tutte le partite della regular season
   (`Calendar.aspx?ID=313` → lista match, poi `MatchStats.aspx?ID=313&MID=...`
   per il tabellino di ognuna) e produce `data/pace_A1_2025-26_all_teams.csv`
   (220 righe = 110 partite × 2 squadre, formula avanzata: FGA/FGM/FTA/OR/
   rimbalzi difensivi avversari/TOV). Rate limit 1 req/s, ~2 minuti totali.
   Rilanciare solo se cambia la formula o serve un'altra stagione/competizione.
2. `scripts/pace.py` — formule (`team_possessions_advanced`, `game_minutes`).
3. Script di plotting, tutti leggono il CSV master e scrivono in `data/`:
   - `plot_pace.py` → `data/pace_per_team/` (pace per giornata, per squadra)
   - `plot_pace_scatter.py --all` → `data/pace_vs_opponent/` (pace propria vs avversaria)
   - `plot_pace_deviation.py --all` → `data/pace_deviation/` (scostamento da media propria/avversaria)
   - `plot_pace_vs_winrate.py`, `plot_pace_bar.py` → `data/summary/`
4. `scripts/team_aliases.json` — nomi corti usati nei grafici (Schio, Venezia,
   Derthona, San Giovanni, Brixia, ecc.), letti da `plot_pace.py::team_alias()`.
   I nomi file usano l'alias; i dati nel CSV usano il nome ufficiale completo.

## Addendum — finale playoff

`scripts/finals_pace.py` + `scripts/plot_finals_pace.py` → `data/finals/`:
pace delle 3 partite della finale scudetto (Schio-Venezia), fuori dal CSV
master (playoff, non regular season). I `MID` delle partite sono hardcoded
nello script, individuati una tantum via postback ASP.NET con Playwright
(`scripts/explore_playoff.py`, tab "Play Off" su `Calendar.aspx`).

## Report

- `report.md` — report tecnico completo (fonti valutate, formula, findings su
  Serie B femminile — dati insufficienti per il pace, solo per la A1/A2 funziona).
- `report_cv.html` — versione minimale (1 pagina, letta in 30s) da allegare a un
  CV, con caso di studio Schio+Venezia. Generato da `scripts/build_cv_report.py`
  a partire da grafici "puliti" (senza linee di media) in `data/cv_report/`,
  costruiti da `scripts/make_cv_charts.py`. Non tocca la pipeline principale.

## Note

- Ambiente: `.venv/` (requests, beautifulsoup4, pandas, matplotlib, seaborn,
  playwright — quest'ultimo usato solo in fase di ricognizione iniziale).
- Serie B femminile: niente hub nazionale, tabellini regionali (romagnasport.it,
  playbasket.it) non riportano tiri/rimbalzi/palle perse → pace non calcolabile,
  solo risultato. Dettagli in `report.md`.
- `scripts/explore_*.py` sono script di ricognizione one-off (non parte della
  pipeline), utili come riferimento se serve ri-esplorare la struttura del sito.
