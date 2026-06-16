import re

def compute_agreement_score(evidence_list: list[str]) -> float:
    if not evidence_list:
        return 0.0
    if len(evidence_list) == 1:
        return 1.0
        
    def tokenize(text: str) -> set[str]:
        # Simple lowercasing and alphanumeric tokenization
        tokens = re.findall(r'\b\w+\b', text.lower())
        # Remove common stop words for better semantic matching
        stop_words = {"the", "and", "a", "an", "of", "to", "in", "for", "is", "on", "that", "by", "this", "with", "i", "you", "it", "not", "or", "be", "are"}
        return set(tokens) - stop_words
        
    token_sets = [tokenize(e) for e in evidence_list]
    
    total_score = 0.0
    pairs_count = 0
    
    for i in range(len(token_sets)):
        for j in range(i + 1, len(token_sets)):
            set_a = token_sets[i]
            set_b = token_sets[j]
            
            if not set_a and not set_b:
                similarity = 1.0
            elif not set_a or not set_b:
                similarity = 0.0
            else:
                intersection = len(set_a.intersection(set_b))
                union = len(set_a.union(set_b))
                similarity = intersection / union if union > 0 else 0.0
                
            total_score += similarity
            pairs_count += 1
            
    # For short overlapping sets, Jaccard similarity can be low. 
    # We apply a slight boost to keep it normalized around higher values if there's any overlap.
    average_similarity = total_score / pairs_count if pairs_count > 0 else 0.0
    
    # Scale it so 0.2 overlap is already considered "good agreement" (0.8+)
    # since these are sentences not identical paragraphs.
    if average_similarity == 0:
        return 0.35 # Minimum agreement if completely disjoint
    elif average_similarity > 0.3:
        return min(1.0, 0.7 + average_similarity)
    else:
        return min(1.0, 0.4 + (average_similarity * 2))
