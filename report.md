# Report: calcolo del "pace" per squadra/partita — basket femminile italiano

## Formula usata

Fonte: [hackastat.eu — Possessi e Pace](https://hackastat.eu/learn-a-stat-possessi-e-pace/) (Dean Oliver). Inizialmente usata la versione semplice, poi passati alla versione **avanzata** (in `scripts/pace.py`, `team_possessions_advanced`) non appena verificato che i dati necessari erano disponibili nel tabellino:

```
Possessi_squadra ≈ FGA + 0.44 × FTA − 1.07 × (OR / (OR + oppDR)) × (FGA − FGM) + TOV
Pace_squadra = (Possessi_squadra / minuti_giocati) × 40
```

dove FGA/FGM = tiri da 2+3 tentati/realizzati, FTA = tiri liberi tentati, OR = rimbalzi offensivi propri, oppDR = rimbalzi difensivi dell'avversaria nella stessa partita, TOV = palle perse. I 40 minuti sono la durata regolamentare italiana (4×10'); si aggiungono 5' per ogni eventuale overtime (3 partite su 110 sono andate ai supplementari).

La formula stima i possessi di **una** squadra, ma in una partita di basket le due squadre giocano necessariamente lo stesso numero di possessi (a meno di frazioni residue): applicandola separatamente a squadra e avversaria si ottengono due stime leggermente diverse, per via dei coefficienti su tiri liberi e rimbalzi. Il pace "vero" della partita è quindi la **media delle due stime**:

```
Pace_partita = (Pace_squadra + Pace_avversaria) / 2
```

ed è lo stesso identico numero per entrambe le squadre che hanno giocato quell'incontro — non ha senso parlare di "pace nostro" vs "pace avversario" nella stessa partita, sono la stessa cosa stimata due volte con rumore diverso. Questo valore è la colonna `game_pace` nel dataset; le due stime grezze non mediate restano salvate come `team_pace`/`opp_pace` solo a scopo diagnostico (per verificare che la formula sia stabile, vedi sotto), non vanno usate come metriche a sé stanti.

## Serie A1 femminile (legabasketfemminile.it) — ✅ dati completi, formula applicabile

- Il calendario (`Calendar.aspx?ID=313`) è HTML statico (nessun JS necessario, `requests` puro basta) e contiene, per ogni partita, un link `MatchStats.aspx?ID=313&MID={matchId}` — un **tabellino per singola partita**.
- Ogni `MatchStats.aspx` ha, per squadra, una riga `TOTALI DI SQUADRA` con: tiri da 2 (realizzati/tentati/%), tiri da 3 (realizzati/tentati/%), tiri liberi (realizzati/tentati/%), rimbalzi offensivi/difensivi/totali, palle perse/recuperate, assist, valutazione — **tutti i campi necessari sia alla formula semplice che a quella avanzata**, già aggregati a livello di squadra (non serve nemmeno sommare le giocatrici).
- Punteggio finale e parziali per quarto sono in campi HTML con id stabili (`Content_L_Punteggio_Casa/Fuori`, `Content_L_Quarti`), quindi anche l'eventuale overtime è rilevabile in modo affidabile.
- La stagione 2025/26 di Serie A1 (competizione ID 313) ha **110 partite** (11 squadre, doppio girone) — coerente con l'elenco squadre del sito.
- **Nessun ostacolo tecnico**: niente postback ASP.NET da gestire per queste pagine, niente rate limit nel `robots.txt` (assente/404).

Proof of concept eseguito: script `scripts/lbf_scraper.py`, ha scaricato tutte le partite di una squadra (Alama San Martino di Lupari) per la stagione 2025/26, calcolato pace e W/L partita per partita, salvato in `data/pace_Alama_A1_2025-26.csv` (vedi tabella/grafico sotto).

## Serie B femminile — ❌ dati insufficienti per il pace, ok solo per W/L

Testato su **due piattaforme diverse** (come richiesto), entrambe con robots.txt permissivo:

