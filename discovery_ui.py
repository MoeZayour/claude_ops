#!/usr/bin/env python3
"""
OPS Framework - UI Selector Discovery Script
Dumps DOM structure to identify correct selectors for Odoo 17/18
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import os

def discover():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')
    
    service = Service(executable_path='/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 20)
    
    try:
        print("🚀 Navigating to Odoo...")
        driver.get("http://localhost:8089/web/login?db=mz-db")
        time.sleep(3)
        
        # Login
        driver.find_element(By.ID, "login").send_keys("admin")
        driver.find_element(By.ID, "password").send_keys("admin")
        driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
        
        print("🔐 Logged in, waiting for dashboard...")
        time.sleep(10)
        
        # Take screenshot of main view
        driver.save_screenshot("/opt/gemini_odoo19/screenshots/discovery_main.png")
        
        # Dump navbar HTML
        try:
            navbar = driver.find_element(By.CSS_SELECTOR, "nav.o_main_navbar, .o_navbar, header")
            with open("/tmp/navbar_dump.html", "w") as f:
                f.write(navbar.get_attribute('outerHTML'))
            print("📦 Navbar HTML dumped to /tmp/navbar_dump.html")
        except:
            print("❌ Could not find navbar")
            # Dump body if navbar not found
            with open("/tmp/body_dump.html", "w") as f:
                f.write(driver.find_element(By.TAG_NAME, "body").get_attribute('outerHTML'))

        # Try to open app switcher and dump
        try:
            # Try various app switcher toggles
            toggles = [
                "nav.o_main_navbar .o_navbar_apps_menu",
                ".o_menu_toggle",
                "i.oi-apps",
                ".o_app_switcher_toggle"
            ]
            for selector in toggles:
                try:
                    toggle = driver.find_element(By.CSS_SELECTOR, selector)
                    toggle.click()
                    print(f"✅ Opened App Switcher with {selector}")
                    time.sleep(2)
                    driver.save_screenshot("/opt/gemini_odoo19/screenshots/discovery_apps.png")
                    apps_view = driver.find_element(By.CSS_SELECTOR, ".o_app_switcher, .o_apps")
                    with open("/tmp/apps_dump.html", "w") as f:
                        f.write(apps_view.get_attribute('outerHTML'))
                    break
                except: continue
        except:
            print("❌ Failed to dump App Switcher")

        # Try search
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.CONTROL, 'k')
            time.sleep(2)
            driver.save_screenshot("/opt/gemini_odoo19/screenshots/discovery_command.png")
            try:
                command_palette = driver.find_element(By.CSS_SELECTOR, ".o_command_palette")
                with open("/tmp/command_dump.html", "w") as f:
                    f.write(command_palette.get_attribute('outerHTML'))
            except: pass
        except:
            print("❌ Failed to dump Command Palette")

    finally:
        driver.quit()

if __name__ == "__main__":
    discover()
