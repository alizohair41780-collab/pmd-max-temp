import pandas as pd
from playwright.sync_api import sync_playwright
import time
from datetime import datetime
import os

def scrape_ncm_uae():
    print("🚀 Starting NCM UAE Scraper...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a standard desktop window size
        context = browser.new_context(viewport={'width': 1280, 'height': 2000})
        page = context.new_page()

        URL = "https://www.ncm.gov.ae/services/climate-reports-daily?lang=en"
        
        try:
            print(f"🔗 Navigating to {URL}")
            page.goto(URL, wait_until="domcontentloaded", timeout=120000)
            
            # Wait for the table container to appear
            print("⏳ Waiting for the data table...")
            page.wait_for_selector("table", timeout=60000)
            
            # Give the JavaScript 5 seconds to fill the table with numbers
            time.sleep(5)

            # Capture Screenshot
            date_str = datetime.now().strftime("%Y-%m-%d")
            screenshot_name = f"ncm_snapshot_{date_str}.png"
            page.screenshot(path=screenshot_name, full_page=True)
            print(f"📸 Screenshot saved: {screenshot_name}")

            # Scrape Table
            rows = page.query_selector_all("table tr")
            data = []
            for row in rows:
                cols = row.query_selector_all("td")
                if len(cols) == 10:
                    data.append([col.inner_text().strip() for col in cols])

            if not data:
                print("⚠️ No data found in the table. Check the website layout.")
                return

            # Save to Excel
            headers = ["No", "Stations", "Precipitation", "Min Hum", "Max Hum", "Avg Hum", "Min Temp", "Max Temp", "Avg Temp", "Wind"]
            df = pd.DataFrame(data, columns=headers)
            excel_name = f"UAE_Report_{date_str}.xlsx"
            df.to_excel(excel_name, index=False)
            
            print(f"✅ Success! Created {excel_name}")

        except Exception as e:
            print(f"❌ Scraping failed: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    scrape_ncm_uae()
