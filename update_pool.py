"""Exécuté par GitHub Actions dans le dépôt du pool : stats LNH du jour -> index.html."""
import json
import time

import scoring
import web_export
from nhl_api import NHL

pool = json.load(open("pool.json", encoding="utf-8"))
nhl = NHL(".cache", ttl_hours=0)
season = pool["rules"]["season"]
abbrs = [t["abbr"] for t in pool["teams"]]
stats = {str(k): v for k, v in nhl.all_club_stats(season, abbrs, force=True).items()}
teams = [t for t in nhl.standings("now", force=True) if t["season"] == season]
rows = scoring.standings(pool, pool["players"], stats, teams)
updated = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
html = web_export.build_html(pool, rows, {t["abbr"]: t for t in pool["teams"]}, updated)
open("index.html", "w", encoding="utf-8").write(html)
print(f"{len(stats)} joueurs, {len(teams)} équipes, {updated}")
