import json
from unittest.mock import AsyncMock, patch

import pytest

from backend.reasoning.icp_reasoner import analyze_icp


@pytest.mark.asyncio
async def test_icp_reasoning():

    mock_response = json.dumps(
        {
            "icp_summary": "enterprise engineering teams",
            "icp_keywords": [
                "developers",
                "engineers",
                "enterprise",
            ],
            "signals": [],
            "evidence": [
                "enterprise engineering teams"
            ],
        }
    )

    with patch(
        "backend.reasoning.icp_reasoner.call_openrouter",
        new=AsyncMock(return_value=mock_response),
    ):

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

        assert any(
            "engineer" in kw.lower()
            or "developer" in kw.lower()
            for kw in parsed["icp_keywords"]
        )
