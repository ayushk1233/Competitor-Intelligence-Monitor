import re

with open('backend/retrieval/signal_extractor.py', 'r') as f:
    content = f.read()

# Fix LAUNCH_PATTERNS
lp_old = """    (r"new\\s+product[:\\s]+(.{5,80})", 1),
    (r"added\\s+support\\s+for\\s+(.{5,80})", 1),
]"""
lp_new = """    (r"new\\s+product[:\\s]+(.{5,80})", 1),
    (r"added\\s+support\\s+for\\s+(.{5,80})", 1),
    (r"([A-Za-z][A-Za-z0-9\\- ]{5,40}\\s+published\\s+20\\d\\d)", 1),
    (r"(new feature)", 1),
    (r"(feature release)", 1),
    (r"(semantic search)", 1),
    (r"(reinforcement learning)", 1)
]"""
content = content.replace(lp_old, lp_new)

# Fix LAUNCH_SENTENCE_PATTERNS
ls_old = """    r"\\bhelps power\\b",
    r"published\\s+20\\d\\d",
    r"new feature",
    r"feature release",
    r"agent",
    r"indexing",
    r"semantic search",
    r"reinforcement learning"
]"""
ls_new = """    r"\\bhelps power\\b"
]"""
content = content.replace(ls_old, ls_new)

with open('backend/retrieval/signal_extractor.py', 'w') as f:
    f.write(content)
