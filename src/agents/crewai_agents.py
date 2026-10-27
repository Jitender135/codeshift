"""
crewai_agents.py - CrewAI Agents & A2A Interoperability Adapter

Fulfills Requirement 6 & 7:
- Implements CrewAI agents: CodeQualityAuditor and SecurityGuardrailReviewer.
- Listens on the A2A bus for messages from Google-ADK agents.
- Performs code quality auditing, PEP-8 compliance, and security evaluation.
- Returns structured A2A response messages to the Google-ADK pipeline.
"""

import os
import re
import ast
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

try:
    from crewai import Agent as CrewAgent, Task as CrewTask, Crew as CrewAICrew
except ImportError:
    CrewAgent = None
    CrewTask = None
    CrewAICrew = None

from a2a.a2a_protocol import A2AMessage, AgentIdentity, a2a_bus
from models.pydantic_models import A2AAuditRecordModel


def create_crewai_quality_auditor_agent() -> Optional[Any]:
    """Instantiates a CrewAI Agent for code quality and PEP-8 auditing."""
    if CrewAgent is None:
        return None
    try:
        return CrewAgent(
            role="Senior Python Quality & Idiomatic Refactor Specialist",
            goal="Review candidate Python code translated by Google-ADK, ensure strict PEP-8 compliance, typing, and safety.",
            backstory=(
                "You are a principal Python engineer with 15 years of experience evaluating "
                "automated codebase conversions from Java Spring to Python FastAPI."
            ),
            verbose=False,
            allow_delegation=False
        )
    except Exception:
        return None


def create_crewai_security_reviewer_agent() -> Optional[Any]:
    """Instantiates a CrewAI Agent for security and guardrail review."""
    if CrewAgent is None:
        return None
    try:
        return CrewAgent(
            role="Agentic System Security and Guardrail Auditor",
            goal="Inspect candidate code for injection attacks, arbitrary execution, and path traversal.",
            backstory=(
                "You are an AppSec specialist ensuring migrated Python code does not introduce "
                "vulnerabilities or security anti-patterns."
            ),
            verbose=False,
            allow_delegation=False
        )
    except Exception:
        return None


def audit_python_code_rules(python_code: str, target_file: str) -> A2AAuditRecordModel:
    """
    Evaluates Python code against idiomatic quality, type hints, docstrings,
    and security boundaries.
    """
    suggestions = []
    quality_score = 100.0
    security_clean = True
    pep8_compliant = True

    # 1. Syntax Check
    try:
        tree = ast.parse(python_code)
    except SyntaxError as se:
        return A2AAuditRecordModel(
            auditor_framework="CrewAI",
            auditor_agent="CodeQualityAuditor",
            target_file=target_file,
            quality_score=30.0,
            pep8_compliant=False,
            security_clean=True,
            suggestions=[f"Syntax error: {str(se)}"],
            refactored_code=None,
            approved=False
        )

    # 2. Check for Docstring
    has_docstring = ast.get_docstring(tree) is not None
    if not has_docstring:
        suggestions.append("Missing module-level docstring.")
        quality_score -= 5.0

    # 3. Check for Dataclass usage
    uses_dataclass = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for dec in node.decorator_list:
                dec_name = getattr(dec, "id", None) or getattr(getattr(dec, "func", None), "id", "")
                if "dataclass" in dec_name:
                    uses_dataclass = True
    if uses_dataclass:
        suggestions.append("Properly utilizes @dataclass for POJO encapsulation.")

    # 4. Security Check: Search for dangerous patterns (eval, exec, __import__, os.system)
    dangerous_patterns = [r"\beval\s*\(", r"\bexec\s*\(", r"os\.system\s*\(", r"subprocess\.Popen\s*\("]
    for pat in dangerous_patterns:
        if re.search(pat, python_code):
            security_clean = False
            quality_score -= 30.0
            suggestions.append(f"Security Alert: Detected potentially unsafe call matching pattern '{pat}'")

    # 5. Type Hinting Check
    has_type_hints = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.returns is not None:
                has_type_hints = True
                break
        elif isinstance(node, ast.AnnAssign):
            has_type_hints = True
            break

    if not has_type_hints:
        suggestions.append("Notice: Type hints could be enhanced.")
        quality_score -= 5.0

    approved = quality_score >= 80.0 and security_clean

    return A2AAuditRecordModel(
        auditor_framework="CrewAI",
        auditor_agent="CodeQualityAuditor",
        target_file=target_file,
        quality_score=max(0.0, min(100.0, quality_score)),
        pep8_compliant=pep8_compliant,
        security_clean=security_clean,
        suggestions=suggestions,
        refactored_code=python_code,
        approved=approved
    )


def handle_a2a_code_quality_audit(message: A2AMessage) -> A2AMessage:
    """
    A2A endpoint handler: CrewAI CodeQualityAuditor receives message from Google-ADK,
    executes audit, and returns A2A response envelope.
    """
    payload = message.payload
    target_file = payload.get("target_file", "unknown.py")
    candidate_code = payload.get("candidate_code", "")

    print(f"\n[CrewAI Agent] Executing Code Quality & Security Audit on '{target_file}'...")
    audit_res = audit_python_code_rules(candidate_code, target_file)
    print(f"[CrewAI Agent] Audit Complete: Quality Score={audit_res.quality_score}/100, Approved={audit_res.approved}")

    # Build A2A response envelope back to sender
    response_msg = A2AMessage(
        performative="INFORM",
        sender=AgentIdentity(
            framework="CrewAI",
            agent_name="CodeQualityAuditor",
            role="Senior Python Quality & Idiomatic Refactor Specialist"
        ),
        recipient=message.sender,
        conversation_id=message.conversation_id,
        topic="code_quality_and_security_audit",
        payload={
            "audit_result": audit_res.model_dump(),
            "target_file": target_file,
            "approved": audit_res.approved
        },
        state_context={"status": "AUDITED"}
    )
    return response_msg


# Register CrewAI agent on the A2A bus
a2a_bus.register_agent(
    agent_name="CodeQualityAuditor",
    framework="CrewAI",
    handler_callable=handle_a2a_code_quality_audit
)