1. **romagnasport.com / emiliaromagnasport.com** (girone Serie B Femminile Romagna, `gir=597`): le pagine `classifica.php`, `calendario.php` e `squadra.php` offrono solo classifica, calendario e **punteggio finale**. Nessuna pagina di tabellino/box score: zero tracce di tiri, rimbalzi, palle perse su tutto il sito per questo girone.
2. **playbasket.it** (testato su Veneto e Lombardia, girone B femminile): esiste una vera pagina di dettaglio partita (`match.php`) con una **tabella box score predisposta** per tutti i campi necessari (Pts, TL/TL%, T2/T2%, T3/T3%, RD, RO, Ff, Fs, PR, PP, Ass, St, Min) — la struttura è quella giusta. **Ma nei campionati femminili di Serie B controllati (4 partite su 2 regioni diverse) questi campi sono sempre vuoti ("-")**: viene compilato solo il punteggio finale, i parziali per quarto e la lista marcatori con soli punti totali (non tiri tentati). La compilazione del box score dipende dal collaboratore/statistico della squadra di casa, che a questo livello spesso non lo fa.

**Conclusione**: con le fonti attualmente verificate, per la Serie B femminile è possibile calcolare in modo affidabile solo **risultato (W/L)**, data e punteggio per quarto — non il pace, nemmeno con la formula semplice, perché mancano sistematicamente tiri tentati, rimbalzi offensivi e palle perse. Non è un limite della formula ma dei dati disponibili "a monte".

## Cosa è stato scartato/non ancora provato

- App FIP Stats (Final Event Serie B): non testata in questo giro — richiederebbe reverse engineering del traffico mobile (mitmproxy), più invasivo; utile solo per le 16 squadre della fase finale nazionale, non per la regular season.
- Altri gironi regionali di Serie B (basketmarche.it, altri playbasket.it, ecc.): non testati singolarmente, ma il pattern osservato (nessun box score compilato) è probabilmente comune, dato che è un limite organizzativo/di risorse dei comitati regionali più che tecnico del sito.

## Dataset completo — tutte le 11 squadre di Serie A1 2025/26

Lo scraper (`scripts/lbf_scraper.py::build_full_season_dataset`) scarica **ogni partita della regular season una sola volta** (110 partite, 110 richieste totali invece di 1100 se fatto per squadra) e produce due righe per partita — una per prospettiva squadra — condividendo lo stesso `game_pace` (media delle due stime) su entrambe.

- `data/pace_A1_2025-26_all_teams.csv` — dataset master: 220 righe (110 partite × 2 squadre), colonne `match_id, date, giornata, team, opponent, is_home, team_score, opp_score, result, n_periods`, i box score grezzi (`team_fga, team_fgm, team_fta, team_oreb, team_dreb, team_tov` e le stesse per `opp_*`) e i pace derivati: `team_pace`/`opp_pace` (stime grezze non mediate, per squadra) e **`game_pace`** (la media delle due — è questa la metrica usata in tutti i grafici e le aggregazioni). Aver salvato anche i campi grezzi evita di dover ri-scrapare se in futuro si vuole ritoccare ancora la formula.
- Verifica di correttezza: incrociando le righe casa/ospite della stessa partita, `team_pace` di una squadra coincide esattamente con `opp_pace` dell'altra in tutte le 110 partite (0 mismatch) — conferma che la formula avanzata è applicata in modo simmetrico prima di essere mediata in `game_pace`.

I grafici sono organizzati in sottocartelle dentro `data/`:

