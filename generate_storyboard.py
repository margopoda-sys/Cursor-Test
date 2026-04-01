#!/usr/bin/env python3
"""Generate Astra Inc. SD-WAN Outage 4-panel cinematic storyboard.
Output: storyboard.svg  (3840 × 2560 px, print-ready 8K)
"""
import math

# ── Layout ─────────────────────────────────────────────────────────────────
W, H   = 3840, 2560
PW, PH = 1840, 1035      # each panel ≈ 16:9
M      = 60              # outer / inter-column margin
TH     = 130             # title strip height
RH     = 90              # row gap / caption height

# panel top-left corners
P = [
    (M,          TH),             # 1 – global overview
    (M + PW + M, TH),             # 2 – SD-WAN outage
    (M,          TH + PH + RH),   # 3 – alert flood
    (M + PW + M, TH + PH + RH),   # 4 – the challenge
]

# ── Palette ────────────────────────────────────────────────────────────────
BG   = "#070E1A"
NV1  = "#0D1B2A"
NV2  = "#1A2B45"
NV3  = "#243554"
NV4  = "#0A2540"
BE   = "#0EA5E9"    # electric blue
BB   = "#38BDF8"    # bright blue
BL2  = "#7DD3FC"    # light glow blue
RC   = "#EF4444"    # critical red
RD   = "#7F1D1D"    # dark red
OW   = "#F97316"    # orange warning
AMB  = "#F59E0B"    # amber / yellow
GRN  = "#22C55E"    # green ok
WHT  = "#FFFFFF"
LGR  = "#CBD5E1"    # light gray
MGR  = "#64748B"    # mid gray
DGR  = "#1E293B"    # dark gray / card bg

FONT = "Inter,'Segoe UI',Helvetica,Arial,sans-serif"

# ── SVG helpers ────────────────────────────────────────────────────────────

def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def tag(name, content="", **attrs):
    parts = []
    for k, v in attrs.items():
        k2 = k.replace("_", "-").replace("__", ":")
        parts.append(f'{k2}="{v}"')
    a = (" " + " ".join(parts)) if parts else ""
    if content == "":
        return f"<{name}{a}/>"
    return f"<{name}{a}>{content}</{name}>"

def rect(x, y, w, h, fill, rx=0, **kw):
    return tag("rect", x=x, y=y, width=w, height=h, fill=fill, rx=rx, **kw)

def circ(cx, cy, r, fill, **kw):
    return tag("circle", cx=cx, cy=cy, r=r, fill=fill, **kw)

def line(x1, y1, x2, y2, stroke, **kw):
    return tag("line", x1=x1, y1=y1, x2=x2, y2=y2, stroke=stroke, **kw)

def txt(x, y, s, sz, fill=WHT, anchor="middle", **kw):
    kw.setdefault("font_family", FONT)
    return tag("text", esc(s), x=x, y=y, font_size=sz, fill=fill,
               text_anchor=anchor, **kw)

def path(d, fill="none", stroke="none", **kw):
    return tag("path", d=d, fill=fill, stroke=stroke, **kw)

def group(content, **kw):
    return tag("g", content, **kw)

def clip_group(clip_id, content, **kw):
    return tag("g", content, clip_path=f"url(#{clip_id})", **kw)

# ── Defs (gradients, filters, clip paths) ─────────────────────────────────

def make_defs():
    d = "<defs>"

    # radial glow filter
    d += """<filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="8" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>"""

    d += """<filter id="glow-sm" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="4" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>"""

    d += """<filter id="blur-bg" x="-10%" y="-10%" width="120%" height="120%">
      <feGaussianBlur stdDeviation="18"/>
    </filter>"""

    d += """<filter id="blur-light" x="-10%" y="-10%" width="120%" height="120%">
      <feGaussianBlur stdDeviation="40"/>
    </filter>"""

    d += """<filter id="drop-shadow">
      <feDropShadow dx="0" dy="4" stdDeviation="12" flood-color="#000" flood-opacity="0.6"/>
    </filter>"""

    # gradient: electric blue radial (globe glow)
    d += """<radialGradient id="globe-glow" cx="50%" cy="50%" r="60%">
      <stop offset="0%" stop-color="#0EA5E9" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="#070E1A" stop-opacity="0"/>
    </radialGradient>"""

    # gradient: red outage glow
    d += """<radialGradient id="red-glow" cx="50%" cy="50%" r="60%">
      <stop offset="0%" stop-color="#EF4444" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#070E1A" stop-opacity="0"/>
    </radialGradient>"""

    # gradient: spotlight beam
    d += """<linearGradient id="spotlight" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8" stop-opacity="0.55"/>
      <stop offset="100%" stop-color="#38BDF8" stop-opacity="0"/>
    </linearGradient>"""

    # gradient: panel 1 ambient
    d += f"""<linearGradient id="p1-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{NV4}"/>
      <stop offset="100%" stop-color="{BG}"/>
    </linearGradient>"""

    # gradient: panel 2 red tint
    d += f"""<linearGradient id="p2-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{NV1}"/>
      <stop offset="100%" stop-color="#1A0808"/>
    </linearGradient>"""

    # gradient: panel 4 dark
    d += f"""<linearGradient id="p4-bg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#050B14"/>
      <stop offset="100%" stop-color="#020508"/>
    </linearGradient>"""

    # gradient: node active
    d += f"""<radialGradient id="node-active" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{BB}"/>
      <stop offset="100%" stop-color="{BE}"/>
    </radialGradient>"""

    # gradient: node critical
    d += f"""<radialGradient id="node-crit" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#F87171"/>
      <stop offset="100%" stop-color="{RC}"/>
    </radialGradient>"""

    # clip paths for panels
    for i, (px, py) in enumerate(P):
        d += f'<clipPath id="clip{i+1}"><rect x="{px}" y="{py}" width="{PW}" height="{PH}"/></clipPath>'

    d += "</defs>"
    return d


