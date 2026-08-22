"""Scraper: compile web interfaces into verified agent capabilities."""

from .models import (
    Capability,
    CapabilityStatus,
    Evidence,
    ExecutionResult,
    LeadProfile,
    LeadSignal,
)

__all__ = [
    "Capability",
    "CapabilityStatus",
    "Evidence",
    "ExecutionResult",
    "LeadProfile",
    "LeadSignal",
]

__version__ = "0.1.0"
