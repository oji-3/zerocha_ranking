import time
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def get_ranking_data():
    urls = ["https://mixch.tv/live/event/19995#ranking"]
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--disable-extensions")

    service = Service(executable_path="/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    data = [("UserID", "Points")]
    
    try:
        for url in urls:
            logging.info(f"Moving to: {url}")
            start_time = time.time()
            driver.get(url)

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "a.nav-link.active[data-rr-ui-event-key='#ranking']")
                    )
                )
            except Exception as e:
                logging.warning(f"Timeout or error: {url} => {e}")
                continue

            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            li_items = soup.select("ul.list li")

            for li in li_items:
                user_link = li.select_one("a.user-name")
                user_id = user_link["href"].split("/")[-1] if user_link else "N/A"
                point_tag = li.select_one("span.css-kidsya span.num")
                points = point_tag.get_text(strip=True).replace(",", "") if point_tag else "0"
                data.append((user_id, points))

            elapsed = time.time() - start_time
            logging.info(f"Fetched {len(li_items)} items from {url} in {elapsed:.2f} sec")
    finally:
        driver.quit()
    
    return data