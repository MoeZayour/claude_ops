#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

def discover():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')
    service = Service(executable_path='/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get("http://localhost:8089/web/login?db=mz-db")
        time.sleep(2)
        driver.find_element(By.ID, "login").send_keys("admin")
        driver.find_element(By.ID, "password").send_keys("admin")
        driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
        time.sleep(5)
        
        # Open Home Menu
        btn = driver.find_element(By.CSS_SELECTOR, "div.o_navbar_apps_menu button")
        btn.click()
        time.sleep(2)
        
        # Dump the whole body
        with open("/tmp/full_apps_view.html", "w") as f:
            f.write(driver.find_element(By.TAG_NAME, "body").get_attribute('outerHTML'))
        
        driver.save_screenshot("/opt/gemini_odoo19/screenshots/discovery_apps_full.png")
        print("✅ Full apps view dumped")
    finally:
        driver.quit()

if __name__ == "__main__":
    discover()
