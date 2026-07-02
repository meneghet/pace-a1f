
# Istruzioni: scraping statistiche basket femminile italiano (Serie A1/A2/B)

## Obiettivo
Costruire un dataset di statistiche (base + avanzate derivate) per il basket femminile italiano, priorità Serie B, va bene anche Serie A1/A2.

## Contesto già raccolto (non ripartire da zero)

### Serie A1 / A2 — legabasketfemminile.it
Sito **ASP.NET WebForms** (pagine `.aspx` con parametro `ID` numerico per competizione). Piattaforma: DataProject (stesso vendor di altre leghe volley/basket europee — asset serviti da `dataprojectstoragewe.blob.core.windows.net`).

URL utili (pattern `https://www.legabasketfemminile.it/{Pagina}.aspx?ID={id}`):
- `Competition.aspx?ID={id}` → classifica + risultati
- `PlayerStats.aspx?ID={id}` → statistiche di squadra/giocatrici (già verificato: contiene 2P R/T/%, 3P R/T/%, TL R/T/%, rimbalzi O/D/Tot, palle perse/recuperate, stoppate date/subite, assist, falli fatti/subiti, VAL)
- `CompetitionTeams.aspx?ID={id}` → elenco squadre
- `Calendar.aspx?ID={id}` → calendario

ID competizione già mappati:
| Competizione | ID |
|---|---|
| Serie A1 2025/26 | 313 |
| Serie A1 2024/25 | 307 |
| Serie A1 2023/24 | 300 |
| Serie A2 2025/26 | 314 |
| Serie A2 2024/25 | 308 |
| Coppa Italia A1 | 316 |
| Coppa Italia A2 | 317 |
| Supercoppa | 315 |

Nota: gli ID non seguono un pattern ovvio (non sono sequenziali per stagione), quindi vanno scoperti navigando il menu del sito o l'archivio: `CompetitionArchive.aspx`.

### Serie B femminile — NIENTE hub nazionale
Il campionato è organizzato in **9 gironi regionali indipendenti**, gestiti da comitati regionali diversi, ognuno con sito proprio (es. playbasket.it, romagnasport.com, basketmarche.it, emiliaromagnasport.com...). Non esiste una piattaforma unica con box score strutturati per la regular season. Il digitale/referto elettronico con acquisizione statistiche per ora copre solo A1/A2, non la B.

L'unico momento in cui la Serie B ha dati "ricchi" (shot chart, play-by-play, confronti giocatrici) è il **Final Event nazionale** (fase finale a 16 squadre per la promozione in A2), tramite l'app mobile **FIP Stats**. Quella è verosimilmente un'app con API REST dietro (non verificata, vedi task 3 sotto).

## Cosa fare, in ordine di priorità

### 1. Verificare se legabasketfemminile.it ha chiamate AJAX/JSON nascoste
Non dare per scontato che sia tutto HTML server-side. Usa Playwright (o Selenium) headless, apri `PlayerStats.aspx?ID=313`, e logga TUTTE le richieste di rete:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    requests_log = []
    page.on("request", lambda req: requests_log.append(req.url))
    page.goto("https://www.legabasketfemminile.it/PlayerStats.aspx?ID=313")
    page.wait_for_timeout(3000)
    browser.close()

for url in requests_log:
    if any(x in url for x in [".json", ".asmx", ".ashx", "/api/"]):
        print(url)
```

Se salta fuori un endpoint JSON, usa quello (molto più pulito e stabile di un parser HTML). Se non salta fuori niente, si procede con lo scraping HTML (punto 2).

### 2. Scraping HTML delle pagine PlayerStats/Competition (A1/A2)
Se non c'è API, scraping diretto con `requests` + `BeautifulSoup`:

```python
import requests
from bs4 import BeautifulSoup
import pandas as pd

HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_player_stats(competition_id: int) -> pd.DataFrame:
    url = f"https://www.legabasketfemminile.it/PlayerStats.aspx?ID={competition_id}"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    tables = pd.read_html(resp.text)  # spesso funziona diretto su tabelle HTML pulite
    return tables  # ispezionare quale indice contiene i dati giocatrici vs squadra

df_list = get_player_stats(313)
```

**Attenzione**: se la pagina ha filtri (es. toggle "Regular Season / Playoff / Playout" come visto su `Competition.aspx?ID=313`, o paginazione sulle statistiche individuali delle giocatrici) è WebForms classico → probabilmente serve gestire postback con `__VIEWSTATE` e `__EVENTVALIDATION`:

```python
# pattern generico per postback ASP.NET, da adattare dopo aver ispezionato il form
def get_viewstate(html):
    soup = BeautifulSoup(html, "html.parser")
    return {
        "__VIEWSTATE": soup.find("input", {"name": "__VIEWSTATE"})["value"],
        "__EVENTVALIDATION": soup.find("input", {"name": "__EVENTVALIDATION"})["value"],
        "__VIEWSTATEGENERATOR": soup.find("input", {"name": "__VIEWSTATEGENERATOR"}).get("value", ""),
    }
```

Verificare con le devtools del browser (tab Network, filtro "Doc"/"XHR") cosa viene mandato quando si clicca su "Play Off" o si cambia pagina nelle statistiche giocatrici — copiare l'`__EVENTTARGET` esatto usato.

### 3. Reverse engineering app FIP Stats (opzionale, per dati Serie B più ricchi)
Se interessano shot chart / play-by-play della Serie B (solo Final Event, non regular season):
- Intercettare il traffico dell'app con **mitmproxy** o **Charles Proxy** mentre si naviga una partita nell'app FIP Stats
- Cercare endpoint tipo `api.fip.it`, `*.dataproject.com`, o simili
- Questo è più invasivo e va fatto solo se serve davvero quel livello di dettaglio

### 4. Serie B regular season (gironi regionali)
Non c'è scorciatoia: bisogna scegliere quali gironi/regioni interessano e scrivere un parser HTML per ciascun sito (struttura diversa per ognuno). Esempi di siti da mappare singolarmente:
- playbasket.it (multi-regione, es. `/veneto/b-femminile`, `/lombardia/b-femminile`, `/campania/b-femminile`)
- romagnasport.com / emiliaromagnasport.com (`classifica.php?gir={id}&anno={anno}`)
- basketmarche.it

Dati disponibili qui: perlopiù tabellini partita per partita (punteggio per quarto, marcatori con tiri 2/3 realizzati/tentati per singola giocatrice), NON statistiche aggregate di stagione già pronte — quelle vanno costruite sommando i tabellini.


## Vincoli/avvertenze
- Controllare `robots.txt` e termini di servizio dei siti prima di uno scraping massivo e sistematico
- Mettere rate limiting (es. 1 richiesta/secondo) per non sovraccaricare siti piccoli come quelli regionali
- I nomi degli ID competizione (`ID=313` ecc.) possono cambiare stagione per stagione: va scritta una funzione che li scopre da `CompetitionArchive.aspx` invece di hardcodarli