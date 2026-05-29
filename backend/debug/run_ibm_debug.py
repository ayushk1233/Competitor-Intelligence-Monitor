import asyncio
import os
import sys

# Ensure backend module is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.services.analysis_service import AnalysisService
from backend.services.scraper_service import ScraperService

async def main():
    print("Running IBM Debug Pipeline...")
    
    scraper = ScraperService()
    analyzer = AnalysisService()
    
    try:
        print("\n[DEBUG] Fetching competitor pages...")
        competitor_pages = await scraper.fetch_competitor("IBM")
        
        print("\n[DEBUG] Analyzing competitor...")
        result = await analyzer.analyze_competitor(competitor_pages)
        
        print("\n[DEBUG] Done!")
    finally:
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(main())
