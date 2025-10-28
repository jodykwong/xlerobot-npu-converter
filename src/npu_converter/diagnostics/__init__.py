"""
Diagnostics Module

Intelligent diagnostic and repair guidance system for model validation failures.
Extends the ErrorHandler from Story 1.7 with smart diagnosis capabilities.
"""

from .diagnostic_engine import DiagnosticEngine
from .knowledge_base import DiagnosticKnowledgeBase
from .repair_guide import RepairGuide

__all__ = [
    'DiagnosticEngine',
    'DiagnosticKnowledgeBase',
    'RepairGuide'
]
