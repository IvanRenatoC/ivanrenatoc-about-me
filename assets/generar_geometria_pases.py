#!/usr/bin/env python3
"""
Genera la portada del episodio 4: geometría de opciones de pase.
Campo vectorial tipo dipolo eléctrico que simula el flujo de pases
en una cancha horizontal (ataque izq → der).

Uso:
    python3 assets/generar_geometria_pases.py
Salida:
    podcast/covers/ep04-futbol1.png
"""

import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches

try:
    from mplsoccer import Pitch
    USE_MPLSOCCER = True
except ImportError:
    USE_MPLSOCCER = False
    print("mplsoccer no disponible — dibujando cancha con matplotlib patches (fallback).")


# ── Constantes de la cancha ─────────────────────────────────────────────────
FW, FH = 120.0, 80.0   # StatsBomb: 120×80
CX, CY = FW / 2, FH / 2

PITCH_COLOR  = '#8FCB9B'
LINE_COLOR   = '#c2d9c8'
BG_COLOR     = '#1b2b1b'
OUTPUT_PATH  = 'podcast/covers/ep04-futbol1.png'


# ── Campo vectorial tipo dipolo ──────────────────────────────────────────────
def dipole_field(px, py, exp=1.4):
    """
    Superpone dos 'cargas':
      + fuente en (−10, 40): repulsiva (arco propio)
      − sumidero en (130, 40): atractiva (arco rival)
    Crea líneas de campo curvas entre los dos extremos —
    visualmente idéntico a las líneas de un campo magnético dipolar.
    """
    src  = np.array([-10.0, CY])
    sink = np.array([FW + 10.0, CY])
    p    = np.array([px, py])

    r1 = max(np.linalg.norm(p - src),  6.0)
    r2 = max(np.linalg.norm(p - sink), 6.0)

    E1 = (p - src)  / r1 ** exp      # repulsión
    E2 = -(p - sink) / r2 ** exp     # atracción

    return E1 + E2


def build_field_grid(nx=32, ny=18):
    xs = np.linspace(2, FW - 2, nx)
    ys = np.linspace(2, FH - 2, ny)
    X, Y = np.meshgrid(xs, ys)
    VX = np.zeros_like(X)
    VY = np.zeros_like(Y)
    for i in range(ny):
        for j in range(nx):
            vx, vy = dipole_field(X[i, j], Y[i, j])
            VX[i, j] = vx
            VY[i, j] = vy
    return X, Y, VX, VY


