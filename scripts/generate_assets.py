import json
import os
import re
import urllib.request
from datetime import date, datetime, timedelta

USER = os.environ.get("GH_USER", "supratim-paul")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = os.path.join(os.path.dirname(__file__), "..", "assets")
os.makedirs(OUT, exist_ok=True)

BG = "#0d1117"
CARD = "#161b22"
BORDER = "#30363d"
TEXT = "#c4b5fd"
MUTED = "#8b949e"
ACCENT = "#a78bfa"
LEVELS = ["#1f2430", "#3b2a73", "#5b21b6", "#7c3aed", "#a78bfa"]
FONT = "Segoe UI, Ubuntu, Helvetica, Arial, sans-serif"


def get(url, api=False):
    headers = {"User-Agent": "profile-assets"}
    if api and TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
        return r.read().decode("utf-8")


def contributions():
    html = get(f"https://github.com/users/{USER}/contributions")
    cells = re.findall(
        r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*?id="(contribution-day-component-\d+-\d+)"[^>]*?data-level="(\d)"',
        html,
    )
    tips = dict(
        re.findall(r'for="(contribution-day-component-\d+-\d+)"[^>]*>\s*(No|\d+) contributions?', html)
    )
    days = []
    for d, cid, lvl in cells:
        n = tips.get(cid, "0")
        days.append((datetime.strptime(d, "%Y-%m-%d").date(), 0 if n == "No" else int(n), int(lvl)))
    days.sort()
    return days


def profile():
    try:
        u = json.loads(get(f"https://api.github.com/users/{USER}", api=True))
        repos = json.loads(get(f"https://api.github.com/users/{USER}/repos?per_page=100", api=True))
        return u["public_repos"], u["followers"], sum(r["stargazers_count"] for r in repos)
    except Exception:
        return 5, 0, 5


def streaks(days):
    today = date.today()
    counted = [(d, n) for d, n, _ in days if d <= today]
    longest = run = 0
    for _, n in counted:
        run = run + 1 if n > 0 else 0
        longest = max(longest, run)
    cur = 0
    for i in range(len(counted) - 1, -1, -1):
        if counted[i][1] > 0:
            cur += 1
        elif i == len(counted) - 1:
            continue
        else:
            break
    return cur, longest


def activity_svg(days):
    cell, gap, left, top = 11, 3, 40, 46
    first = days[0][0]
    offset = (first.weekday() + 1) % 7
    weeks = (len(days) + offset + 6) // 7
    w = left + weeks * (cell + gap) + 20
    h = top + 7 * (cell + gap) + 40
    total = sum(n for _, n, _ in days)
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{FONT}">',
        f'<rect width="{w}" height="{h}" rx="10" fill="{BG}"/>',
        f'<text x="20" y="22" font-size="13" font-weight="600" fill="{ACCENT}">{total} contributions in the last year</text>',
    ]
    for i, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        p.append(f'<text x="10" y="{top + i * (cell + gap) + 9}" font-size="9" fill="{MUTED}">{label}</text>')
    last_month = None
    for i, (d, n, lvl) in enumerate(days):
        idx = i + offset
        col, row = idx // 7, idx % 7
        x, y = left + col * (cell + gap), top + row * (cell + gap)
        if row == 0 and d.month != last_month:
            p.append(f'<text x="{x}" y="{top - 6}" font-size="9" fill="{MUTED}">{d.strftime("%b")}</text>')
            last_month = d.month
        p.append(
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{LEVELS[lvl]}">'
            f'<title>{n} contributions on {d.isoformat()}</title></rect>'
        )
    ly = h - 16
    p.append(f'<text x="{w - 190}" y="{ly + 9}" font-size="9" fill="{MUTED}">Less</text>')
    for i, c in enumerate(LEVELS):
        p.append(f'<rect x="{w - 165 + i * 16}" y="{ly}" width="11" height="11" rx="2" fill="{c}"/>')
    p.append(f'<text x="{w - 78}" y="{ly + 9}" font-size="9" fill="{MUTED}">More</text>')
    p.append("</svg>")
    return "\n".join(p)


def trophies_svg(days):
    repos, followers, stars = profile()
    total = sum(n for _, n, _ in days)
    cur, longest = streaks(days)
    items = [
        ("Contributions", total, "past year"),
        ("Repositories", repos, "public"),
        ("Followers", followers, "on GitHub"),
        ("Stars", stars, "earned"),
        ("Longest Streak", longest, "days"),
        ("Current Streak", cur, "days"),
    ]
    cw, ch, g = 120, 120, 12
    w = len(items) * cw + (len(items) - 1) * g + 24
    h = ch + 24
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{FONT}">',
        "<defs>",
        '<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#4c1d95"/><stop offset="1" stop-color="#7c3aed"/></linearGradient>',
        "</defs>",
        f'<rect width="{w}" height="{h}" rx="10" fill="{BG}"/>',
    ]
    for i, (name, val, sub) in enumerate(items):
        x = 12 + i * (cw + g)
        cx = x + cw / 2
        p += [
            f'<rect x="{x}" y="12" width="{cw}" height="{ch}" rx="10" fill="{CARD}" stroke="{BORDER}"/>',
            f'<rect x="{x}" y="12" width="{cw}" height="6" rx="3" fill="url(#g)"/>',
            f'<circle cx="{cx}" cy="58" r="24" fill="none" stroke="url(#g)" stroke-width="3"/>',
            f'<text x="{cx}" y="65" text-anchor="middle" font-size="20" font-weight="700" fill="{ACCENT}">{val}</text>',
            f'<text x="{cx}" y="104" text-anchor="middle" font-size="11" font-weight="600" fill="{TEXT}">{name}</text>',
            f'<text x="{cx}" y="119" text-anchor="middle" font-size="9" fill="{MUTED}">{sub}</text>',
        ]
    p.append("</svg>")
    return "\n".join(p)


if __name__ == "__main__":
    days = contributions()
    with open(os.path.join(OUT, "activity.svg"), "w") as f:
        f.write(activity_svg(days))
    with open(os.path.join(OUT, "trophies.svg"), "w") as f:
        f.write(trophies_svg(days))
    print("ok", len(days), "days")
