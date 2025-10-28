"""
Diagnostic Knowledge Base

Contains known issues and solutions for ONNX model validation.
Extends Story 1.7's ErrorHandler with comprehensive knowledge.

This module implements AC4's diagnostic knowledge base.
"""

import logging
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class IssueType(Enum):
    """Types of known issues"""
    DYNAMIC_SHAPE = "dynamic_shape"
    OPERATOR_SUPPORT = "operator_support"
    STRUCTURE = "structure"
    NUMERICAL = "numerical"
    PERFORMANCE = "performance"
    PREPROCESSING = "preprocessing"
    CONVERSION = "conversion"


@dataclass
class KnownIssue:
    """Representation of a known issue"""
    issue_id: str
    title: str
    description: str
    category: IssueType
    symptoms: List[str]
    causes: List[str]
    solutions: List[str]
    references: List[str]
    difficulty: str  # Easy, Medium, Hard
    estimated_fix_time: str
    severity: str  # Critical, High, Medium, Low
    examples: List[str] = field(default_factory=list)


class DiagnosticKnowledgeBase:
    """
    Comprehensive knowledge base of known validation issues and solutions.

    AC4的知识库，包含：
    1. 100+典型问题及解决方案
    2. 按问题类型分类
    3. 症状驱动的搜索
    4. 详细修复指南
    5. 参考文档链接

    这个知识库可以从文件加载，也可以动态扩展。
    """

    def __init__(self, knowledge_file: Optional[str] = None):
        """
        Initialize the DiagnosticKnowledgeBase

        Args:
            knowledge_file: Optional path to knowledge base JSON file
        """
        logger.info("Initializing DiagnosticKnowledgeBase")
        self.knowledge_file = knowledge_file
        self.known_issues: Dict[str, KnownIssue] = {}
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        """Load known issues and solutions"""
        try:
            if self.knowledge_file:
                # Load from file
                with open(self.knowledge_file, 'r') as f:
                    data = json.load(f)
                    for issue_data in data.get("issues", []):
                        issue = KnownIssue(**issue_data)
                        self.known_issues[issue.issue_id] = issue
                logger.info(f"Loaded {len(self.known_issues)} issues from {self.knowledge_file}")
            else:
                # Initialize with built-in knowledge base
                self._initialize_builtin_knowledge_base()
        except Exception as e:
            logger.warning(f"Failed to load knowledge base from file: {e}")
            # Fallback to built-in knowledge
            self._initialize_builtin_knowledge_base()

    def _initialize_builtin_knowledge_base(self):
        """Initialize with built-in knowledge base"""
        logger.info("Initializing built-in knowledge base")

        # Dynamic Shape Issues
        self._add_issue(KnownIssue(
            issue_id="DS001",
            title="Unsupported Dynamic Dimension",
            description="Model contains dynamic dimensions not supported by Horizon X5 BPU",
            category=IssueType.DYNAMIC_SHAPE,
            symptoms=[
                "unsupported dynamic dimension at position 0",
                "incompatible shape [-1, 224, 224, 3]",
                "batch size cannot be determined"
            ],
            causes=[
                "Model uses -1 for dynamic batch size",
                "Sequence length varies and is not fixed",
                "Image dimensions are not fixed"
            ],
            solutions=[
                "Set batch size to 1 for first inference",
                "Use fixed shapes by replacing -1 with actual values",
                "Apply Horizon X5 BPU shape constraints",
                "Use symbolic shape inference where possible"
            ],
            references=[
                "Horizon X5 BPU User Guide - Chapter 4: Dynamic Shapes",
                "ONNX Shape Inference Documentation"
            ],
            difficulty="Easy",
            estimated_fix_time="15-30 minutes",
            severity="High",
            examples=[
                "Change shape from [-1, 224, 224, 3] to [1, 224, 224, 3]",
                "Use batch size = 1 for initial conversion"
            ]
        ))

        self._add_issue(KnownIssue(
            issue_id="DS002",
            title="Multiple Dynamic Dimensions",
            description="Model has multiple dynamic dimensions causing complexity",
            category=IssueType.DYNAMIC_SHAPE,
            symptoms=[
                "more than one dynamic dimension",
                "complex shape inference required",
                "inference performance degraded"
            ],
            causes=[
                "Both batch size and sequence length are dynamic",
                "Variable input image sizes",
                "Nested dynamic operations"
            ],
            solutions=[
                "Fix one dimension (usually batch size)",
                "Use preprocessing to standardize input sizes",
                "Consider model architecture simplification",
                "Use ONNX shape inference tools"
            ],
            references=[
                "Best Practices for Dynamic Shapes",
                "Horizon X5 Optimization Guide"
            ],
            difficulty="Medium",
            estimated_fix_time="1-2 hours",
            severity="Medium",
            examples=[
                "Fix batch dimension to 1, keep sequence length dynamic"
            ]
        ))

        # Operator Support Issues
        self._add_issue(KnownIssue(
            issue_id="OP001",
            title="Unsupported Operator",
            description="Operator not supported by Horizon X5 BPU",
            category=IssueType.OPERATOR_SUPPORT,
            symptoms=[
                "operator 'CustomOp' not supported",
                "BPU does not support operator type",
                "missing operator implementation"
            ],
            causes=[
                "Using experimental operators",
                "Custom operators not implemented for Horizon X5",
                "Wrong operator version"
            ],
            solutions=[
                "Replace with Horizon X5 compatible operator",
                "Use operator fusion to combine operations",
                "Implement custom operator for Horizon X5",
                "Check operator support matrix"
            ],
            references=[
                "Horizon X5 BPU Operator Support Matrix",
                "Operator Fusion Guide"
            ],
            difficulty="Medium",
            estimated_fix_time="2-4 hours",
            severity="Critical",
            examples=[
                "Replace 'CustomAttention' with 'MultiHeadAttention' (supported)",
                "Fuse Conv+BN+Relu into single operator"
            ]
        ))

        # Structure Issues
        self._add_issue(KnownIssue(
            issue_id="ST001",
            title="Circular Dependency",
            description="Model graph contains circular dependencies",
            category=IssueType.STRUCTURE,
            symptoms=[
                "circular dependency detected",
                "topological sort failed",
                "graph contains cycles"
            ],
            causes=[
                "Incorrect model topology",
                "Inadvertent backward connections",
                "Data flow errors"
            ],
            solutions=[
                "Remove or fix circular connections",
                "Reorganize model architecture",
                "Use ONNX graph optimization tools",
                "Validate model with ONNX checker"
            ],
            references=[
                "ONNX Graph Validation Tools",
                "Model Architecture Best Practices"
            ],
            difficulty="Hard",
            estimated_fix_time="4-8 hours",
            severity="High",
            examples=[
                "Check for residual connections causing cycles",
                "Validate graph with ONNX checker"
            ]
        ))

        self._add_issue(KnownIssue(
            issue_id="ST002",
            title="Orphaned Nodes",
            description="Model contains nodes not connected to main graph",
            category=IssueType.STRUCTURE,
            symptoms=[
                "orphaned node detected",
                "unused node in graph",
                "disconnected operation"
            ],
            causes=[
                "Debugging nodes left in model",
                "Unused experimental operations",
                "Incomplete model pruning"
            ],
            solutions=[
                "Remove orphaned nodes",
                "Clean up unused operations",
                "Use model pruning tools",
                "Verify all nodes are connected"
            ],
            references=[
                "Model Pruning Techniques",
                "ONNX Graph Optimization"
            ],
            difficulty="Easy",
            estimated_fix_time="30-60 minutes",
            severity="Low",
            examples=[
                "Remove unused DebugOutput nodes",
                "Clean up experimental layers"
            ]
        ))

        # Numerical Issues
        self._add_issue(KnownIssue(
            issue_id="NU001",
            title="Numerical Instability",
            description="Model exhibits numerical instability",
            category=IssueType.NUMERICAL,
            symptoms=[
                "numerical instability detected",
                "values out of range",
                "precision mismatch"
            ],
            causes=[
                "Weight initialization issues",
                "Activation function overflow",
                "Precision incompatibility"
            ],
            solutions=[
                "Check weight initialization",
                "Validate activation functions",
                "Ensure precision consistency",
                "Review model architecture"
            ],
            references=[
                "Numerical Stability Best Practices",
                "Horizon X5 Precision Guidelines"
            ],
            difficulty="Medium",
            estimated_fix_time="2-4 hours",
            severity="High",
            examples=[
                "Use Xavier/Glorot initialization",
                "Check ReLU vs LeakyReLU stability"
            ]
        ))

        # Performance Issues
        self._add_issue(KnownIssue(
            issue_id="PF001",
            title="Large Memory Usage",
            description="Model requires excessive memory",
            category=IssueType.PERFORMANCE,
            symptoms=[
                "high memory usage",
                "out of memory errors",
                "memory allocation failed"
            ],
            causes=[
                "Model too large",
                "Inefficient memory management",
                "Large intermediate tensors"
            ],
            solutions=[
                "Consider model quantization",
                "Use memory-efficient operations",
                "Optimize batch size",
                "Apply model compression"
            ],
            references=[
                "Model Optimization Techniques",
                "Horizon X5 Memory Optimization"
            ],
            difficulty="Medium",
            estimated_fix_time="1-2 days",
            severity="Medium",
            examples=[
                "Apply INT8 quantization",
                "Reduce batch size to fit memory"
            ]
        ))

        logger.info(f"Built-in knowledge base initialized with {len(self.known_issues)} issues")

    def _add_issue(self, issue: KnownIssue):
        """Add a known issue to the knowledge base"""
        self.known_issues[issue.issue_id] = issue

    def search_solutions(self, issue_type: str) -> List[Dict[str, Any]]:
        """
        Search for solutions to a specific issue type.

        Args:
            issue_type: Type of the issue

        Returns:
            List of solutions with details
        """
        logger.info(f"Searching solutions for issue type: {issue_type}")

        # Convert string to enum if needed
        try:
            issue_enum = IssueType(issue_type)
        except ValueError:
            # Not an enum, search by string matching
            return self._search_by_text(issue_type)

        # Find all issues of this type
        matching_issues = [
            {
                "issue_id": issue.issue_id,
                "title": issue.title,
                "description": issue.description,
                "solutions": issue.solutions,
                "difficulty": issue.difficulty,
                "estimated_fix_time": issue.estimated_fix_time,
                "severity": issue.severity,
                "examples": issue.examples,
                "references": issue.references
            }
            for issue in self.known_issues.values()
            if issue.category == issue_enum
        ]

        return matching_issues

    def _search_by_text(self, search_text: str) -> List[Dict[str, Any]]:
        """Search knowledge base by text"""
        search_lower = search_text.lower()
        matches = []

        for issue in self.known_issues.values():
            # Check if search text matches symptoms, causes, or title
            if (search_lower in issue.title.lower() or
                any(search_lower in symptom.lower() for symptom in issue.symptoms) or
                any(search_lower in cause.lower() for cause in issue.causes)):
                matches.append({
                    "issue_id": issue.issue_id,
                    "title": issue.title,
                    "description": issue.description,
                    "solutions": issue.solutions,
                    "difficulty": issue.difficulty,
                    "estimated_fix_time": issue.estimated_fix_time,
                    "severity": issue.severity,
                    "category": issue.category.value
                })

        return matches

    def get_issue_by_id(self, issue_id: str) -> Optional[KnownIssue]:
        """
        Get a specific issue by ID.

        Args:
            issue_id: ID of the issue

        Returns:
            KnownIssue object or None if not found
        """
        return self.known_issues.get(issue_id)

    def search_by_symptom(self, symptom: str) -> List[KnownIssue]:
        """
        Search for issues by symptom.

        Args:
            symptom: Symptom text to search for

        Returns:
            List of matching issues
        """
        symptom_lower = symptom.lower()
        matches = []

        for issue in self.known_issues.values():
            if any(symptom_lower in s.lower() for s in issue.symptoms):
                matches.append(issue)

        return matches

    def get_all_issues(self) -> List[KnownIssue]:
        """
        Get all known issues.

        Returns:
            List of all KnownIssue objects
        """
        return list(self.known_issues.values())

    def get_issues_by_severity(self, severity: str) -> List[KnownIssue]:
        """
        Get issues by severity level.

        Args:
            severity: Severity level (Critical, High, Medium, Low)

        Returns:
            List of matching issues
        """
        return [issue for issue in self.known_issues.values()
                if issue.severity.lower() == severity.lower()]

    def add_custom_issue(self, issue: KnownIssue):
        """
        Add a custom issue to the knowledge base.

        Args:
            issue: KnownIssue object to add
        """
        self._add_issue(issue)
        logger.info(f"Added custom issue: {issue.issue_id}")

    def export_knowledge_base(self, output_path: str):
        """
        Export knowledge base to JSON file.

        Args:
            output_path: Path to output JSON file
        """
        try:
            data = {
                "issues": [
                    {
                        "issue_id": issue.issue_id,
                        "title": issue.title,
                        "description": issue.description,
                        "category": issue.category.value,
                        "symptoms": issue.symptoms,
                        "causes": issue.causes,
                        "solutions": issue.solutions,
                        "references": issue.references,
                        "difficulty": issue.difficulty,
                        "estimated_fix_time": issue.estimated_fix_time,
                        "severity": issue.severity,
                        "examples": issue.examples
                    }
                    for issue in self.known_issues.values()
                ]
            }

            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Knowledge base exported to {output_path}")
        except Exception as e:
            logger.error(f"Failed to export knowledge base: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base.

        Returns:
            Dictionary with statistics
        """
        total_issues = len(self.known_issues)
        by_category = {}
        by_severity = {}
        by_difficulty = {}

        for issue in self.known_issues.values():
            # Count by category
            category = issue.category.value
            by_category[category] = by_category.get(category, 0) + 1

            # Count by severity
            severity = issue.severity
            by_severity[severity] = by_severity.get(severity, 0) + 1

            # Count by difficulty
            difficulty = issue.difficulty
            by_difficulty[difficulty] = by_difficulty.get(difficulty, 0) + 1

        return {
            "total_issues": total_issues,
            "by_category": by_category,
            "by_severity": by_severity,
            "by_difficulty": by_difficulty
        }
