import re
import pandas as pd
from playwright.sync_api import sync_playwright

def fetch_max_temps():
    url = 'https://metkhi.pmd.gov.pk/Max-Temp.php'
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        
        # Extra wait for the table to fully load (this fixes most cloud issues)
        page.wait_for_timeout(8000)
        page.wait_for_selector('div.date', timeout=15000)
        
        html = page.content()
        browser.close()
    
    print("✅ Page loaded. HTML length:", len(html))
    
    # Extract date
    date_match = re.search(r'class="date">\s*([^<]+)\s*</div>', html)
    date_str = date_match.group(1).strip() if date_match else 'Unknown'
    date_str = re.sub(r'^[^0-9]+', '', date_str)
    date_str = re.sub(r'\s+\d{1,2}:\d{2}:\d{2}.*$', '', date_str).strip()
    print("📅 Extracted date:", date_str)
    
    # Extract temperatures
    temp_regex = r'<tr><td>\d+<\/td><td>\d+<\/td><td>[^<]+<\/td><td>([\d.]+)<\/td><\/tr>'
    temps = re.findall(temp_regex, html)
    print("🔢 Found temperatures:", len(temps))
    
    if len(temps) != 19:
        print("⚠️ ERROR: Expected 19 rows but found", len(temps))
        print("First 300 characters of HTML for debugging:")
        print(html[:300])
        print("Last 300 characters of HTML:")
        print(html[-300:])
        return  # This caused the exit code 1
    
    stations = ["BADIN","CHHOR","DADU","HYDERABAD","HYDERABAD AIRPORT","JACOBABAD","KARACHI","KHAIRPUR","LARKANA","MIR PUR KHAS","MITHI","MOHENJO DARO","NAWABSHAH","PADIDAN","ROHRI","SAKRAND","SUKKUR","TANDO JAM","THATTA"]
    
    today_data = {'Date': [date_str]} | {station: [float(temp)] for station, temp in zip(stations, temps)}
    today_df = pd.DataFrame(today_data)
    
    excel_file = 'PMD_Max_Temperatures.xlsx'
    
    try:
        existing_df = pd.read_excel(excel_file)
        if date_str in existing_df['Date'].astype(str).values:
            existing_df.loc[existing_df['Date'].astype(str) == date_str, stations] = today_df[stations].values
            print(f"✅ Updated → {date_str}")
        else:
            existing_df = pd.concat([existing_df, today_df], ignore_index=True)
            print(f"✅ Added new row → {date_str}")
    except FileNotFoundError:
        existing_df = today_df
        print(f"✅ Created new Excel → {date_str}")
    
    existing_df.to_excel(excel_file, index=False)
    print(f"📁 Excel updated successfully!")

if __name__ == "__main__":
    fetch_max_temps()