# ── Continent shapes (simplified, Mercator-like coords) ───────────────────
# Each shape: list of (lon, lat) pairs

CONTINENTS = {
    "north_america": [
        (-168, 72), (-140, 72), (-110, 60), (-85, 48), (-70, 46),
        (-60, 44), (-65, 25), (-80, 22), (-90, 18), (-95, 20),
        (-110, 22), (-120, 28), (-132, 35), (-140, 48), (-158, 58), (-168, 68),
    ],
    "south_america": [
        (-80, 12), (-68, 8), (-52, 6), (-40, -4), (-36, -12),
        (-38, -24), (-48, -32), (-58, -40), (-68, -56),
        (-74, -48), (-78, -34), (-80, -18), (-82, 0), (-80, 12),
    ],
    "europe": [
        (-10, 36), (0, 36), (12, 38), (28, 38), (35, 42),
        (32, 50), (22, 52), (10, 58), (0, 58), (-10, 48), (-10, 36),
    ],
    "africa": [
        (-18, 36), (50, 36), (58, 18), (52, 4), (44, 10),
        (40, -2), (50, -20), (36, -36), (22, -36),
        (16, -28), (8, -6), (-4, 6), (-18, 16), (-18, 36),
    ],
    "asia": [
        (28, 72), (80, 78), (140, 72), (148, 56), (148, 34),
        (122, 18), (108, 10), (82, 10), (62, 16), (44, 10),
        (38, 22), (28, 38), (28, 52), (28, 72),
    ],
    "australia": [
        (116, -20), (138, -14), (152, -24), (152, -38),
        (138, -40), (124, -36), (116, -28), (116, -20),
    ],
}

def lon_lat_to_svg(lon, lat, ox, oy, pw, ph, scale=0.82, off_x=0.0, off_y=0.05):
    """Mercator-projection lon/lat → SVG coords relative to panel origin."""
    x = (lon + 180) / 360.0
    # Mercator lat
    lat_r = math.radians(max(-85, min(85, lat)))
    merc  = math.log(math.tan(math.pi / 4 + lat_r / 2))
    y     = 0.5 - merc / (2 * math.pi)
    # scale & center
    cx, cy = 0.50 + off_x, 0.48 + off_y
    x2 = cx + (x - 0.5) * scale
    y2 = cy + (y - 0.5) * scale
    return ox + x2 * pw, oy + y2 * ph

def continent_path(name, shape, ox, oy, fill, opacity=1.0):
    pts = [lon_lat_to_svg(lo, la, ox, oy, PW, PH) for lo, la in shape]
    d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"
    return path(d, fill=fill, stroke=BE, stroke_width="1.5",
                stroke_opacity="0.5", opacity=str(opacity))

# ── Grid lines helper ──────────────────────────────────────────────────────

def grid_lines(ox, oy, cols=24, rows=14, stroke=NV3, opacity="0.4"):
    lines = []
    for i in range(cols + 1):
        x = ox + i * PW / cols
        lines.append(line(x, oy, x, oy + PH, stroke,
                          stroke_width="0.8", opacity=opacity))
    for j in range(rows + 1):
        y = oy + j * PH / rows
        lines.append(line(ox, y, ox + PW, y, stroke,
                          stroke_width="0.8", opacity=opacity))
    return "".join(lines)

# ── Store location nodes ───────────────────────────────────────────────────

STORE_LOCS = [
    # (lon, lat, label)
    (-74, 40.7, "NYC"),     (-118, 34, "LA"),     (-87, 41.8, "CHI"),
    (-80, 25.8, "MIA"),     (-0.1, 51.5, "LON"),  (2.3, 48.8, "PAR"),
    (13.4, 52.5, "BER"),    (28.9, 41, "IST"),    (55.3, 25.2, "DXB"),
    (72.8, 18.9, "BOM"),    (77, 28.6, "DEL"),    (103.8, 1.3, "SGP"),
    (121.4, 31.2, "SHA"),   (139.7, 35.7, "TYO"), (-43.1, -22.9, "RIO"),
    (-58.4, -34.6, "BUE"),  (18.4, -33.9, "CPT"), (37.6, 55.7, "MOW"),
    (116.4, 39.9, "BEJ"),   (151.2, -33.9, "SYD"),
    (-99.1, 19.4, "MEX"),   (-79.4, 43.6, "TOR"), (4.9, 52.4, "AMS"),
]

# ── Panel 1: Global Overview ───────────────────────────────────────────────

