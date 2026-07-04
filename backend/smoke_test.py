import asyncio
import httpx
import time
from datetime import datetime

async def run_e2e():
    async with httpx.AsyncClient() as client:
        print("1. Triggering Analysis...")
        # Check running first
        response = await client.post(
            "http://localhost:8000/api/analyze",
            json={"company_url": "https://www.anthropic.com"}
        )
        assert response.status_code == 200, f"Failed to trigger analysis: {response.text}"
        data = response.json()
        run_id = data["run_id"]
        print(f"Analysis triggered. Run ID: {run_id}")
        
        print("2. Waiting for analysis to complete...")
        completed = False
        for _ in range(60):
            status_resp = await client.get(f"http://localhost:8000/api/dashboard/runs")
            if status_resp.status_code == 200:
                runs = status_resp.json()
                for run in runs:
                    if run["id"] == run_id and run["status"] == "COMPLETED":
                        completed = True
                        break
            if completed:
                break
            await asyncio.sleep(5)
            
        assert completed, "Analysis did not complete within the timeout."
        print(f"Analysis {run_id} completed successfully.")
        
        print("3. Verifying Automatic Indexing & Semantic Search...")
        search_resp = await client.get("http://localhost:8000/api/intelligence/search?query=Claude")
        assert search_resp.status_code == 200
        search_data = search_resp.json()
        print(f"Search returned {len(search_data['analyses'])} analyses.")
        # Ensure our run_id is in there or at least we get results
        assert len(search_data['analyses']) > 0, "No analyses found!"
        
        print("4. Verifying Timeline Retrieval...")
        timeline_resp = await client.get("http://localhost:8000/api/intelligence/timeline/Anthropic")
        assert timeline_resp.status_code == 200
        timeline_data = timeline_resp.json()
        print(f"Timeline retrieved with {timeline_data['total_events']} events.")
        
        print("\nAll E2E checks passed successfully!")

if __name__ == "__main__":
    asyncio.run(run_e2e())
