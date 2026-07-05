from enum import Enum

class TemporalChangeCategory(str, Enum):
    MESSAGING = "messaging"
    PRICING = "pricing"
    ICP = "icp"
    PRODUCT = "product"
    HIRING = "hiring"
    PARTNERSHIP = "partnership"
    GTM = "gtm"
    POSITIONING = "positioning"
    MARKET = "market"
    UNKNOWN = "unknown"

class TemporalChangeDirection(str, Enum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    STRENGTHENED = "strengthened"
    WEAKENED = "weakened"
    STABLE = "stable"
    UNKNOWN = "unknown"

class TemporalConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
