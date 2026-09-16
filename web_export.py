"""Page web autonome des résultats du pool (HTML unique, CSS inline, logos depuis assets.nhle.com)."""
import time
from html import escape as esc

LOGO = "https://assets.nhle.com/logos/nhl/svg/{abbr}_light.svg"
POS_FR = {"F": "Attaquant", "D": "Défenseur", "G": "Gardien"}

CSS = """
:root{--bg:#070B14;--panel:#111A2E;--line:#24314F;--ice:#E8EEF7;--muted:#8A98B8;--gold:#F1D77A}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ice);font:15px/1.45 "Segoe UI",system-ui,-apple-system,sans-serif}
.wrap{max-width:1100px;margin:0 auto;padding:22px 16px 60px}
h1,h2,h3{font-family:Bahnschrift,"Arial Narrow",Impact,sans-serif;letter-spacing:2px;text-transform:uppercase;margin:0}
h1{font-size:38px;line-height:1.1}h2{font-size:20px;color:var(--gold);margin:34px 0 12px}h3{font-size:18px}
.sub{color:var(--muted);margin:6px 0 0}
.card{background:linear-gradient(180deg,var(--panel),#0D1424);border:1px solid var(--line);border-radius:14px;padding:16px 18px;box-shadow:0 10px 30px rgba(0,0,0,.35)}
.podium{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:16px}
.pod{border-radius:14px;padding:16px 10px;text-align:center;border:1px solid var(--line);background:linear-gradient(160deg,var(--c1,#1B2745),#0B1222 80%)}
.pod.p1{box-shadow:0 0 0 2px #C9A227,0 20px 40px rgba(0,0,0,.4)}
.pod .r{font-family:Bahnschrift,"Arial Narrow",sans-serif;font-size:12px;letter-spacing:3px;color:var(--gold)}
.pod .n{font-family:Bahnschrift,"Arial Narrow",sans-serif;font-size:24px;letter-spacing:1px;margin:6px 0 2px}
.pod .t{font-family:Bahnschrift,"Arial Narrow",sans-serif;font-size:36px;font-weight:700}.pod .t small{font-size:12px;color:var(--muted);letter-spacing:2px}
.logo{width:34px;height:34px;vertical-align:middle;filter:drop-shadow(0 2px 3px rgba(0,0,0,.6))}.logo.lg{width:72px;height:72px}.logo.sm{width:20px;height:20px}
table{width:100%;border-collapse:collapse;font-size:14px}th{text-align:left;padding:9px 10px;color:var(--muted);font-size:11px;letter-spacing:1px;text-transform:uppercase;border-bottom:1px solid var(--line)}
td{padding:9px 10px;border-bottom:1px solid rgba(36,49,79,.6)}.num{text-align:right;font-variant-numeric:tabular-nums}
.tot{font-family:Bahnschrift,"Arial Narrow",sans-serif;font-size:20px;color:var(--gold)}.rk{font-family:Bahnschrift,"Arial Narrow",sans-serif;font-size:18px;width:36px}
.dot{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:8px;vertical-align:middle}
.tag{display:inline-block;padding:1px 7px;border-radius:6px;font-size:11px;font-weight:700;letter-spacing:1px}
.F{background:rgba(58,134,255,.2);color:#8EB8FF}.D{background:rgba(47,191,113,.2);color:#7BE0A6}.G{background:rgba(201,162,39,.25);color:var(--gold)}
.bar{height:6px;border-radius:3px;background:rgba(255,255,255,.08);overflow:hidden}.bar i{display:block;height:100%;background:linear-gradient(90deg,#3A86FF,#C9A227)}
.roster{margin-top:14px}.roster .head{display:flex;align-items:center;gap:12px;margin-bottom:8px}.roster .head .meta{color:var(--muted);font-size:13px}
.muted{color:var(--muted)}.foot{margin-top:40px;color:var(--muted);font-size:12px;text-align:center}
@media(max-width:640px){.podium{grid-template-columns:1fr}h1{font-size:28px}td,th{padding:7px 6px}.hide-sm{display:none}}
"""


def _fmt(v):
    return int(v) if isinstance(v, float) and v.is_integer() else v


def _season(sid):
    s = str(sid)
    return f"{s[:4]}-{s[6:]}"


