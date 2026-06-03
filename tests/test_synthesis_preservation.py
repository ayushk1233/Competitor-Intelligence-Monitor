import json
from unittest.mock import AsyncMock, patch

import pytest

from backend.reasoning.synthesis_reasoner import (
    synthesize_intelligence,
)


@pytest.mark.asyncio
async def test_synthesis_preservation():

    mock_response = json.dumps(
        {
            "icp_keywords": [
                "engineers",
                "enterprise",
            ],
            "icp_evidence": [
                "enterprise focus"
            ],
            "tone_evidence": [
                "Developer platform"
            ],
            "momentum_evidence": [
                "Strong AI launches"
            ],
            "momentum_score": 8,
        }
    )

    with patch(
        "backend.reasoning.synthesis_reasoner.call_openrouter",
        new=AsyncMock(return_value=mock_response),
    ):

        context = "Sample context."

        momentum = (
            '{"momentum_score": 8, '
            '"evidence": ["Strong AI launches"]}'
        )

        tone = (
            '{"messaging_tone": "technical", '
            '"evidence": ["Developer platform"]}'
        )

        icp = (
            '{"icp_summary": '
            '"enterprise engineering teams", '
            '"icp_keywords": ["engineers", "enterprise"], '
            '"evidence": ["enterprise focus"]}'
        )

        result = await synthesize_intelligence(
            context,
            momentum,
            tone,
            icp,
        )

        parsed = json.loads(result)

        assert "icp_keywords" in parsed
        assert "icp_evidence" in parsed
        assert "tone_evidence" in parsed
        assert "momentum_evidence" in parsed
        assert "momentum_score" in parsed

        assert parsed["momentum_score"] == 8
