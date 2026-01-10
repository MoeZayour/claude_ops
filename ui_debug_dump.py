import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

ODOO_URL = "http://localhost:8089"
DUMP_DIR = "/opt/gemini_odoo19/debug_dump"
if not os.path.exists(DUMP_DIR): os.makedirs(DUMP_DIR)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=chrome_options)

def dump_view(name, url):
    print(f"Dumping {name}...")
    driver.get(f"{ODOO_URL}{url}")
    time.sleep(10)
    with open(os.path.join(DUMP_DIR, f"{name}.html"), "w") as f:
        f.write(driver.page_source)
    driver.save_screenshot(os.path.join(DUMP_DIR, f"{name}.png"))

try:
    # 1. Login Page
    dump_view("login", "/web/login")
    
    # 2. Try to log in to see other pages
    driver.find_element(By.CSS_SELECTOR, "input[name='login']").send_keys("admin")
    driver.find_element(By.CSS_SELECTOR, "input[name='password']").send_keys("admin")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(10)
    
    # 3. Business Units
    dump_view("business_units", "/web#action=ops_matrix_core.action_ops_business_unit")
    
    # 4. Products
    dump_view("products", "/web#action=product.product_normal_action_sell")

finally:
    driver.quit()
