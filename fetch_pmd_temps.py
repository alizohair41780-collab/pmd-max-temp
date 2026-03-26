import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- GOOGLE DRIVE SETTINGS ---
FOLDER_ID = "1wN8BNnwAYOLspRmlBGnxfH5vaUsMfbWL"

def upload_to_drive(file_path):
    print(f"🚀 Preparing to upload {file_path} to Google Drive...")
    try:
        # Load the secret key from GitHub environment
        service_account_info = json.loads(os.environ["GDRIVE_SERVICE_ACCOUNT_KEY"])
        credentials = service_account.Credentials.from_service_account_info(service_account_info)
        
        service = build('drive', 'v3', credentials=credentials)
        
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [FOLDER_ID]
        }
        media = MediaFileUpload(file_path, mimetype='application/pdf')
        
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"✅ Success! File uploaded to Drive. ID: {file.get('id')}")
    except Exception as e:
        print(f"❌ Drive Upload Error: {e}")

async def scrape_ncm_to_pdf():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
        context = await browser.new_context(viewport={"width": 1280, "height": 1000})
        page = await context.new_page()
        
        url = "https://www.ncm.gov.ae/services/climate-reports-daily?lang=en"
        print(f"🔗 Navigating to {url}")
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=120000)
            
            # Dismiss cookies
            try:
                await page.click("text='I Agree'", timeout=5000)
                await asyncio.sleep(2)
            except:
                pass

            # Scroll to load data
            for _ in range(12): 
                await page.mouse.wheel(0, 1000)
                await asyncio.sleep(0.8)

            # Hide UI elements for clean PDF
            await page.evaluate("""
                const hideSelectors = ['header', 'footer', '.cookie-bar', '.cc-window', '#top-nav'];
                hideSelectors.forEach(s => {
                    document.querySelectorAll(s).forEach(el => el.style.display = 'none');
                });
            """)

            # Generate PDF filename
            pkt_time = datetime.utcnow() + timedelta(hours=5)
            timestamp_str = pkt_time.strftime("%Y-%m-%d (%I.%M %p PKT)")
            pdf_name = f"ncm_report_{timestamp_str}.pdf"
            
            print(f"📄 Printing PDF...")
            await page.pdf(path=pdf_name, format="A4", print_background=True)
            
            if os.path.exists(pdf_name):
                # UPLOAD TO DRIVE
                upload_to_drive(pdf_name)
            
        except Exception as e:
            print(f"❌ Scraper Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_ncm_to_pdf())
