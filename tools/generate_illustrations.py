"""Génère les illustrations SVG des micro-pousses Toque Final.

Usage : python3 tools/generate_illustrations.py
Les fichiers sont écrits dans assets/img/. Le tirage est déterministe (graine fixe),
donc relancer le script redonne exactement les mêmes images.
"""
import math
import os
import random

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "img")

# Palette de marque
SOIL = "#4a3426"
SOIL_DOTS = ("#5e4433", "#3a281d", "#6b5040")
TRAY = "#1f3d2b"
TRAY_LIP = "#2c5239"

VARIETIES = {
    "radis":     dict(stem="#9c1d55", base="#f1c6d8", leaf="#4f8a3c", shape="heart",   size=19, n=40, h=(110, 190), bg="#f7e4ea"),
    "petit-pois": dict(stem="#8fbf5a", base="#e4f0cf", leaf="#5fa034", shape="oval",    size=24, n=20, h=(150, 230), bg="#e8f2d8", tendril=True),
    "tournesol": dict(stem="#cfdcae", base="#f3f3e2", leaf="#79b03c", shape="oval",    size=27, n=24, h=(110, 175), bg="#fbf1d3", hull=True),
    "betterave": dict(stem="#b0174a", base="#f0b9c9", leaf="#6d7f2e", shape="pointed", size=20, n=38, h=(100, 170), bg="#f5e1e3"),
    "coriandre": dict(stem="#9cc06a", base="#e6f0d2", leaf="#5c9a37", shape="pointed", size=25, n=30, h=(120, 200), bg="#e9f3df"),
    "basilic":   dict(stem="#6b3a6e", base="#d9c4da", leaf="#4b2350", shape="round",   size=16, n=42, h=(90, 150),  bg="#ece3ef"),
    "moutarde":  dict(stem="#c6dba3", base="#eef4e0", leaf="#7b2d4f", shape="heart",   size=18, n=42, h=(100, 165), bg="#f3e6ea"),
    "roquette":  dict(stem="#cde0aa", base="#f0f6e3", leaf="#5a9838", shape="heart",   size=15, n=46, h=(90, 150),  bg="#eaf3dc"),
}


def leaf_path(shape, L, W):
    """Feuille couchée sur l'axe +x, attachée à l'origine."""
    if shape == "heart":   # cotylédon échancré (radis, moutarde, roquette)
        return (f"M0,0 C{L*.25:.1f},{-W:.1f} {L*1.05:.1f},{-W*1.05:.1f} {L:.1f},{-W*.12:.1f} "
                f"Q{L*.86:.1f},0 {L:.1f},{W*.12:.1f} C{L*1.05:.1f},{W*1.05:.1f} {L*.25:.1f},{W:.1f} 0,0Z")
    if shape == "pointed":  # feuille effilée (betterave, coriandre)
        return (f"M0,0 C{L*.3:.1f},{-W*.6:.1f} {L*.75:.1f},{-W*.45:.1f} {L:.1f},0 "
                f"C{L*.75:.1f},{W*.45:.1f} {L*.3:.1f},{W*.6:.1f} 0,0Z")
    if shape == "round":    # feuille ronde (basilic)
        return (f"M0,0 C{L*.1:.1f},{-W*.9:.1f} {L*1.1:.1f},{-W*.9:.1f} {L:.1f},0 "
                f"C{L*1.1:.1f},{W*.9:.1f} {L*.1:.1f},{W*.9:.1f} 0,0Z")
    # oval (tournesol, petit pois)
    return (f"M0,0 C{L*.2:.1f},{-W*.75:.1f} {L*.95:.1f},{-W*.7:.1f} {L:.1f},0 "
            f"C{L*.95:.1f},{W*.7:.1f} {L*.2:.1f},{W*.75:.1f} 0,0Z")


