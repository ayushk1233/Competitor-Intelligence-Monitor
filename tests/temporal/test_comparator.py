import pytest
from datetime import datetime, timedelta, timezone

from backend.memory.models import CompanyTimeline, TimelineEvent
from backend.temporal.comparator import TimelineComparator
from backend.temporal.exceptions import TimelineComparisonError

def build_timeline(num_events: int) -> CompanyTimeline:
    now = datetime.now(timezone.utc)
    events = []
    
    for i in range(num_events):
        event_time = now + timedelta(days=i)
        events.append(TimelineEvent(
            run_id=f"run_{i}",
            company_name="Acme",
            analyzed_at=event_time,
            executive_briefing=f"Briefing {i}",
            structured_summary=f"Summary {i}",
            supporting_chunks=[]
        ))
        
    return CompanyTimeline(
        company_name="Acme",
        events=events,
        first_seen=events[0].analyzed_at if events else now,
        latest_seen=events[-1].analyzed_at if events else now,
        total_events=len(events)
    )

def test_empty_timeline():
    timeline = build_timeline(0)
    comparator = TimelineComparator()
    
    with pytest.raises(TimelineComparisonError) as exc:
        comparator.compare(timeline)
    assert "0 events" in str(exc.value)

def test_single_event_timeline():
    timeline = build_timeline(1)
    comparator = TimelineComparator()
    
    with pytest.raises(TimelineComparisonError) as exc:
        comparator.compare(timeline)
    assert "1 event" in str(exc.value)

def test_two_event_timeline():
    timeline = build_timeline(2)
    comparator = TimelineComparator()
    
    comparison = comparator.compare(timeline)
    
    assert comparison.company_name == "Acme"
    assert comparison.latest_event.run_id == "run_1"
    assert comparison.previous_event.run_id == "run_0"
    assert len(comparison.historical_context) == 0
    
    assert comparison.metadata.total_events == 2
    assert comparison.metadata.historical_depth == 0
    assert comparison.metadata.days_between_latest_and_previous == 1
    assert comparison.metadata.timeline_span_days == 1

def test_multi_event_timeline():
    # Construct a timeline with June, July, August (0, 1, 2)
    timeline = build_timeline(3)
    comparator = TimelineComparator()
    
    comparison = comparator.compare(timeline)
    
    assert comparison.company_name == "Acme"
    assert comparison.latest_event.run_id == "run_2"
    assert comparison.previous_event.run_id == "run_1"
    assert len(comparison.historical_context) == 1
    assert comparison.historical_context[0].run_id == "run_0"
    
    assert comparison.metadata.total_events == 3
    assert comparison.metadata.historical_depth == 1
    assert comparison.metadata.days_between_latest_and_previous == 1
    assert comparison.metadata.timeline_span_days == 2

def test_immutability():
    timeline = build_timeline(3)
    original_events = list(timeline.events)
    
    comparator = TimelineComparator()
    comparison = comparator.compare(timeline)
    
    # Assert timeline events list is completely unmodified
    assert len(timeline.events) == 3
    for i in range(3):
        assert timeline.events[i].run_id == original_events[i].run_id
    
    # Modifying the returned objects shouldn't affect the input timeline
    # since we slice, it creates a new list.
    comparison.historical_context.pop()
    assert len(timeline.events) == 3
