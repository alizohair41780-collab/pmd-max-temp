import pandas as pd
from playwright.sync_api import sync_playwright
import time

def scrape_ncm_uae_daily():
    print("🚀 Starting NCM UAE Daily Climate Report Scraper...")
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        URL = "https://www.ncm.gov.ae/services/climate-reports-daily?lang=en"
        
        try:
            # 1. Navigate and wait for the main content
            page.goto(URL, wait_until="domcontentloaded", timeout=120000)
            
            # 2. The table is often inside a specific container. 
            # We wait for the 'Stations' text to appear to ensure the table is loaded.
            print("Loading NCM UAE Climate Report table...")
            page.wait_for_selector("table", timeout=60000)
            
            # Give it 5 extra seconds for the JavaScript to populate the numbers
            time.sleep(5)

            # 3. Extract the table rows
            rows = page.query_selector_all("table tr")
            data = []

            for row in rows:
                cols = row.query_selector_all("td")
                if len(cols) > 0:
                    # Clean the text from each cell
                    row_data = [col.inner_text().strip() for col in cols]
                    data.append(row_data)

            # 4. Define Headers based on your screenshot
            headers = [
                "No", "Stations", "Precipitation (mm)", 
                "Min Humidity %", "Max Humidity %", "Avg Humidity %",
                "Min Temp °C", "Max Temp °C", "Avg Temp °C", "Wind Speed km/h"
            ]

            # 5. Create DataFrame and Save
            # We only take rows that have the correct number of columns
            df = pd.DataFrame([r for r in data if len(r) == 10], columns=headers)
            
            filename = "NCM_UAE_Daily_Climate_Report.xlsx"
            df.to_excel(filename, index=False)
            
            print(f"✅ Successfully scraped {len(df)} stations!")
            print(f"Created file: {filename}")

        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            page.screenshot(path="error_debug.png") # Saves a photo of what went wrong
        finally:
            browser.close()

if __name__ == "__main__":
    scrape_ncm_uae_daily()