- `data/pace_per_team/pace_<Squadra>_A1_2025-26.png` × 11 — pace nel tempo (per giornata) colorato per W/L, uno per squadra, valori di `game_pace`. Asse y condiviso (62-83), con media squadra e media campionato (72.4) annotate.
- `data/pace_vs_opponent/pace_scatter_<Squadra>.png` × 11 — scatter pace-propria vs pace-avversaria per ogni partita di regular season, colorato per esito. Dato che `game_pace` è un valore unico condiviso dalle due squadre di ogni partita, ogni punto cade esattamente sulla diagonale (x = y): il grafico resta per coerenza con gli altri per-squadra, ma non aggiunge informazione oltre a quella già in `pace_<Squadra>`. Es. Schio ha chiuso la regular season 20-0, pace medio stagionale 71.0 (min 65.4, max 79.7).
- `data/summary/pace_vs_winrate.png` — scatter a livello di squadra: pace medio stagionale (x, media di `game_pace` sulle partite della squadra) vs win rate (y), un punto per squadra con etichetta. Non emerge una relazione lineare forte tra pace e vittorie: Schio vince tutto con un pace medio-basso (71.0), mentre People Strategy Roseto (75.0) e RMB Brixia (74.4) hanno pace alto ma win rate basso (40% e 15%).
- `data/summary/pace_bar.png` — bar chart orizzontale, una barra per squadra, ordinato per pace medio decrescente con il valore annotato: da Roseto (75.0) a Geas Sesto San Giovanni (69.1). Asse x fisso 60-80.
- `data/pace_deviation/pace_deviation_<Squadra>.png` × 11 — scatter "centrato sulle medie": x = `game_pace` della partita meno il **proprio** pace medio stagionale, y = lo stesso `game_pace` (identico, è la stessa partita) meno **il pace medio stagionale dell'avversaria**. Origine (0,0) = entrambe al proprio ritmo abituale; x e y differiscono solo perché le due baseline (media propria vs media avversaria) sono diverse, non perché la partita abbia due pace distinti. Bordi annotati con lettura discorsiva ("Le facciamo correre" / "Le rallentiamo" / "Ci rallentano" / "Ci fanno correre"), punti verdi/rossi per W/L, e le partite contro le due finaliste (Schio/Venezia) etichettate esplicitamente. Range assi condiviso (-10/+10).

**Nota su una metrica scartata**: una prima versione includeva anche `data/summary/oppdev_vs_winrate.png` (quanto in media le avversarie si scostano dal proprio pace abituale contro una data squadra, vs win rate). È stata rimossa perché, una volta che il pace è un valore unico condiviso per partita (`game_pace`), a livello di riepilogo stagionale questa metrica è una funzione affine esatta del pace medio della squadra stessa — corr = 1.0 su tutte le 11 squadre, dato un calendario a girone doppio perfettamente bilanciato (ogni squadra incontra ciascuna delle altre 10 esattamente due volte). In formula: `opp_dev(A) = 1.1 × pace_medio(A) − S/10`, dove S è la somma dei pace medi di tutte le squadre. Il grafico risultava quindi indistinguibile da `pace_vs_winrate.png`, solo con asse x riscalato. Lo scostamento **per singola partita** (nei grafici `pace_deviation`) resta invece informativo, perché lì non è mediato sulla stagione.
- `data/archive/` — output della prima proof of concept a squadra singola (Alama), superata dal dataset completo.
- `data/logs/` — log testuali delle sessioni di scraping/plotting.

| Metrica (`game_pace`, 110 partite) | Valore |
|---|---|
| Pace medio campionato | 72.4 |
| Pace minimo | 62.9 |
| Pace massimo | 82.5 |

I valori sono in un range plausibile per il basket europeo femminile (tipicamente 65-85 possessi/40'). Non è più riportato un confronto "pace medio nelle vittorie vs nelle sconfitte": dato che `game_pace` è lo stesso identico numero per entrambe le squadre di ogni partita, e ogni partita genera esattamente una riga W e una riga L con quel valore, le due medie sono uguali **per costruzione** (72.36 in entrambi i casi) — non è un finding, è una tautologia della metrica. La domanda "il pace aiuta a vincere?" resta comunque risposta dallo scatter pace-vs-winrate a livello di squadra: il pace da solo non spiega chi vince, conta più la qualità della squadra.

## Raccomandazione

Per avere presto un dataset "pace per partita + W/L" solido e completo, conviene partire da **Serie A1 (o A2, stessa piattaforma)**: i dati ci sono già, formula applicabile al 100%, nessun blocco tecnico. Per la Serie B femminile, l'opzione realistica nel breve termine è costruire un dataset con solo risultato/punteggio (niente pace) a meno di non trovare un girone/stagione dove i collaboratori locali compilano davvero il box score su playbasket.it — andrebbe verificato caso per caso, girone per girone, prima di investire tempo nello scraper.