def sprout(rng, v, x0, y0, scale=1.0, uid="v"):
    h = rng.uniform(*v["h"]) * scale
    lean = rng.uniform(-28, 28) * scale
    x1, y1 = x0 + lean, y0 - h
    cx, cy = x0 + lean * rng.uniform(-.4, .3), y0 - h * .55
    sw = rng.uniform(2.4, 3.6) * scale * (1.3 if v["size"] > 22 else 1)
    parts = [f'<path d="M{x0:.1f},{y0:.1f} Q{cx:.1f},{cy:.1f} {x1:.1f},{y1:.1f}" '
             f'stroke="url(#stem-{uid})" stroke-width="{sw:.1f}" fill="none" stroke-linecap="round"/>']
    # tangente au sommet → orientation des feuilles
    ang = math.degrees(math.atan2(y1 - cy, x1 - cx))
    L = v["size"] * rng.uniform(.85, 1.15) * scale
    W = L * (.62 if v["shape"] != "pointed" else .5)
    spread = rng.uniform(38, 62)
    d = leaf_path(v["shape"], L, W)
    for s in (-1, 1):
        a = ang + s * spread + rng.uniform(-8, 8)
        parts.append(f'<g transform="translate({x1:.1f},{y1:.1f}) rotate({a:.1f})">'
                     f'<path d="{d}" fill="url(#leaf-{uid})"/>'
                     f'<path d="M1,0 L{L*.78:.1f},0" stroke="#ffffff" stroke-opacity=".28" '
                     f'stroke-width="{max(.8, scale):.1f}" stroke-linecap="round"/></g>')
    if v.get("hull") and rng.random() < .35:
        parts.append(f'<ellipse cx="{x1:.1f}" cy="{y1 - 4:.1f}" rx="{5*scale:.1f}" ry="{9*scale:.1f}" '
                     f'transform="rotate({ang + 90:.1f} {x1:.1f} {y1 - 4:.1f})" fill="#2a2420"/>'
                     f'<path d="M{x1 - 2*scale:.1f},{y1 - 11*scale:.1f} l{2*scale:.1f},{14*scale:.1f}" '
                     f'stroke="#d8d2c4" stroke-width="{1.4*scale:.1f}" '
                     f'transform="rotate({ang + 90:.1f} {x1:.1f} {y1 - 4:.1f})"/>')
    if v.get("tendril") and rng.random() < .6:
        tx, ty = x1 + rng.choice((-1, 1)) * 6, y1 - 6
        r = 6 * scale
        parts.append(f'<path d="M{x1:.1f},{y1:.1f} q{(tx - x1):.1f},-14 {(tx - x1) * 2:.1f},-20 '
                     f'a{r:.1f},{r:.1f} 0 1 1 {r:.1f},{-r:.1f} a{r/2:.1f},{r/2:.1f} 0 1 1 -{r/2:.1f},{r/2:.1f}" '
                     f'stroke="{v["stem"]}" stroke-width="{1.4*scale:.1f}" fill="none" stroke-linecap="round"/>')
    return y1, "".join(parts)


def defs(uid, v):
    return (f'<linearGradient id="stem-{uid}" x1="0" y1="1" x2="0" y2="0">'
            f'<stop offset="0" stop-color="{v["base"]}"/><stop offset=".55" stop-color="{v["stem"]}"/></linearGradient>'
            f'<linearGradient id="leaf-{uid}" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{v["leaf"]}"/><stop offset="1" stop-color="{shade(v["leaf"], -.25)}"/></linearGradient>')


def shade(hex_, k):
    r, g, b = (int(hex_[i:i + 2], 16) for i in (1, 3, 5))
    f = (lambda c: int(c + (255 - c) * k)) if k > 0 else (lambda c: int(c * (1 + k)))
    return "#%02x%02x%02x" % tuple(max(0, min(255, f(c))) for c in (r, g, b))


def tray(rng, x, y, w, h, uid):
    dots = "".join(
        f'<circle cx="{rng.uniform(x + 8, x + w - 8):.1f}" cy="{rng.uniform(y + 4, y + 18):.1f}" '
        f'r="{rng.uniform(1, 2.6):.1f}" fill="{rng.choice(SOIL_DOTS)}"/>' for _ in range(int(w / 4)))
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{SOIL}"/>{dots}',
            f'<rect x="{x - 6}" y="{y + 16}" width="{w + 12}" height="{h - 10}" rx="12" fill="{TRAY}"/>'
            f'<rect x="{x - 6}" y="{y + 16}" width="{w + 12}" height="7" rx="3.5" fill="{TRAY_LIP}"/>')


def variety_svg(name, v, seed):
    rng = random.Random(seed)
    W, H, top = 400, 400, 292
    soil, front = tray(rng, 50, top, 300, 78, name)
    sprouts = []
    for _ in range(v["n"]):
        x0 = rng.uniform(70, 330)
        y0 = top + rng.uniform(6, 20)
        sprouts.append(sprout(rng, v, x0, y0, 1.0, name))
    sprouts.sort(key=lambda s: s[0])  # les plus hautes derrière
    body = "".join(s[1] for s in sprouts)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="Illustration de micro-pousses : {name}"><defs>{defs(name, v)}</defs>'
            f'<circle cx="200" cy="215" r="170" fill="{v["bg"]}"/>{soil}{body}{front}</svg>')


def hero_svg(seed=7):
    rng = random.Random(seed)
    W, H, top = 900, 560, 410
    out_defs, layers = [], []
    for k, v in VARIETIES.items():
        out_defs.append(defs(k, v))
    soil, front = tray(rng, 70, top, 760, 96, "hero")
    names = list(VARIETIES)
    sprouts = []
    for i in range(170):
        # bandes de variétés comme dans un vrai bac de culture
        band = min(len(names) - 1, int((i / 170) * len(names)))
        k = names[band]
        x0 = 95 + (band + rng.random()) * (710 / len(names))
        y0 = top + rng.uniform(6, 24)
        sprouts.append(sprout(rng, VARIETIES[k], x0, y0, 1.2, k))
    sprouts.sort(key=lambda s: s[0])
    layers.append("".join(s[1] for s in sprouts))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="Bac de culture rempli de micro-pousses variées"><defs>{"".join(out_defs)}</defs>'
            f'<ellipse cx="450" cy="300" rx="430" ry="250" fill="#e7efd9"/>'
            f'{soil}{"".join(layers)}{front}</svg>')


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for i, (name, v) in enumerate(VARIETIES.items()):
        with open(os.path.join(OUT, f"{name}.svg"), "w") as f:
            f.write(variety_svg(name, v, 100 + i))
    with open(os.path.join(OUT, "hero.svg"), "w") as f:
        f.write(hero_svg())
    print("ok:", ", ".join(VARIETIES), "+ hero")
