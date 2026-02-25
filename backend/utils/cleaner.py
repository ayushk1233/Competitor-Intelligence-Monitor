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