def panel1():
    ox, oy = P[0]
    parts = []

    # Background
    parts.append(rect(ox, oy, PW, PH, "url(#p1-bg)"))

    # subtle grid
    parts.append(grid_lines(ox, oy, 28, 16, NV3, "0.3"))

    # Globe glow blob
    parts.append(rect(ox, oy, PW, PH, "url(#globe-glow)"))

    # Continent fills
    for name, shape in CONTINENTS.items():
        parts.append(continent_path(name, shape, ox, oy, NV2, 0.85))

    # Lat/Lon lines (subtle)
    for lat in [-60, -30, 0, 30, 60]:
        y = lon_lat_to_svg(0, lat, ox, oy, PW, PH)[1]
        parts.append(line(ox, y, ox + PW, y, NV3, stroke_width="1",
                          stroke_dasharray="8,8", opacity="0.35"))
    for lon in [-120, -60, 0, 60, 120]:
        x = lon_lat_to_svg(lon, 0, ox, oy, PW, PH)[0]
        parts.append(line(x, oy, x, oy + PH, NV3, stroke_width="1",
                          stroke_dasharray="8,8", opacity="0.35"))

    # Connection lines between store nodes
    store_xy = [lon_lat_to_svg(lo, la, ox, oy, PW, PH) for lo, la, _ in STORE_LOCS]

    # Hub connections (to NYC as central hub)
    hub_x, hub_y = store_xy[0]
    connections = [(0,4),(0,6),(0,14),(0,20),(4,5),(4,6),(5,7),(7,8),(8,9),
                   (9,11),(11,12),(12,13),(13,19),(3,14),(14,15),(2,1),(1,20)]
    for a, b in connections:
        ax, ay = store_xy[a]
        bx, by = store_xy[b]
        mx, my = (ax+bx)/2, (ay+by)/2 - 40
        d = f"M {ax:.1f} {ay:.1f} Q {mx:.1f} {my:.1f} {bx:.1f} {by:.1f}"
        parts.append(path(d, stroke=BE, stroke_width="1.5",
                          stroke_opacity="0.4", stroke_dasharray="none"))
        # glow pass
        parts.append(path(d, stroke=BB, stroke_width="0.8",
                          stroke_opacity="0.25"))

    # Store location dots
    for i, (lo, la, label) in enumerate(STORE_LOCS):
        sx, sy = store_xy[i]
        r_size = 10 if i < 4 else 7
        # outer glow
        parts.append(circ(sx, sy, r_size + 8, BE, opacity="0.15",
                          filter="url(#blur-bg)"))
        parts.append(circ(sx, sy, r_size + 4, BE, opacity="0.2"))
        # main dot
        parts.append(circ(sx, sy, r_size, "url(#node-active)"))
        parts.append(circ(sx, sy, r_size - 3, WHT, opacity="0.8"))
        # label
        if i < 8:
            loff = -16 if sy > oy + PH * 0.5 else 18
            parts.append(txt(sx, sy + loff, label, 22, BL2,
                             font_weight="600"))

    # "Astra Inc." header bar (top of panel)
    parts.append(rect(ox, oy, PW, 85, NV1, opacity="0.85"))
    # Logo diamond
    ldx, ldy = ox + 48, oy + 42
    parts.append(path(
        f"M {ldx},{ldy-22} L {ldx+18},{ldy} L {ldx},{ldy+22} L {ldx-18},{ldy} Z",
        fill=BE))
    parts.append(path(
        f"M {ldx},{ldy-12} L {ldx+10},{ldy} L {ldx},{ldy+12} L {ldx-10},{ldy} Z",
        fill=WHT))
    parts.append(txt(ox + 80, oy + 52, "Astra Inc.", 40, WHT,
                     anchor="start", font_weight="700", letter_spacing="2"))
    parts.append(txt(ox + PW - 28, oy + 38, "GLOBAL OPERATIONS", 20, BL2,
                     anchor="end", font_weight="600", letter_spacing="3",
                     opacity="0.85"))
    parts.append(txt(ox + PW - 28, oy + 62, "24 Countries  ·  847 Stores  ·  12,500 Employees",
                     22, MGR, anchor="end"))

    # Icon strip – digital commerce & store icons (bottom bar)
    bar_y = oy + PH - 75
    parts.append(rect(ox, bar_y, PW, 75, NV1, opacity="0.80"))

    # Shopping cart icon x3
    for xi, (label_txt, val) in enumerate([
        ("Daily Transactions", "2.4M"),
        ("GMV Online", "$48M"),
        ("In-Store Revenue", "$22M"),
    ]):
        bx = ox + 180 + xi * 580
        # small cart icon
        parts.append(path(
            f"M {bx-44},{bar_y+26} L {bx-38},{bar_y+26} L {bx-32},{bar_y+46} "
            f"L {bx+4},{bar_y+46} L {bx+8},{bar_y+32} L {bx-34},{bar_y+32}",
            stroke=BE, stroke_width="3", stroke_linejoin="round"))
        parts.append(circ(bx - 26, bar_y + 54, 5, BE))
        parts.append(circ(bx - 2, bar_y + 54, 5, BE))
        parts.append(txt(bx + 20, bar_y + 33, label_txt, 20, MGR, anchor="start"))
        parts.append(txt(bx + 20, bar_y + 56, val, 26, WHT, anchor="start",
                         font_weight="700"))

    # Status indicator
    parts.append(circ(ox + PW - 46, bar_y + 38, 10, GRN))
    parts.append(circ(ox + PW - 46, bar_y + 38, 7, GRN, opacity="0.5",
                      filter="url(#glow-sm)"))
    parts.append(txt(ox + PW - 60, bar_y + 42, "ALL SYSTEMS OPERATIONAL", 20,
                     GRN, anchor="end", font_weight="600"))

    return clip_group("clip1", "".join(parts))


# ── Panel 2: SD-WAN Outage ─────────────────────────────────────────────────

