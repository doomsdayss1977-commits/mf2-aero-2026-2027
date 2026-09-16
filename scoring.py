"""Calcul des points fantasy à partir des stats LNH de la saison en cours."""


def skater_points(s, pts):
    if not s:
        return 0
    g, a = s.get("g", 0), s.get("a", 0)
    total = g * pts["goal"] + a * pts["assist"]
    total += s.get("ppg", 0) * pts.get("ppGoal", 0)
    total += s.get("shg", 0) * pts.get("shGoal", 0)
    total += s.get("gwg", 0) * pts.get("gwg", 0)
    total += s.get("otg", 0) * pts.get("otGoal", 0)
    total += s.get("pm", 0) * pts.get("plusMinus", 0)
    return total


def goalie_points(s, pts):
    if not s:
        return 0
    total = s.get("w", 0) * pts["goalieWin"] + s.get("so", 0) * pts["shutout"]
    total += s.get("otl", 0) * pts.get("goalieOtl", 0)
    total += (s.get("g", 0) + s.get("a", 0)) * pts.get("goalieGoalAssist", 0)
    return total


def player_points(player, stat, pts):
    return goalie_points(stat, pts) if player["pos"] == "G" else skater_points(stat, pts)


def team_points(team_row, pts):
    if not team_row:
        return 0
    return team_row.get("wins", 0) * pts["teamWin"] + team_row.get("otl", 0) * pts.get("teamOtl", 0)


def standings(pool, players, stats, cur_teams):
    """Classement du pool. stats = {playerId: statline}, cur_teams = classement LNH en cours (liste)."""
    pts = pool["rules"]["points"]
    teams = {t["abbr"]: t for t in cur_teams} if cur_teams else {}
    rows = []
    for part in pool["participants"]:
        lines = []
        total = 0
        for pk in pool["picks"]:
            if pk["participantId"] != part["id"]:
                continue
            pl = players[str(pk["playerId"])]
            st = (stats or {}).get(str(pl["id"]))
            fp = player_points(pl, st, pts)
            total += fp
            lines.append({"player": pl, "stat": st, "fp": fp, "round": pk["round"], "overall": pk["overall"]})
        order = {"F": 0, "D": 1, "G": 2}
        lines.sort(key=lambda l: (order[l["player"]["pos"]], -l["fp"]))
        trow = teams.get(part["team"])
        tp = team_points(trow, pts)
        total += tp
        rows.append({"participant": part, "lines": lines, "teamRow": trow, "teamPts": tp,
                     "playerPts": total - tp, "total": total})
    rows.sort(key=lambda r: -r["total"])
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    return rows
