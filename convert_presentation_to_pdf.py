import os
import time
from playwright.sync_api import sync_playwright
from PIL import Image

os.makedirs('presentation_slides', exist_ok=True)
slide_images = []

print("Starting slide capture from presentation.html...")

with sync_playwright() as p:
    # 1920x1080 (16:9 widescreen HD)
    browser = p.chromium.launch(headless=True, channel='msedge')
    context = browser.new_context(viewport={'width': 1920, 'height': 1080}, device_scale_factor=2)
    page = context.new_page()

    page.goto("http://127.0.0.1:5000/presentation.html")
    time.sleep(1.5)

    # Hide floating control buttons during capture for clean slides
    page.evaluate("""() => {
        const controls = document.getElementById('controls-bar');
        if (controls) controls.style.display = 'none';
        const resizeBar = document.querySelector('.resize-toolbar');
        if (resizeBar) resizeBar.style.display = 'none';
        const prog = document.querySelector('.progress-bar-container');
        if (prog) prog.style.display = 'none';
    }""")

    total_slides = 12

    for i in range(1, total_slides + 1):
        page.evaluate(f"showSlide({i})")
        # Wait for slide transition / iframe rendering (especially for Slide 2 ER diagram)
        wait_time = 2.5 if i == 2 else 0.8
        time.sleep(wait_time)

        img_path = f"presentation_slides/slide_{i:02d}.png"
        
        # Capture active slide or page viewport
        active_slide = page.query_selector(f"#slide-{i}")
        if active_slide:
            active_slide.screenshot(path=img_path)
        else:
            page.screenshot(path=img_path)

        print(f"Captured Slide {i:02d}/{total_slides}: {img_path}")
        slide_images.append(img_path)

    browser.close()

print("\nAll 12 slides captured. Assembling into PDF...")

# Load images using PIL and convert to RGB
pil_images = []
for p in slide_images:
    img = Image.open(p)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    pil_images.append(img)

pdf_filename = "presentation2.pdf"
if pil_images:
    pil_images[0].save(
        pdf_filename,
        save_all=True,
        append_images=pil_images[1:],
        quality=95,
        optimize=True
    )
    print(f"\nSuccessfully generated {pdf_filename} via PIL (Size: {os.path.getsize(pdf_filename)} bytes)")

# Also create a high-fidelity PDF via HTML + Playwright with exact 16:9 landscape printing
html_slides = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page {
    size: 1920px 1080px;
    margin: 0;
  }
  body {
    margin: 0;
    padding: 0;
    background: #0d1117;
  }
  .slide-page {
    width: 1920px;
    height: 1080px;
    page-break-after: always;
    break-after: page;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }
  .slide-page img {
    width: 1920px;
    height: 1080px;
    object-fit: contain;
    display: block;
  }
</style>
</head>
<body>
"""

for p in slide_images:
    abs_p = os.path.abspath(p).replace('\\', '/')
    html_slides += f'<div class="slide-page"><img src="file:///{abs_p}"></div>\n'

html_slides += "</body></html>"

with open("presentation_print.html", "w", encoding="utf-8") as f:
    f.write(html_slides)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel='msedge')
    page = browser.new_page()
    page.goto(f"file:///{os.path.abspath('presentation_print.html')}")
    time.sleep(1)
    page.pdf(
        path=pdf_filename,
        width="1920px",
        height="1080px",
        print_background=True,
        margin={"top": "0px", "bottom": "0px", "left": "0px", "right": "0px"}
    )
    browser.close()

print(f"High-fidelity PDF written to {pdf_filename} (Size: {os.path.getsize(pdf_filename)} bytes)")
