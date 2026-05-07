#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import math, random

W, H = 1200, 1200
img = Image.new('RGB', (W, H), (245, 240, 232))
draw = ImageDraw.Draw(img)
CX, CY = W//2, H//2

FONT_CN = '/System/Library/Fonts/Songti.ttc'
FONT_HAND = "/Users/ray/.claude/plugins/cache/anthropic-agent-skills/document-skills/98669c11ca63/skills/canvas-design/canvas-fonts/NothingYouCouldDo-Regular.ttf"

# Colors
BROWN = (110, 78, 54)
AMBER = (196, 149, 106)
GREEN = (143, 168, 122)
DARK = (74, 63, 53)
GOLD = (212, 165, 116)

border = 90
outer_r = W//2 - border
inner_r = outer_r - 20
comp_r = inner_r - 15

# --- Rings ---
draw.ellipse([CX-outer_r, CY-outer_r, CX+outer_r, CY+outer_r], outline=DARK, width=3)
draw.ellipse([CX-inner_r, CY-inner_r, CX+inner_r, CY+inner_r], outline=DARK, width=1)

dot_radius = (outer_r + inner_r) // 2
for i in range(20):
    a = 2 * math.pi * i / 20
    dx = math.cos(a) * dot_radius
    dy = math.sin(a) * dot_radius
    s = 4
    draw.ellipse([CX+dx-s, CY+dy-s, CX+dx+s, CY+dy+s], fill=GOLD)

# --- Three trees ---
ground_y = CY + comp_r * 0.30
tree_spacing = comp_r * 0.50

def draw_tree(draw, cx, ground_y, height, canopy_radius, trunk_color, canopy_color, seed):
    rng = random.Random(seed)
    trunk_bottom_w = 12
    trunk_top_w = 4
    trunk_h = height * 0.45

    trunk_points = []
    segs = 20
    for i in range(segs + 1):
        t = i / segs
        y = ground_y - t * trunk_h
        width = trunk_bottom_w + (trunk_top_w - trunk_bottom_w) * t
        w = width/2 + rng.uniform(-0.5, 0.5)
        trunk_points.append((cx - w, y))
    for i in range(segs, -1, -1):
        t = i / segs
        y = ground_y - t * trunk_h
        width = trunk_bottom_w + (trunk_top_w - trunk_bottom_w) * t
        w = width/2 + rng.uniform(-0.5, 0.5)
        trunk_points.append((cx + w, y))

    draw.polygon(trunk_points, fill=trunk_color)

    canopy_cy = ground_y - trunk_h
    n_circles = 5 + rng.randint(0, 2)
    for _ in range(n_circles):
        offset_x = rng.uniform(-canopy_radius*0.6, canopy_radius*0.6)
        offset_y = rng.uniform(-canopy_radius*0.5, canopy_radius*0.3)
        r = rng.uniform(canopy_radius*0.5, canopy_radius*0.8)
        var = rng.randint(-15, 15)
        c = tuple(min(max(v + var, 0), 255) for v in canopy_color)
        draw.ellipse([cx+offset_x-r, canopy_cy+offset_y-r, cx+offset_x+r, canopy_cy+offset_y+r], fill=c)

# Father - left, tall, sturdy
draw_tree(draw, CX - tree_spacing, ground_y, height=290, canopy_radius=85,
          trunk_color=BROWN, canopy_color=(120, 90, 60), seed=10)

# Mother - center, full, blooming
draw_tree(draw, CX, ground_y, height=260, canopy_radius=95,
          trunk_color=AMBER, canopy_color=(200, 155, 115), seed=20)

# Daughter - right, small, fresh
draw_tree(draw, CX + tree_spacing, ground_y, height=210, canopy_radius=65,
          trunk_color=GREEN, canopy_color=(150, 175, 130), seed=30)

# Ground
ground_pts = []
for i in range(41):
    frac = i / 40
    gx = CX - comp_r * 0.65 + frac * comp_r * 1.3
    gy = ground_y + math.sin(frac * math.pi * 2) * 4
    ground_pts.append((gx, gy))
draw.line(ground_pts, fill=DARK, width=3, joint='curve')

# Small roots
for cx in [CX - tree_spacing, CX, CX + tree_spacing]:
    for side in [-1, 1]:
        rx, ry = cx + side * 15, ground_y
        ex = rx + side * random.randint(20, 40)
        ey = ry + random.randint(8, 20)
        draw.line([(rx, ry), (ex, ey)], fill=DARK, width=2)

# --- Text ---
font_big = ImageFont.truetype(FONT_CN, 60)
font_mid = ImageFont.truetype(FONT_CN, 38)
font_sm = ImageFont.truetype(FONT_CN, 22)
font_hand = ImageFont.truetype(FONT_HAND, 30)

# "李" at top
surname = "李"
bb = draw.textbbox((0, 0), surname, font=font_big)
draw.text((CX - (bb[2]-bb[0])//2, CY - comp_r), surname, fill=DARK, font=font_big)

# Names at bottom
names = "壮壮    瑞    沐欣"
bb2 = draw.textbbox((0, 0), names, font=font_mid)
draw.text((CX - (bb2[2]-bb2[0])//2, ground_y + 30), names, fill=DARK, font=font_mid)

# Decorative line
ly = ground_y + 15
draw.line([CX - 100, ly, CX + 100, ly], fill=GOLD, width=1)

# Labels
draw.text((CX - tree_spacing - 15, ground_y + 70), "爸", fill=BROWN, font=font_sm)
draw.text((CX - 10, ground_y + 70), "妈", fill=AMBER, font=font_sm)
draw.text((CX + tree_spacing - 15, ground_y + 70), "欣", fill=GREEN, font=font_sm)

# English tagline
en = "together we grow"
bb3 = draw.textbbox((0, 0), en, font=font_hand)
draw.text((CX - (bb3[2]-bb3[0])//2, CY + outer_r - 45), en, fill=GOLD, font=font_hand)

output = '/Users/ray/dev/projects/internal-plugin-marketplace/design/family-logo-v2.png'
img.save(output)
print(f'Saved: {output}')
