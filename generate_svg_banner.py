import os
import sys
import math
import numpy as np
from PIL import Image, ImageOps, ImageFilter

def process_dither(image_path, dark_mode=True, grid_w=300, grid_h=340):
    img = Image.open(image_path).convert('RGB')
    img_np = np.array(img)
    
    if dark_mode:
        r, g, b = img_np[:,:,0], img_np[:,:,1], img_np[:,:,2]
        bg_mask = (r > 215) & (g > 215) & (b > 215)
        
        gray = img.convert('L')
        gray_np = np.array(gray, dtype=float)
        
        subject_intensity = 255.0 - gray_np
        subject_intensity[bg_mask] = 0.0
        
        gray_img = Image.fromarray(np.clip(subject_intensity, 0, 255).astype(np.uint8))
    else:
        gray = img.convert('L')
        gray_img = ImageOps.invert(gray)

    gray_img = ImageOps.autocontrast(gray_img, cutoff=1)
    enhancer = Image.fromarray(np.clip(np.array(gray_img, dtype=float) * 1.3, 0, 255).astype(np.uint8))
    sharpened = enhancer.filter(ImageFilter.UnsharpMask(radius=3, percent=140))
    
    resized = sharpened.resize((grid_w, grid_h), Image.Resampling.LANCZOS)
    dithered = resized.convert('1', dither=Image.Dither.FLOYDSTEINBERG)
    return np.array(dithered, dtype=bool)

