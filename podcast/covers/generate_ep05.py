#!/usr/bin/env python3
"""Genera ep05-fraude.png (1400x1400) — máscara teatral blanca sobre fondo navy.
Rasteriza el SVG con Playwright (Chromium) para preservar blur/gradientes.
"""

import os, tempfile
from playwright.sync_api import sync_playwright
from PIL import Image

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ep05-fraude.png")

MASK_PATH = (
    "M 700,155 "
    "C 838,148 1005,212 1028,432 "
    "C 1050,588 972,725 865,870 "
    "C 820,938 772,1003 700,1008 "
    "C 628,1003 580,938 535,870 "
    "C 428,725 350,588 372,432 "
    "C 395,212 562,148 700,155 Z"
)

HTML = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1400px;height:1400px;overflow:hidden;background:#0f2342;}}
svg{{display:block;}}
</style>
</head>
<body>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="1400" height="1400" viewBox="0 0 1400 1400">
  <defs>
    <!-- Filtros de desenfoque -->
    <filter id="f-drop" x="-40%" y="-30%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="42"/>
    </filter>
    <filter id="f-edge" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="30"/>
    </filter>
    <filter id="f-mid"  x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="22"/>
    </filter>
    <filter id="f-hi"   x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="16"/>
    </filter>

    <!-- Clip a la silueta de la máscara -->
    <clipPath id="mask-clip">
      <path d="{MASK_PATH}"/>
    </clipPath>

    <!-- Gradiente radial para volumen de la cara -->
    <radialGradient id="face-grad" cx="50%" cy="30%" r="60%" fx="50%" fy="26%">
      <stop offset="0%"   stop-color="#fdfdfe"/>
      <stop offset="28%"  stop-color="#f5f7fb"/>
      <stop offset="58%"  stop-color="#eef1f6"/>
      <stop offset="83%"  stop-color="#dce2ed"/>
      <stop offset="100%" stop-color="#d2d8e3"/>
    </radialGradient>
  </defs>

  <!-- Fondo navy -->
  <rect width="1400" height="1400" fill="#0f2342"/>

  <!-- Sombra proyectada de la máscara (detrás) -->
  <path d="{MASK_PATH}" transform="translate(22,46)"
        fill="#05101f" opacity="0.46" filter="url(#f-drop)"/>

  <!-- Silueta blanca de la máscara -->
  <path d="{MASK_PATH}"
        fill="url(#face-grad)"
        stroke="#c9d1dd" stroke-width="2.5"/>

  <!-- ── Capas de profundidad, recortadas a la silueta ── -->
  <g clip-path="url(#mask-clip)">
    <!-- Sombras laterales (bordes) -->
    <ellipse cx="388" cy="590" rx="135" ry="430"
             fill="#1a2230" opacity="0.18" filter="url(#f-edge)"/>
    <ellipse cx="1012" cy="590" rx="135" ry="430"
             fill="#1a2230" opacity="0.18" filter="url(#f-edge)"/>

    <!-- Sombra bajo arco de cejas -->
    <ellipse cx="562" cy="448" rx="105" ry="34"
             fill="#1a2230" opacity="0.13" filter="url(#f-mid)"/>
    <ellipse cx="838" cy="448" rx="105" ry="34"
             fill="#1a2230" opacity="0.13" filter="url(#f-mid)"/>

    <!-- Huecos de mejillas -->
    <ellipse cx="450" cy="698" rx="88" ry="68"
             fill="#1a2230" opacity="0.14" filter="url(#f-mid)"/>
    <ellipse cx="950" cy="698" rx="88" ry="68"
             fill="#1a2230" opacity="0.14" filter="url(#f-mid)"/>

    <!-- Lados del puente nasal -->
    <ellipse cx="648" cy="690" rx="34" ry="95"
             fill="#1a2230" opacity="0.11" filter="url(#f-hi)"/>
    <ellipse cx="752" cy="690" rx="34" ry="95"
             fill="#1a2230" opacity="0.11" filter="url(#f-hi)"/>

    <!-- Sombra de mandíbula/mentón -->
    <ellipse cx="700" cy="975" rx="205" ry="58"
             fill="#1a2230" opacity="0.18" filter="url(#f-mid)"/>

    <!-- Luz en frente (broad highlight) -->
    <ellipse cx="700" cy="268" rx="248" ry="116"
             fill="white" opacity="0.38" filter="url(#f-hi)"/>
    <!-- Luz franja del puente nasal -->
    <rect x="690" y="558" width="20" height="200"
          fill="white" opacity="0.30" rx="10" filter="url(#f-hi)"/>
    <!-- Luces en pómulos -->
    <ellipse cx="533" cy="558" rx="78" ry="50"
             fill="white" opacity="0.27" filter="url(#f-hi)"/>
    <ellipse cx="867" cy="558" rx="78" ry="50"
             fill="white" opacity="0.27" filter="url(#f-hi)"/>
  </g>

  <!-- ── Ojos en forma de almendra (puntiagudos en comisuras) ── -->
  <!-- Ojo izquierdo -->
  <path d="M 508,457 C 526,416 638,412 654,458 C 638,502 526,498 508,457 Z"
        fill="#0a1a33"/>
  <!-- Ojo derecho (simétrico) -->
  <path d="M 892,457 C 874,416 762,412 746,458 C 762,502 874,498 892,457 Z"
        fill="#0a1a33"/>

  <!-- ── Narinas (sugerencia de nariz) ── -->
  <ellipse cx="668" cy="760" rx="14" ry="9" fill="#39404c"/>
  <ellipse cx="732" cy="760" rx="14" ry="9" fill="#39404c"/>

  <!-- ── Ranura de la boca ── -->
  <rect x="632" y="842" width="136" height="20" rx="10" fill="#2b313c"/>

  <!-- ── Pestañas laterales / clips de la correa ── -->
  <rect x="369" y="420" width="17" height="50" rx="5" fill="#0a1830"/>
  <rect x="1014" y="420" width="17" height="50" rx="5" fill="#0a1830"/>

  <!-- ══════════════════════════════════════════════════════════ -->
  <!-- MARCO DE SERIE — mismo que ep01–ep04                      -->
  <!-- ══════════════════════════════════════════════════════════ -->

  <!-- Wordmark -->
  <text x="700" y="98"
        font-family="'Helvetica Neue', Helvetica, Arial, sans-serif"
        font-size="34" font-weight="300" letter-spacing="8"
        text-anchor="middle" fill="#9db8e0">D A T A   E N   A U D I O</text>

  <!-- Separador sutil (línea) -->
  <line x1="560" y1="118" x2="840" y2="118" stroke="#9db8e0" stroke-width="0.8" opacity="0.4"/>

  <!-- Etiqueta episodio -->
  <text x="700" y="1142"
        font-family="'Helvetica Neue', Helvetica, Arial, sans-serif"
        font-size="28" font-weight="300" letter-spacing="5"
        text-anchor="middle" fill="#9db8e0" opacity="0.85">EPISODIO 5</text>

  <!-- Título en serif -->
  <text x="700" y="1220"
        font-family="Georgia, 'Times New Roman', serif"
        font-size="74"
        text-anchor="middle" fill="#ffffff">Detecci&#xF3;n de fraude</text>
</svg>
</body>
</html>
"""

# Escribe HTML temporal
with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as f:
    f.write(HTML)
    html_path = f.name

print(f"HTML temporal: {html_path}")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1400, "height": 1400})
    page.goto(f"file://{html_path}")
    page.wait_for_timeout(800)   # tiempo para renderizar blur/gradientes
    page.screenshot(path=OUT, clip={"x": 0, "y": 0, "width": 1400, "height": 1400})
    browser.close()

os.unlink(html_path)

img = Image.open(OUT)
print(f"✓  Portada guardada: {OUT}")
print(f"   Dimensiones: {img.width}×{img.height} px")
