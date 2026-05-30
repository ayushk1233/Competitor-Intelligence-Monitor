from backend.eval.models import EvalExpectation


TEST_CASES = [
    {
        "company_name": "Basecamp",
        "expectation": EvalExpectation(
            expected_tone="startup",
            momentum_min=1,
            momentum_max=3,
            expected_keywords=[
                "project management",
                "teams",
                "communication",
                "productivity"
            ],
            expected_icp_keywords=[
                "small teams",
                "businesses",
                "remote teams"
            ]
        )
    },

    {
        "company_name": "Stripe",
        "expectation": EvalExpectation(
            expected_tone="technical",
            momentum_min=8,
            momentum_max=10,
            expected_keywords=[
                "payments",
                "api",
                "developers",
                "infrastructure"
            ],
            expected_icp_keywords=[
                "developers",
                "businesses",
                "platforms"
            ]
        )
    },

    {
        "company_name": "IBM",
        "expectation": EvalExpectation(
            expected_tone="enterprise",
            momentum_min=5,
            momentum_max=7,
            expected_keywords=[
                "enterprise",
                "cloud",
                "consulting",
                "ai"
            ],
            expected_icp_keywords=[
                "enterprises",
                "governments",
                "large organizations"
            ]
        )
    },

    {
        "company_name": "Cursor",
        "expectation": EvalExpectation(
            expected_tone="technical",
            momentum_min=8,
            momentum_max=10,
            expected_keywords=[
                "ai",
                "code",
                "developer",
                "editor"
            ],
            expected_icp_keywords=[
                "developers",
                "engineers",
                "programmers"
            ]
        )
    },

    {
        "company_name": "HubSpot",
        "expectation": EvalExpectation(
            expected_tone="hybrid",
            momentum_min=6,
            momentum_max=8,
            expected_keywords=[
                "crm",
                "marketing",
                "sales",
                "automation"
            ],
            expected_icp_keywords=[
                "businesses",
                "sales teams",
                "marketing teams"
            ]
        )
    }
]