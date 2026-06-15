import pytest
from backend.eval.signal_trace import find_source_snapshot

def test_find_source_snapshot():
    snapshots = [
        {"content_text": "This is a launch signal.", "page_type": "homepage", "source_url": "https://example.com"}
    ]
    
    # Exact match
    res = find_source_snapshot("This is a launch signal.", snapshots)
    assert res is not None
    assert res["page_type"] == "homepage"
    
    # Partial match (case insensitive)
    res2 = find_source_snapshot("this is a launch", snapshots)
    assert res2 is not None
    
    # No match
    res3 = find_source_snapshot("Not found", snapshots)
    assert res3 is None
