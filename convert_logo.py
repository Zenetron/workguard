from PIL import Image
import os

input_path = "WorkGuard Logo.png"
output_path = "favicon.png"

if os.path.exists(input_path):
    print(f"Loading {input_path}...")
    img = Image.open(input_path)
    print(f"Original size: {img.size}")
    
    img.thumbnail((128, 128))
    img.save(output_path, "PNG", optimize=True)
    
    print(f"Saved to {output_path}")
    print(f"New size: {os.path.getsize(output_path)} bytes")
else:
    print(f"Error: {input_path} not found.")
