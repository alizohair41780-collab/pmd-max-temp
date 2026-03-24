from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import os
import time

URL = "https://metkhi.pmd.gov.pk/Max-Temp.php"   # ← Your desired Sindh page
EXCEL_FILE = "PMD_Max_Temperatures.xlsx"

def scrape_pmd_max_temperatures():
    print("🚀 Starting Sindh Max Temperature Scraper...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print(f"Loading Sindh Max Temp page: {URL}")
        page.goto(URL, wait_until="networkidle", timeout=90000)
        time.sleep(8)  # Give time for table to load

        # Debugging files
        page.screenshot(path="debug_screenshot.png")
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        print("📸 Screenshot and HTML saved for debugging")

        # Find the table (Sindh page usually has one main table)
        print("Looking for temperature table...")
        table = page.locator("table").first
        rows = table.locator("tr").all()

        data = []
        date_info = "Unknown Date"

        for i, row in enumerate(rows):
            cells = row.locator("td").all()
            if len(cells) >= 2:
                city = cells[0].inner_text().strip()
                temp = cells[1].inner_text().strip().replace("°C", "").replace(" ", "")
                
                if city and temp and city.upper() != "STATION" and city.upper() != "CITY":
                    data.append({"City": city, "Max_Temperature_C": temp})
            elif len(cells) == 1 and i < 3:   # Try to capture date from top rows
                date_info = cells[0].inner_text().strip()

        browser.close()

    if not data:
        print("❌ No data extracted from Sindh page. Check debug files.")
        return

    print(f"✅ Scraped {len(data)} stations from Sindh. Date: {date_info}")

    # Save to Excel
    df = pd.DataFrame(data)
    today = datetime.now().strftime("%Y-%m-%d")
    df["Scrape_Date"] = today
    df["Source_Date"] = date_info

    if os.path.exists(EXCEL_FILE):
        with pd.ExcelWriter(EXCEL_FILE, mode='a', if_sheet_exists='new', engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=today, index=False)
        print(f"Appended new sheet: {today}")
    else:
        df.to_excel(EXCEL_FILE, sheet_name=today, index=False)
        print(f"Created new Excel file: {EXCEL_FILE}")

    # Update Latest sheet
    with pd.ExcelWriter(EXCEL_FILE, mode='a', if_sheet_exists='replace', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="Latest", index=False)

    print("🎉 Done! Excel file is ready.")

if __name__ == "__main__":
    scrape_pmd_max_temperatures()
