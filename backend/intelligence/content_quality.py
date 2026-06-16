import re
from typing import Tuple, Dict
from backend.retrieval.signal_extractor import split_into_sentences

NOISE_PATTERNS = [
    # Explicit hero/example prompts
    r"plan a surf trip",
    r"find hiking boots",
    r"fantasy football",
    r"teach me mahjong",
    r"help me debug",
    
    # Generic marketing/CTA noise
    r"what can i help with\?",
    r"try chatgpt",
    r"talk with chatgpt",
    r"download the app",
    r"download on the app store",
    r"get it on google play",
    r"\blogin\b",
    r"\bsign up\b",
    r"\bsign in\b",
    r"create account",
    r"forgot password",
    r"cookie policy",
    r"terms of service",
    r"privacy policy",
    
    # Cookie Banners
    r"we use cookies",
    r"accept cookies",
    r"manage cookies",
    r"cookie preferences",
    r"accept all cookies",
    
    # Common navigation artifacts
    r"skip to content",
    r"skip to main content",
    
    # Footer elements
    r"copyright \d{4}",
    r"all rights reserved",
]

EXACT_NOISE_WORDS = {
    "menu", "search", "close", "login", "sign up", "sign in", "home", "about us",
    "contact us", "careers", "pricing", "products", "solutions", "resources", "company"
}

def is_noise_chunk(text: str) -> bool:
    """Detect boilerplate, CTAs, and prompt examples."""
    lower_text = text.lower().strip()
    
    # Too short and lacking punctuation might mean it's a menu item, but let's stick to explicit checks
    # since short phrases like 'GPT-5' or 'Gemini 1.5' shouldn't be dropped if they stand alone.
    
    for pattern in NOISE_PATTERNS:
        if re.search(pattern, lower_text):
            return True
            
    words = lower_text.split()
    # Check for exact noise words if the chunk is very short
    if len(words) < 5:
        # remove punctuation for exact check
        clean_short = re.sub(r'[^\w\s]', '', lower_text).strip()
        if clean_short in EXACT_NOISE_WORDS:
            return True

    return False

def clean_content(text: str) -> Tuple[str, Dict]:
    """
    Cleans raw text by splitting it line by line and filtering out noise.
    Returns the cleaned text and diagnostic metrics.
    """
    original_length = len(text)
    if original_length == 0:
        return text, {
            "content_retention_ratio": 100.0,
            "noise_removed_count": 0,
            "noise_removed_examples": []
        }
        
    sentences = split_into_sentences(text)
    cleaned_sentences = []
    removed_examples = []
    removed_count = 0
    
    for sentence in sentences:
        if not sentence.strip():
            continue
            
        if is_noise_chunk(sentence):
            removed_count += 1
            if len(removed_examples) < 10:
                removed_examples.append(sentence.strip()[:100])
        else:
            cleaned_sentences.append(sentence)
            
    cleaned_text = "\n".join(cleaned_sentences)
    cleaned_length = len(cleaned_text)
    
    retention_ratio = (cleaned_length / original_length) * 100 if original_length > 0 else 0.0
    
    metrics = {
        "content_retention_ratio": round(retention_ratio, 2),
        "noise_removed_count": removed_count,
        "noise_removed_examples": removed_examples
    }
    
    return cleaned_text, metrics
