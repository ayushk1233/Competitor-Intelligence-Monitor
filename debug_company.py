import asyncio
import os
import sys

# Ensure backend module is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.services.analysis_service import AnalysisService
from backend.services.scraper_service import ScraperService

class Tee:
    def __init__(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        self.file = open(filename, 'w')
        self.stdout = sys.stdout

    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)

    def flush(self):
        self.file.flush()
        self.stdout.flush()

    def close(self):
        self.file.close()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python debug_company.py <CompanyName>")
        sys.exit(1)
        
    company_name = sys.argv[1]
    log_file = f"logs/{company_name.lower()}_debug.log"
    tee = Tee(log_file)
    sys.stdout = tee
    
    print(f"Running Debug Pipeline for {company_name}...")
    
    scraper = ScraperService()
    analyzer = AnalysisService()
    
    try:
        print(f"\n[DEBUG] Fetching competitor pages for {company_name}...")
        competitor_pages = await scraper.fetch_competitor(company_name)
        
        print(f"\n[DEBUG] Analyzing {company_name}...")
        result = await analyzer.analyze_competitor(competitor_pages)
        
        print("\n[DEBUG] Done!")
    finally:
        await scraper.close()
        sys.stdout = tee.stdout
        tee.close()
        print(f"\nDebug logs saved to {log_file}")

if __name__ == "__main__":
    asyncio.run(main())
