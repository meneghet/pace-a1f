# Report: calcolo del "pace" per squadra/partita — basket femminile italiano

## Formula usata

Fonte: [hackastat.eu — Possessi e Pace](https://hackastat.eu/learn-a-stat-possessi-e-pace/) (Dean Oliver), versione **semplice**:

```
Possessi_squadra ≈ FGA + 0.44 × FTA − OR + TOV
Pace_partita = (media(Possessi_casa, Possessi_ospite) / minuti_giocati) × 40
```

dove FGA = tiri da 2 tentati + tiri da 3 tentati, FTA = tiri liberi tentati, OR = rimbalzi offensivi, TOV = palle perse. I 40 minuti sono la durata regolamentare italiana (4×10'); si aggiungono 5' per ogni eventuale overtime.

## Serie A1 femminile (legabasketfemminile.it) — ✅ dati completi, formula applicabile

- Il calendario (`Calendar.aspx?ID=313`) è HTML statico (nessun JS necessario, `requests` puro basta) e contiene, per ogni partita, un link `MatchStats.aspx?ID=313&MID={matchId}` — un **tabellino per singola partita**.
- Ogni `MatchStats.aspx` ha, per squadra, una riga `TOTALI DI SQUADRA` con: tiri da 2 (realizzati/tentati/%), tiri da 3 (realizzati/tentati/%), tiri liberi (realizzati/tentati/%), rimbalzi offensivi/difensivi/totali, palle perse/recuperate, assist, valutazione — **esattamente i 4 campi necessari alla formula del pace**, già aggregati a livello di squadra (non serve nemmeno sommare le giocatrici).
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

Lo scraper (`scripts/lbf_scraper.py::build_full_season_dataset`) scarica **ogni partita della regular season una sola volta** (110 partite, 110 richieste totali invece di 1100 se fatto per squadra) e produce due righe per partita — una per prospettiva squadra — con il pace **calcolato separatamente per ciascuna squadra**.

- `data/pace_A1_2025-26_all_teams.csv` — dataset master: 220 righe (110 partite × 2 squadre), colonne `match_id, date, giornata, team, opponent, is_home, team_score, opp_score, result, team_pace, opp_pace, game_pace`.
- Verifica di correttezza: incrociando le righe casa/ospite della stessa partita, `team_pace` di una squadra coincide esattamente con `opp_pace` dell'altra in tutte le 110 partite (0 mismatch).

I grafici sono organizzati in sottocartelle dentro `data/`:

- `data/pace_per_team/pace_<Squadra>_A1_2025-26.png` × 11 — pace nel tempo (per giornata) colorato per W/L, uno per squadra.
- `data/pace_vs_opponent/pace_scatter_<Squadra>.png` × 11 — scatter pace-propria vs pace-avversaria per ogni partita di regular season, colorato per esito, con riferimento diagonale y=x. Es. Schio ha chiuso la regular season 20-0 (tutti i punti sono vittorie), pace medio stagionale 71.2 (min 65.9, max 80.2); Venezia mostra invece qualche sconfitta concentrata nelle partite a pace più basso/medio.
- `data/summary/pace_vs_winrate.png` — scatter a livello di squadra: pace medio stagionale (x) vs win rate (y), un punto per squadra con etichetta. Non emerge una relazione lineare forte tra pace e vittorie: Schio vince tutto con un pace medio-basso (71.5), mentre People Strategy Roseto e RMB Brixia hanno pace alto (>75) ma win rate basso (40% e 15%) — sembra più una questione di qualità della squadra che di ritmo di gioco, osservazione visiva su 11 punti, non un'analisi statistica.
- `data/pace_deviation/pace_deviation_<Squadra>.png` × 11 — variante dello scatter precedente ma "centrata sulle medie": x = pace della squadra meno il **proprio** pace medio stagionale, y = pace dell'avversaria meno **il pace medio stagionale dell'avversaria stessa** (ognuna rispetto alla propria media). L'origine (0,0) rappresenta "entrambe hanno giocato esattamente al proprio ritmo abituale", utile per vedere a colpo d'occhio se le vittorie/sconfitte si concentrano quando la squadra accelera/rallenta rispetto al proprio standard, indipendentemente da quanto sia "veloce" l'avversaria in assoluto. Range assi condiviso (-10/+10, simmetrico per costruzione).
- `data/archive/` — output della prima proof of concept a squadra singola (Alama), superata dal dataset completo.
- `data/logs/` — log testuali delle sessioni di scraping/plotting.

| Metrica | Valore |
|---|---|
| Pace medio stagione | 74.2 |
| Pace minimo | 67.9 (vs Geas Sesto San Giovanni, 15/02/2026) |
| Pace massimo | 83.0 (vs RMB Brixia Basket San Paolo, fuori casa) |
| Pace medio nelle vittorie (9 partite) | 73.7 |
| Pace medio nelle sconfitte (11 partite) | 74.5 |

I valori sono in un range plausibile per il basket europeo femminile (tipicamente 65-85 possessi/40'), buon segnale che la formula e il parsing sono corretti. La differenza pace vittorie/sconfitte è minima e su un campione di 20 partite non è indicativa di nulla — semplicemente non ci si aspettava un pattern forte, era solo un controllo di sanità dei numeri.

## Raccomandazione

Per avere presto un dataset "pace per partita + W/L" solido e completo, conviene partire da **Serie A1 (o A2, stessa piattaforma)**: i dati ci sono già, formula applicabile al 100%, nessun blocco tecnico. Per la Serie B femminile, l'opzione realistica nel breve termine è costruire un dataset con solo risultato/punteggio (niente pace) a meno di non trovare un girone/stagione dove i collaboratori locali compilano davvero il box score su playbasket.it — andrebbe verificato caso per caso, girone per girone, prima di investire tempo nello scraper.