def panel2():
    ox, oy = P[1]
    parts = []

    # Background
    parts.append(rect(ox, oy, PW, PH, "url(#p2-bg)"))
    parts.append(grid_lines(ox, oy, 28, 16, NV3, "0.25"))

    # Red glow bloom at center-right
    cx_g, cy_g = ox + PW * 0.55, oy + PH * 0.5
    parts.append(rect(ox, oy, PW, PH, "url(#red-glow)"))

    # ── Network Topology ──────────────────────────────────────────────────
    # Hub: central Meraki SD-WAN controller
    hx, hy = ox + PW * 0.52, oy + PH * 0.50

    # Spoke nodes
    nodes = []
    node_labels = ["NYC HQ", "LA Hub", "EU Core", "APAC Hub",
                   "MIA DC", "CHI Branch", "DAL Store", "SEA Store"]
    angles = [300, 30, 80, 140, 200, 240, 275, 320]  # degrees
    dists  = [260, 280, 300, 290, 270, 310, 220, 260]
    crit_nodes = {0, 2, 4}   # severed by outage

    for i, (ang, dist, lbl) in enumerate(zip(angles, dists, node_labels)):
        rad = math.radians(ang)
        nx = hx + dist * math.cos(rad)
        ny = hy + dist * math.sin(rad)
        nodes.append((nx, ny, lbl, i in crit_nodes))

    # Draw connection lines first
    for i, (nx, ny, lbl, is_crit) in enumerate(nodes):
        if is_crit:
            # broken line – draw two segments with a gap at fracture
            fx = (hx + nx) / 2 + (ny - hy) * 0.08
            fy = (hy + ny) / 2 - (nx - hx) * 0.08
            # segment hub → fracture
            parts.append(line(hx, hy, fx - 18, fy - 18, RC,
                              stroke_width="3", stroke_dasharray="12,4"))
            parts.append(line(hx, hy, fx - 18, fy - 18, "#F87171",
                              stroke_width="1.5", opacity="0.4"))
            # segment fracture → node (darker, fading)
            parts.append(line(fx + 18, fy + 18, nx, ny, RD,
                              stroke_width="3", stroke_dasharray="6,8",
                              opacity="0.6"))
            # Fracture spark mark
            fw, fh = 22, 22
            parts.append(path(
                f"M {fx-fw},{fy} L {fx},{fy-fh} L {fx+fw*0.3},{fy-fh*0.3} "
                f"L {fx+fw},{fy} L {fx},{fy+fh} L {fx-fw*0.3},{fy+fh*0.3} Z",
                fill=RC, opacity="0.9", filter="url(#glow-sm)"))
        else:
            # healthy – dim blue connection
            parts.append(line(hx, hy, nx, ny, BE, stroke_width="2",
                              opacity="0.35"))
            parts.append(line(hx, hy, nx, ny, BB, stroke_width="1",
                              opacity="0.2"))

    # Draw spoke nodes
    for nx, ny, lbl, is_crit in nodes:
        if is_crit:
            # Red warning node
            parts.append(circ(nx, ny, 30, RD, opacity="0.5",
                              filter="url(#blur-bg)"))
            parts.append(circ(nx, ny, 22, "url(#node-crit)"))
            parts.append(circ(nx, ny, 14, "#FCA5A5"))
            # Warning triangle
            tw = 18
            parts.append(path(
                f"M {nx},{ny-tw-4} L {nx+tw},{ny+tw-4} L {nx-tw},{ny+tw-4} Z",
                fill=AMB, opacity="0.0"))
            # X mark
            parts.append(line(nx - 8, ny - 8, nx + 8, ny + 8, WHT,
                              stroke_width="3", stroke_linecap="round"))
            parts.append(line(nx + 8, ny - 8, nx - 8, ny + 8, WHT,
                              stroke_width="3", stroke_linecap="round"))
        else:
            parts.append(circ(nx, ny, 20, NV2))
            parts.append(circ(nx, ny, 14, "url(#node-active)"))
            parts.append(circ(nx, ny, 7, WHT, opacity="0.9"))

        # Node label
        ly = ny + (38 if ny > hy else -28)
        parts.append(txt(nx, ly, lbl, 22, LGR if not is_crit else "#FCA5A5",
                         font_weight="600"))

    # Hub node (critical)
    parts.append(circ(hx, hy, 50, RC, opacity="0.25",
                      filter="url(#blur-light)"))
    parts.append(circ(hx, hy, 42, RC, opacity="0.3"))
    parts.append(circ(hx, hy, 34, RD))
    parts.append(circ(hx, hy, 26, RC))
    # X on hub
    for d in [(-14, -14, 14, 14), (14, -14, -14, 14)]:
        parts.append(line(hx+d[0], hy+d[1], hx+d[2], hy+d[3], WHT,
                          stroke_width="5", stroke_linecap="round"))

    # Hub label
    parts.append(rect(hx - 70, hy + 42, 140, 30, RD, rx=6))
    parts.append(txt(hx, hy + 63, "SD-WAN CORE", 20, WHT,
                     font_weight="700"))

    # Meraki device panel (top-right)
    mpx, mpy = ox + PW - 360, oy + 28
    parts.append(rect(mpx, mpy, 340, 210, DGR, rx=10, opacity="0.9",
                      filter="url(#drop-shadow)"))
    parts.append(rect(mpx, mpy, 340, 40, NV3, rx="10 10 0 0"))
    parts.append(txt(mpx + 170, mpy + 26, "MERAKI DEVICE STATUS", 18, LGR,
                     font_weight="600"))
    dev_names = ["MX-Core-01", "MX-Core-02", "MS-480-01", "MR-46-Floor3",
                 "MX-Branch-NY"]
    dev_states = [("OFFLINE", RC), ("OFFLINE", RC), ("WARNING", OW),
                  ("WARNING", OW), ("ONLINE", GRN)]
    for di, (dname, (dstate, dcolor)) in enumerate(zip(dev_names, dev_states)):
        dy = mpy + 60 + di * 32
        parts.append(circ(mpx + 22, dy, 8, dcolor))
        if dstate != "ONLINE":
            parts.append(circ(mpx + 22, dy, 14, dcolor, opacity="0.2"))
        parts.append(txt(mpx + 38, dy + 5, dname, 20, LGR, anchor="start"))
        parts.append(txt(mpx + 318, dy + 5, dstate, 20, dcolor, anchor="end",
                         font_weight="700"))

    # POS Terminal silhouettes (bottom)
    for pi in range(7):
        ptx = ox + 60 + pi * 220
        pty = oy + PH - 160
        # monitor
        mon_col = "#0A1628" if pi < 3 else NV2
        scr_col = "#050A10" if pi < 3 else NV3
        parts.append(rect(ptx, pty, 140, 95, mon_col, rx=5))
        parts.append(rect(ptx + 8, pty + 8, 124, 72, scr_col, rx=3))
        if pi < 3:
            # dark screens – offline
            parts.append(rect(ptx + 8, pty + 8, 124, 72, RC, rx=3,
                               opacity="0.08"))
            parts.append(txt(ptx + 70, pty + 52, "NO SIGNAL", 16, RC,
                             font_weight="600", opacity="0.7"))
        else:
            # faint activity remaining
            parts.append(rect(ptx + 14, pty + 18, 80, 8, NV3, rx=2))
            parts.append(rect(ptx + 14, pty + 32, 60, 8, NV3, rx=2))
        # stand
        parts.append(rect(ptx + 60, pty + 95, 20, 20, mon_col))
        parts.append(rect(ptx + 44, pty + 112, 52, 8, mon_col, rx=2))

    # Store-worker silhouettes (helpless) – 3 figures bottom-right
    for wi in range(3):
        wx = ox + PW - 220 + wi * 75
        wy = oy + PH - 60
        # simple person silhouette
        parts.append(circ(wx, wy - 80, 18, MGR))
        parts.append(path(
            f"M {wx},{wy-62} L {wx-16},{wy-10} L {wx-8},{wy} "
            f"L {wx},{wy-20} L {wx+8},{wy} L {wx+16},{wy-10} Z",
            fill=MGR))

    # Critical alert banner (top-left)
    parts.append(rect(ox, oy, PW, 52, RC, opacity="0.9"))
    parts.append(txt(ox + PW // 2, oy + 32,
                     "⚠  CRITICAL: SD-WAN BACKBONE FAILURE — MULTIPLE SITES UNREACHABLE",
                     24, WHT, font_weight="700"))

    # Timestamp
    parts.append(txt(ox + 28, oy + 90, "12:43:07 PM EST", 28, AMB,
                     anchor="start", font_weight="700", font_family="'Courier New', monospace"))
    parts.append(txt(ox + 220, oy + 90, "EVENT DETECTED", 20, MGR,
                     anchor="start"))

    return clip_group("clip2", "".join(parts))


