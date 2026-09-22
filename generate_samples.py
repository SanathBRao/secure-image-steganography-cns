"""
Script: generate_samples.py
Description: Generates sample cover images in sample_images/ directory
  for immediate testing and viva demonstration.
"""

import os
from PIL import Image, ImageDraw

def create_sample_images():
    output_dir = os.path.join(os.path.dirname(__file__), "sample_images")
    os.makedirs(output_dir, exist_ok=True)

    # 1. Landscape Gradient (600x400) - Simulating natural scenery
    img1 = Image.new("RGB", (600, 400), color=(135, 206, 235))
    draw1 = ImageDraw.Draw(img1)
    
    # Sky to grass gradient
    for y in range(250, 400):
        green_val = int(100 + (y - 250) * 0.8)
        draw1.line([(0, y), (600, y)], fill=(34, green_val, 34))

    # Sun
    draw1.ellipse([450, 40, 530, 120], fill=(255, 223, 0), outline=(255, 180, 0))
    # Mountain
    draw1.polygon([(50, 250), (200, 100), (350, 250)], fill=(105, 105, 105))
    draw1.polygon([(250, 250), (400, 130), (520, 250)], fill=(128, 128, 128))

    path1 = os.path.join(output_dir, "sample_landscape.png")
    img1.save(path1, "PNG")
    print(f"Created: {path1} (Size: 600x400)")

    # 2. Geometric / Tech Pattern (400x400)
    img2 = Image.new("RGB", (400, 400), color=(20, 25, 40))
    draw2 = ImageDraw.Draw(img2)
    for i in range(0, 400, 20):
        color_val = (i * 255) // 400
        draw2.line([(i, 0), (400, 400 - i)], fill=(color_val, 120, 220), width=2)
        draw2.line([(0, i), (400 - i, 400)], fill=(40, color_val, 200), width=2)
    draw2.rectangle([120, 120, 280, 280], outline=(0, 255, 200), width=3)

    path2 = os.path.join(output_dir, "sample_geometric.png")
    img2.save(path2, "PNG")
    print(f"Created: {path2} (Size: 400x400)")

    # 3. Small Avatar (150x150) - useful for testing low-capacity edge conditions
    img3 = Image.new("RGB", (150, 150), color=(240, 242, 245))
    draw3 = ImageDraw.Draw(img3)
    draw3.ellipse([30, 30, 120, 120], fill=(65, 105, 225))
    draw3.ellipse([50, 50, 100, 100], fill=(255, 255, 255))
    path3 = os.path.join(output_dir, "sample_avatar.png")
    img3.save(path3, "PNG")
    print(f"Created: {path3} (Size: 150x150)")

if __name__ == "__main__":
    create_sample_images()
