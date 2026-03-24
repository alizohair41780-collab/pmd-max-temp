from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import os
import time

URL = "https://metkhi.pmd.gov.pk/Max-Temp.php"
EXCEL_FILE = "PMD_Sindh_Max_Temperatures.xlsx"

def scrape_pmd_sindh():
    print("🚀 Starting Sindh Max Temperature Scraper (Final Attempt)...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=1000)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0",
            viewport={"width": 1920, "height": 1080},
            locale="en-PK",
            timezone_id="Asia/Karachi",
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.pmd.gov.pk/"
            }
        )
        page = context.new_page()

        print(f"Loading: {URL}")
        page.goto(URL, wait_until="networkidle", timeout=120000)
        time.sleep(12)

        page.screenshot(path="debug_screenshot.png", full_page=True)
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(page.content())

        print("Debug files saved.")

        # Look for any table
        tables = page.locator("table").all()
        print(f"Found {len(tables)} table(s)")

        data = []
        for table in tables:
            rows = table.locator("tr").all()
            for row in rows[1:]:   # skip header
                cells = row.locator("td").all()
                if len(cells) >= 2:
                    city = cells[0].inner_text().strip()
                    temp = cells[1].inner_text().strip().replace("°C", "").strip()
                    if city and temp and len(city) > 1:
                        data.append({"City": city, "Max_Temperature_C": temp})

        browser.close()

    if not data:
        print("❌ Still blocked (403). Automation not possible right now.")
        return

    # Save data if any
    df = pd.DataFrame(data)
    today = datetime.now().strftime("%Y-%m-%d")
    df["Scrape_Date"] = today

    if os.path.exists(EXCEL_FILE):
        with pd.ExcelWriter(EXCEL_FILE, mode='a', if_sheet_exists='new', engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=today, index=False)
    else:
        df.to_excel(EXCEL_FILE, sheet_name=today, index=False)

    with pd.ExcelWriter(EXCEL_FILE, mode='a', if_sheet_exists='replace', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="Latest", index=False)

    print("✅ Success! Excel updated.")

if __name__ == "__main__":
    scrape_pmd_sindh()