# ── Panel 3: Alert Flood & Revenue Impact ─────────────────────────────────

def panel3():
    ox, oy = P[2]
    parts = []

    # Background
    parts.append(rect(ox, oy, PW, PH, NV1))
    parts.append(grid_lines(ox, oy, 28, 16, NV3, "0.2"))

    # Left sidebar – Meraki device list
    sb_w = 320
    parts.append(rect(ox, oy, sb_w, PH, DGR, opacity="0.95"))
    parts.append(rect(ox, oy, sb_w, 50, NV3))
    parts.append(txt(ox + sb_w // 2, oy + 32, "MERAKI DEVICES", 20, LGR,
                     font_weight="700", letter_spacing="2"))

    dev_scroll = [
        ("MX-Core-01",     RC, "OFFLINE"),
        ("MX-Core-02",     RC, "OFFLINE"),
        ("MS-480-01",      OW, "WARN"),
        ("MR-46-Floor3",   OW, "WARN"),
        ("MX-Branch-NY",   GRN, "OK"),
        ("MX-LA-001",      RC, "OFFLINE"),
        ("MX-MIA-002",     RC, "OFFLINE"),
        ("MS-250-CHI",     OW, "WARN"),
        ("MR-44-CHI-2",    RC, "OFFLINE"),
        ("MX-SEA-003",     OW, "WARN"),
        ("MS-225-ATL",     RC, "OFFLINE"),
        ("MX-DAL-004",     RC, "OFFLINE"),
        ("MR-52-BOS",      GRN, "OK"),
        ("MX-DEN-005",     OW, "WARN"),
        ("MS-350-SF",      RC, "OFFLINE"),
    ]
    for di, (dname, dc, ds) in enumerate(dev_scroll):
        dy = oy + 62 + di * 61
        row_col = "#0F1A28" if di % 2 == 0 else "#111F30"
        parts.append(rect(ox, dy, sb_w, 60, row_col))
        parts.append(rect(ox, dy, 5, 60, dc))  # left accent
        parts.append(circ(ox + 22, dy + 30, 9, dc))
        if ds != "OK":
            parts.append(circ(ox + 22, dy + 30, 16, dc, opacity="0.2"))
        parts.append(txt(ox + 38, dy + 22, dname, 21, LGR, anchor="start",
                         font_weight="600"))
        parts.append(txt(ox + 38, dy + 44, ds, 18, dc, anchor="start",
                         font_weight="700"))
        # mini alert count badge
        if ds != "OK":
            badge_x = ox + sb_w - 20
            badge_n = str(3 + (di * 7) % 18)
            parts.append(circ(badge_x, dy + 30, 16, RC if ds == "OFFLINE" else OW))
            parts.append(txt(badge_x, dy + 35, badge_n, 18, WHT,
                             font_weight="700"))

    # Main content area
    mx = ox + sb_w + 20
    mw = PW - sb_w - 20

    # Revenue impact hero card
    parts.append(rect(mx, oy + 18, mw - 20, 130, DGR, rx=12,
                      filter="url(#drop-shadow)"))
    parts.append(rect(mx, oy + 18, mw - 20, 8, RC, rx="6 6 0 0"))
    parts.append(txt(mx + 24, oy + 60, "PROJECTED REVENUE IMPACT", 24, MGR,
                     anchor="start", font_weight="600", letter_spacing="2"))
    parts.append(txt(mx + 24, oy + 120, "$1,000,000", 72, RC,
                     anchor="start", font_weight="900", letter_spacing="-2"))
    parts.append(txt(mx + mw - 44, oy + 90, "PER HOUR", 22, OW,
                     anchor="end", font_weight="700"))
    parts.append(txt(mx + mw - 44, oy + 118, "847 stores offline", 22, MGR,
                     anchor="end"))

    # Incident ticket feed
    feed_y = oy + 168
    feed_h = PH - 168 - 20
    parts.append(rect(mx, feed_y, mw - 20, feed_h, DGR, rx=10,
                      filter="url(#drop-shadow)"))
    parts.append(rect(mx, feed_y, mw - 20, 44, NV3, rx="8 8 0 0"))
    parts.append(txt(mx + 24, feed_y + 28, "INCIDENT FEED", 22, LGR,
                     anchor="start", font_weight="700", letter_spacing="2"))

    # Alert count badge
    parts.append(rect(mx + mw - 180, feed_y + 8, 140, 28, RC, rx=14))
    parts.append(txt(mx + mw - 110, feed_y + 27, "1,284 ACTIVE", 18, WHT,
                     font_weight="700"))

    tickets = [
        (RC, "P0", "SD-WAN Core Failure – Sites Unreachable", "0m ago"),
        (RC, "P0", "POS Systems Down – Revenue Impact Critical", "1m ago"),
        (RC, "P0", "Meraki MX-Core-01 OFFLINE", "2m ago"),
        (OW, "P1", "MX-LA-001 Connectivity Degraded", "3m ago"),
        (OW, "P1", "Inventory Sync Failure – 847 Stores", "3m ago"),
        (RC, "P0", "MX-MIA-002 OFFLINE – South District", "4m ago"),
        (OW, "P1", "Network Latency >500ms – APAC Region", "5m ago"),
        (AMB, "P2", "Payment Gateway Timeout – Checkout Blocked", "5m ago"),
        (OW, "P1", "MS-480-01 Port Utilization Critical", "6m ago"),
        (AMB, "P2", "DNS Failover Triggered – Monitoring", "7m ago"),
        (RC, "P0", "Store #1148 – Network Loop Detected", "8m ago"),
        (OW, "P1", "BGP Route Flap – AS64512", "9m ago"),
    ]
    for ti, (tc, pri, desc, age) in enumerate(tickets):
        ty = feed_y + 52 + ti * 70
        row_bg = "#0F1A28" if ti % 2 == 0 else "#111F30"
        parts.append(rect(mx, ty, mw - 20, 68, row_bg))
        parts.append(rect(mx, ty, 6, 68, tc))
        # Priority badge
        parts.append(rect(mx + 16, ty + 18, 44, 28, tc, rx=6))
        parts.append(txt(mx + 38, ty + 38, pri, 18, WHT,
                         anchor="middle", font_weight="700"))
        parts.append(txt(mx + 70, ty + 30, desc, 22, LGR,
                         anchor="start", font_weight="500"))
        parts.append(txt(mx + 70, ty + 52, age, 18, MGR, anchor="start"))
        # small alert bell icon
        parts.append(txt(mx + mw - 50, ty + 36, "🔔", 20, tc, anchor="end"))

    # Shopping cart X icons (abandoned carts) – floating top-right area
    for ci in range(4):
        cx2 = mx + mw - 480 + ci * 110
        cy2 = feed_y + 56
        # cart
        parts.append(path(
            f"M {cx2-26},{cy2-14} L {cx2-18},{cy2-14} L {cx2-10},{cy2+10} "
            f"L {cx2+16},{cy2+10} L {cx2+22},{cy2-6} L {cx2-12},{cy2-6}",
            stroke=RC, stroke_width="3", stroke_opacity="0.7",
            stroke_linejoin="round"))
        parts.append(circ(cx2 - 4, cy2 + 18, 5, RC, opacity="0.7"))
        parts.append(circ(cx2 + 12, cy2 + 18, 5, RC, opacity="0.7"))
        # X over cart
        parts.append(line(cx2 - 8, cy2 - 8, cx2 + 8, cy2 + 8, RC,
                          stroke_width="3", opacity="0.8"))
        parts.append(line(cx2 + 8, cy2 - 8, cx2 - 8, cy2 + 8, RC,
                          stroke_width="3", opacity="0.8"))

    # Store silhouettes bottom
    sil_y = oy + PH - 80
    parts.append(rect(ox + sb_w, sil_y, PW - sb_w, 80, NV1, opacity="0.9"))
    for si in range(6):
        sx2 = ox + sb_w + 90 + si * 250
        # storefront silhouette
        parts.append(rect(sx2 - 40, sil_y + 18, 80, 50, NV3, rx=2))
        parts.append(path(
            f"M {sx2-50},{sil_y+18} L {sx2},{sil_y} L {sx2+50},{sil_y+18} Z",
            fill=NV2))
        # dark door
        parts.append(rect(sx2 - 12, sil_y + 36, 24, 32, NV1, rx=2))
        # dark window
        parts.append(rect(sx2 - 36, sil_y + 26, 24, 18, "#050A10", rx=2))
        parts.append(rect(sx2 + 12, sil_y + 26, 24, 18, "#050A10", rx=2))
    parts.append(txt(ox + sb_w + (PW - sb_w) // 2, sil_y + 68,
                     "847 STORES · SYSTEMS DOWN · TRANSACTIONS HALTED",
                     22, RC, font_weight="600", letter_spacing="2",
                     opacity="0.8"))

    return clip_group("clip3", "".join(parts))


