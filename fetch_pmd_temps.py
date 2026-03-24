from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import os

# ================== CONFIG ==================
URL = "https://www.pmd.gov.pk/datadecoders/pmd-maxtemp-print-filtered.php/?rmc=0"
EXCEL_FILE = "PMD_Max_Temperatures.xlsx"
# ===========================================

def scrape_pmd_max_temperatures():
    print("Starting PMD Max Temperature Scraper...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"Loading page: {URL}")
        page.goto(URL, wait_until="networkidle", timeout=60000)
        
        # Wait for table to load
        page.wait_for_selector("table", timeout=30000)
        
        # Extract date from page
        try:
            date_text = page.locator("text=Maximum Temperatures").first.inner_text()
            print(f"Found date info: {date_text}")
        except:
            date_text = "Unknown Date"
        
        # Get all table rows
        rows = page.locator("table tr").all()
        
        data = []
        for row in rows[1:]:  # Skip header row
            cells = row.locator("td").all()
            if len(cells) >= 2:
                city = cells[0].inner_text().strip()
                temp = cells[1].inner_text().strip()
                if city and temp:
                    data.append({"City": city, "Max_Temperature_C": temp})
        
        browser.close()

    if not data:
        print("No data found! Check the website structure.")
        return

    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Add scrape date
    today = datetime.now().strftime("%Y-%m-%d")
    df["Scrape_Date"] = today
    df["Source_Date"] = date_text

    print(f"\nScraped {len(df)} cities on {today}")

    # Save to Excel (append if file exists, create new otherwise)
    if os.path.exists(EXCEL_FILE):
        with pd.ExcelWriter(EXCEL_FILE, mode='a', if_sheet_exists='new', engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=today, index=False)
        print(f"Data appended to existing file as new sheet: {today}")
    else:
        df.to_excel(EXCEL_FILE, sheet_name=today, index=False)
        print(f"New Excel file created: {EXCEL_FILE}")

    # Also save latest data as "Latest" sheet
    with pd.ExcelWriter(EXCEL_FILE, mode='a', if_sheet_exists='replace', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="Latest", index=False)

    print("Scraping completed successfully!")


if __name__ == "__main__":
    scrape_pmd_max_temperatures()
