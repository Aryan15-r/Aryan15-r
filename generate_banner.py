"""
GitHub Profile Dithered Terminal Banner Generator Script
Generates dark.svg and light.svg from a source portrait image.
"""
import os
import sys
try:
    from PIL import Image, ImageEnhance, ImageOps, ImageFilter
    import numpy as np
except ImportError:
    print("Installing required packages (Pillow, numpy)...")
    os.system(f"{sys.executable} -m pip install Pillow numpy")
    from PIL import Image, ImageEnhance, ImageOps, ImageFilter
    import numpy as np

def process_portrait(image_path, target_width=300, target_height=340):
    img = Image.open(image_path).convert('L')
    img = ImageOps.autocontrast(img, cutoff=1)
    
    # UnsharpMask(radius=3, percent=140)
    img = img.filter(ImageFilter.UnsharpMask(radius=3, percent=140))
    
    # Resize to target grid
    img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    # 1-bit Floyd-Steinberg dither
    dithered = img.convert('1', dither=Image.Dither.FLOYDSTEINBERG)
    return dithered

if __name__ == '__main__':
    print("Banner generator initialized for Aryan15-r. Provide a head-and-shoulders photo to run dither generation.")
