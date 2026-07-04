"""Debug script to find correct Quora DOM selectors."""
import time, os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
load_dotenv()

DIR = os.path.dirname(__file__)
profile_dir = os.path.join(DIR, "data", "quora_chrome_profile")

options = webdriver.ChromeOptions()
options.add_argument(f"--user-data-dir={profile_dir}")
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    q = "What is the best AI voice generator in 2026"
    url = f"https://www.quora.com/search?q={q.replace(' ','+')}&type=question"
    print(f"Going to: {url}")
    driver.get(url)
    time.sleep(5)

    print(f"\nPage title: {driver.title}")
    print(f"Current URL: {driver.current_url}")

    # Print all <a> hrefs to find question links
    links = driver.find_elements(By.TAG_NAME, "a")
    print(f"\nFound {len(links)} links total. First 20 with /quora.com in href:")
    count = 0
    for a in links:
        href = a.get_attribute("href") or ""
        text = a.text.strip()[:80]
        if "quora.com" in href and text and count < 20:
            print(f"  href: {href[:100]}")
            print(f"  text: {text}")
            print()
            count += 1

    # Save page source for inspection
    src_path = os.path.join(DIR, "data", "quora_debug.html")
    with open(src_path, "w", encoding="utf-8") as f:
        f.write(driver.page_source[:50000])
    print(f"\nPage source (50KB) saved to: {src_path}")

    input("Press Enter to close...")
finally:
    driver.quit()
