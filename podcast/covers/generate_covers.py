"""
Genera los covers del podcast "DATA EN AUDIO" (1400x1400 px).
Requiere: Pillow
"""
from PIL import Image, ImageDraw, ImageFont
import math, os, random

# ── Paleta ──────────────────────────────────────────────────────────────────
NAVY  = (15,  35,  66)
BLUE  = (37,  99, 235)
LBLUE = (219, 234, 254)
GOLD  = (245, 158, 11)
WHITE = (255, 255, 255)

SIZE    = 1400
SERIF   = "/System/Library/Fonts/Supplemental/Georgia.ttf"
SANS    = "/System/Library/Fonts/Helvetica.ttc"
OUT_DIR = os.path.dirname(__file__)


def make_base():
    return Image.new("RGBA", (SIZE, SIZE), NAVY + (255,))


def load_font(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except Exception:
        return ImageFont.load_default()


def draw_wordmark(draw, y=80):
    font = load_font(SANS, 34)
    text = "D A T A   E N   A U D I O"
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text(((SIZE - w) // 2, y), text, font=font, fill=LBLUE + (255,))


def draw_title(draw, text, y=SIZE - 200):
    font = load_font(SERIF, 82)
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text(((SIZE - w) // 2, y), text, font=font, fill=WHITE + (255,))


def draw_ep_label(draw, number, y=SIZE - 268):
    font = load_font(SANS, 30)
    text = f"EPISODIO {number}"
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text(((SIZE - w) // 2, y), text, font=font, fill=LBLUE + (180,))


# ── COVER 1 — Clasificación binaria ─────────────────────────────────────────

def make_cover_1():
    img = make_base()
    draw = ImageDraw.Draw(img, "RGBA")

    # Plot area — centrado, con aire
    PX, PY = 180, 210
    PW, PH = 1040, 800

    # Grilla tenue (10% opacidad)
    G = (255, 255, 255, 25)
    for i in range(1, 5):
        x = PX + i * PW // 5
        draw.line([(x, PY), (x, PY + PH)], fill=G, width=1)
    for i in range(1, 5):
        y = PY + i * PH // 5
        draw.line([(PX, y), (PX + PW, y)], fill=G, width=1)

    # Grupo A (azul) — zona superior-izquierda, bien centrado
    group_a = [
        (310,310),(355,370),(290,440),(370,295),(425,385),(340,465),
        (275,355),(400,325),(330,500),(450,420),(385,275),(300,490),
        (440,345),(360,440),(315,400),(465,300),(280,445),(410,465),
        (345,315),(425,490),(300,330),(375,395),(450,365),(325,455),
    ]
    # Grupo B (dorado) — zona inferior-derecha
    group_b = [
        (870,620),(925,690),(880,755),(955,630),(1005,715),(895,800),
        (830,670),(985,660),(915,735),(1030,695),(855,780),(920,630),
        (975,760),(845,710),(1005,645),(895,690),(820,750),(965,720),
        (1020,775),(880,660),(940,795),(820,700),(990,650),(875,730),
    ]

    R = 20  # radio del punto

    def dot(cx, cy, color):
        draw.ellipse([cx - R, cy - R, cx + R, cy + R], fill=color + (255,))

    for cx, cy in group_a:
        dot(cx, cy, BLUE)
    for cx, cy in group_b:
        dot(cx, cy, GOLD)

    # Frontera de decisión: línea diagonal suave punteada, blanca
    # Va de esquina superior-derecha del grupo A hacia esquina inferior-izquierda del B
    # Aprox. desde (600, 220) hasta (660, 990)
    boundary_pts = []
    steps = 140
    for i in range(steps + 1):
        t = i / steps
        # curva suave: pequeña S
        x = 600 + 55 * math.tanh(4 * (t - 0.5))
        y = PY + 20 + t * (PH - 30)
        boundary_pts.append((x, y))

    # Dibuja punteado
    SEG, GAP = 16, 10
    acc = 0
    on = True
    for i in range(len(boundary_pts) - 1):
        x0, y0 = boundary_pts[i]
        x1, y1 = boundary_pts[i + 1]
        if on:
            draw.line([(x0, y0), (x1, y1)], fill=(255, 255, 255, 210), width=3)
        acc += math.hypot(x1 - x0, y1 - y0)
        if acc >= (SEG if on else GAP):
            acc = 0
            on = not on

    draw_wordmark(draw)
    draw_ep_label(draw, 1)
    draw_title(draw, "Clasificación binaria")

    img = img.convert("RGB")
    out = os.path.join(OUT_DIR, "ep01-clasificacion-binaria.png")
    img.save(out, "PNG", dpi=(300, 300))
    print(f"  ✓  {out}  ({img.size[0]}×{img.size[1]})")


# ── COVER 2 — Series de tiempo ───────────────────────────────────────────────

def make_cover_2():
    img = make_base()
    draw = ImageDraw.Draw(img, "RGBA")

    PX, PY = 120, 200
    PW, PH = 1160, 790
    NOW_X = PX + int(PW * 0.63)

    # Grilla horizontal tenue
    G = (255, 255, 255, 22)
    for i in range(1, 6):
        y = PY + i * PH // 6
        draw.line([(PX, y), (PX + PW, y)], fill=G, width=1)

    # Serie histórica: tendencia + estacionalidad + ruido controlado
    random.seed(42)
    n_hist = 30
    n_fore = 14

    def series_y(i, total):
        t = i / total
        trend   = -0.22 * t * PH
        season  = math.sin(t * math.pi * 4.2) * PH * 0.075
        noise   = (random.random() - 0.5) * PH * 0.04
        return PY + PH * 0.52 + trend + season + noise

    hist_xs = [PX + int(i * (NOW_X - PX) / (n_hist - 1)) for i in range(n_hist)]
    hist_ys = [series_y(i, n_hist) for i in range(n_hist)]

    # Pronóstico: continúa con tendencia suavizada, menos ruido
    last_y  = hist_ys[-1]
    slope   = (hist_ys[-1] - hist_ys[-6]) / 5 * 0.55
    fore_xs = [NOW_X + int((i + 1) * (PX + PW - NOW_X - 30) / n_fore) for i in range(n_fore)]
    fore_ys = []
    for i in range(n_fore):
        t = (i + 1) / n_fore
        fore_ys.append(last_y + slope * (i + 1) - math.sin(t * math.pi * 2) * PH * 0.04)

    # Banda de confianza (se ensancha)
    spread = PH * 0.065
    upper = [(fore_xs[i], fore_ys[i] - spread * (i + 1) / n_fore) for i in range(n_fore)]
    lower = [(fore_xs[i], fore_ys[i] + spread * (i + 1) / n_fore) for i in range(n_fore)]
    poly  = [(NOW_X, last_y)] + upper + list(reversed(lower)) + [(NOW_X, last_y)]
    draw.polygon(poly, fill=BLUE + (50,))

    # Línea vertical "ahora"
    draw.line([(NOW_X, PY + 10), (NOW_X, PY + PH - 10)], fill=(255, 255, 255, 70), width=2)

    # Línea histórica — sólida azul, gruesa
    hist_pts = list(zip(hist_xs, hist_ys))
    for i in range(len(hist_pts) - 1):
        draw.line([hist_pts[i], hist_pts[i + 1]], fill=BLUE + (255,), width=5)

    # Línea pronóstico — punteada dorada, bien visible
    fore_pts = [(NOW_X, last_y)] + list(zip(fore_xs, fore_ys))
    SEG, GAP = 20, 12
    acc = 0
    on  = True
    for i in range(len(fore_pts) - 1):
        x0, y0 = fore_pts[i]
        x1, y1 = fore_pts[i + 1]
        if on:
            draw.line([(x0, y0), (x1, y1)], fill=GOLD + (255,), width=5)
        acc += math.hypot(x1 - x0, y1 - y0)
        if acc >= (SEG if on else GAP):
            acc = 0
            on = not on

    # Label "PRONÓSTICO" arriba del tramo dorado
    font_sm = load_font(SANS, 28)
    draw.text((NOW_X + 24, PY + 24), "PRONÓSTICO", font=font_sm, fill=GOLD + (210,))

    draw_wordmark(draw)
    draw_ep_label(draw, 2)
    draw_title(draw, "Series de tiempo")

    img = img.convert("RGB")
    out = os.path.join(OUT_DIR, "ep02-series-de-tiempo.png")
    img.save(out, "PNG", dpi=(300, 300))
    print(f"  ✓  {out}  ({img.size[0]}×{img.size[1]})")


if __name__ == "__main__":
    print("Generando covers…")
    make_cover_1()
    make_cover_2()
    print("Listo.")