# ── Fallback: cancha manual ───────────────────────────────────────────────────
def draw_pitch_manually(ax):
    ax.set_facecolor(PITCH_COLOR)
    ax.set_xlim(-5, FW + 5)
    ax.set_ylim(-5, FH + 5)
    ax.set_aspect('equal')
    ax.axis('off')

    lw, lc = 1.8, LINE_COLOR

    def rect(x, y, w, h):
        ax.add_patch(mpatches.FancyBboxPatch((x, y), w, h, boxstyle='square,pad=0',
                     linewidth=lw, edgecolor=lc, facecolor='none', zorder=2))

    # Perímetro
    rect(0, 0, FW, FH)
    # Línea media
    ax.plot([CX, CX], [0, FH], color=lc, lw=lw, zorder=2)
    # Círculo central
    circ = plt.Circle((CX, CY), 9.15, color=lc, fill=False, lw=lw, zorder=2)
    ax.add_patch(circ)
    ax.plot(CX, CY, 'o', color=lc, ms=2, zorder=2)
    # Áreas grandes
    rect(0, (FH - 40.32) / 2, 16.5, 40.32)
    rect(FW - 16.5, (FH - 40.32) / 2, 16.5, 40.32)
    # Áreas chicas
    rect(0, (FH - 18.32) / 2, 5.5, 18.32)
    rect(FW - 5.5, (FH - 18.32) / 2, 5.5, 18.32)
    # Arcos (rectángulos muy delgados)
    gw = 7.32
    rect(-2.0, (FH - gw) / 2, 2.0, gw)
    rect(FW,   (FH - gw) / 2, 2.0, gw)
    # Puntos de penal
    ax.plot(11, CY, 'o', color=lc, ms=2.5, zorder=2)
    ax.plot(FW - 11, CY, 'o', color=lc, ms=2.5, zorder=2)


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    fig, ax = plt.subplots(figsize=(14, 9))
    fig.patch.set_facecolor(BG_COLOR)

    if USE_MPLSOCCER:
        pitch = Pitch(
            pitch_type='statsbomb',
            pitch_color=PITCH_COLOR,
            line_color=LINE_COLOR,
            linewidth=1.8,
            goal_type='box',
            corner_arcs=True,
        )
        ax.remove()
        fig, ax = pitch.draw(figsize=(14, 9))
        fig.patch.set_facecolor(BG_COLOR)
    else:
        draw_pitch_manually(ax)

    # ── Campo vectorial ────────────────────────────────────────────────────
    X, Y, VX, VY = build_field_grid()

    mag = np.sqrt(VX**2 + VY**2) + 1e-8
    VXn = VX / mag
    VYn = VY / mag

    # Colorear por componente x (azul=retroceso → rojo=avance)
    color_norm = (VX - VX.min()) / (VX.max() - VX.min() + 1e-8)
    cmap = matplotlib.colormaps['RdYlBu_r']
    colors = cmap(color_norm.ravel())

    ax.quiver(
        X.ravel(), Y.ravel(),
        VXn.ravel(), VYn.ravel(),
        color=colors,
        scale=26,
        scale_units='xy',
        width=0.0028,
        headwidth=5,
        headlength=6,
        headaxislength=5,
        alpha=0.72,
        zorder=4,
    )

    # ── Líneas de campo (streamlines sobre grid denso para el look "magnético") ──
    xs_stream = np.linspace(2, FW - 2, 200)
    ys_stream = np.linspace(2, FH - 2, 120)
    Xs, Ys = np.meshgrid(xs_stream, ys_stream)
    US = np.zeros_like(Xs)
    VS = np.zeros_like(Ys)
    for i in range(120):
        for j in range(200):
            u, v = dipole_field(Xs[i, j], Ys[i, j])
            US[i, j] = u
            VS[i, j] = v

    try:
        ax.streamplot(
            xs_stream, ys_stream, US, VS,
            color='white',
            linewidth=0.55,
            density=0.9,
            arrowsize=0.6,
            arrowstyle='->',
            alpha=0.22,
            zorder=3,
        )
    except Exception:
        pass  # streamplot puede fallar en versiones viejas de matplotlib

    # ── 4 Zonas de origen ────────────────────────────────────────────────
    zones = [
        (18,  CY, '#FF6B6B', 'Zona\nDefensiva'),
        (45,  CY, '#FFD93D', 'Mediocampo\nPropio'),
        (75,  CY, '#4FC3F7', 'Mediocampo\nRival'),
        (102, CY, '#A8FF78', 'Zona\nAtacante'),
    ]

    for zx, zy, zcol, zlabel in zones:
        # Glow externo (círculo suave)
        for r, alpha in [(11, 0.10), (9, 0.20), (7.5, 0.35)]:
            glow = plt.Circle((zx, zy), r, color=zcol, fill=True,
                               alpha=alpha, zorder=5)
            ax.add_patch(glow)
        # Anillo
        ring = plt.Circle((zx, zy), 7.5, color=zcol, fill=False,
                           lw=2.2, alpha=0.9, zorder=6)
        ax.add_patch(ring)
        # Punto central
        ax.plot(zx, zy, 'o', color=zcol, markersize=7,
                zorder=7, alpha=1.0, markeredgewidth=1.5,
                markeredgecolor='white')
        # Etiqueta
        offset_y = -15 if zy > CY / 2 else 13
        ax.text(zx, zy + offset_y, zlabel,
                color=zcol, fontsize=8.5, ha='center', va='center',
                fontweight='bold', zorder=8,
                multialignment='center',
                bbox=dict(boxstyle='round,pad=0.25', fc=BG_COLOR,
                          ec='none', alpha=0.65))

    # ── Flecha de dirección de ataque ────────────────────────────────────
    ax.annotate('', xy=(FW - 6, 6), xytext=(6, 6),
                arrowprops=dict(arrowstyle='->', color='white',
                                lw=1.4, alpha=0.45))
    ax.text(CX, 4, 'Dirección de ataque →',
            color='white', fontsize=8, ha='center', alpha=0.5, zorder=8)

    # ── Títulos ───────────────────────────────────────────────────────────
    fig.text(0.5, 0.975,
             'Geometría de las opciones de pase',
             ha='center', va='top',
             fontsize=17, color='white', fontweight='bold')
    fig.text(0.5, 0.012,
             'El campo vectorial revela cómo la geometría curva las decisiones en el fútbol',
             ha='center', va='bottom',
             fontsize=10, color='#AACCAA', style='italic')

    # ── Leyenda compacta ──────────────────────────────────────────────────
    patches = [
        mpatches.Patch(color=cmap(0.05), label='Pase atrás / lateral'),
        mpatches.Patch(color=cmap(0.95), label='Pase hacia adelante'),
    ]
    ax.legend(handles=patches, loc='upper right', fontsize=8,
              framealpha=0.55, facecolor=BG_COLOR, edgecolor='none',
              labelcolor='white')

    # ── Guardar ───────────────────────────────────────────────────────────
    fig.savefig(OUTPUT_PATH, dpi=160, bbox_inches='tight',
                facecolor=BG_COLOR)
    print(f'✓ Imagen guardada: {OUTPUT_PATH}')
    plt.close(fig)


if __name__ == '__main__':
    main()
