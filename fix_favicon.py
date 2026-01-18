from PIL import Image
import os

input_path = "favicon.png"
output_path = "favicon_sq.png"

if os.path.exists(input_path):
    print(f"Loading {input_path}...")
    img = Image.open(input_path)
    print(f"Original size: {img.size}")
    
    # Create valid square canvas (Transparent)
    # Using 128x128 or max dimension
    max_dim = max(img.size)
    new_img = Image.new("RGBA", (max_dim, max_dim), (0, 0, 0, 0))
    
    # Calculate position to center
    x = (max_dim - img.size[0]) // 2
    y = (max_dim - img.size[1]) // 2
    
    new_img.paste(img, (x, y))
    new_img.save(output_path, "PNG")
    
    print(f"Saved to {output_path}")
    print(f"New size: {new_img.size}")
else:
    print(f"Error: {input_path} not found.")
