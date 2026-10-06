import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel='msedge')
    context = browser.new_context(viewport={'width': 1600, 'height': 1000})
    page = context.new_page()

    # 1. Open presentation.html and navigate to slide 2
    page.goto("http://127.0.0.1:5000/presentation.html")
    time.sleep(1)
    # Click next button or call showSlide(2)
    page.evaluate("showSlide(2)")
    time.sleep(2)
    page.screenshot(path="report_assets/presentation_slide_2_er.png")
    print("Captured presentation slide 2")

    # 2. Open er_diagram.html in high resolution directly
    page.goto("http://127.0.0.1:5000/er_diagram.html")
    time.sleep(2)
    page.screenshot(path="report_assets/er_diagram_fullscreen.png")
    print("Captured fullscreen ER diagram")

    browser.close()

print("ER Screenshots updated!")
