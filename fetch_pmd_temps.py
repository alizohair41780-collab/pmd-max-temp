from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import os
import time

URL = "https://pmd.gov.pk/datadecoders/pmd-maxtemp-print-filtered.php/?rmc=0"
EXCEL_FILE = "PMD_Max_Temperatures.xlsx"

def scrape_pmd_max_temperatures():
    print("🚀 Starting PMD Max Temperature Scraper...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()

        print(f"Loading URL: {URL}")
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)  # Extra wait for dynamic content

        # Try multiple ways to find the table
        print("Looking for temperature table...")
        table = None
        selectors = ["table", "tbody", ".table", "table[class*='table']"]
        
        for sel in selectors:
            try:
                table = page.locator(sel).first
                if table.count() > 0:
                    print(f"Found table using selector: {sel}")
                    break
            except:
                pass

        if not table:
            print("❌ No table found on the page. Saving page content for debugging...")
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            browser.close()
            raise Exception("Table not found - check debug_page.html")

        # Extract rows
        rows = table.locator("tr").all()
        data = []
        date_info = "Unknown Date"

        for i, row in enumerate(rows):
            cells = row.locator("td").all()
            if len(cells) >= 2:
                city = cells[0].inner_text().strip()
                temp = cells[1].inner_text().strip().replace("°C", "").strip()
                if city and temp and city.upper() != "CITY":
                    data.append({"City": city, "Max_Temperature_C": temp})
            elif len(cells) == 1 and i == 0:  # Try to get date from first row
                date_info = cells[0].inner_text().strip()

        browser.close()

    if not data:
        print("❌ No temperature data extracted!")
        return

    print(f"✅ Successfully scraped {len(data)} cities. Date info: {date_info}")

    # Create DataFrame
    df = pd.DataFrame(data)
    today = datetime.now().strftime("%Y-%m-%d")
    df["Scrape_Date"] = today
    df["Source_Date"] = date_info

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
    scrape_pmd_temps.py
