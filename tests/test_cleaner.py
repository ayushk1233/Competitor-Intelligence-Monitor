import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.utils.cleaner import clean_page_content

def test_hubspot_cookie_removal():
    input_text = "Title: HubSpot | Software & Tools for your Business - Homepage [___](https://hubspot. com/#) cookies. Without a selection, our default will apply. You can change your preferences at any time. To learn more, check out our Cookie Policy (https://legal. Accept all Decline all com/#global-nav-main-content) * * [Deutsch](https://www. com/&hubs_content-cta=cl-dropdown-menu-link) * [English] HubSpot provides a full platform of marketing, sales, customer service, and CRM software."
    
    cleaned = clean_page_content(input_text)
    print("\nCLEANED:", cleaned)
    
    assert "Accept all" not in cleaned
    assert "Decline all" not in cleaned
    assert "Cookie Policy" not in cleaned
    assert "HubSpot provides a full platform of marketing" in cleaned

def test_cursor_nav_removal():
    input_text = "Enterprise Pricing Resources Changelog Sign in Contact sales Cursor: The best coding agent. Built to make you extraordinarily productive."
    cleaned = clean_page_content(input_text)
    print("\nCLEANED:", cleaned)
    
    assert "Sign in" not in cleaned
    assert "Contact sales" not in cleaned
    assert "Cursor: The best coding agent" in cleaned

if __name__ == "__main__":
    test_hubspot_cookie_removal()
    test_cursor_nav_removal()
    print("Tests passed!")
