import pytest
import uuid
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError

from backend.temporal.enums import (
    TemporalChangeCategory, TemporalChangeDirection, TemporalConfidenceLevel
)
from backend.signals.enums import SignalSeverity
from backend.signals.models import StrategicSignal
from backend.signals.repository import StrategicSignalRepository

class MockResult:
    def __init__(self, items):
        self._items = items
        
    def scalars(self):
        return self
        
    def all(self):
        return self._items
        
    def first(self):
        return self._items[0] if self._items else None

class MockSession:
    def __init__(self, existing_signals=None):
        self.existing_signals = existing_signals or []
        self.added = []

    async def execute(self, stmt):
        # We just return the mock results
        return MockResult(self.existing_signals)

    def add(self, instance):
        self.added.append(instance)


@pytest.mark.asyncio
async def test_repository_save_and_retrieve():
    org_id = uuid.uuid4()
    run_id = "run_123"
    
    session = MockSession()
    repo = StrategicSignalRepository(session)
    
    signal = StrategicSignal(
        signal_id=uuid.uuid4(),
        signal_fingerprint="fingerprint_1",
        company_name="Acme",
        category=TemporalChangeCategory.PRICING,
        direction=TemporalChangeDirection.ADDED,
        summary="New pricing",
        business_impact="More revenue",
        confidence_score=0.9,
        confidence_level=TemporalConfidenceLevel.HIGH,
        severity=SignalSeverity.CRITICAL,
        evidence=[],
        originating_run_id=run_id,
        signal_source="test",
        prompt_version="v1",
        model_name="test-model",
        analysis_version="test-engine-v1",
        detected_at=datetime.now(timezone.utc)
    )
    
    # Save
    inserted = await repo.save([signal], org_id)
    assert inserted == 1
    assert len(session.added) == 1
    
    # Check duplicate prevention by changing mock session to return existing
    session.existing_signals = [signal.signal_id]
    inserted_again = await repo.save([signal], org_id)
    assert inserted_again == 0

@pytest.mark.asyncio
async def test_repository_empty_save():
    session = MockSession()
    repo = StrategicSignalRepository(session)
    org_id = uuid.uuid4()
    
    inserted = await repo.save([], org_id)
    assert inserted == 0

@pytest.mark.asyncio
async def test_getters():
    signal_id = uuid.uuid4()
    from backend.database.models import StrategicSignalRecord
    
    # We need to construct a record for the mock to return
    record = StrategicSignalRecord(
        signal_id=signal_id,
        organization_id=uuid.uuid4(),
        company_name="Acme",
        category="pricing",
        direction="added",
        summary="sum",
        business_impact="impact",
        confidence_score=0.9,
        confidence_level="high",
        severity="critical",
        evidence=[],
        originating_run_id="run_123",
        prompt_version="v1",
        model_name="test-model",
        analysis_version="v1",
        signal_source="test",
        signal_fingerprint="fingerprint_1",
        detected_at=datetime.now(timezone.utc)
    )
    
    session = MockSession(existing_signals=[record])
    repo = StrategicSignalRepository(session)
    
    # Retrieve by company
    signals = await repo.get_by_company("Acme")
    assert len(signals) == 1
    assert signals[0].company_name == "Acme"
    
    # Retrieve by run
    run_signals = await repo.get_by_run("run_123")
    assert len(run_signals) == 1
    
    # Retrieve by fingerprint
    fp_signals = await repo.get_by_fingerprint("fingerprint_1")
    assert len(fp_signals) == 1