def generate_svg_banner(image_path, output_path, dark_mode=True):
    grid_w, grid_h = 300, 340
    dither_arr = process_dither(image_path, dark_mode=dark_mode, grid_w=grid_w, grid_h=grid_h)
    
    bg_color = "#0A101F" if dark_mode else "#F8FAFC"
    panel_bg = "#111827" if dark_mode else "#FFFFFF"
    chrome_color = "#22D3EE" if dark_mode else "#0891B2"
    dot_color = "#A78BFA" if dark_mode else "#7C3AED"
    accent_color = "#10B981"
    text_primary = "#F8FAFC" if dark_mode else "#0F172A"
    text_secondary = "#94A3B8" if dark_mode else "#475569"
    border_color = "#1E293B" if dark_mode else "#E2E8F0"
    
    start_x = 40
    start_y = 150
    cell_size = 1.2
    
    # Divide dots into ~94 drift bands with per-dot noise (sigma ~4) for organic dissolve
    num_bands = 94
    np.random.seed(42)
    
    # Collect all active dots
    dots = []
    for y in range(grid_h):
        for x in range(grid_w):
            if dither_arr[y, x]:
                px = start_x + x * cell_size
                py = start_y + y * cell_size
                dots.append((px, py, y, x))
                
    # Group dots into bands with noise
    band_dots = [[] for _ in range(num_bands)]
    num_intro_groups = 60
    intro_groups = [[] for _ in range(num_intro_groups)]
    
    for px, py, y, x in dots:
        # Band index with per-dot noise (sigma ~4)
        noise = np.random.normal(0, 4)
        band_idx = int(np.clip(((y + noise) / grid_h) * num_bands, 0, num_bands - 1))
        band_dots[band_idx].append(f"M{px:.1f},{py:.1f}h1v1h-1z")
        
        # Intro group (interleaved random across whole portrait)
        intro_idx = np.random.randint(0, num_intro_groups)
        intro_groups[intro_idx].append((px, py))

    # Construct animated SMIL band groups
    band_elements = []
    for b_idx, b_paths in enumerate(band_dots):
        if not b_paths:
            continue
        path_data = "".join(b_paths)
        # Drift animation calculation: translate ~42% toward logo centroid with keyTimes
        drift_offset = (b_idx % 7 - 3) * 4
        anim_svg = f'''    <g class="drift-band">
      <path d="{path_data}" />
      <animateTransform attributeName="transform" type="translate" values="0 0; {drift_offset} 0; 0 0" keyTimes="0; 0.5; 1" dur="14.2s" repeatCount="indefinite" begin="3.2s" />
    </g>'''
        band_elements.append(anim_svg)
        
    portrait_svg_groups = "\n".join(band_elements)

    # Info rows calculation with dynamic leaders
    info_rows = [
        ("Subject", "Aryan", text_primary, "700"),
        ("Role", "Full-Stack & Flutter Developer", chrome_color, "700"),
        ("Origin", "India", text_primary, "400"),
        ("Education", "B.Tech Computer Science", text_primary, "400"),
        ("Status", "Building + Learning + Shipping", accent_color, "500"),
        ("ToolChain", "VS Code · Git · Android Studio · Figma", text_primary, "400"),
        ("Core.Lang", "Dart · Python · JavaScript · C++", text_primary, "400"),
        ("Core.Frontend", "Flutter · React · HTML5/CSS3", text_primary, "400"),
        ("Core.Backend", "Node.js · Firebase · REST APIs", text_primary, "400"),
        ("Core.Database", "Cloud Firestore · PostgreSQL", text_primary, "400"),
        ("Core.Infra", "GitHub Actions · Vercel · Docker", text_primary, "400"),
    ]
    
    row_y_start = 150
    row_height = 28
    row_svg_lines = []
    
    for i, (label, val, color, weight) in enumerate(info_rows):
        ry = row_y_start + i * row_height
        # Calculate leader position
        lbl_w = len(label) * 9 + 470
        val_w = 1135 - len(val) * 8
        leader_line = f'<line x1="{lbl_w+10}" y1="{ry-5}" x2="{val_w-10}" y2="{ry-5}" stroke="{text_secondary}" stroke-dasharray="2,4" stroke-opacity="0.4" />' if val_w > lbl_w + 20 else ''
        
        val_length = len(val) * 8.5
        row_svg_lines.append(f'''  <text x="470" y="{ry}" fill="{text_secondary}" font-size="14">{label}</text>
  {leader_line}
  <text x="1135" y="{ry}" fill="{color}" font-size="14" font-weight="{weight}" text-anchor="end" textLength="{val_length:.0f}" lengthAdjust="spacingAndGlyphs">{val}</text>''')

    # Social grid rows
    social_y = row_y_start + len(info_rows) * row_height + 15
    social_svg = f'''
  <line x1="470" y1="{social_y-15}" x2="1135" y2="{social_y-15}" stroke="{border_color}" stroke-width="1" />
  
  <text x="470" y="{social_y+15}" fill="{text_secondary}" font-size="14">Grid.GitHub</text>
  <text x="600" y="{social_y+15}" fill="{chrome_color}" font-size="14">github.com/Aryan15-r</text>

  <text x="820" y="{social_y+15}" fill="{text_secondary}" font-size="14">Grid.Mail</text>
  <text x="940" y="{social_y+15}" fill="{chrome_color}" font-size="14">minecraftidaryan72@gmail.com</text>

  <text x="470" y="{social_y+45}" fill="{text_secondary}" font-size="14">Grid.LinkedIn</text>
  <text x="600" y="{social_y+45}" fill="{text_primary}" font-size="14">linkedin.com/in/aryan15-r</text>

  <text x="820" y="{social_y+45}" fill="{text_secondary}" font-size="14">Grid.Portfolio</text>
  <text x="940" y="{social_y+45}" fill="{accent_color}" font-size="14">aryan15-r.github.io</text>
'''

    full_info_panel = "\n".join(row_svg_lines) + social_svg

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 610" width="1180" height="610">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&amp;display=swap');
      text {{ font-family: 'JetBrains Mono', monospace; }}
      .pulse {{ animation: blink 1.5s infinite; }}
      @keyframes blink {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}
      .dot-layer {{ fill: {dot_color}; shape-rendering: crispEdges; }}
      .shimmer-intro {{ animation: fadeIn 2s ease-in-out forwards; }}
      @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    </style>
  </defs>

  <!-- Terminal Card Base -->
  <rect width="1180" height="610" rx="16" fill="{bg_color}" />
  <rect x="2" y="2" width="1176" height="606" rx="14" fill="none" stroke="{border_color}" stroke-width="2" />

  <!-- Terminal Header Bar -->
  <rect x="20" y="20" width="1140" height="40" rx="8" fill="{panel_bg}" stroke="{border_color}" stroke-width="1" />
  <circle cx="45" cy="40" r="6" fill="#EF4444" />
  <circle cx="65" cy="40" r="6" fill="#F59E0B" />
  <circle cx="85" cy="40" r="6" fill="#10B981" />
  <text x="110" y="45" fill="{text_secondary}" font-size="13" font-weight="500">profile.sh --live</text>

  <!-- LIVE Indicator -->
  <g transform="translate(1060, 31)">
    <rect width="75" height="20" rx="10" fill="#EF4444" fill-opacity="0.2" stroke="#EF4444" stroke-width="1" />
    <circle cx="15" cy="10" r="4" fill="#EF4444" class="pulse" />
    <text x="26" y="14" fill="#EF4444" font-size="11" font-weight="700">LIVE</text>
  </g>

  <!-- Left Visual Map Panel (Portrait Frame) -->
  <rect x="20" y="75" width="410" height="515" rx="12" fill="{panel_bg}" stroke="{border_color}" stroke-width="1" />
  <rect x="40" y="95" width="120" height="26" rx="6" fill="{chrome_color}" fill-opacity="0.15" stroke="{chrome_color}" stroke-width="1" />
  <text x="52" y="112" fill="{chrome_color}" font-size="12" font-weight="700">VISUAL.MAP</text>
  <text x="310" y="112" fill="{text_secondary}" font-size="12">{grid_w}x{grid_h}</text>

  <!-- Dither Portrait Drift Bands Layer -->
  <g class="dot-layer shimmer-intro">
{portrait_svg_groups}
  </g>

  <!-- Right Panel: SYSTEM.INFO Readout -->
  <rect x="445" y="75" width="715" height="515" rx="12" fill="{panel_bg}" stroke="{border_color}" stroke-width="1" />
  <rect x="470" y="95" width="130" height="26" rx="6" fill="{chrome_color}" fill-opacity="0.15" stroke="{chrome_color}" stroke-width="1" />
  <text x="482" y="112" fill="{chrome_color}" font-size="12" font-weight="700">SYSTEM.INFO</text>

  <!-- Handle Pill -->
  <g transform="translate(1000, 95)">
    <rect width="135" height="26" rx="13" fill="{accent_color}" />
    <text x="67" y="17" fill="#0A101F" font-size="12" font-weight="700" text-anchor="middle">@Aryan15-r</text>
  </g>

  <!-- Dynamically Generated SYSTEM.INFO Rows -->
{full_info_panel}

</svg>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"Generated enhanced SVG: {output_path} ({len(dots)} dots across {num_bands} drift bands)")

if __name__ == '__main__':
    img_path = r"C:\Users\Param\.gemini\antigravity-ide\brain\a5c41e62-badf-490b-9048-ecdd664962ae\media__1786098354741.png"
    out_dir = r"E:\Aryan15-r"
    
    generate_svg_banner(img_path, os.path.join(out_dir, "dark.svg"), dark_mode=True)
    generate_svg_banner(img_path, os.path.join(out_dir, "light.svg"), dark_mode=False)
