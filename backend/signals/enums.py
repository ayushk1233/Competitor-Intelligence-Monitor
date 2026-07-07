from enum import Enum

class SignalSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SignalStatus(str, Enum):
    NEW = "new"
    ACTIVE = "active"
    RESOLVED = "resolved"
    SUPERSEDED = "superseded"
