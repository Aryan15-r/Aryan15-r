import os
import sys
import math
import numpy as np
from PIL import Image, ImageOps, ImageFilter

def process_dither(image_path, dark_mode=True, grid_w=300, grid_h=340):
    img = Image.open(image_path).convert('RGB')
    
    # 1. Background segmentation for dark mode vs light mode
    img_np = np.array(img)
    
    if dark_mode:
        # Background is white/bright, subject is darker/person
        # For dark mode: segment background out (keep subject, lit subject on dark panel)
        # Background threshold on near white (R,G,B > 220)
        r, g, b = img_np[:,:,0], img_np[:,:,1], img_np[:,:,2]
        bg_mask = (r > 215) & (g > 215) & (b > 215)
        
        # Convert to grayscale
        gray = img.convert('L')
        gray_np = np.array(gray, dtype=float)
        
        # Subject is dark on white bg, so invert for dither intensity (subject = bright dots on dark bg)
        # 255 - pixel value, but background forced to 0
        subject_intensity = 255.0 - gray_np
        subject_intensity[bg_mask] = 0.0
        
        gray_img = Image.fromarray(np.clip(subject_intensity, 0, 255).astype(np.uint8))
    else:
        # Light mode: keep background, dots draw dark parts of photo (normal dither on inverted gray)
        gray = img.convert('L')
        # Dark parts draw dark dots
        gray_img = ImageOps.invert(gray)

    # 2. Contrast adjustment & UnsharpMask
    gray_img = ImageOps.autocontrast(gray_img, cutoff=1)
    enhancer = Image.fromarray(np.clip(np.array(gray_img, dtype=float) * 1.3, 0, 255).astype(np.uint8))
    sharpened = enhancer.filter(ImageFilter.UnsharpMask(radius=3, percent=140))
    
    # 3. Resize to grid
    resized = sharpened.resize((grid_w, grid_h), Image.Resampling.LANCZOS)
    
    # 4. 1-bit Floyd-Steinberg Dither
    dithered = resized.convert('1', dither=Image.Dither.FLOYDSTEINBERG)
    dither_arr = np.array(dithered, dtype=bool)
    
    return dither_arr

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
    
    # Scale dots into frame 40px left, 170px top, box size 360x420 (dot size ~1.1px)
    start_x = 40
    start_y = 150
    cell_size = 1.2
    
    # Build dither dots path
    path_runs = []
    dot_count = 0
    for y in range(grid_h):
        for x in range(grid_w):
            if dither_arr[y, x]:
                px = start_x + x * cell_size
                py = start_y + y * cell_size
                path_runs.append(f"M{px:.1f},{py:.1f}h1v1h-1z")
                dot_count += 1
                
    dither_path_data = "".join(path_runs)
    
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 610" width="1180" height="610">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&amp;display=swap');
      text {{ font-family: 'JetBrains Mono', monospace; }}
      .pulse {{ animation: blink 1.5s infinite; }}
      @keyframes blink {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}
      .dot-layer {{ fill: {dot_color}; shape-rendering: crispEdges; }}
    </style>
  </defs>

  <!-- Background Card -->
  <rect width="1180" height="610" rx="16" fill="{bg_color}" />
  <rect x="2" y="2" width="1176" height="606" rx="14" fill="none" stroke="{border_color}" stroke-width="2" />

  <!-- Terminal Header -->
  <rect x="20" y="20" width="1140" height="40" rx="8" fill="{panel_bg}" stroke="{border_color}" stroke-width="1" />
  <circle cx="45" cy="40" r="6" fill="#EF4444" />
  <circle cx="65" cy="40" r="6" fill="#F59E0B" />
  <circle cx="85" cy="40" r="6" fill="#10B981" />
  <text x="110" y="45" fill="{text_secondary}" font-size="13" font-weight="500">profile.sh --live</text>

  <!-- Pulsing LIVE Badge -->
  <g transform="translate(1060, 31)">
    <rect width="75" height="20" rx="10" fill="#EF4444" fill-opacity="0.2" stroke="#EF4444" stroke-width="1" />
    <circle cx="15" cy="10" r="4" fill="#EF4444" class="pulse" />
    <text x="26" y="14" fill="#EF4444" font-size="11" font-weight="700">LIVE</text>
  </g>

  <!-- Main Grid Layout -->
  <!-- Left Panel: Visual Portrait -->
  <rect x="20" y="75" width="410" height="515" rx="12" fill="{panel_bg}" stroke="{border_color}" stroke-width="1" />
  
  <!-- Header Pill for VISUAL.MAP -->
  <rect x="40" y="95" width="120" height="26" rx="6" fill="{chrome_color}" fill-opacity="0.15" stroke="{chrome_color}" stroke-width="1" />
  <text x="52" y="112" fill="{chrome_color}" font-size="12" font-weight="700">VISUAL.MAP</text>
  <text x="310" y="112" fill="{text_secondary}" font-size="12">{grid_w}x{grid_h}</text>

  <!-- Portrait Dither Layer -->
  <g class="dot-layer">
    <path d="{dither_path_data}" />
  </g>

  <!-- Right Panel: SYSTEM.INFO -->
  <rect x="445" y="75" width="715" height="515" rx="12" fill="{panel_bg}" stroke="{border_color}" stroke-width="1" />

  <!-- Header Pill for SYSTEM.INFO & Handle -->
  <rect x="470" y="95" width="130" height="26" rx="6" fill="{chrome_color}" fill-opacity="0.15" stroke="{chrome_color}" stroke-width="1" />
  <text x="482" y="112" fill="{chrome_color}" font-size="12" font-weight="700">SYSTEM.INFO</text>

  <g transform="translate(1000, 95)">
    <rect width="135" height="26" rx="13" fill="{accent_color}" />
    <text x="67" y="17" fill="#0A101F" font-size="12" font-weight="700" text-anchor="middle">@Aryan15-r</text>
  </g>

  <!-- Information Rows with Leader Lines -->
  <!-- Row 1: Name -->
  <text x="470" y="160" fill="{text_secondary}" font-size="14">Subject</text>
  <line x1="545" y1="155" x2="880" y2="155" stroke="{text_secondary}" stroke-dasharray="2,4" stroke-opacity="0.4" />
  <text x="890" y="160" fill="{text_primary}" font-size="14" font-weight="700" textLength="240" lengthAdjust="spacingAndGlyphs">Aryan</text>

  <!-- Row 2: Role -->
  <text x="470" y="195" fill="{text_secondary}" font-size="14">Role</text>
  <line x1="515" y1="190" x2="780" y2="190" stroke="{text_secondary}" stroke-dasharray="2,4" stroke-opacity="0.4" />
  <text x="790" y="195" fill="{chrome_color}" font-size="14" font-weight="700" textLength="340" lengthAdjust="spacingAndGlyphs">Full-Stack &amp; Flutter Dev</text>

  <!-- Row 3: Status -->
  <text x="470" y="230" fill="{text_secondary}" font-size="14">Status</text>
  <line x1="535" y1="225" x2="750" y2="225" stroke="{text_secondary}" stroke-dasharray="2,4" stroke-opacity="0.4" />
  <text x="760" y="230" fill="{accent_color}" font-size="14" textLength="370" lengthAdjust="spacingAndGlyphs">Building + Learning + Shipping</text>

  <!-- Row 4: ToolChain -->
  <text x="470" y="265" fill="{text_secondary}" font-size="14">ToolChain</text>
  <line x1="555" y1="260" x2="720" y2="260" stroke="{text_secondary}" stroke-dasharray="2,4" stroke-opacity="0.4" />
  <text x="730" y="265" fill="{text_primary}" font-size="14" textLength="400" lengthAdjust="spacingAndGlyphs">VS Code · Git · Flutter · Android Studio</text>

  <!-- Separator -->
  <line x1="470" y1="295" x2="1135" y2="295" stroke="{border_color}" stroke-width="1" />

  <!-- Technical Breakdown Section -->
  <text x="470" y="330" fill="{text_secondary}" font-size="14">Core.Lang</text>
  <line x1="555" y1="325" x2="800" y2="325" stroke="{text_secondary}" stroke-dasharray="2,4" stroke-opacity="0.4" />
  <text x="810" y="330" fill="{text_primary}" font-size="14" textLength="320" lengthAdjust="spacingAndGlyphs">Dart · Python · JavaScript · C++</text>

  <text x="470" y="365" fill="{text_secondary}" font-size="14">Core.Frontend</text>
  <line x1="590" y1="360" x2="840" y2="360" stroke="{text_secondary}" stroke-dasharray="2,4" stroke-opacity="0.4" />
  <text x="850" y="365" fill="{text_primary}" font-size="14" textLength="280" lengthAdjust="spacingAndGlyphs">Flutter · React · HTML5/CSS3</text>

  <text x="470" y="400" fill="{text_secondary}" font-size="14">Core.Backend</text>
  <line x1="580" y1="395" x2="850" y2="395" stroke="{text_secondary}" stroke-dasharray="2,4" stroke-opacity="0.4" />
  <text x="860" y="400" fill="{text_primary}" font-size="14" textLength="270" lengthAdjust="spacingAndGlyphs">Node.js · Firebase · REST APIs</text>

  <text x="470" y="435" fill="{text_secondary}" font-size="14">Core.Database</text>
  <line x1="590" y1="430" x2="870" y2="430" stroke="{text_secondary}" stroke-dasharray="2,4" stroke-opacity="0.4" />
  <text x="880" y="435" fill="{text_primary}" font-size="14" textLength="250" lengthAdjust="spacingAndGlyphs">Cloud Firestore · PostgreSQL</text>

  <!-- Separator -->
  <line x1="470" y1="465" x2="1135" y2="465" stroke="{border_color}" stroke-width="1" />

  <!-- Social & Contact Grid -->
  <text x="470" y="500" fill="{text_secondary}" font-size="14">Grid.GitHub</text>
  <text x="600" y="500" fill="{chrome_color}" font-size="14">github.com/Aryan15-r</text>

  <text x="820" y="500" fill="{text_secondary}" font-size="14">Grid.Mail</text>
  <text x="920" y="500" fill="{chrome_color}" font-size="14">minecraftidaryan72@gmail.com</text>

  <text x="470" y="535" fill="{text_secondary}" font-size="14">Grid.LinkedIn</text>
  <text x="600" y="535" fill="{text_primary}" font-size="14">linkedin.com/in/aryan15-r</text>

  <text x="820" y="535" fill="{text_secondary}" font-size="14">Grid.Portfolio</text>
  <text x="940" y="535" fill="{accent_color}" font-size="14">aryan15-r.github.io</text>

</svg>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"Successfully generated SVG: {output_path} ({dot_count} dither dots)")

if __name__ == '__main__':
    img_path = r"C:\Users\Param\.gemini\antigravity-ide\brain\a5c41e62-badf-490b-9048-ecdd664962ae\media__1786098354741.png"
    out_dir = r"E:\Aryan15-r"
    
    generate_svg_banner(img_path, os.path.join(out_dir, "dark.svg"), dark_mode=True)
    generate_svg_banner(img_path, os.path.join(out_dir, "light.svg"), dark_mode=False)
