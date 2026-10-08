"""Couche présentation de « Heri Kwetu Sign » : CSS et blocs HTML.

Ne contient aucune logique de reconnaissance. Les fonctions ci-dessous
reçoivent des valeurs déjà calculées et renvoient du HTML à injecter
via st.markdown(..., unsafe_allow_html=True).
"""

from html import escape
from urllib.parse import quote

# --------------------------------------------------------------------------
# Icônes SVG (tracés simples, style « outline »)
# --------------------------------------------------------------------------
_ICONS = {
    "camera": '<path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "book": '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
    "sliders": '<line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/>',
    "hand": '<path d="M18 11V6a2 2 0 0 0-2-2a2 2 0 0 0-2 2"/><path d="M14 10V4a2 2 0 0 0-2-2a2 2 0 0 0-2 2v2"/><path d="M10 10.5V6a2 2 0 0 0-2-2a2 2 0 0 0-2 2v8"/><path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="14" y2="17"/>',
    "pin": '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
    "eye": '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>',
    "cpu": '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/>',
}


def icon(name: str, size: int = 20, color: str = "currentColor", stroke: float = 1.8) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke}" '
        f'stroke-linecap="round" stroke-linejoin="round" '
        f'style="vertical-align:middle;flex-shrink:0">{_ICONS[name]}</svg>'
    )


def _compact(text: str) -> str:
    """Supprime retours à la ligne et indentations : évite que le Markdown
    interprète des lignes indentées comme un bloc de code."""
    return "".join(line.strip() for line in text.splitlines())


