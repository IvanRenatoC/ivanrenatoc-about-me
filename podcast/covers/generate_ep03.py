"""
Genera ep03-segmentacion.png (1400×1400 px) — "DATA EN AUDIO"
Tema: K-Means + Computer Vision (clustering sobre cuadrícula de píxeles)
"""
from PIL import Image, ImageDraw, ImageFont
import math, os

NAVY  = (15,  35,  66)
BLUE  = (37,  99, 235)
LBLUE = (219, 234, 254)
GOLD  = (245, 158, 11)
WHITE = (255, 255, 255)

SIZE    = 1400
SERIF   = "/System/Library/Fonts/Supplemental/Georgia.ttf"
SANS    = "/System/Library/Fonts/Helvetica.ttc"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))


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


def make_cover_3():
    img = Image.new("RGBA", (SIZE, SIZE), NAVY + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Área del motivo central ──────────────────────────────────────────────
    CX, CY = SIZE // 2, 640   # centro visual
    CELL = 52                  # tamaño de celda de la cuadrícula

    # ── Cuadrícula de píxeles (grilla de "imagen") ───────────────────────────
    GRID_X1, GRID_Y1 = 190, 195
    GRID_X2, GRID_Y2 = 1210, 1000

    cols = (GRID_X2 - GRID_X1) // CELL
    rows = (GRID_Y2 - GRID_Y1) // CELL

    # Fondo de celdas: cada celda coloreada suavemente según cluster más cercano
    clusters = [
        {"cx": 430,  "cy": 380,  "color": BLUE},
        {"cx": 760,  "cy": 700,  "color": LBLUE},
        {"cx": 1020, "cy": 380,  "color": GOLD},
    ]

    for r in range(rows):
        for c in range(cols):
            cell_x = GRID_X1 + c * CELL + CELL // 2
            cell_y = GRID_Y1 + r * CELL + CELL // 2
            # Asignar al cluster más cercano
            best = min(clusters, key=lambda k: math.hypot(cell_x - k["cx"], cell_y - k["cy"]))
            dist = math.hypot(cell_x - best["cx"], cell_y - best["cy"])
            # Opacidad decae con la distancia al centroide
            alpha = max(18, min(55, int(55 - dist * 0.045)))
            col = best["color"] + (alpha,)
            x1 = GRID_X1 + c * CELL
            y1 = GRID_Y1 + r * CELL
            draw.rectangle([x1, y1, x1 + CELL - 1, y1 + CELL - 1], fill=col)

    # Líneas de la cuadrícula (muy tenues)
    G = (255, 255, 255, 18)
    for c in range(cols + 1):
        x = GRID_X1 + c * CELL
        draw.line([(x, GRID_Y1), (x, GRID_Y2)], fill=G, width=1)
    for r in range(rows + 1):
        y = GRID_Y1 + r * CELL
        draw.line([(GRID_X1, y), (GRID_X2, y)], fill=G, width=1)

    # ── Bounding box (marco de detección — computer vision) ──────────────────
    BB_X1, BB_Y1, BB_X2, BB_Y2 = 192, 197, 1208, 998
    CORNER = 48   # longitud de cada esquina
    BW = 3        # grosor

    corners = [
        (BB_X1, BB_Y1, +1, +1),
        (BB_X2, BB_Y1, -1, +1),
        (BB_X2, BB_Y2, -1, -1),
        (BB_X1, BB_Y2, +1, -1),
    ]
    for (bx, by, dx, dy) in corners:
        draw.line([(bx, by), (bx + dx * CORNER, by)], fill=GOLD + (220,), width=BW)
        draw.line([(bx, by), (bx, by + dy * CORNER)], fill=GOLD + (220,), width=BW)

    # ── Puntos de datos por cluster ──────────────────────────────────────────
    cluster_points = {
        0: [(360,320),(410,280),(310,360),(450,310),(375,400),(295,420),
            (490,350),(340,460),(420,390),(275,355),(510,290),(430,450)],
        1: [(720,660),(780,620),(690,710),(760,740),(820,670),(700,750),
            (840,710),(740,790),(790,630),(660,690),(810,760),(730,820)],
        2: [(970,320),(1040,280),(990,380),(1070,340),(950,430),(1090,300),
            (1000,450),(1060,390),(920,350),(1040,420),(980,290),(1020,460)],
    }
    colors_cluster = [BLUE, LBLUE, GOLD]
    R = 16   # radio punto

    for ci, pts in cluster_points.items():
        col = colors_cluster[ci]
        for (px, py) in pts:
            draw.ellipse([px - R, py - R, px + R, py + R], fill=col + (240,))

    # ── Círculos tenues alrededor de cada cluster ────────────────────────────
    radii = [230, 200, 220]
    for i, clust in enumerate(clusters):
        r2 = radii[i]
        col = colors_cluster[i]
        draw.ellipse(
            [clust["cx"] - r2, clust["cy"] - r2, clust["cx"] + r2, clust["cy"] + r2],
            outline=col + (55,), width=2
        )

    # ── Centroides (X grande + punto central) ────────────────────────────────
    for i, clust in enumerate(clusters):
        ccx, ccy = clust["cx"], clust["cy"]
        col = colors_cluster[i]
        arm = 22
        lw  = 5
        draw.line([(ccx - arm, ccy - arm), (ccx + arm, ccy + arm)], fill=WHITE + (240,), width=lw)
        draw.line([(ccx + arm, ccy - arm), (ccx - arm, ccy + arm)], fill=WHITE + (240,), width=lw)
        draw.ellipse([ccx - 8, ccy - 8, ccx + 8, ccy + 8], fill=WHITE + (255,))

    # ── Etiqueta "K-MEANS" ───────────────────────────────────────────────────
    font_sm = load_font(SANS, 26)
    draw.text((GRID_X1 + 12, GRID_Y2 - 44), "K-MEANS", font=font_sm, fill=LBLUE + (180,))

    # ── Wordmark + episodio + título (idéntico a ep01/ep02) ──────────────────
    draw_wordmark(draw)
    draw_ep_label(draw, 3)
    draw_title(draw, "Segmentación")

    out = os.path.join(OUT_DIR, "ep03-segmentacion.png")
    img.convert("RGB").save(out, "PNG", dpi=(300, 300))
    print(f"  ✓  {out}  (1400×1400)")


if __name__ == "__main__":
    print("Generando cover ep03…")
    make_cover_3()
    print("Listo.")
