#!/usr/bin/env python3
"""
make-library-covers.py

Generates a consistent set of branded 1920x1080 cover images for Jellyfin
(or Plex/Emby) library tiles — a dark, cinematic template with a per-library
icon, title, and accent colour. Original artwork, so no copyright concerns.

Output: one PNG per entry in LIBRARIES, written to ./covers/.

Requires: cairosvg  (pip install cairosvg)
"""

import os
import cairosvg

OUT_DIR = "covers"

# Accent colour pairs (gradient start, gradient end, glow)
AMBER = ("#f5b14c", "#e0892f", "#f5b14c")
CYAN  = ("#4cc9f5", "#2f9fe0", "#4cc9f5")

# Icon glyphs, drawn around the emblem centre. Use url(#accent) so each
# library's accent colour is applied automatically.
ICONS = {
    "film": '''<g><rect x="-60" y="-60" width="120" height="80" rx="10" fill="url(#accent)"/><rect x="-42" y="-48" width="84" height="56" rx="4" fill="#11151f"/>
        <g fill="#11151f"><rect x="-56" y="-54" width="10" height="9" rx="2"/><rect x="-56" y="-39" width="10" height="9" rx="2"/><rect x="-56" y="-24" width="10" height="9" rx="2"/><rect x="-56" y="-9" width="10" height="9" rx="2"/>
        <rect x="46" y="-54" width="10" height="9" rx="2"/><rect x="46" y="-39" width="10" height="9" rx="2"/><rect x="46" y="-24" width="10" height="9" rx="2"/><rect x="46" y="-9" width="10" height="9" rx="2"/></g></g>''',
    "tv": '''<g><rect x="-60" y="-62" width="120" height="78" rx="12" fill="url(#accent)"/><rect x="-46" y="-50" width="92" height="54" rx="5" fill="#11151f"/>
        <rect x="-30" y="20" width="60" height="7" rx="3.5" fill="url(#accent)"/><rect x="-14" y="14" width="28" height="9" fill="url(#accent)"/></g>''',
    "star": '''<g fill="url(#accent)"><path d="M0,-66 C7,-22 22,-7 64,0 C22,7 7,22 0,66 C-7,22 -22,7 -64,0 C-22,-7 -7,-22 0,-66 Z"/><circle cx="40" cy="-40" r="6"/><circle cx="-44" cy="34" r="4"/></g>''',
    "boltcircle": '''<g><circle cx="0" cy="-22" r="60" fill="none" stroke="url(#accent)" stroke-width="9"/><path d="M 10,-58 L -24,-10 L -2,-10 L -12,16 L 26,-30 L 2,-30 Z" fill="url(#accent)"/></g>''',
    "boltbox": '''<g><rect x="-60" y="-64" width="120" height="84" rx="12" fill="none" stroke="url(#accent)" stroke-width="9"/><path d="M 10,-50 L -22,-4 L -2,-4 L -12,20 L 24,-22 L 2,-22 Z" fill="url(#accent)"/></g>''',
    "play": '''<g><circle cx="0" cy="-20" r="58" fill="none" stroke="url(#accent)" stroke-width="9"/><path d="M -22 -48 L 30 -20 L -22 8 Z" fill="url(#accent)"/></g>''',
}

# (slug, TITLE, subtitle, accent, icon, title_size, letter_spacing, underline_x, underline_w)
LIBRARIES = [
    ("collections",    "COLLECTIONS",    "CURATED · ORGANIZED · YOURS", AMBER, "play",       118, 14, 860, 200),
    ("movies",         "MOVIES",         "FILMS · EVERY GENRE",         AMBER, "film",       96,  16, 760, 400),
    ("shows",          "SHOWS",          "SERIES · BINGE READY",        AMBER, "tv",         96,  18, 770, 380),
    ("anime",          "ANIME",          "SUB · DUB · OST",             AMBER, "star",       96,  22, 790, 340),
    ("instant-movies", "INSTANT MOVIES", "STREAM · INSTANT PLAY",       CYAN,  "boltcircle", 82,  12, 800, 320),
    ("instant-shows",  "INSTANT SHOWS",  "STREAM · INSTANT SERIES",     CYAN,  "boltbox",    82,  12, 800, 320),
]

TEMPLATE = '''<svg width="1920" height="1080" viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#11151f"/><stop offset="0.55" stop-color="#0c0f17"/><stop offset="1" stop-color="#070910"/>
    </linearGradient>
    <linearGradient id="card" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2a3142"/><stop offset="1" stop-color="#171b27"/>
    </linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="__A1__"/><stop offset="1" stop-color="__A2__"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.42" r="0.6">
      <stop offset="0" stop-color="__GLOW__" stop-opacity="0.16"/><stop offset="1" stop-color="__GLOW__" stop-opacity="0"/>
    </radialGradient>
    <filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6"/></filter>
  </defs>
  <rect width="1920" height="1080" fill="url(#bg)"/>
  <rect width="1920" height="1080" fill="url(#glow)"/>
  <g transform="translate(960,470)" opacity="0.92">
    <g transform="translate(-360,40) rotate(-13)"><rect x="-150" y="-225" width="300" height="450" rx="16" fill="url(#card)" filter="url(#soft)" opacity="0.65"/></g>
    <g transform="translate(360,40) rotate(13)"><rect x="-150" y="-225" width="300" height="450" rx="16" fill="url(#card)" filter="url(#soft)" opacity="0.65"/></g>
    <g transform="translate(-190,18) rotate(-6)"><rect x="-155" y="-235" width="310" height="470" rx="18" fill="url(#card)" filter="url(#soft)" opacity="0.85"/></g>
    <g transform="translate(190,18) rotate(6)"><rect x="-155" y="-235" width="310" height="470" rx="18" fill="url(#card)" filter="url(#soft)" opacity="0.85"/></g>
    <g>
      <rect x="-170" y="-258" width="340" height="516" rx="20" fill="url(#card)"/>
      <rect x="-170" y="-258" width="340" height="86" rx="20" fill="#000000" opacity="0.18"/>
      __ICON__
    </g>
  </g>
  <text x="960" y="852" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-size="__TS__" font-weight="700" fill="#f4f6fb" letter-spacing="__LS__">__TITLE__</text>
  <rect x="__UX__" y="902" width="__UW__" height="6" rx="3" fill="url(#accent)"/>
  <text x="960" y="966" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-size="34" font-weight="400" fill="#9aa3b5" letter-spacing="8">__SUB__</text>
</svg>'''


def build(slug, title, sub, acc, icon, ts, ls, ux, uw):
    svg = (TEMPLATE
           .replace("__A1__", acc[0]).replace("__A2__", acc[1]).replace("__GLOW__", acc[2])
           .replace("__ICON__", ICONS[icon]).replace("__TITLE__", title).replace("__SUB__", sub)
           .replace("__TS__", str(ts)).replace("__LS__", str(ls))
           .replace("__UX__", str(ux)).replace("__UW__", str(uw)))
    cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(OUT_DIR, f"{slug}.png"),
                     output_width=1920, output_height=1080)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for lib in LIBRARIES:
        build(*lib)
        print(f"wrote {OUT_DIR}/{lib[0]}.png")


if __name__ == "__main__":
    main()
