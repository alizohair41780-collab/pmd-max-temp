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
        # Get credentials from GitHub Secrets
        service_account_info = json.loads(os.environ["GDRIVE_SERVICE_ACCOUNT_KEY"])
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info, 
            scopes=['https://www.googleapis.com/auth/drive']
        )
        service = build('drive', 'v3', credentials=credentials)
        
        file_metadata = {'name': os.path.basename(file_path)}
        
        # resumable=False is used for service account reliability
        media = MediaFileUpload(file_path, mimetype='application/pdf', resumable=False)
        
        # Create the file in the Service Account's "temporary" space
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        file_id = file.get('id')
        print(f"✅ File Created! ID: {file_id}")

        # TRANSFER OWNERSHIP: Moves storage cost and visibility to YOUR email
        service.permissions().create(
            fileId=file_id,
            body={'type': 'user', 'role': 'owner', 'emailAddress': USER_EMAIL},
            transferOwnership=True
        ).execute()
        
        print(f"📧 Ownership transferred to {USER_EMAIL}. Check your 'My Drive'!")

    except Exception as e:
        print(f"❌ DRIVE ERROR: {e}")

async def scrape_pmd_balochistan():
    async with async_playwright() as p:
        # Optimized launch arguments for GitHub Actions environment
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = await browser.new_context(viewport={"width": 1280, "height": 1600})
        page = await context.new_page()
        
        url = "https://rmcbalochistan.pmd.gov.pk/www/dailyforecast.php"
        print(f"🔗 Connecting to PMD Balochistan (Waiting up to 3 mins)...")
        
        try:
            # wait_until="domcontentloaded" is better for slow gov servers than "networkidle"
            await page.goto(url, wait_until="domcontentloaded", timeout=180000)
            
            # Explicit wait to let the dynamic table load its data
            print(f"⏳ Page structure loaded. Waiting 15s for data rendering...")
            await asyncio.sleep(15) 

            # Timestamp for PKT (UTC+5)
            pkt_now = datetime.utcnow() + timedelta(hours=5)
            pdf_name = f"balochistan_forecast_{pkt_now.strftime('%Y-%m-%d_%H-%M')}_PKT.pdf"
            
            print(f"📄 Generating PDF: {pdf_name}")
            # print_background=True ensures table colors/borders are captured
            await page.pdf(path=pdf_name, format="A4", print_background=True)
            
            if os.path.exists(pdf_name):
                upload_to_drive(pdf_name)
            else:
                print("❌ PDF generation failed: File not found on disk.")
            
        except Exception as e:
            print(f"❌ SCRAPE ERROR: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_pmd_balochistan())
