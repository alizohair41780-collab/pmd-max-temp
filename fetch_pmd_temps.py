from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import os
import time

URL = "https://www.ncm.gov.ae/services/climate-reports-daily?lang=en"
EXCEL_FILE = "NCM_UAE_Daily_Climate_Report.xlsx"

def scrape_ncm_uae_daily():
    print("🚀 Starting NCM UAE Daily Climate Report Scraper...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()

        print(f"Loading NCM UAE Climate Report page...")
        page.goto(URL, wait_until="networkidle", timeout=90000)
        time.sleep(8)  # Wait for the big table to fully load

        # Save debug files (helpful if anything goes wrong)
        page.screenshot(path="debug_screenshot.png", full_page=True)
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        print("📸 Debug files saved (screenshot + HTML)")

        print("Extracting data from the table...")

        # Find all rows in the main table
        rows = page.locator("table tr").all()
        
        data = []
        report_date = "Unknown Date"

        for row in rows[1:]:   # Skip header row
            cells = row.locator("td").all()
            if len(cells) >= 7:   # Station + Precip + Humidity (3) + Temp (3) + Wind
                station = cells[0].inner_text().strip()
                max_temp = cells[5].inner_text().strip()   # Max °C column (adjust if needed)
                
                if station and max_temp and station != "Station":
                    data.append({
                        "Station": station,
                        "Max_Temperature_C": max_temp
                    })

        browser.close()

    if not data:
        print("❌ No data extracted. Check the debug files.")
        return

    print(f"✅ Successfully scraped {len(data)} stations!")

    # Create DataFrame and add date
    df = pd.DataFrame(data)
    today = datetime.now().strftime("%Y-%m-%d")
    df["Scrape_Date"] = today
    df["Report_Period"] = report_date

    # Save to Excel
    if os.path.exists(EXCEL_FILE):
        with pd.ExcelWriter(EXCEL_FILE, mode='a', if_sheet_exists='new', engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=today, index=False)
        print(f"Appended as new sheet: {today}")
    else:
        df.to_excel(EXCEL_FILE, sheet_name=today, index=False)
        print(f"Created new Excel file: {EXCEL_FILE}")

    # Update "Latest" sheet
    with pd.ExcelWriter(EXCEL_FILE, mode='a', if_sheet_exists='replace', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="Latest", index=False)

    print("🎉 Scraping completed successfully!")

if __name__ == "__main__":
    scrape_ncm_uae_daily()
