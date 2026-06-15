class EvidenceRegistry:
    def __init__(self):
        self.evidence = []
        
    def add_evidence(self, field: str, evidence: str, source_url: str = "", source_type: str = "", page_type: str = ""):
        self.evidence.append({
            "field": field,
            "evidence": evidence,
            "source_url": source_url,
            "source_type": source_type,
            "page_type": page_type
        })
        
    def get_evidence(self, field: str) -> list[dict]:
        return [e for e in self.evidence if e["field"] == field]
        
    def clear(self):
        self.evidence = []
