import pytest
from evaluation.retrieval.metrics import RetrievalMetrics

def test_recall_at_k():
    expected = ["run_1", "run_2"]
    retrieved = ["run_3", "run_1", "run_4"]
    
    # Recall@1: retrieved[:1] is ["run_3"], expected is ["run_1", "run_2"]. Intersection: 0/2 = 0.0
    assert RetrievalMetrics.calculate_recall_at_k(expected, retrieved, 1) == 0.0
    
    # Recall@3: retrieved[:3] is ["run_3", "run_1", "run_4"]. Intersection: "run_1". 1/2 = 0.5
    assert RetrievalMetrics.calculate_recall_at_k(expected, retrieved, 3) == 0.5

def test_mrr():
    expected = ["run_1", "run_2"]
    # 1st place: run_3. 2nd place: run_1. So rank is 2. MRR = 1/2 = 0.5
    retrieved = ["run_3", "run_1", "run_4"]
    assert RetrievalMetrics.calculate_mrr(expected, retrieved) == 0.5
    
    # 1st place: run_1. Rank = 1. MRR = 1.0
    retrieved2 = ["run_1", "run_3"]
    assert RetrievalMetrics.calculate_mrr(expected, retrieved2) == 1.0
    
    # Not found
    retrieved3 = ["run_3", "run_4"]
    assert RetrievalMetrics.calculate_mrr(expected, retrieved3) == 0.0

def test_company_filter_accuracy():
    retrieved_companies = ["Anthropic", "Anthropic", "OpenAI"]
    assert RetrievalMetrics.calculate_company_filter_accuracy("Anthropic", retrieved_companies) == 2 / 3

def test_timeline_order_accuracy():
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    dates_perfect = [now, now + timedelta(days=1), now + timedelta(days=2)]
    assert RetrievalMetrics.calculate_timeline_order_accuracy(dates_perfect) == 1.0
    
    dates_reversed = [now + timedelta(days=2), now + timedelta(days=1), now]
    assert RetrievalMetrics.calculate_timeline_order_accuracy(dates_reversed) == 0.0

def test_duplicate_rate():
    # 3 items, 1 unique, 2 duplicates. (3 - 2) / 3 = 1/3 = 0.33...
    runs = ["run_1", "run_1", "run_2"]
    assert round(RetrievalMetrics.calculate_duplicate_rate(runs), 3) == 0.333