# --------------------------------------------------------------------------
# CSS global
# --------------------------------------------------------------------------
_CSS_RULES = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root{--bg:#0a1220;--panel:#0f1b2e;--panel2:#0c1627;--line:rgba(148,163,184,.14);--accent:#22d3ee;--accent-soft:rgba(34,211,238,.12);--ok:#22c55e;--bad:#ef4444;--warn:#f59e0b;--text:#e6edf7;--muted:#8ba0b8;}
.stApp{font-family:'Inter',system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;background:radial-gradient(1100px 560px at 78% -12%,rgba(34,211,238,.08),transparent 60%),var(--bg);color:var(--text);}
header[data-testid="stHeader"]{background:transparent;}
[data-testid="stToolbar"],[data-testid="stDecoration"],#MainMenu,footer{display:none!important;}
.block-container{padding-top:1.4rem;padding-bottom:1rem;max-width:1600px;}
section[data-testid="stSidebar"]{background:#0b1424;border-right:1px solid var(--line);width:290px!important;min-width:290px!important;}
[data-testid="stSidebarUserContent"]{padding-top:.4rem;}

.sb-wrap{display:flex;flex-direction:column;justify-content:space-between;min-height:calc(100vh - 4rem);}
.sb-brand{display:flex;align-items:center;gap:.8rem;margin-bottom:1.6rem;}
.sb-logo{width:52px;height:52px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:radial-gradient(circle at 30% 30%,rgba(34,211,238,.28),rgba(34,211,238,.05));border:1.5px solid rgba(34,211,238,.55);color:var(--accent);box-shadow:0 0 22px rgba(34,211,238,.25);}
.sb-name{font-size:1.18rem;font-weight:800;letter-spacing:.2px;line-height:1.1;color:var(--text);}
.sb-name span{color:var(--accent);}
.sb-sub{font-size:.72rem;color:var(--muted);margin-top:.25rem;line-height:1.25;}
.sb-item{display:flex;align-items:center;gap:.85rem;padding:.8rem 1rem;margin-bottom:.35rem;border-radius:12px;color:#a9b8cc;font-size:.95rem;font-weight:500;}
.sb-item.active{background:linear-gradient(90deg,rgba(34,211,238,.18),rgba(34,211,238,.06));color:#fff;border:1px solid rgba(34,211,238,.28);}
.sb-item.active svg{color:var(--accent);}
.sb-foot{border:1px solid var(--line);border-radius:14px;padding:1rem;background:rgba(15,27,46,.7);}
.sb-foot-name{display:flex;align-items:center;gap:.5rem;font-weight:600;font-size:.9rem;}
.sb-foot-city{color:var(--accent);font-size:.78rem;margin:.15rem 0 .7rem 1.7rem;}
.sb-foot-quote{color:var(--muted);font-size:.74rem;line-height:1.4;border-top:1px solid var(--line);padding-top:.7rem;}

.page-title{display:flex;align-items:center;gap:.8rem;font-size:2rem;font-weight:800;letter-spacing:-.3px;line-height:1.15;}
.page-title svg{color:var(--accent);}
.page-sub{color:var(--muted);font-size:.98rem;margin-top:.35rem;}
.pill{display:inline-flex;align-items:center;gap:.6rem;padding:.55rem 1.1rem;border-radius:999px;font-size:.9rem;font-weight:500;float:right;margin-top:.4rem;}
.pill.on{background:rgba(34,197,94,.1);border:1px solid rgba(34,197,94,.45);color:#d7f7e2;}
.pill.off{background:rgba(148,163,184,.08);border:1px solid var(--line);color:var(--muted);}
.dot{width:10px;height:10px;border-radius:50%;display:inline-block;}
.on .dot{background:var(--ok);box-shadow:0 0 10px var(--ok);}
.off .dot{background:#64748b;}

.st-key-cam_card,.st-key-mode_card,.st-key-detect_card,.st-key-text_card{background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--line);border-radius:18px;padding:1.25rem 1.4rem;box-shadow:0 12px 32px rgba(0,0,0,.35);}
.st-key-cam_card iframe{border-radius:14px;}

.chips{display:flex;gap:.6rem;align-items:center;margin:.2rem 0 .1rem 0;}
.chip{display:inline-flex;align-items:center;gap:.45rem;padding:.3rem .7rem;border-radius:8px;font-size:.78rem;font-weight:600;background:rgba(15,27,46,.9);border:1px solid var(--line);color:#c9d6e8;}
.chip.live{background:rgba(239,68,68,.14);border-color:rgba(239,68,68,.5);color:#fecaca;}
.chip.live .dot{width:8px;height:8px;background:var(--bad);animation:pulse 1.4s ease-in-out infinite;}
@keyframes pulse{0%{opacity:1}50%{opacity:.3}100%{opacity:1}}

.card-title{display:flex;align-items:center;gap:.7rem;font-size:1.08rem;font-weight:700;margin-bottom:.9rem;}
.card-title svg{color:var(--accent);}
.card-sub{color:var(--muted);font-size:.85rem;margin:-.55rem 0 .9rem 0;}

.sign-box{display:flex;align-items:center;gap:1.3rem;padding:1.3rem 1.5rem;border-radius:14px;background:rgba(10,18,32,.65);border:1px solid var(--line);min-height:104px;}
.sign-box svg{color:var(--accent);}
.sign-word{font-size:3.1rem;font-weight:800;letter-spacing:1px;color:var(--accent);line-height:1;text-shadow:0 0 28px rgba(34,211,238,.28);}
.sign-word.dim{color:#5b6b82;text-shadow:none;}
.conf-row{display:flex;justify-content:space-between;align-items:baseline;margin:1.1rem 0 .55rem 0;font-weight:600;}
.conf-val{font-size:1.25rem;font-weight:700;}
.bar{height:9px;border-radius:99px;background:rgba(148,163,184,.16);overflow:hidden;}
.bar span{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,#06b6d4,#22d3ee);}
.bar span.warn{background:linear-gradient(90deg,#d97706,#f59e0b);}
.badge{display:inline-flex;align-items:center;gap:.5rem;margin-top:1rem;padding:.45rem .9rem;border-radius:999px;font-size:.85rem;font-weight:500;}
.badge.ok{background:rgba(34,197,94,.1);border:1px solid rgba(34,197,94,.4);color:#c9f4d6;}
.badge.low{background:rgba(245,158,11,.1);border:1px solid rgba(245,158,11,.4);color:#fde7b0;}
.badge.wrong_mode,.badge.paused,.badge.idle{background:rgba(148,163,184,.1);border:1px solid var(--line);color:#b6c3d6;}

.text-box{padding:1.15rem 1.3rem;border-radius:14px;background:rgba(10,18,32,.65);border:1px solid var(--line);font-size:1.7rem;font-weight:700;letter-spacing:.5px;min-height:70px;word-break:break-word;}
.text-box.empty{color:#5b6b82;font-weight:500;font-size:1.15rem;}
.recent-head{margin:1.1rem 0 .6rem 0;font-weight:600;font-size:.95rem;}
.recent{display:flex;flex-wrap:wrap;gap:.55rem;min-height:34px;}
.rchip{padding:.35rem .95rem;border-radius:999px;font-size:.8rem;font-weight:600;}
.rchip.letter{background:rgba(59,130,246,.16);border:1px solid rgba(59,130,246,.5);color:#bcd7ff;}
.rchip.word{background:rgba(139,92,246,.16);border:1px solid rgba(139,92,246,.5);color:#dccdff;}
.rchip.none{color:#5b6b82;border:1px dashed var(--line);}

.stButton button,[data-testid="stPopover"] button{height:2.9rem;border-radius:12px;border:1px solid rgba(148,163,184,.22);background:#101d31;color:var(--text);font-weight:600;transition:all .15s ease;width:100%;}
.stButton button:hover,[data-testid="stPopover"] button:hover{border-color:var(--accent);color:var(--accent);background:#12243a;}
[data-testid="stButton"],[data-testid="stPopover"]{width:100%;}
.stButton button{height:auto;min-height:2.9rem;}
.stButton button p{margin:0;line-height:1.15;}
.st-key-btn_new button{background:var(--accent);color:#04222b;border:none;}
.st-key-btn_new button:hover{background:#67e8f9;color:#04222b;}

[class*="st-key-card_"]{background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--line);border-radius:18px;padding:1.25rem 1.4rem;box-shadow:0 12px 32px rgba(0,0,0,.35);}
[class*="st-key-nav_"] button{justify-content:flex-start;height:3rem;min-height:3rem;padding:0 1rem;background:transparent;border:1px solid transparent;color:#a9b8cc;font-weight:500;font-size:.95rem;}
[class*="st-key-nav_"] button:hover{background:rgba(34,211,238,.07);border-color:transparent;color:#fff;}
[class*="st-key-nav_"] button p{display:flex;align-items:center;}
[class*="st-key-nav_"] button p::before{content:"";display:inline-block;width:22px;height:22px;margin-right:.85rem;background:currentColor;-webkit-mask-repeat:no-repeat;mask-repeat:no-repeat;-webkit-mask-size:contain;mask-size:contain;-webkit-mask-position:center;mask-position:center;}
.sb-foot-fixed{position:fixed;bottom:1.2rem;width:256px;}
.stat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1rem;margin-bottom:1rem;}
.stat-card{padding:1rem 1.2rem;border-radius:14px;background:rgba(10,18,32,.65);border:1px solid var(--line);}
.stat-val{font-size:1.9rem;font-weight:800;color:var(--accent);line-height:1.1;}
.stat-lab{color:var(--muted);font-size:.82rem;margin-top:.3rem;}
.sign-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(92px,1fr));gap:.8rem;}
.tile{position:relative;padding:.9rem .4rem .7rem;border-radius:14px;text-align:center;background:rgba(10,18,32,.65);border:1px solid var(--line);}
.tile .t-lab{font-size:1.5rem;font-weight:800;color:var(--text);line-height:1.1;word-break:break-word;}
.tile.word .t-lab{font-size:1.05rem;letter-spacing:.5px;color:#dccdff;}
.tile .t-cnt{font-size:.7rem;color:var(--muted);margin-top:.35rem;}
.tile.off{opacity:.38;border-style:dashed;}
.tile.warn{border-color:rgba(245,158,11,.55);}
.tile .t-warn{position:absolute;top:.35rem;right:.5rem;font-size:.75rem;color:var(--warn);}
.legend{color:var(--muted);font-size:.78rem;margin-top:.9rem;}
.empty-note{padding:1.2rem;border-radius:14px;border:1px dashed var(--line);color:var(--muted);font-size:.92rem;}
.htable{width:100%;border-collapse:collapse;font-size:.92rem;}
.htable th{text-align:left;color:var(--muted);font-weight:600;font-size:.78rem;text-transform:uppercase;letter-spacing:.6px;padding:.5rem .7rem;border-bottom:1px solid var(--line);}
.htable td{padding:.65rem .7rem;border-bottom:1px solid rgba(148,163,184,.08);}
.htable tr:last-child td{border-bottom:none;}
.htable .h-time{color:var(--muted);font-variant-numeric:tabular-nums;}
.htable .h-sign{font-weight:700;letter-spacing:.4px;}
.htable .h-conf{font-weight:600;color:var(--accent);text-align:right;}
.htable th.r{text-align:right;}
.tech-footer{display:flex;justify-content:flex-end;align-items:center;gap:2rem;margin-top:1.2rem;padding-top:1rem;border-top:1px solid var(--line);color:#a9b8cc;font-size:.88rem;}
.tech-footer span{display:inline-flex;align-items:center;gap:.5rem;}
.tech-footer svg{color:var(--accent);}
"""

CSS = "<style>" + _compact(_CSS_RULES) + "</style>"


def dynamic_css(mode_active_key: str, paused: bool) -> str:
    """CSS dépendant de l'état : bouton de mode actif et bouton pause."""
    pause_rule = (
        ".st-key-btn_pause button{background:linear-gradient(90deg,#ef4444,#f43f5e);"
        "border:none;color:#fff;}"
        if not paused
        else ".st-key-btn_pause button{background:var(--accent);border:none;color:#04222b;}"
    )
    active_rule = (
        f".st-key-{mode_active_key} button{{background:rgba(34,211,238,.14);"
        f"border:1.5px solid var(--accent);color:#fff;}}"
    )
    return f"<style>{pause_rule}{active_rule}</style>"


# --------------------------------------------------------------------------
# Blocs HTML
# --------------------------------------------------------------------------
def sidebar_brand_html() -> str:
    return _compact(f"""
    <div class="sb-brand">
      <div class="sb-logo">{icon("hand", 28, stroke=1.6)}</div>
      <div>
        <div class="sb-name">Heri Kwetu <span>Sign</span></div>
        <div class="sb-sub">Ensemble pour une<br>communication inclusive</div>
      </div>
    </div>
    """)


def sidebar_footer_html() -> str:
    return _compact(f"""
    <div class="sb-foot-fixed"><div class="sb-foot">
      <div class="sb-foot-name">{icon("pin", 18, "#22d3ee")}<span>Centre Heri Kwetu</span></div>
      <div class="sb-foot-city">Bukavu, RDC</div>
      <div class="sb-foot-quote">« La technologie au service de l'inclusion »</div>
    </div></div>
    """)


def _mask_uri(icon_name: str) -> str:
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        'stroke="black" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
        f"{_ICONS[icon_name]}</svg>"
    )
    return 'url("data:image/svg+xml,' + quote(svg) + '")'


def nav_css(nav_items: list, active_key: str) -> str:
    """Icônes des boutons de navigation + mise en évidence de la page active."""
    rules = []
    for key, _label, icon_name in nav_items:
        uri = _mask_uri(icon_name)
        rules.append(
            f".st-key-nav_{key} button p::before"
            f"{{-webkit-mask-image:{uri};mask-image:{uri};}}"
        )
    rules.append(
        f".st-key-nav_{active_key} button{{background:linear-gradient(90deg,"
        "rgba(34,211,238,.18),rgba(34,211,238,.06));border:1px solid rgba(34,211,238,.28);color:#fff;}}"
    )
    rules.append(f".st-key-nav_{active_key} button p::before{{background:var(--accent);}}")
    return "<style>" + "".join(rules) + "</style>"


def page_header_html(icon_name: str, title: str, subtitle: str) -> str:
    return _compact(f"""
    <div class="page-title">{icon(icon_name, 38, stroke=1.6)}<span>{escape(title)}</span></div>
    <div class="page-sub">{escape(subtitle)}</div>
    """)


def header_html() -> str:
    return page_header_html(
        "camera", "Reconnaissance des signes",
        "Faites un signe devant la caméra pour obtenir sa traduction.",
    )


def status_html(playing: bool) -> str:
    if playing:
        return '<div class="pill on"><span class="dot"></span>Caméra active</div>'
    return '<div class="pill off"><span class="dot"></span>Caméra inactive</div>'


def chips_html(playing: bool) -> str:
    live = (
        '<span class="chip live"><span class="dot"></span>LIVE</span>'
        if playing
        else '<span class="chip">Hors ligne</span>'
    )
    return _compact(
        f'<div class="chips">{live}'
        f'<span class="chip">{icon("hand", 14)}MediaPipe · 21 points</span></div>'
    )


def card_title(icon_name: str, title: str, subtitle: str = "") -> str:
    sub = f'<div class="card-sub">{escape(subtitle)}</div>' if subtitle else ""
    return f'<div class="card-title">{icon(icon_name, 24)}<span>{escape(title)}</span></div>{sub}'


def detection_html(view: dict) -> str:
    """Contenu de la carte « Signe détecté » à partir de detection_view()."""
    word = escape(str(view["word"]))
    dim = " dim" if view["kind"] in ("idle", "low", "wrong_mode", "paused") else ""
    pct = max(0.0, min(100.0, view["conf_pct"]))
    bar_cls = "warn" if view["kind"] == "low" else ""
    check = "✓ " if view["kind"] == "ok" else ""
    return _compact(f"""
    <div class="sign-box">{icon("hand", 54, stroke=1.4)}<div class="sign-word{dim}">{word}</div></div>
    <div class="conf-row"><span>Confiance</span><span class="conf-val">{pct:.1f}%</span></div>
    <div class="bar"><span class="{bar_cls}" style="width:{pct:.1f}%"></span></div>
    <div class="badge {view['kind']}">{check}{escape(view['message'])}</div>
    """)


def text_html(text: str) -> str:
    if not text:
        return '<div class="text-box empty">Le texte reconnu apparaîtra ici…</div>'
    return f'<div class="text-box">{escape(text)}</div>'


def recent_html(items: list) -> str:
    if not items:
        chips = '<span class="rchip none">Aucun élément pour l\'instant</span>'
    else:
        chips = "".join(
            f'<span class="rchip {"letter" if len(it) == 1 else "word"}">{escape(it)}</span>'
            for it in items
        )
    return f'<div class="recent-head">Éléments récents</div><div class="recent">{chips}</div>'


def footer_html() -> str:
    return _compact(f"""
    <div class="tech-footer">
      <span>{icon("eye", 20)}OpenCV</span>
      <span>{icon("hand", 20)}MediaPipe</span>
      <span>{icon("cpu", 20)}IA</span>
    </div>
    """)


def stat_cards_html(stats: list) -> str:
    """stats : liste de (valeur, libellé)."""
    cards = "".join(
        f'<div class="stat-card"><div class="stat-val">{escape(str(v))}</div>'
        f'<div class="stat-lab">{escape(l)}</div></div>'
        for v, l in stats
    )
    return f'<div class="stat-grid">{cards}</div>'


def signs_grid_html(tiles: list, word: bool = False) -> str:
    """tiles : liste de dicts {label, count, available, note}."""
    out = []
    for t in tiles:
        cls = "tile" + (" word" if word else "")
        if not t["available"]:
            cls += " off"
        if t.get("note"):
            cls += " warn"
        warn = '<span class="t-warn">⚠</span>' if t.get("note") else ""
        title = f' title="{escape(t["note"])}"' if t.get("note") else ""
        cnt = f'{t["count"]} éch.' if t["available"] else "non appris"
        out.append(
            f'<div class="{cls}"{title}>{warn}<div class="t-lab">{escape(t["label"])}</div>'
            f'<div class="t-cnt">{cnt}</div></div>'
        )
    return f'<div class="sign-grid">{"".join(out)}</div>'


def note_html(text: str) -> str:
    return f'<div class="empty-note">{escape(text)}</div>'


def legend_html(text: str) -> str:
    return f'<div class="legend">{escape(text)}</div>'


def history_table_html(entries: list, limit: int = 100) -> str:
    """Tableau des reconnaissances, de la plus récente à la plus ancienne."""
    rows = []
    for e in reversed(entries[-limit:]):
        hour = e["ts"].partition("T")[2]
        kind = "letter" if e["category"] == "Alphabet" else "word"
        rows.append(
            f'<tr><td class="h-time">{escape(hour)}</td>'
            f'<td class="h-sign">{escape(e["label"])}</td>'
            f'<td><span class="rchip {kind}">{escape(e["category"])}</span></td>'
            f'<td class="h-conf">{e["conf"] * 100:.0f} %</td></tr>'
        )
    head = ('<tr><th>Heure</th><th>Signe</th><th>Catégorie</th>'
            '<th class="r">Confiance</th></tr>')
    return f'<table class="htable">{head}{"".join(rows)}</table>'
