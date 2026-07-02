"""Assemble the CV-attachment HTML report with embedded base64 images."""

import base64

OUT_DIR = "."

IMAGES = {
    "bar": "data/summary/pace_bar.png",
    "timeline_schio": "data/cv_report/pace_over_time_schio_clean.png",
    "timeline_venezia": "data/cv_report/pace_over_time_venezia_clean.png",
    "deviation_schio": "data/pace_deviation/pace_deviation_Schio.png",
    "deviation_venezia": "data/pace_deviation/pace_deviation_Venezia.png",
    "finali": "data/finals/pace_finali.png",
}


def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def main():
    imgs = {k: b64(v) for k, v in IMAGES.items()}

    html = f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8" />
<title>Il pace nel basket femminile italiano</title>
<style>
  :root {{
    --paper: #f3f4f1;
    --ink: #14171a;
    --muted: #5e6672;
    --accent: #c1541f;
    --hairline: #dbddd5;
    --chip: #eaebe4;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    background: var(--paper);
    color: var(--ink);
    font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
  }}
  .page {{
    max-width: 640px;
    margin: 0 auto;
    padding: 56px 24px 72px;
  }}
  .eyebrow {{
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--accent);
    margin: 0 0 10px;
  }}
  h1 {{
    font-size: 30px;
    font-weight: 700;
    letter-spacing: -0.01em;
    margin: 0 0 14px;
    text-wrap: balance;
  }}
  .intro {{
    font-size: 15px;
    color: var(--muted);
    max-width: 62ch;
    margin: 0 0 8px;
  }}
  .intro a {{ color: var(--ink); text-decoration: underline; text-decoration-color: var(--hairline); }}
  .meta {{
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    font-size: 12px;
    color: var(--muted);
    margin: 20px 0 0;
    padding-top: 16px;
    border-top: 1px solid var(--hairline);
  }}
  .meta span {{ font-weight: 600; color: var(--ink); }}

  section {{
    margin-top: 40px;
    padding-top: 32px;
    border-top: 1px solid var(--hairline);
  }}
  .chip {{
    display: inline-block;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.04em;
    color: var(--muted);
    background: var(--chip);
    border-radius: 3px;
    padding: 3px 8px;
    margin-bottom: 10px;
  }}
  h2 {{
    font-size: 18px;
    font-weight: 700;
    margin: 0 0 8px;
    text-wrap: balance;
  }}
  p.caption {{
    font-size: 14.5px;
    color: var(--muted);
    margin: 0 0 16px;
    max-width: 60ch;
  }}
  figure {{
    margin: 0;
  }}
  figure img {{
    display: block;
    width: 100%;
    height: auto;
    border: 1px solid var(--hairline);
    border-radius: 4px;
    background: #fff;
  }}
  .pair {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }}
  .pair.stacked {{
    grid-template-columns: 1fr;
    gap: 24px;
  }}
  .pair .team-label {{
    font-size: 12px;
    font-weight: 700;
    color: var(--ink);
    margin: 0 0 6px;
  }}
  @media (max-width: 560px) {{
    .pair {{ grid-template-columns: 1fr; }}
  }}

  footer {{
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid var(--hairline);
    font-size: 12px;
    color: var(--muted);
  }}
  footer p {{ margin: 0 0 6px; }}

  @media print {{
    .page {{ padding: 0; max-width: none; }}
  }}
</style>
</head>
<body>

<div class="page">

  <p class="eyebrow">Progetto personale — analisi dati sportivi</p>
  <h1>Il pace nel basket femminile italiano</h1>
  <p class="intro">
    Ho scaricato i tabellini di tutte le 110 partite della regular season di Serie A1 2025/26
    da <a href="https://www.legabasketfemminile.it">legabasketfemminile.it</a> e calcolato il
    <strong>pace</strong> (possessi stimati ogni 40 minuti) di ogni squadra partita per partita,
    con la formula avanzata di Dean&nbsp;Oliver descritta su
    <a href="https://hackastat.eu/learn-a-stat-possessi-e-pace/">hackastat.eu</a>.
  </p>
  <section>
    <p class="chip">01 — CLASSIFICA RITMO</p>
    <h2>Pace medio per squadra</h2>
    <p class="caption">
      Chi corre più delle altre in tutta la Serie A1. Roseto e Brixia giocano il basket più
      veloce, Broni e San Giovanni il più lento — quasi 6 possessi a partita di differenza.
    </p>
    <figure><img src="data:image/png;base64,{imgs['bar']}" alt="Pace medio per squadra" /></figure>
  </section>

  <section>
    <p class="chip">02 — CASO DI STUDIO: LE DUE FINALISTE</p>
    <h2>Il ritmo di Schio e Venezia, partita per partita</h2>
    <p class="caption">
      Le due squadre arrivate in finale. Schio (20-0 in regular season) oscilla molto, da 65 a
      quasi 80; Venezia è leggermente più veloce in media e altrettanto incostante.
    </p>
    <div class="pair stacked">
      <div>
        <p class="team-label">Schio</p>
        <figure><img src="data:image/png;base64,{imgs['timeline_schio']}" alt="Pace per partita di Schio nel corso della stagione" /></figure>
      </div>
      <div>
        <p class="team-label">Venezia</p>
        <figure><img src="data:image/png;base64,{imgs['timeline_venezia']}" alt="Pace per partita di Venezia nel corso della stagione" /></figure>
      </div>
    </div>
  </section>

  <section>
    <p class="chip">03 — CASO DI STUDIO: LE DUE FINALISTE</p>
    <h2>Chi si scosta dal proprio ritmo abituale</h2>
    <p class="caption">
      Ogni punto è una partita: sulla x quanto la squadra si è scostata dal proprio pace medio
      stagionale, sulla y quanto l'avversaria si è scostata dal proprio. Origine (0,0) =
      entrambe al ritmo abituale.
    </p>
    <div class="pair stacked">
      <div>
        <p class="team-label">Schio</p>
        <figure><img src="data:image/png;base64,{imgs['deviation_schio']}" alt="Scostamento dal pace medio, Schio vs avversaria" /></figure>
      </div>
      <div>
        <p class="team-label">Venezia</p>
        <figure><img src="data:image/png;base64,{imgs['deviation_venezia']}" alt="Scostamento dal pace medio, Venezia vs avversaria" /></figure>
      </div>
    </div>
  </section>

  <section>
    <p class="chip">04 — COM'È FINITA</p>
    <h2>Il pace nella finale scudetto</h2>
    <p class="caption">
      Venezia elimina Schio (unica sconfitta stagionale) in Gara 1, sul ritmo più lento delle tre
      partite — sotto la media stagionale di entrambe. Schio chiude la serie 2-1 vincendo Gara 2 e
      Gara 3 su un pace vicino al proprio standard, ma sempre più lento di quello abituale di
      Venezia: la finale si è giocata su ritmi imposti da Schio, non da Venezia.
    </p>
    <figure><img src="data:image/png;base64,{imgs['finali']}" alt="Pace nelle 3 partite della finale Schio-Venezia" /></figure>
  </section>

  <footer>
    <p>Fonte dati: legabasketfemminile.it, Serie A1 femminile 2025/26 (regular season). Formula del pace: hackastat.eu.</p>
    <p>Scraping, calcolo e visualizzazioni realizzati con Python (requests, BeautifulSoup, pandas, matplotlib/seaborn).</p>
  </footer>

</div>
</body>
</html>
"""

    out_path = f"{OUT_DIR}/report_cv.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {out_path} ({len(html)} chars)")


if __name__ == "__main__":
    main()
