import time
import logging
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def get_ranking_data():
    urls = ["https://mixch.tv/live/event/19995#ranking"]
    data = [("UserID", "Points")]
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox']
            )
            
            page = browser.new_page()
            
            for url in urls:
                try:
                    logging.info(f"Moving to: {url}")
                    start_time = time.time()
                    
                    page.goto(url, timeout=30000)
                    page.wait_for_selector("a.nav-link.active[data-rr-ui-event-key='#ranking']", timeout=10000)
                    
                    html = page.content()
                    soup = BeautifulSoup(html, "html.parser")
                    li_items = soup.select("ul.list li")
                    
                    for li in li_items:
                        user_link = li.select_one("a.user-name")
                        user_id = user_link["href"].split("/")[-1] if user_link and "href" in user_link.attrs else "N/A"
                        point_tag = li.select_one("span.css-kidsya span.num")
                        points = point_tag.get_text(strip=True).replace(",", "") if point_tag else "0"
                        data.append((user_id, points))
                    
                    elapsed = time.time() - start_time
                    logging.info(f"Fetched {len(li_items)} items from {url} in {elapsed:.2f} sec")
                
                except Exception as e:
                    logging.error(f"Error with URL {url}: {e}")
            
            browser.close()
    
    except Exception as e:
        logging.error(f"Playwright error: {e}")
    
    return data