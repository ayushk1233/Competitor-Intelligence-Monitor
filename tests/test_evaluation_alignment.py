from unittest.mock import MagicMock, patch

from backend.eval.scorer import semantic_similarity


def test_semantic_similarity_overlap():

    expected = {
        "developer platform",
        "artificial intelligence",
        "engineering tools",
    }

    actual = {
        "developer infrastructure",
        "AI",
        "tools for engineers",
    }

    fake_model = MagicMock()

    fake_model.encode.side_effect = [
        [1, 2, 3],  # expected embeddings
        [4, 5, 6],  # actual embeddings
    ]

    fake_scores = MagicMock()

    fake_scores.max.side_effect = [
        (MagicMock(mean=lambda: MagicMock(item=lambda: 0.8)), None),
        (MagicMock(mean=lambda: MagicMock(item=lambda: 0.8)), None),
    ]

    with patch("backend.eval.scorer._model", fake_model):
        with patch(
            "backend.eval.scorer.util.cos_sim",
            return_value=fake_scores,
        ):
            score = semantic_similarity(
                expected,
                actual,
                is_recall=False,
            )

    assert score > 0.45


def test_semantic_similarity_recall():

    expected = {
        "large organizations",
        "global scale",
    }

    actual = {
        "enterprise",
        "worldwide operations",
        "startups",
    }

    fake_model = MagicMock()

    fake_model.encode.side_effect = [
        [1, 2],
        [3, 4],
    ]

    fake_scores = MagicMock()

    fake_scores.max.side_effect = [
        (MagicMock(mean=lambda: MagicMock(item=lambda: 0.75)), None),
    ]

    with patch("backend.eval.scorer._model", fake_model):
        with patch(
            "backend.eval.scorer.util.cos_sim",
            return_value=fake_scores,
        ):
            score = semantic_similarity(
                expected,
                actual,
                is_recall=True,
            )

    assert score > 0.45
