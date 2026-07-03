import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from backend.main import app
from backend.api.intelligence import get_memory_service
from backend.memory.models import MemorySearchResult, CompanyTimeline, TimelineEvent, RetrievedAnalysis

class MockMemoryService:
    async def search(self, query: str, limit: int = 5):
        if query == "empty_query":
            return MemorySearchResult(query=query, analyses=[], retrieved_chunks=0, runtime_ms=1.0)
        return MemorySearchResult(
            query=query, 
            analyses=[
                RetrievedAnalysis(
                    run_id="run_1",
                    company_name="Acme",
                    analyzed_at=datetime.now(timezone.utc),
                    similarity_score=0.1,
                    executive_briefing="Test",
                    structured_summary="Test",
                    supporting_chunks=[]
                )
            ], 
            retrieved_chunks=1, 
            runtime_ms=5.0
        )

    async def search_company(self, company_name: str, query: str, limit: int = 5):
        return MemorySearchResult(
            query=query, 
            analyses=[
                RetrievedAnalysis(
                    run_id="run_2",
                    company_name=company_name,
                    analyzed_at=datetime.now(timezone.utc),
                    similarity_score=0.2,
                    executive_briefing="Test",
                    structured_summary="Test",
                    supporting_chunks=[]
                )
            ], 
            retrieved_chunks=1, 
            runtime_ms=5.0
        )

    async def search_timerange(self, company_name: str, start_date: datetime, end_date: datetime, query: str, limit: int = 5):
        return MemorySearchResult(
            query=query, 
            analyses=[
                RetrievedAnalysis(
                    run_id="run_3",
                    company_name=company_name,
                    analyzed_at=start_date,
                    similarity_score=0.3,
                    executive_briefing="Test",
                    structured_summary="Test",
                    supporting_chunks=[]
                )
            ], 
            retrieved_chunks=1, 
            runtime_ms=5.0
        )

    async def timeline(self, company_name: str):
        if company_name == "InvalidCompany":
            return CompanyTimeline(company_name=company_name, events=[], first_seen=datetime.now(timezone.utc), latest_seen=datetime.now(timezone.utc), total_events=0)
            
        event = TimelineEvent(
            run_id="run_4",
            company_name=company_name,
            analyzed_at=datetime.now(timezone.utc),
            executive_briefing="Timeline",
            structured_summary="Timeline",
            supporting_chunks=[]
        )
        return CompanyTimeline(company_name=company_name, events=[event], first_seen=datetime.now(timezone.utc), latest_seen=datetime.now(timezone.utc), total_events=1)

    async def latest(self, company_name: str):
        if company_name == "InvalidCompany":
            return None
        return TimelineEvent(
            run_id="run_5",
            company_name=company_name,
            analyzed_at=datetime.now(timezone.utc),
            executive_briefing="Latest",
            structured_summary="Latest",
            supporting_chunks=[]
        )
        
    async def previous(self, company_name: str):
        if company_name == "InvalidCompany":
            return None
        return TimelineEvent(
            run_id="run_6",
            company_name=company_name,
            analyzed_at=datetime.now(timezone.utc),
            executive_briefing="Previous",
            structured_summary="Previous",
            supporting_chunks=[]
        )

app.dependency_overrides[get_memory_service] = lambda: MockMemoryService()
client = TestClient(app)

def test_semantic_search():
    response = client.get("/api/intelligence/search?query=pricing")
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "pricing"
    assert len(data["analyses"]) == 1
    assert data["analyses"][0]["run_id"] == "run_1"

def test_company_search():
    response = client.get("/api/intelligence/search?query=pricing&company=Anthropic")
    assert response.status_code == 200
    data = response.json()
    assert len(data["analyses"]) == 1
    assert data["analyses"][0]["company_name"] == "Anthropic"
    assert data["analyses"][0]["run_id"] == "run_2"

def test_date_filtering():
    response = client.get("/api/intelligence/search?query=pricing&company=Anthropic&start_date=2026-06-01T00:00:00Z&end_date=2026-07-01T00:00:00Z")
    assert response.status_code == 200
    data = response.json()
    assert len(data["analyses"]) == 1
    assert data["analyses"][0]["run_id"] == "run_3"

def test_timeline():
    response = client.get("/api/intelligence/timeline/Anthropic")
    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == "Anthropic"
    assert len(data["events"]) == 1
    assert data["events"][0]["run_id"] == "run_4"

def test_latest():
    response = client.get("/api/intelligence/latest/Anthropic")
    assert response.status_code == 200
    data = response.json()
    assert data["run_id"] == "run_5"

def test_previous():
    response = client.get("/api/intelligence/previous/Anthropic")
    assert response.status_code == 200
    data = response.json()
    assert data["run_id"] == "run_6"

def test_invalid_company_latest():
    response = client.get("/api/intelligence/latest/InvalidCompany")
    assert response.status_code == 404

def test_invalid_company_timeline():
    response = client.get("/api/intelligence/timeline/InvalidCompany")
    assert response.status_code == 404

def test_empty_results():
    response = client.get("/api/intelligence/search?query=empty_query")
    assert response.status_code == 200
    data = response.json()
    assert len(data["analyses"]) == 0

def test_invalid_date_format():
    response = client.get("/api/intelligence/search?query=pricing&company=Anthropic&start_date=invalid-date")
    assert response.status_code == 422
