import asyncio
import numpy as np
from datetime import datetime, timezone

from backend.database.connection import AsyncSessionLocal
from backend.memory.retrieval import RetrievalRepository
from backend.memory.providers.factory import ProviderFactory
from backend.memory.service import MemoryService

from evaluation.retrieval.dataset import RetrievalDataset
from evaluation.retrieval.metrics import RetrievalMetrics
from evaluation.retrieval.report import EvaluationReport

class RetrievalEvaluationRunner:
    def __init__(self):
        self.dataset = RetrievalDataset()
        
    async def run(self):
        queries = self.dataset.load()
        if not queries:
            print("No queries in dataset.")
            return

        print(f"Starting evaluation on {len(queries)} golden queries...")
        
        async with AsyncSessionLocal() as session:
            repo = RetrievalRepository(session)
            provider = ProviderFactory.create()
            service = MemoryService(provider, repo)
            
            latencies = []
            recalls_1 = []
            recalls_3 = []
            recalls_5 = []
            mrrs = []
            company_filter_accs = []
            timeline_order_accs = []
            duplicate_rates = []
            
            for i, q in enumerate(queries):
                # 1. Semantic Search Evaluation
                search_result = await service.search(query=q.query, limit=5)
                
                latencies.append(search_result.runtime_ms)
                retrieved_runs = [a.run_id for a in search_result.analyses]
                
                recalls_1.append(RetrievalMetrics.calculate_recall_at_k(q.expected_runs, retrieved_runs, 1))
                recalls_3.append(RetrievalMetrics.calculate_recall_at_k(q.expected_runs, retrieved_runs, 3))
                recalls_5.append(RetrievalMetrics.calculate_recall_at_k(q.expected_runs, retrieved_runs, 5))
                mrrs.append(RetrievalMetrics.calculate_mrr(q.expected_runs, retrieved_runs))
                duplicate_rates.append(RetrievalMetrics.calculate_duplicate_rate(retrieved_runs))
                
                # 2. Company Filter Evaluation
                company_search_result = await service.search_company(company_name=q.company, query=q.query, limit=5)
                retrieved_companies = [a.company_name for a in company_search_result.analyses]
                company_filter_accs.append(RetrievalMetrics.calculate_company_filter_accuracy(q.company, retrieved_companies))
                
                # 3. Timeline Order Evaluation
                timeline = await service.timeline(company_name=q.company)
                analyzed_dates = [e.analyzed_at for e in timeline.events]
                timeline_order_accs.append(RetrievalMetrics.calculate_timeline_order_accuracy(analyzed_dates))
                
                print(f"Processed [{i+1}/{len(queries)}] {q.query[:50]}...")
                
            report = EvaluationReport(
                timestamp=datetime.now(timezone.utc).isoformat(),
                dataset_size=len(queries),
                recall_at_1=float(np.mean(recalls_1)),
                recall_at_3=float(np.mean(recalls_3)),
                recall_at_5=float(np.mean(recalls_5)),
                mrr=float(np.mean(mrrs)),
                average_latency_ms=float(np.mean(latencies)),
                p50_latency_ms=float(np.percentile(latencies, 50)),
                p95_latency_ms=float(np.percentile(latencies, 95)),
                max_latency_ms=float(np.max(latencies)),
                company_filter_accuracy=float(np.mean(company_filter_accs)),
                timeline_order_accuracy=float(np.mean(timeline_order_accs)),
                duplicate_rate=float(np.mean(duplicate_rates))
            )
            
            filepath = report.save()
            print(f"\nEvaluation Complete! Report saved to {filepath}")
            print(json.dumps(report.model_dump(), indent=2))

if __name__ == "__main__":
    import json
    runner = RetrievalEvaluationRunner()
    asyncio.run(runner.run())
