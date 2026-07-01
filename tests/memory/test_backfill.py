import pytest
import uuid
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from backend.memory.backfill import HistoricalBackfillService, BackfillResult
from backend.database.models import CompetitorAnalysisRecord, ComparisonRecord
from backend.models.schemas import CompetitorAnalysis, ComparisonResult

pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_pipeline():
    pipeline = MagicMock()
    pipeline.ingest_many = AsyncMock()
    
    # Return a mock IngestionResult
    mock_result = MagicMock()
    mock_result.inserted_chunks = 5
    mock_result.skipped_duplicates = 0
    mock_result.processed_documents = 2
    mock_result.processed_chunks = 5
    mock_result.runtime_ms = 100.0
    
    pipeline.ingest_many.return_value = mock_result
    return pipeline

@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session

def create_mock_analysis_record(id_val, run_id, org_id=None):
    record = CompetitorAnalysisRecord(
        id=id_val,
        run_id=run_id,
        competitor_name="Test",
        domain="test.com",
        created_at=datetime.now(timezone.utc),
    )
    analysis_dict = {
        "name": "Test",
        "domain": "test.com",
        "core_offering": "Testing",
        "icp": "Devs",
        "messaging_tone": "Technical",
        "pricing_signals": "Free",
        "hiring_signals": "None",
        "recent_launches": [],
        "strategic_keywords": [],
        "growth_signals": [],
        "risk_flags": [],
        "momentum_score": 5,
        "analyst_note": "A note",
        "pages_analyzed": ["test.com"]
    }
    record.full_analysis = analysis_dict
    return (record, org_id)

def create_mock_comparison_record(id_val, run_id, org_id=None):
    record = ComparisonRecord(
        id=id_val,
        run_id=run_id,
        created_at=datetime.now(timezone.utc),
    )
    comp_dict = {
        "market_leader": "Test",
        "fastest_mover": "Test2",
        "pivot_detected": None,
        "smb_to_enterprise_shift": [],
        "ai_emphasis_ranking": [],
        "messaging_gaps": "None",
        "threat_ranking": [],
        "executive_briefing": "Briefing"
    }
    record.full_comparison = comp_dict
    return (record, org_id)


async def test_empty_database(mock_pipeline, mock_session):
    # Mock execute to always return no rows
    mock_result = MagicMock()
    mock_result.all.return_value = []
    mock_session.execute.return_value = mock_result
    
    service = HistoricalBackfillService(mock_pipeline)
    result = await service.backfill(mock_session, batch_size=10, resume=False)
    
    assert result.analyses_processed == 0
    assert result.comparisons_processed == 0
    assert result.documents_generated == 0
    assert result.chunks_inserted == 0


async def test_single_batch(mock_pipeline, mock_session):
    run_id = str(uuid.uuid4())
    org_id = uuid.uuid4()
    
    analysis_row = create_mock_analysis_record(1, run_id, org_id)
    comp_row = create_mock_comparison_record(1, run_id, org_id)
    
    # First call: analyses, Second call: empty analyses, Third call: comparisons, Fourth: empty comparisons
    def execute_side_effect(query):
        mock_result = MagicMock()
        # Very simple checking of table being queried
        q_str = str(query)
        if "competitor_analyses" in q_str:
            if "last_id" in getattr(test_single_batch, 'state', {}):
                mock_result.all.return_value = []
            else:
                test_single_batch.state = {'last_id': 1}
                mock_result.all.return_value = [analysis_row]
        elif "comparison_results" in q_str:
            if "last_comp_id" in getattr(test_single_batch, 'state', {}):
                mock_result.all.return_value = []
            else:
                test_single_batch.state['last_comp_id'] = 1
                mock_result.all.return_value = [comp_row]
        return mock_result
        
    mock_session.execute.side_effect = execute_side_effect
    
    service = HistoricalBackfillService(mock_pipeline)
    result = await service.backfill(mock_session, batch_size=10, resume=False)
    
    assert result.analyses_processed == 1
    assert result.comparisons_processed == 1
    assert result.documents_generated > 0
    assert result.chunks_inserted == 10  # 5 from analysis, 5 from comp based on mock


