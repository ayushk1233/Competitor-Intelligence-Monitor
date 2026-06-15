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
    },
    {
        "company_name": "Openai",
        "expectation": EvalExpectation(
            expected_tone="visionary",
            momentum_min=8,
            momentum_max=10,
            expected_keywords=["ai", "models", "api", "enterprise"],
            expected_icp_keywords=["developers", "enterprises", "consumers"],
            expected_company_concepts=[
                "foundation models",
                "enterprise AI",
                "API ecosystem",
                "platform company"
            ],
            expected_strategic_pass=[
                "commercially established",
                "platform ecosystem"
            ],
            expected_strategic_fail=[
                "early commercialization",
                "developer tools only"
            ]
        )
    },
    {
        "company_name": "Google",
        "expectation": EvalExpectation(
            expected_tone="enterprise",
            momentum_min=6,
            momentum_max=9,
            expected_keywords=["cloud", "ai", "search", "workspace"],
            expected_icp_keywords=["enterprises", "consumers", "developers"],
            expected_company_concepts=[
                "cloud",
                "AI platform",
                "search ecosystem",
                "consumer ecosystem"
            ],
            expected_strategic_pass=[
                "ecosystem company",
                "platform company"
            ],
            expected_strategic_fail=[
                "primarily a developer tools company",
                "niche provider"
            ]
        )
    },
    {
        "company_name": "Anthropic",
        "expectation": EvalExpectation(
            expected_tone="visionary",
            momentum_min=8,
            momentum_max=10,
            expected_keywords=["claude", "safety", "ai", "enterprise"],
            expected_icp_keywords=["enterprises", "developers", "researchers"],
            expected_company_concepts=[
                "Claude",
                "AI safety",
                "enterprise AI",
                "foundation models"
            ],
            expected_strategic_pass=[
                "enterprise focused",
                "safety focused"
            ],
            expected_strategic_fail=[
                "consumer only",
                "unestablished"
            ]
        )
    }
]