"""Assemble the CV-attachment HTML report with embedded base64 images.

Layout/styling only lives here. All wording (headings, captions, footer)
lives in content.yaml next to this file — edit that for text changes,
this file only for structure/CSS.
"""

import base64
from pathlib import Path

import yaml

OUT_DIR = "."
CONTENT_PATH = Path(__file__).parent / "content.yaml"

IMAGES = {
    "bar": "data/summary/pace_bar.png",
    "timeline_schio": "data/cv_report/pace_over_time_schio_clean.png",
    "timeline_venezia": "data/cv_report/pace_over_time_venezia_clean.png",
    "deviation_schio": "data/pace_deviation/pace_deviation_Schio.png",
    "deviation_venezia": "data/pace_deviation/pace_deviation_Venezia.png",
    "finali": "data/finals/pace_finali.png",
}

CSS = """
  :root {
    --paper: #f3f4f1;
    --ink: #14171a;
    --muted: #5e6672;
    --accent: #c1541f;
    --hairline: #dbddd5;
    --chip: #eaebe4;
  }
  * { box-sizing: border-box; }
  body {
    background: var(--paper);
    color: var(--ink);
    font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
  }
  .page {
    max-width: 640px;
    margin: 0 auto;
    padding: 56px 24px 72px;
  }
  .eyebrow {
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--accent);
    margin: 0 0 10px;
  }
  h1 {
    font-size: 30px;
    font-weight: 700;
    letter-spacing: -0.01em;
    margin: 0 0 14px;
    text-wrap: balance;
  }
  .intro {
    font-size: 15px;
    color: var(--muted);
    max-width: 62ch;
    margin: 0 0 8px;
  }
  .intro a { color: var(--ink); text-decoration: underline; text-decoration-color: var(--hairline); }
  .meta {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    font-size: 12px;
    color: var(--muted);
    margin: 20px 0 0;
    padding-top: 16px;
    border-top: 1px solid var(--hairline);
  }
  .meta span { font-weight: 600; color: var(--ink); }

  section {
    margin-top: 40px;
    padding-top: 32px;
    border-top: 1px solid var(--hairline);
  }
  .chip {
    display: inline-block;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.04em;
    color: var(--muted);
    background: var(--chip);
    border-radius: 3px;
    padding: 3px 8px;
    margin-bottom: 10px;
  }
  h2 {
    font-size: 18px;
    font-weight: 700;
    margin: 0 0 8px;
    text-wrap: balance;
  }
  p.caption {
    font-size: 14.5px;
    color: var(--muted);
    margin: 0 0 16px;
    max-width: 60ch;
  }
  figure {
    margin: 0;
  }
  figure img {
    display: block;
    width: 100%;
    height: auto;
    border: 1px solid var(--hairline);
    border-radius: 4px;
    background: #fff;
  }
  .pair {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
  .pair.stacked {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  .pair .team-label {
    font-size: 12px;
    font-weight: 700;
    color: var(--ink);
    margin: 0 0 6px;
  }
  @media (max-width: 560px) {
    .pair { grid-template-columns: 1fr; }
  }

  footer {
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid var(--hairline);
    font-size: 12px;
    color: var(--muted);
  }
  footer p { margin: 0 0 6px; }

  .section-head { break-inside: avoid; page-break-inside: avoid; break-after: avoid; page-break-after: avoid; }
  section, figure, .pair, .pair > div { break-inside: avoid; page-break-inside: avoid; }
  h2, .chip { break-after: avoid; page-break-after: avoid; }

  @media print {
    body { margin: 0; }
    .page { padding: 40px 32px; max-width: none; }
    .pair.cols-2 { grid-template-columns: 1fr 1fr; gap: 16px; }
    section { break-inside: avoid; page-break-inside: avoid; }
    section + section { break-before: page; page-break-before: always; }
  }
"""

HTML_SKELETON = """<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8" />
<title>{title}</title>
<style>{css}</style>
</head>
<body>

<div class="page">

  <p class="eyebrow">{eyebrow}</p>
  <h1>{title}</h1>
  <p class="intro">
    {intro}
  </p>
{sections}
  <footer>
{footer}  </footer>

</div>
</body>
</html>
"""


def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def render_figure(image_key, alt, imgs):
    return f'<figure><img src="data:image/png;base64,{imgs[image_key]}" alt="{alt}" /></figure>'


def render_section(section, imgs):
    layout = section.get("layout", "single")

    if layout == "single":
        body = render_figure(section["image"], section.get("alt", ""), imgs)
    elif layout == "pair":
        columns = "\n".join(f"""      <div>
        <p class="team-label">{item['label']}</p>
        {render_figure(item['image'], item.get('alt', ''), imgs)}
      </div>""" for item in section["pair"])
        cols_class = "cols-2" if section.get("pair_columns") == 2 else "stacked"
        body = f'<div class="pair {cols_class}">\n{columns}\n    </div>'
    else:
        raise ValueError(f"unknown layout: {layout!r} in section {section.get('chip')!r}")

    return f"""
  <section>
    <div class="section-head">
      <p class="chip">{section['chip']}</p>
      <h2>{section['heading']}</h2>
      <p class="caption">
        {section['caption'].strip()}
      </p>
    </div>
    {body}
  </section>
"""


def main():
    content = yaml.safe_load(CONTENT_PATH.read_text(encoding="utf-8"))
    imgs = {k: b64(v) for k, v in IMAGES.items()}

    sections_html = "".join(render_section(s, imgs) for s in content["sections"])
    footer_html = "".join(f"    <p>{line}</p>\n" for line in content["footer"])

    html = HTML_SKELETON.format(
        title=content["title"],
        eyebrow=content["eyebrow"],
        intro=content["intro"].strip(),
        css=CSS,
        sections=sections_html,
        footer=footer_html,
    )

    out_path = f"{OUT_DIR}/report_cv.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {out_path} ({len(html)} chars)")


if __name__ == "__main__":
    main()
