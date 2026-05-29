import asyncio
import pytest
from backend.reasoning.icp_reasoner import analyze_icp
import json

@pytest.mark.asyncio
async def test_icp_reasoning():
    sample = """
    Our developer platform helps
    enterprise engineering teams
    build scalable AI applications
    using advanced APIs.
    """
    result = await analyze_icp(sample)
    parsed = json.loads(result)
    
    assert "icp_summary" in parsed
    assert "icp_keywords" in parsed
    assert "signals" in parsed
    assert "evidence" in parsed
    
    assert any("engineer" in kw.lower() or "developer" in kw.lower() for kw in parsed["icp_keywords"])
