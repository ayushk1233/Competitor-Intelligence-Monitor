import re
from bs4 import BeautifulSoup


def clean_html(raw_html: str) -> str:
    """
    Strip all HTML noise and return readable plain text.
    Removes: scripts, styles, nav, footer, header, ads.
    """
    soup = BeautifulSoup(raw_html, "lxml")

    # Remove all non-content tags
    for tag in soup(["script", "style", "nav", "footer",
                     "header", "aside", "form", "noscript",
                     "iframe", "svg", "img", "button", "input"]):
        tag.decompose()

    # Get visible text
    text = soup.get_text(separator=" ", strip=True)

    # Collapse multiple whitespace/newlines into single space
    text = re.sub(r'\s+', ' ', text)

    # Remove very short lines that are usually menu fragments
    lines = [line.strip() for line in text.split('.') if len(line.strip()) > 40]
    text = '. '.join(lines)

    return text.strip()


def extract_page_title(raw_html: str) -> str:
    """Extract the page <title> tag content."""
    soup = BeautifulSoup(raw_html, "lxml")
    title = soup.find("title")
    return title.get_text(strip=True) if title else ""


def estimate_word_count(text: str) -> int:
    return len(text.split())


# Targeted noise patterns to strip specific spam phrases
# without destroying surrounding legitimate content.
NOISE_PATTERNS = [
    # Metadata pollution
    r"\btitle:\b",
    r"\burl source:\b",
    r"\bpublished time:\b",
    r"\bmarkdown content:\b",

    # Cookie and language banners
    r"\bwe use cookies[^.]*\.",
    r"\bcookies\. without a selection, our default[^.]*\.",
    r"\baccept all(?: cookies)?\b",
    r"\baccept cookies\b",
    r"\bdecline all(?: cookies)?\b",
    r"\bmanage cookies\b",
    r"\bmanage preferences\b",
    r"\bcookie preferences\b",
    r"\bcookie policy\b",
    r"\bcookie settings\b",
    r"×close",
    r"\bsome cookies are necessary[^.]*\.",
    r"\bother cookies are optional[^.]*\.",
    r"\byou can consent to all cookies.*?(?:manage [a-z]+|analytics\.)",
    r"\[skip to content\](?:\([^)]+\))?",
    r"\* english select a language",
    r"\blanguage selector\b",
    r"\[deutsch\](?:\([^)]+\))?",
    r"\[english\](?:\([^)]+\))?",
    r"\[español\](?:\([^)]+\))?",
    r"\[日本語\](?:\([^)]+\))?",
    r"\[português\](?:\([^)]+\))?",
    r"\[français\](?:\([^)]+\))?",
    r"\bportuguês\b",
    r"\bfrançais\b",
    r"\* high contrast",

    # Navigation / Menus / CTAs
    r"\bcontact sales\b",
    r"\bsign in\b",
    r"\blog in\b",
    r"\blogin\b",
    r"\bcustomer support\b",
    r"\bdashboard\b",
    r"\bchat with sales\b",
    r"\bstart free trial\b",
    r"\brequest demo\b",
    r"\bbook a call\b",
    r"\bpricing\b",
    r"\benterprise\b",
    r"\bresources\b",
]

_NOISE_RE = re.compile(
    "|".join(NOISE_PATTERNS),
    re.IGNORECASE
)


def clean_page_content(text: str) -> str:
    """
    Strip cookie consent banners, language selectors, and navigation
    boilerplate from Jina-fetched page content before chunking.
    """
    original_length = len(text)
    
    # Remove Jina metadata pollution
    #cleaned = re.sub(r"Title:.*?(?=URL Source:|$)", "", text, flags=re.IGNORECASE|re.DOTALL)
    #cleaned = re.sub(r"^Title:\s*[^\n]+\n?", "", text,flags=re.IGNORECASE | re.MULTILINE)
    if "URL Source:" in text or "Markdown Content:" in text:
        cleaned = re.sub(
            r"Title:.*?(?=URL Source:|Markdown Content:)",
            "",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
    else:
        cleaned = text

    cleaned = re.sub(
        r"URL Source:.*?(?=Published Time:|Markdown Content:|$)",
        "",
        cleaned,
        flags=re.IGNORECASE | re.DOTALL
    )

    cleaned = re.sub(
        r"Published Time:.*?(?=Markdown Content:|$)",
        "",
        cleaned,
        flags=re.IGNORECASE | re.DOTALL
    )

    cleaned = re.sub(
        r"Markdown Content:\s*",
        "",
        cleaned,
        flags=re.IGNORECASE
    )
    
    # Remove image markdown: ![alt](url)
    cleaned = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', cleaned)
    
    # Remove specific noisy links entirely (Navigation & CTAs)
    noisy_links = r'Pricing|Enterprise|Resources|Contact Sales|Sign In|Dashboard|Chat with sales|Start free trial|Request demo|Book a call'
    cleaned = re.sub(rf'\[(?:{noisy_links})\]\([^)]+\)', '', cleaned, flags=re.IGNORECASE)
    
    # Extract text from remaining link markdown: [text](url) -> text
    cleaned = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', cleaned)
    
    # Remove raw URLs
    cleaned = re.sub(r'https?://[^\s]+', '', cleaned)
    
    # Remove specific noise phrases
    cleaned = _NOISE_RE.sub(" ", cleaned)

    # Collapse resulting extra whitespace
    cleaned = re.sub(r" {3,}", "  ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = cleaned.strip()

    cleaned_length = len(cleaned)
    
    removed_pct = 0
    if original_length > 0:
        removed_pct = 100 - (cleaned_length / original_length * 100)
        
    print(
        f"[cleaner]\n"
        f"before={original_length}\n"
        f"after={cleaned_length}\n"
        f"removed={removed_pct:.0f}%"
    )

    return cleaned