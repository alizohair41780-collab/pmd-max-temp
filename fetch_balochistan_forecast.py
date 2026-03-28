import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# YOUR PERSONAL EMAIL (To become the new owner of the file)
USER_EMAIL = "alizohair3173@gmail.com"

def upload_to_drive(file_path):
    print(f"🚀 Initializing Google Drive Upload...")
    try:
        service_account_info = json.loads(os.environ["GDRIVE_SERVICE_ACCOUNT_KEY"])
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info, 
            scopes=['https://www.googleapis.com/auth/drive']
        )
        service = build('drive', 'v3', credentials=credentials)
        
        file_metadata = {'name': os.path.basename(file_path)}
        media = MediaFileUpload(file_path, mimetype='application/pdf', resumable=False)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        file_id = file.get('id')
        print(f"✅ File Created! ID: {file_id}")

        # Transfer ownership to your personal email
        service.permissions().create(
            fileId=file_id,
            body={'type': 'user', 'role': 'owner', 'emailAddress': USER_EMAIL},
            transferOwnership=True
        ).execute()
        
        print(f"📧 Ownership transferred to {USER_EMAIL}.")

    except Exception as e:
        print(f"❌ DRIVE ERROR: {e}")

async def scrape_pmd_balochistan():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = await browser.new_context(viewport={"width": 1280, "height": 1400})
        page = await context.new_page()
        
        url = "https://rmcbalochistan.pmd.gov.pk/www/dailyforecast.php"
        print(f"🔗 Connecting to PMD Balochistan...")
        
        try:
            # Increased timeout for slower government servers
            await page.goto(url, wait_until="networkidle", timeout=90000)
            await asyncio.sleep(5) 

            # Clean the page of unnecessary navigation or sidebars if needed
            # This site is quite simple, but we'll ensure the table is visible
            await page.wait_for_selector("table")

            # PST/PKT Timestamp
            pkt_now = datetime.utcnow() + timedelta(hours=5)
            pdf_name = f"balochistan_forecast_{pkt_now.strftime('%Y-%m-%d_%H-%M')}_PKT.pdf"
            
            print(f"📄 Generating PDF...")
            # We use full_page=True to ensure the whole forecast table is captured
            await page.pdf(path=pdf_name, format="A4", print_background=True)
            
            if os.path.exists(pdf_name):
                upload_to_drive(pdf_name)
            
        except Exception as e:
            print(f"❌ SCRAPE ERROR: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_pmd_balochistan())
