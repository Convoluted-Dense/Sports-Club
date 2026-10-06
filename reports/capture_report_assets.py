import os
import time
from playwright.sync_api import sync_playwright

os.makedirs('report_assets', exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel='msedge')
    context = browser.new_context(viewport={'width': 1280, 'height': 800})
    page = context.new_page()

    # 1. Login Screen
    page.goto('http://127.0.0.1:5000')
    time.sleep(1)
    page.screenshot(path='report_assets/01_login_screen.png')
    print('1. Captured Login')

    # 2. Admin Dashboard
    page.fill('#login-email', 'Admin')
    page.fill('#login-password', 'Admin')
    page.click('form button[type="submit"]')
    time.sleep(1.5)
    page.screenshot(path='report_assets/02_admin_dashboard.png')
    print('2. Captured Admin Dashboard')

    # 3. Admin Table Explorer
    page.click('button[data-tab="a-tables"]')
    time.sleep(1)
    page.screenshot(path='report_assets/03_admin_table_explorer.png')
    print('3. Captured Admin Table Explorer')

    # 4. Admin Smart SQL Studio
    page.click('button[data-tab="a-studio"]')
    time.sleep(1)
    page.fill('#smart-sql-prompt', 'Show club rosters with sports, coaches, and enrolled athletes')
    page.click('#smart-sql-submit-btn')
    time.sleep(1.5)
    page.screenshot(path='report_assets/04_smart_sql_studio.png')
    print('4. Captured Smart SQL Studio')

    # 5. Admin ER Diagram tab
    page.goto('http://127.0.0.1:5000/er_diagram.html')
    time.sleep(1.5)
    page.screenshot(path='report_assets/05_er_diagram.png')
    print('5. Captured ER Diagram')

    # 6. Member Portal Dashboard
    page.goto('http://127.0.0.1:5000')
    page.evaluate('localStorage.clear()')
    page.goto('http://127.0.0.1:5000')
    time.sleep(1)
    page.fill('#login-email', 'aarav.sharma@gmail.com')
    page.fill('#login-password', 'aaravsharma')
    page.click('form button[type="submit"]')
    time.sleep(1.5)
    page.screenshot(path='report_assets/06_member_dashboard.png')
    print('6. Captured Member Dashboard')

    # 7. Member Clubs & Roles Tab (Join & Leave feature)
    page.click('button[data-tab="m-clubs"]')
    time.sleep(1)
    page.screenshot(path='report_assets/07_member_clubs_join_leave.png')
    print('7. Captured Member Clubs')

    # 8. Member Payments & Checkout
    page.click('button[data-tab="m-payments"]')
    time.sleep(0.5)
    page.click('button:has-text("Renew / Upgrade Plan")')
    time.sleep(1)
    page.screenshot(path='report_assets/08_checkout_screen.png')
    print('8. Captured Checkout')

    # 9. Presentation Deck
    page.goto('http://127.0.0.1:5000/presentation.html')
    time.sleep(1.5)
    page.screenshot(path='report_assets/09_presentation_deck.png')
    print('9. Captured Presentation Deck')

    browser.close()

print('All screenshots captured successfully!')
