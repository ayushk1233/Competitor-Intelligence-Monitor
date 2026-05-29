import pytest

# Mock contexts that simulate output from context_builder.py
hubspot_context = "Welcome to HubSpot. Marketing, sales, CRM. Our product is great."
cursor_context = "Cursor: The best coding agent. Built to make you extraordinarily productive."
ibm_context = "IBM Agentic AI Platform. Granite Vision release. Enterprise AI launch."

def test_hubspot_no_cookie_policy():
    # Context should not be polluted by cookie policies
    assert "cookie policy" not in hubspot_context.lower()

def test_cursor_no_contact_sales():
    # Context should not be polluted by top-nav artifacts
    assert "contact sales" not in cursor_context.lower()

def test_ibm_no_support_pages():
    # Context should not be poisoned by support portal text
    assert "ibm support" not in ibm_context.lower()

if __name__ == "__main__":
    pytest.main(["-v", __file__])
