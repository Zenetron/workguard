from PIL import Image

def create_apple_icon():
    try:
        # 1. Ouvrir le logo (favicon.png est dispo)
        img = Image.open("favicon.png")
        img = img.convert("RGBA")
        
        # 2. Rogner les bords transparents (Auto-Crop)
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
        
        # 3. Créer un canvas carré BLANC 180x180 (iOS préfère fond non-transparent pour éviter le noir)
        # Mais un fond blanc propre fait plus "App Native"
        size = 180
        new_img = Image.new("RGBA", (size, size), (255, 255, 255, 255)) # Fond BLANC
        
        # 4. Redimensionner le logo pour qu'il rentre dedans (avec marge)
        # On veut qu'il prenne ~80% de la place (144px)
        target_size = int(size * 0.8)
        
        # Ratio
        ratio = min(target_size / img.width, target_size / img.height)
        new_w = int(img.width * ratio)
        new_h = int(img.height * ratio)
        
        img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # 5. Centrer
        x = (size - new_w) // 2
        y = (size - new_h) // 2
        
        # Coller (avec masque pour transparence)
        new_img.paste(img_resized, (x, y), img_resized)
        
        # 6. Sauvegarder
        new_img.save("static/apple-touch-icon.png", "PNG")
        print("✅ apple-touch-icon.png (180x180) généré dans static/ !")
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    create_apple_icon()