def build_html(pool, rows, teams_by_abbr, updated_at):
    pts = pool["rules"]["points"]
    season = _season(pool["rules"]["season"])
    mx = max(1, *[r["total"] for r in rows]) if rows else 1
    team = lambda ab: teams_by_abbr.get(ab, {"nameFr": ab, "short": ab, "colors": ["#1B2745"]})
    logo = lambda ab, cls="logo": f'<img class="{cls}" src="{LOGO.format(abbr=ab)}" alt="{ab}" loading="lazy">'

    def pod(i):
        if i >= len(rows):
            return "<div></div>"
        x = rows[i]; t = team(x["participant"]["team"])
        return (f'<div class="pod p{i+1}" style="--c1:{t["colors"][0]}"><div class="r">{["1RE PLACE","2E PLACE","3E PLACE"][i]}</div>'
                f'{logo(x["participant"]["team"], "logo lg")}<div class="n" style="color:{x["participant"]["color"]}">{esc(x["participant"]["name"])}</div>'
                f'<div class="t">{_fmt(x["total"])} <small>PTS</small></div></div>')

    stand = "".join(
        f'<tr><td class="rk">{x["rank"]}</td><td><span class="dot" style="background:{x["participant"]["color"]}"></span><b>{esc(x["participant"]["name"])}</b></td>'
        f'<td>{logo(x["participant"]["team"], "logo sm")} {esc(team(x["participant"]["team"])["short"])} '
        f'<span class="muted hide-sm">{f"{x['teamRow']['wins']}-{x['teamRow']['losses']}-{x['teamRow']['otl']}" if x.get("teamRow") else ""}</span></td>'
        f'<td class="num hide-sm">{_fmt(x["playerPts"])}</td><td class="num hide-sm">{_fmt(x["teamPts"])}</td><td class="num tot">{_fmt(x["total"])}</td>'
        f'<td class="hide-sm" style="width:20%"><div class="bar"><i style="width:{100 * x["total"] / mx:.0f}%"></i></div></td></tr>'
        for x in rows)

    def roster(x):
        p = x["participant"]; t = team(p["team"]); tr = x.get("teamRow") or {}
        lines = "".join(
            f'<tr><td class="muted hide-sm">{l["round"]}</td><td><b>{esc(l["player"]["first"])} {esc(l["player"]["last"])}</b></td>'
            f'<td><span class="tag {l["player"]["pos"]}">{l["player"]["pos"]}</span></td><td>{logo(l["player"]["team"], "logo sm")} <span class="hide-sm">{l["player"]["team"]}</span></td>'
            f'<td class="num hide-sm">{(l["stat"] or {}).get("gp", 0)}</td>'
            f'<td class="num">{"–" if l["player"]["pos"] == "G" else (l["stat"] or {}).get("g", 0)}</td><td class="num">{"–" if l["player"]["pos"] == "G" else (l["stat"] or {}).get("a", 0)}</td>'
            f'<td class="num">{(l["stat"] or {}).get("w", 0) if l["player"]["pos"] == "G" else "–"}</td><td class="num">{(l["stat"] or {}).get("so", 0) if l["player"]["pos"] == "G" else "–"}</td>'
            f'<td class="num tot" style="font-size:16px">{_fmt(l["fp"])}</td></tr>'
            for l in x["lines"])
        return (f'<div class="card roster" id="p-{p["id"]}"><div class="head">{logo(p["team"])}<div><h3 style="color:{p["color"]}">{x["rank"]}. {esc(p["name"])}</h3>'
                f'<div class="meta">{esc(t["nameFr"])}{f" · {tr['wins']}-{tr['losses']}-{tr['otl']}" if tr else ""} · victoires × {_fmt(pts["teamWin"])} = {_fmt(x["teamPts"])} pts</div></div>'
                f'<div style="margin-left:auto" class="tot">{_fmt(x["total"])} pts</div></div>'
                f'<table><thead><tr><th class="hide-sm">R</th><th>Joueur</th><th>Pos</th><th>Éq.</th><th class="num hide-sm">PJ</th><th class="num">B</th><th class="num">A</th><th class="num">V</th><th class="num">BL</th><th class="num">Pts</th></tr></thead>'
                f'<tbody>{lines}</tbody></table></div>')

    bareme = " · ".join(f"{lbl} {_fmt(pts[k])}" for k, lbl in (("goal", "but"), ("assist", "passe"), ("teamWin", "victoire d'équipe"), ("goalieWin", "victoire du gardien"), ("shutout", "blanchissage")))
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(pool["name"])} — Pool LNH {season}</title><style>{CSS}</style></head><body><div class="wrap">
<h1>{esc(pool["name"])}</h1><p class="sub">Pool fantasy LNH · saison {season} · stats au {esc(updated_at or "—")} · page générée le {time.strftime("%Y-%m-%d %H:%M")}</p>
<div class="podium">{pod(1)}{pod(0)}{pod(2)}</div>
<h2>Classement</h2><div class="card" style="padding:0;overflow:hidden"><table><thead><tr><th></th><th>Participant</th><th>Équipe LNH</th><th class="num hide-sm">Pts joueurs</th><th class="num hide-sm">Pts équipe</th><th class="num">Total</th><th class="hide-sm"></th></tr></thead><tbody>{stand}</tbody></table></div>
<h2>Alignements</h2>{"".join(roster(x) for x in rows)}
<p class="foot">Barème : {bareme}. Données : NHL.com. Généré par Repêchage Fantasy LNH.</p></div></body></html>"""
