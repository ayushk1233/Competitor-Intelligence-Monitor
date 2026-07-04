class RetrievalMetrics:
    @staticmethod
    def calculate_recall_at_k(expected_runs: list[str], retrieved_runs: list[str], k: int) -> float:
        if not expected_runs:
            return 1.0
        
        retrieved_k = set(retrieved_runs[:k])
        expected_set = set(expected_runs)
        
        matches = len(expected_set.intersection(retrieved_k))
        return matches / len(expected_set)

    @staticmethod
    def calculate_mrr(expected_runs: list[str], retrieved_runs: list[str]) -> float:
        if not expected_runs:
            return 1.0
            
        expected_set = set(expected_runs)
        
        for i, run_id in enumerate(retrieved_runs):
            if run_id in expected_set:
                return 1.0 / (i + 1)
        return 0.0

    @staticmethod
    def calculate_company_filter_accuracy(expected_company: str, retrieved_companies: list[str]) -> float:
        if not retrieved_companies:
            return 1.0
            
        matches = sum(1 for c in retrieved_companies if c == expected_company)
        return matches / len(retrieved_companies)

    @staticmethod
    def calculate_timeline_order_accuracy(analyzed_dates: list) -> float:
        """
        Timeline ordering must be oldest -> newest (ascending).
        """
        if len(analyzed_dates) <= 1:
            return 1.0
            
        correct_order = 0
        for i in range(len(analyzed_dates) - 1):
            if analyzed_dates[i] <= analyzed_dates[i+1]:
                correct_order += 1
                
        return correct_order / (len(analyzed_dates) - 1)

    @staticmethod
    def calculate_duplicate_rate(retrieved_runs: list[str]) -> float:
        if not retrieved_runs:
            return 0.0
            
        unique_runs = len(set(retrieved_runs))
        total_runs = len(retrieved_runs)
        
        return (total_runs - unique_runs) / total_runs
