import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- GOOGLE DRIVE SETTINGS ---
# Note: If you want files to go directly inside the "2026" folder, 
# make sure this ID matches the one in your URL when you are INSIDE that folder.
FOLDER_ID = "1wN8BNnwAYOLspRmlBGnxfH5vaUsMfbWL"

def upload_to_drive(file_path):
    print(f"🚀 Preparing to upload {file_path} to Google Drive...")
    try:
        # Load the secret key from GitHub environment
        if "GDRIVE_SERVICE_ACCOUNT_KEY" not in os.environ:
            print("❌ Error: GDRIVE_SERVICE_ACCOUNT_KEY not found in Environment Variables!")
            return

        service_account_info = json.loads(os.environ["GDRIVE_SERVICE_ACCOUNT_KEY"])
        credentials = service_account.Credentials.from_service_account_info(service_account_info)
        
        service = build('drive', 'v3', credentials=credentials)
        
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [FOLDER_ID]
        }
        
        # Using resumable=True helps with larger PDF files
        media = MediaFileUpload(file_path, mimetype='application/pdf', resumable=True)
        
        file = service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields='id, name, parents'
        ).execute()
        
        print(f"✅ Success! File uploaded to Drive.")
        print(f"📄 File Name: {file.get('name')}")
        print(f"🆔 File ID: {file.get('id')}")
        print(f"📍 Parent Folder: {file.get('parents')}")

    except Exception as e:
        print(f"❌ Drive Upload Error: {e}")

async def scrape_ncm_to_pdf():
    async with async_playwright() as p:
        # Launching browser
        browser = await p.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
        context = await browser.new_context(viewport={"width": 1280, "height": 1000})
        page = await context.new_page()
        
        url = "https://www.ncm.gov.ae/services/climate-reports-daily?lang=en"
        print(f"🔗 Navigating to {url}")
        
        try:
            # Increase timeout for slow loading weather data
            await page.goto(url, wait_until="networkidle", timeout=120000)
            
            # --- 1. DISMISS COOKIES ---
            print("⏳ Handling cookie banner...")
            try:
                await page.click("text='I Agree'", timeout=10000)
                await asyncio.sleep(2)
            except:
                print("⚠️ Cookie banner not found or already closed.")

            # --- 2. SCROLL TO LOAD ALL WEATHER STATIONS ---
            print("📜 Scrolling to load data rows...")
            for _ in range(15): 
                await page.mouse.wheel(0, 800)
                await asyncio.sleep(0.5)

            # --- 3. CLEAN PAGE FOR PDF ---
            print("🧹 Removing website headers/footers for a clean report...")
            await page.evaluate("""
                const selectors = [
                    'header', 'footer', '.header', '.footer', 
                    '.cookie-bar', '.cc-window', '#top-nav', 
                    '.modal-backdrop', '.breadcrumb'
                ];
                selectors.forEach(s => {
                    document.querySelectorAll(s).forEach(el => el.style.display = 'none');
                });
            """)

            # --- 4. GENERATE FILENAME (PKT) ---
            pkt_now = datetime.utcnow() + timedelta(hours=5)
            timestamp_str = pkt_now.strftime("%Y-%m-%d (%I.%M %p PKT)")
            pdf_name = f"ncm_report_{timestamp_str}.pdf"
            
            # --- 5. CREATE PDF ---
            print(f"📄 Generating Copyable PDF: {pdf_name}")
            # format="A4" ensures it fits standard document sizes
            await page.pdf(
                path=pdf_name, 
                format="A4", 
                print_background=True,
                margin={"top": "20px", "bottom": "20px", "left": "20px", "right": "20px"}
            )
            
            # --- 6. UPLOAD ---
            if os.path.exists(pdf_name):
                upload_to_drive(pdf_name)
            else:
                print("❌ PDF was not created locally.")
            
        except Exception as e:
            print(f"❌ Scraper Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_ncm_to_pdf())
