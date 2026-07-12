from PIL import Image
import os

shield_src = 'C:/Users/dhara/.gemini/antigravity-ide/brain/a7585e79-17df-4c2d-8df7-d4d3a1bfae2e/media__1783818658185.png'
img = Image.open(shield_src).convert("RGBA")

res_base = 'c:/Users/dhara/Downloads/topcorn-master/topcorn-master/app/src/main/res'

# Android mipmap icon sizes: (folder, size)
mipmap_sizes = [
    ('mipmap-mdpi',    48),
    ('mipmap-hdpi',    72),
    ('mipmap-xhdpi',   96),
    ('mipmap-xxhdpi',  144),
    ('mipmap-xxxhdpi', 192),
]

for folder, size in mipmap_sizes:
    resized = img.resize((size, size), Image.LANCZOS)
    for fname in ['ic_launcher.png', 'ic_launcher_round.png']:
        out_path = os.path.join(res_base, folder, fname)
        resized.save(out_path, 'PNG')
        print(f"Saved {out_path} ({size}x{size})")

# Also replace drawable/logo.png (splash screen logo)
# Use a larger size for splash - 512x512
splash = img.resize((512, 512), Image.LANCZOS)
splash_path = os.path.join(res_base, 'drawable', 'logo.png')
splash.save(splash_path, 'PNG')
print(f"Saved {splash_path} (512x512)")

print("\nDone! All icons replaced.")
