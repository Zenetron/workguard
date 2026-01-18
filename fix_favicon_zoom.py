from PIL import Image
import os

input_path = "WorkGuard Logo.png" # Try original first
if not os.path.exists(input_path):
    input_path = "favicon.png" # Fallback to existing favicon if source lost

output_path = "favicon_sq.png"

if os.path.exists(input_path):
    print(f"Loading {input_path}...")
    img = Image.open(input_path)
    print(f"Original size: {img.size}")
    
    # 1. Convert to RGBA
    img = img.convert("RGBA")
    
    # 2. Auto-Crop (Trim transparent borders)
    bbox = img.getbbox()
    if bbox:
        print(f"Cropping to content: {bbox}")
        img = img.crop(bbox)
    
    # 3. Create Square Canvas (128x128)
    # We want to maximize the logo within this square
    # Calculate scale factor to FIT inside 128x128
    
    target_size = 128
    w, h = img.size
    
    # Scale based on the largest dimension of the cropped image
    ratio = min(target_size / w, target_size / h)
    
    new_w = int(w * ratio)
    new_h = int(h * ratio)
    
    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # 4. Paste centered on 128x128 canvas
    final_img = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 0))
    x = (target_size - new_w) // 2
    y = (target_size - new_h) // 2
    
    final_img.paste(img, (x, y))
    
    final_img.save(output_path, "PNG")
    
    print(f"Saved optimized & zoomed favicon to {output_path}")
    print(f"New size: {final_img.size}")

else:
    print(f"Error: {input_path} not found.")
