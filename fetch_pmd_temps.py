from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import os
import time

URL = "https://metkhi.pmd.gov.pk/Max-Temp.php"
EXCEL_FILE = "PMD_Sindh_Max_Temperatures.xlsx"   # Renamed for clarity

def scrape_pmd_sindh_max_temp():
    print("🚀 Starting Sindh Max Temperature Scraper...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
            locale="en-US",
            timezone_id="Asia/Karachi"
        )
        page = context.new_page()

        print(f"Loading page: {URL}")
        response = page.goto(URL, wait_until="networkidle", timeout=90000)
        
        print(f"Response status: {response.status if response else 'Unknown'}")
        
        time.sleep(10)   # Extra long wait

        # Save debug files
        page.screenshot(path="debug_screenshot.png", full_page=True)
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        print("📸 Debug files saved: debug_screenshot.png and debug_page.html")

        # Try to find table
        print("Searching for table...")
        tables = page.locator("table").all()
        print(f"Found {len(tables)} table(s) on the page")

        data = []
        date_info = "Unknown Date"

        for table in tables:
            rows = table.locator("tr").all()
            for row in rows:
                cells = row.locator("td").all()
                if len(cells) >= 2:
                    city = cells[0].inner_text().strip()
                    temp = cells[1].inner_text().strip().replace("°C", "").strip()
                    if city and temp and len(city) > 2 and "station" not in city.lower():
                        data.append({"City": city, "Max_Temperature_C": temp})

        browser.close()

    if not data:
        print("❌ Still no data extracted. The website is likely blocking automated access.")
        print("   Please download debug_screenshot.png and check what it shows.")
        return

    print(f"✅ Successfully scraped {len(data)} stations!")

    # Save data
    df = pd.DataFrame(data)
    today = datetime.now().strftime("%Y-%m-%d")
    df["Scrape_Date"] = today
    df["Source_Date"] = date_info

    if os.path.exists(EXCEL_FILE):
        with pd.ExcelWriter(EXCEL_FILE, mode='a', if_sheet_exists='new', engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=today, index=False)
    else:
        df.to_excel(EXCEL_FILE, sheet_name=today, index=False)

    with pd.ExcelWriter(EXCEL_FILE, mode='a', if_sheet_exists='replace', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="Latest", index=False)

    print("🎉 Excel file updated successfully!")

if __name__ == "__main__":
    scrape_pmd_sindh_max_temp()
