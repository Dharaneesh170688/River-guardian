from PIL import Image
import os

# The shield logo was shared directly in the conversation
# We need to crop just the shield from the first uploaded image
# The media artifact is the phone screenshot - let's work with what we have

src = 'C:/Users/dhara/.gemini/antigravity-ide/brain/a7585e79-17df-4c2d-8df7-d4d3a1bfae2e/media__1783815903571.png'
img = Image.open(src)
print(f"Source: {img.size} {img.mode}")

# The first image in the conversation is the shield logo - it's separate from the screenshot
# Let's check if there are any other media files in the artifact dir
import glob
files = glob.glob('C:/Users/dhara/.gemini/antigravity-ide/brain/a7585e79-17df-4c2d-8df7-d4d3a1bfae2e/media_*.png')
print("Media files:", files)