async def test_resume_mode_skips_existing(mock_pipeline, mock_session):
    run_id = str(uuid.uuid4())
    org_id = uuid.uuid4()
    
    analysis_row = create_mock_analysis_record(1, run_id, org_id)
    comp_row = create_mock_comparison_record(1, run_id, org_id)
    
    def execute_side_effect(query):
        mock_result = MagicMock()
        q_str = str(query)
        
        # When querying for embeddings existence (resume mode)
        if "intelligence_embeddings" in q_str:
            mock_result.scalar_one_or_none.return_value = uuid.uuid4() # Exists
            return mock_result
            
        if "competitor_analyses" in q_str:
            if "last_id" in getattr(test_resume_mode_skips_existing, 'state', {}):
                mock_result.all.return_value = []
            else:
                test_resume_mode_skips_existing.state = {'last_id': 1}
                mock_result.all.return_value = [analysis_row]
        elif "comparison_results" in q_str:
            if "last_comp_id" in getattr(test_resume_mode_skips_existing, 'state', {}):
                mock_result.all.return_value = []
            else:
                test_resume_mode_skips_existing.state['last_comp_id'] = 1
                mock_result.all.return_value = [comp_row]
        return mock_result
        
    mock_session.execute.side_effect = execute_side_effect
    
    service = HistoricalBackfillService(mock_pipeline)
    result = await service.backfill(mock_session, batch_size=10, resume=True)
    
    # Processed but skipped generation/ingestion
    assert result.analyses_processed == 1
    assert result.comparisons_processed == 1
    assert result.documents_generated == 0
    assert result.chunks_inserted == 0
    assert mock_pipeline.ingest_many.call_count == 0


async def test_malformed_historical_json(mock_pipeline, mock_session):
    run_id = str(uuid.uuid4())
    
    analysis_row = create_mock_analysis_record(1, run_id)
    # Malform the dict to cause validation error
    analysis_row[0].full_analysis = {"invalid": "data"} 
    
    def execute_side_effect(query):
        mock_result = MagicMock()
        q_str = str(query)
        if "competitor_analyses" in q_str:
            if "last_id" in getattr(test_malformed_historical_json, 'state', {}):
                mock_result.all.return_value = []
            else:
                test_malformed_historical_json.state = {'last_id': 1}
                mock_result.all.return_value = [analysis_row]
        elif "comparison_results" in q_str:
            mock_result.all.return_value = []
        return mock_result
        
    mock_session.execute.side_effect = execute_side_effect
    
    service = HistoricalBackfillService(mock_pipeline)
    result = await service.backfill(mock_session, batch_size=10, resume=False)
    
    assert result.analyses_processed == 0
    assert result.failures == 1
    assert result.documents_generated == 0

async def test_ingestion_failure(mock_pipeline, mock_session):
    run_id = str(uuid.uuid4())
    analysis_row = create_mock_analysis_record(1, run_id)
    
    def execute_side_effect(query):
        mock_result = MagicMock()
        q_str = str(query)
        if "competitor_analyses" in q_str:
            if "last_id" in getattr(test_ingestion_failure, 'state', {}):
                mock_result.all.return_value = []
            else:
                test_ingestion_failure.state = {'last_id': 1}
                mock_result.all.return_value = [analysis_row]
        elif "comparison_results" in q_str:
            mock_result.all.return_value = []
        return mock_result
        
    mock_session.execute.side_effect = execute_side_effect
    mock_pipeline.ingest_many.side_effect = Exception("DB Error")
    
    service = HistoricalBackfillService(mock_pipeline)
    result = await service.backfill(mock_session, batch_size=10, resume=False)
    
    assert result.failures == 1
    mock_session.rollback.assert_called()
