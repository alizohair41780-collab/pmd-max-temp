import asyncio
from playwright.async_api import async_playwright
import playwright_stealth
from datetime import datetime, timedelta
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# YOUR PERSONAL EMAIL
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
        # Launching with automation-hiding flags
        browser = await p.chromium.launch(headless=True, args=[
            "--no-sandbox", 
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled"
        ])
        
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        
        context = await browser.new_context(
            viewport={"width": 1280, "height": 1600},
            user_agent=user_agent,
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive"
            }
        )
        
        page = await context.new_page()
        
        # FIXED: Using the async-compatible stealth method
        await playwright_stealth.stealth_async(page)
        
        url = "https://rmcbalochistan.pmd.gov.pk/www/dailyforecast.php"
        print(f"🔗 Attempting Stealth Connection to PMD Balochistan...")
        
        try:
            # Visit Google first
            await page.goto("https://www.google.com", wait_until="domcontentloaded")
            await asyncio.sleep(5)
            
            print(f"🛰️ Navigating to target site...")
            await page.goto(url, wait_until="domcontentloaded", timeout=180000)
            
            # Wait for firewall clearance
            print(f"⏳ Waiting 55 seconds for firewall clearance...")
            await asyncio.sleep(55) 

            # Filename generation
            pkt_now = datetime.utcnow() + timedelta(hours=5)
            pdf_name = f"balochistan_forecast_{pkt_now.strftime('%Y-%m-%d_%H-%M')}_PKT.pdf"
            
            print(f"📄 Capturing PDF...")
            await page.pdf(path=pdf_name, format="A4", print_background=True)
            
            if os.path.exists(pdf_name):
                upload_to_drive(pdf_name)
            else:
                print("❌ PDF generation failed.")
            
        except Exception as e:
            print(f"❌ SCRAPE ERROR: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_pmd_balochistan())
