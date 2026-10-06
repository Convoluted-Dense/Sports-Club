import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel='msedge')
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()

    # 1. Slide 2 of presentation.html
    page.goto("http://127.0.0.1:5000/presentation.html")
    time.sleep(1)
    page.evaluate("showSlide(2)")
    time.sleep(2.5)
    page.screenshot(path="report_assets/er_diagram_slide2.png")
    print("Slide 2 captured!")

    # 2. Direct embedded view of er_diagram.html
    page.goto("http://127.0.0.1:5000/er_diagram.html?embed=true")
    time.sleep(2.5)
    page.screenshot(path="report_assets/er_diagram_canvas_hd.png")
    print("Canvas HD captured!")

    browser.close()
