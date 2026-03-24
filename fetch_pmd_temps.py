import pandas as pd
from playwright.sync_api import sync_playwright
import time
from datetime import datetime
import os

def scrape_ncm_uae():
    print("🚀 Starting NCM UAE Scraper...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 2000})
        page = context.new_page()

        URL = "https://www.ncm.gov.ae/services/climate-reports-daily?lang=en"
        
        try:
            print(f"🔗 Navigating to {URL}")
            page.goto(URL, wait_until="domcontentloaded", timeout=120000)
            
            # Wait for the table to appear
            print("⏳ Waiting for the data table...")
            page.wait_for_selector("table", timeout=60000)
            time.sleep(5) # Let the JavaScript finish loading numbers

            # --- CAPTURE SCREENSHOT ---
            date_str = datetime.now().strftime("%Y-%m-%d")
            screenshot_name = f"ncm_snapshot_{date_str}.png"
            page.screenshot(path=screenshot_name, full_page=True)
            print(f"📸 Screenshot saved: {screenshot_name}")

            # --- SCRAPE DATA (Stable Method) ---
            print("📊 Extracting table data...")
            data = page.evaluate("""() => {
                const rows = Array.from(document.querySelectorAll('table tr'));
                return rows.map(row => {
                    const cols = Array.from(row.querySelectorAll('td'));
                    return cols.map(col => col.innerText.trim());
                }).filter(row => row.length === 10);
            }""")

            if not data:
                print("⚠️ No data found. The table might be empty or layout changed.")
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
