import time
import logging
import subprocess
import sys
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def install_playwright_browser():
    """Install Playwright browser automatically for environments like Streamlit Cloud"""
    try:
        logging.info("Installing Playwright browser...")
        from playwright.__main__ import main
        sys.argv = ['playwright', 'install', 'chromium']
        main()
        logging.info("Playwright browser installation complete")
    except Exception as e:
        logging.error(f"Failed to install Playwright browser: {e}")
        # Fallback method using subprocess
        try:
            subprocess.check_call([
                sys.executable, "-m", 
                "playwright", "install", "chromium"
            ])
            logging.info("Playwright browser installation complete (subprocess)")
        except Exception as sub_e:
            logging.error(f"Subprocess installation failed: {sub_e}")

def get_ranking_data():
    # Ensure browser is installed
    install_playwright_browser()
    
    urls = ["https://mixch.tv/live/event/19995#ranking"]
    data = [("UserID", "Points")]
    
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            for url in urls:
                logging.info(f"Moving to: {url}")
                start_time = time.time()
                page.goto(url, wait_until="networkidle")

                try:
                    # Wait for the ranking tab to be active
                    page.wait_for_selector("a.nav-link.active[data-rr-ui-event-key='#ranking']", timeout=10000)
                except Exception as e:
                    logging.warning(f"Timeout or error: {url} => {e}")
                    continue

                html = page.content()
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
            browser.close()
    
    return data