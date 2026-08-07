import os
import numpy as np
from PIL import Image, ImageOps, ImageFilter

def generate_portrait_dither(image_path, dark_mode=True, grid_w=300, grid_h=340):
    img = Image.open(image_path).convert('RGB')
    
    # 1. Background segmentation: photo has plain white backdrop
    img_np = np.array(img, dtype=float)
    r, g, b = img_np[:,:,0], img_np[:,:,1], img_np[:,:,2]
    
    # Background threshold (white backdrop)
    bg_mask = (r > 210) & (g > 210) & (b > 210)
    
    gray = img.convert('L')
    gray_np = np.array(gray, dtype=float)
    
    if dark_mode:
        # In dark mode: dots draw the lit subject on dark panel.
        # Subject intensity = normal gray (bright face = dense dots, shadows = lower density)
        # Background is masked out completely to 0.
        intensity = gray_np.copy()
        intensity[bg_mask] = 0.0
        
        # Boost contrast on subject
        intensity_img = Image.fromarray(np.clip(intensity, 0, 255).astype(np.uint8))
        intensity_img = ImageOps.autocontrast(intensity_img, cutoff=1)
        enhancer = Image.fromarray(np.clip(np.array(intensity_img, dtype=float) * 1.25, 0, 255).astype(np.uint8))
    else:
        # In light mode: dots draw dark parts of photo on light panel.
        # Invert gray so dark features/shadows = high density dots
        intensity_img = ImageOps.invert(gray)
        intensity_img = ImageOps.autocontrast(intensity_img, cutoff=1)
        enhancer = Image.fromarray(np.clip(np.array(intensity_img, dtype=float) * 1.3, 0, 255).astype(np.uint8))

    sharpened = enhancer.filter(ImageFilter.UnsharpMask(radius=3, percent=140))
    resized = sharpened.resize((grid_w, grid_h), Image.Resampling.LANCZOS)
    
    dithered = resized.convert('1', dither=Image.Dither.FLOYDSTEINBERG)
    return dithered

if __name__ == '__main__':
    img_path = r"C:\Users\Param\.gemini\antigravity-ide\brain\a5c41e62-badf-490b-9048-ecdd664962ae\media__1786098354741.png"
    dark_dither = generate_portrait_dither(img_path, dark_mode=True)
    light_dither = generate_portrait_dither(img_path, dark_mode=False)
    
    dark_dither.save(r"E:\Aryan15-r\dark_preview.png")
    light_dither.save(r"E:\Aryan15-r\light_preview.png")
    print("Dither preview images saved successfully!")