# ── Panel 4: The Challenge ─────────────────────────────────────────────────

def panel4():
    ox, oy = P[3]
    parts = []

    # Background – near black
    parts.append(rect(ox, oy, PW, PH, "url(#p4-bg)"))

    # Noise wall – dense grid of tiny alert text (background layer)
    noise_items = [
        "MX-Core-01 OFFLINE", "BGP Flap AS64512", "POS #1148 DOWN",
        "Latency 840ms", "P0 INCIDENT", "SD-WAN FAILURE",
        "Revenue -$12k/min", "MR-46 OFFLINE", "Store #0892 Dark",
        "DNS Timeout", "VPN Tunnel Down", "Port Flap MS-480",
        "CRITICAL ALERT", "847 Sites Affected", "Packet Loss 72%",
        "QoS Policy Failed", "WAN Failover", "Auth Timeout",
        "Checkout Error", "BGP Reset", "Link Down", "Jitter >200ms",
    ]
    cols_noise, rows_noise = 7, 18
    for ri in range(rows_noise):
        for ci in range(cols_noise):
            ni = (ri * cols_noise + ci) % len(noise_items)
            nx2 = ox + 40 + ci * (PW - 80) // cols_noise
            ny2 = oy + 28 + ri * (PH - 56) // rows_noise
            alpha = 0.06 + (ri + ci) % 4 * 0.04
            nc = RC if (ri + ci) % 5 == 0 else OW if (ri + ci) % 3 == 0 else MGR
            parts.append(txt(nx2, ny2, noise_items[ni], 20, nc,
                             anchor="start", opacity=str(round(alpha, 2))))

    # Spotlight cone from top-center
    scx = ox + PW * 0.5
    parts.append(path(
        f"M {scx-30},{oy} L {scx+30},{oy} "
        f"L {scx+220},{oy+PH*0.70} L {scx-220},{oy+PH*0.70} Z",
        fill="url(#spotlight)", opacity="0.6"))

    # bright core of spotlight
    parts.append(path(
        f"M {scx-12},{oy} L {scx+12},{oy} "
        f"L {scx+90},{oy+PH*0.70} L {scx-90},{oy+PH*0.70} Z",
        fill="url(#spotlight)", opacity="0.5"))

    # Magnifying glass circle at spotlight focal point
    mgx, mgy = scx, oy + int(PH * 0.43)
    mg_r = 130
    parts.append(circ(mgx, mgy, mg_r + 18, BB, opacity="0.08",
                      filter="url(#blur-bg)"))
    parts.append(circ(mgx, mgy, mg_r, "none", stroke=BB, stroke_width="6",
                      filter="url(#glow-sm)"))
    parts.append(circ(mgx, mgy, mg_r, "none", stroke=BL2, stroke_width="2",
                      opacity="0.5"))
    # Handle
    parts.append(line(mgx + mg_r * 0.70, mgy + mg_r * 0.70,
                      mgx + mg_r * 0.70 + 70, mgy + mg_r * 0.70 + 70,
                      BB, stroke_width="10", stroke_linecap="round",
                      filter="url(#glow-sm)"))
    parts.append(line(mgx + mg_r * 0.70, mgy + mg_r * 0.70,
                      mgx + mg_r * 0.70 + 70, mgy + mg_r * 0.70 + 70,
                      BL2, stroke_width="4", stroke_linecap="round"))

    # Inside magnifying glass: isolated clean signal
    parts.append(circ(mgx, mgy, mg_r, NV4, opacity="0.55"))
    # a single clean alert card inside the lens
    parts.append(rect(mgx - 90, mgy - 36, 180, 72, NV3, rx=8, opacity="0.9"))
    parts.append(rect(mgx - 90, mgy - 36, 8, 72, RC, rx="4 0 0 4"))
    parts.append(txt(mgx, mgy - 14, "ROOT CAUSE", 18, RC,
                     font_weight="700", letter_spacing="2"))
    parts.append(txt(mgx, mgy + 12, "MX-Core-01", 24, WHT,
                     font_weight="700"))
    parts.append(txt(mgx, mgy + 32, "SD-WAN CONTROLLER", 16, BL2))

    # Analyst silhouette (foreground, center-bottom)
    ax, ay = int(scx), oy + PH - 30
    # head
    parts.append(circ(ax, ay - 155, 30, LGR, opacity="0.6"))
    # body
    parts.append(path(
        f"M {ax},{ay-125} L {ax-44},{ay-52} L {ax-28},{ay-38} "
        f"L {ax-18},{ay-70} L {ax},{ay-48} "
        f"L {ax+18},{ay-70} L {ax+28},{ay-38} L {ax+44},{ay-52} Z",
        fill=LGR, opacity="0.6"))
    # legs
    parts.append(path(
        f"M {ax-18},{ay-48} L {ax-26},{ay} M {ax+18},{ay-48} L {ax+26},{ay}",
        stroke=LGR, stroke_width="24", stroke_linecap="round",
        stroke_opacity="0.55"))

    # Clock (urgency) – top-right of panel
    ckx, cky = ox + PW - 120, oy + 120
    ck_r = 80
    parts.append(circ(ckx, cky, ck_r + 6, NV3, opacity="0.5"))
    parts.append(circ(ckx, cky, ck_r, DGR))
    parts.append(circ(ckx, cky, ck_r, "none", stroke=NV3, stroke_width="3"))
    # tick marks
    for ti in range(12):
        ang = math.radians(ti * 30)
        r1 = ck_r - 6
        r2 = ck_r - (16 if ti % 3 == 0 else 10)
        parts.append(line(
            ckx + r1 * math.sin(ang), cky - r1 * math.cos(ang),
            ckx + r2 * math.sin(ang), cky - r2 * math.cos(ang),
            LGR, stroke_width="3" if ti % 3 == 0 else "1.5"))
    # hour hand ~at 12:43 → hour at ~25° past 12
    parts.append(line(ckx, cky,
                      ckx + 38 * math.sin(math.radians(13)),
                      cky - 38 * math.cos(math.radians(13)),
                      WHT, stroke_width="5", stroke_linecap="round"))
    # minute hand ~43 min → 258°
    parts.append(line(ckx, cky,
                      ckx + 60 * math.sin(math.radians(258)),
                      cky - 60 * math.cos(math.radians(258)),
                      BB, stroke_width="4", stroke_linecap="round",
                      filter="url(#glow-sm)"))
    # center dot
    parts.append(circ(ckx, cky, 6, WHT))
    parts.append(txt(ckx, cky + ck_r + 22, "12:43 PM", 20, AMB,
                     font_weight="700"))
    parts.append(txt(ckx, cky + ck_r + 42, "T+0:00 ELAPSED", 16, MGR))

    # Stat counters top-left
    parts.append(rect(ox + 24, oy + 24, 260, 80, DGR, rx=10, opacity="0.85"))
    parts.append(txt(ox + 36, oy + 52, "847", 42, RC, anchor="start",
                     font_weight="900"))
    parts.append(txt(ox + 36, oy + 76, "Stores Affected", 20, MGR,
                     anchor="start"))
    parts.append(rect(ox + 24, oy + 120, 260, 80, DGR, rx=10, opacity="0.85"))
    parts.append(txt(ox + 36, oy + 148, "1,284", 42, OW, anchor="start",
                     font_weight="900"))
    parts.append(txt(ox + 36, oy + 172, "Active Alerts", 20, MGR,
                     anchor="start"))

    # hero question text
    qy = oy + PH - 130
    parts.append(rect(ox, qy, PW, 130, BG, opacity="0.88"))
    parts.append(txt(ox + PW // 2, qy + 56,
                     "847 Stores. 1,284 Alerts.", 46, WHT,
                     font_weight="800"))
    parts.append(txt(ox + PW // 2, qy + 106,
                     "Where is the signal in the noise?", 38, BL2,
                     font_weight="400", font_style="italic"))

    return clip_group("clip4", "".join(parts))


