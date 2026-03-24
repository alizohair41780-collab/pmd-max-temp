import pandas as pd
from playwright.sync_api import sync_playwright
import time
from datetime import datetime

def scrape_ncm_uae():
    print("🚀 Starting NCM UAE Scraper...")
    
    with sync_playwright() as p:
        # Open a browser window
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 2000})
        page = context.new_page()

        URL = "https://www.ncm.gov.ae/services/climate-reports-daily?lang=en"
        
        try:
            # Navigate to the website
            page.goto(URL, wait_until="domcontentloaded", timeout=120000)
            
            # Wait for the table to actually appear on screen
            print("⏳ Waiting for table to load...")
            page.wait_for_selector("table", timeout=60000)
            time.sleep(5)  # Brief pause to let numbers load

            # --- CAPTURE SCREENSHOT ---
            date_str = datetime.now().strftime("%Y-%m-%d")
            screenshot_name = f"ncm_snapshot_{date_str}.png"
            page.screenshot(path=screenshot_name, full_page=True)
            print(f"📸 Screenshot saved as: {screenshot_name}")

            # --- SCRAPE DATA ---
            rows = page.query_selector_all("table tr")
            data = []
            for row in rows:
                cols = row.query_selector_all("td")
                if len(cols) == 10:
                    row_data = [col.inner_text().strip() for col in cols]
                    data.append(row_data)

            # Create Excel File
            headers = [
                "No", "Stations", "Precipitation (mm)", 
                "Min Humidity %", "Max Humidity %", "Avg Humidity %",
                "Min Temp °C", "Max Temp °C", "Avg Temp °C", "Wind Speed km/h"
            ]
            df = pd.DataFrame(data, columns=headers)
            excel_name = f"UAE_Climate_Report_{date_str}.xlsx"
            df.to_excel(excel_name, index=False)
            
            print(f"✅ Scraped {len(df)} stations into {excel_name}")

        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    scrape_ncm_uae()