# ── Outer chrome (title bar, panel labels, global BG) ─────────────────────

def outer_chrome():
    parts = []

    # Global background
    parts.append(rect(0, 0, W, H, BG))

    # Subtle outer grid
    for i in range(0, W, 80):
        parts.append(line(i, 0, i, H, NV1, stroke_width="1", opacity="0.4"))
    for j in range(0, H, 80):
        parts.append(line(0, j, W, j, NV1, stroke_width="1", opacity="0.4"))

    # Title strip
    parts.append(rect(0, 0, W, TH, NV1))
    parts.append(rect(0, TH - 2, W, 2, BE, opacity="0.6"))

    # Logo diamond (small)
    ldx, ldy = 54, TH // 2
    parts.append(path(
        f"M {ldx},{ldy-20} L {ldx+16},{ldy} L {ldx},{ldy+20} L {ldx-16},{ldy} Z",
        fill=BE))
    parts.append(path(
        f"M {ldx},{ldy-11} L {ldx+9},{ldy} L {ldx},{ldy+11} L {ldx-9},{ldy} Z",
        fill=WHT))

    parts.append(txt(84, TH // 2 + 6, "Astra Inc.", 36, WHT,
                     anchor="start", font_weight="700", letter_spacing="2"))
    parts.append(txt(W // 2, TH // 2 + 6,
                     "SD-WAN OUTAGE · INCIDENT STORYBOARD", 30, LGR,
                     font_weight="600", letter_spacing="4"))
    parts.append(txt(W - M, TH // 2 - 8, "CONFIDENTIAL · INTERNAL USE ONLY",
                     20, MGR, anchor="end", letter_spacing="3"))
    parts.append(txt(W - M, TH // 2 + 18, "April 1, 2026  ·  PANEL SEQUENCE A",
                     20, MGR, anchor="end"))

    # Panel border frames
    for i, (px2, py2) in enumerate(P):
        # outer glow border
        parts.append(rect(px2 - 3, py2 - 3, PW + 6, PH + 6,
                          "none", rx=4, stroke=NV3, stroke_width="2"))
        # inner highlight on top
        parts.append(rect(px2, py2, PW, 3, BE, opacity="0.5"))

    # Panel captions (below each panel)
    captions = [
        ("01", "GLOBAL OVERVIEW",
         "Astra Inc. worldwide retail footprint — 847 stores, 24 countries"),
        ("02", "OUTAGE MOMENT",
         "SD-WAN backbone failure severs connectivity across all regions"),
        ("03", "ALERT FLOOD & IMPACT",
         "$1M/hr revenue impact · 1,284 cascading alerts overwhelm NOC"),
        ("04", "THE CHALLENGE",
         "847 stores. 1,284 alerts. Isolating root cause under pressure"),
    ]
    for i, (num, title, sub) in enumerate(captions):
        px2, py2 = P[i]
        cy2 = py2 + PH + 14
        # panel number
        parts.append(txt(px2, cy2 + 28, f"[ {num} ]", 22, BE,
                         anchor="start", font_weight="700", letter_spacing="3"))
        parts.append(txt(px2 + 90, cy2 + 28, title, 26, WHT,
                         anchor="start", font_weight="700", letter_spacing="3"))
        parts.append(txt(px2, cy2 + 54, sub, 22, MGR, anchor="start"))

    # Footer strip
    fy = TH + PH * 2 + RH + 30
    parts.append(rect(0, fy, W, H - fy, NV1, opacity="0.5"))
    parts.append(line(0, fy, W, fy, NV3, stroke_width="1"))
    parts.append(txt(W // 2, fy + 40, "ASTRA INC. · NETWORK OPERATIONS CENTER · SD-WAN INCIDENT REVIEW",
                     22, MGR, letter_spacing="3"))

    return "".join(parts)


# ── Assemble & write ───────────────────────────────────────────────────────

def build():
    parts = []
    parts.append(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 {W} {H}" width="{W}" height="{H}"
     shape-rendering="geometricPrecision" text-rendering="optimizeLegibility">''')
    parts.append(make_defs())
    parts.append(outer_chrome())
    parts.append(panel1())
    parts.append(panel2())
    parts.append(panel3())
    parts.append(panel4())
    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    svg = build()
    out = "storyboard.svg"
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Written {out}  ({len(svg):,} bytes)")
    size_kb = len(svg) / 1024
    print(f"Size: {size_kb:.1f} KB")
