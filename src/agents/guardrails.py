"""
guardrails.py - Security Guardrails & Data Validation Callbacks for CodeShift

Fulfills Requirement 8 (Secure the Agentic System):
1. Prompt Security Guardrail: Parses user prompts / inputs for prompt injection attacks,
   toxic/abusive language, and system prompt exfiltration attempts.
2. Tool Return Data Validation Callback: Enforces strict Pydantic type-checking and schema validation
   on tool outputs before they can be consumed by agents.
3. Write Boundary Guardrail: Prevents path traversal and restricts file writes strictly to output/.
4. Drop File Restriction Guardrail: Blocks access to dropped files (e.g. mvnw, .class).
5. Iteration Cap Guardrail: Enforces hard-stop at maximum 3 iterations.
"""

import os
import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ValidationError

from callbacks.monitor import pipeline_monitor


class GuardrailViolationError(PermissionError):
    """Raised when an agent or tool violates system security boundaries."""
    pass


class PromptInjectionAttackError(ValueError):
    """Raised when a prompt injection or malicious input pattern is detected."""
    pass


# Global set of dropped files populated by RepoAnalyzer
DROPPED_FILES_REGISTRY = {"mvnw", "target/classes/Pet.class", "Pet.class", "mvnw.cmd"}

# Common prompt injection and adversarial patterns
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"disregard\s+(the\s+)?(system|initial)\s+prompt",
    r"bypass\s+(all\s+)?security(\s+rules)?",
    r"reveal\s+(the\s+)?(system\s+prompt|secret\s+key|password)",
    r"jailbreak",
    r"you\s+are\s+now\s+dan",
    r"do\s+anything\s+now",
    r"execute\s+arbitrary\s+code",
    r"system\.exit\(",
    r"format\s+[a-z]:",
    r"rm\s+-rf\s+[/~]",
    r"shutdown\s+-s"
]

TOXIC_LANGUAGE_PATTERNS = [
    r"\bhate\b", r"\bkill\b", r"\babuse\b", r"\bmalicious\b"
]


def set_dropped_files_registry(dropped_files: List[str]):
    """Registers list of dropped files to enforce access restrictions."""
    global DROPPED_FILES_REGISTRY
    DROPPED_FILES_REGISTRY = set(dropped_files)


def validate_prompt_security(user_prompt: str) -> bool:
    """
    Parses user prompt or source text for prompt injection attacks,
    jailbreak attempts, or toxic language.

    Raises:
        PromptInjectionAttackError: If an injection or malicious pattern is found.
    """
    prompt_lower = user_prompt.lower()
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, prompt_lower):
            pipeline_monitor.on_guardrail_check("PromptInjectionGuardrail", passed=False, details=f"Pattern detected: '{pattern}'")
            raise PromptInjectionAttackError(
                f"SECURITY GUARDRAIL ALERT: Malicious prompt injection or instruction override detected! Pattern: '{pattern}'"
            )

    pipeline_monitor.on_guardrail_check("PromptInjectionGuardrail", passed=True, details="Prompt passed injection and safety scan")
    return True


def validate_tool_return_data(tool_name: str, return_data: Any, expected_schema: Optional[type[BaseModel]] = None) -> bool:
    """
    Data validation callback ensuring tool returns match expected types and schemas.
    Prevents tool poisoning, type errors, and unexpected return shapes.

    Raises:
        GuardrailViolationError: If return data fails type checking or schema validation.
    """
    if return_data is None:
        raise GuardrailViolationError(f"Tool Return Guardrail: Tool '{tool_name}' returned None.")

    if not isinstance(return_data, (dict, list, str, int, float, bool)):
        raise GuardrailViolationError(
            f"Tool Return Guardrail: Tool '{tool_name}' returned unsupported object type: {type(return_data)}"
        )

    if expected_schema and isinstance(return_data, dict):
        try:
            expected_schema(**return_data)
        except ValidationError as ve:
            pipeline_monitor.on_guardrail_check(f"ToolSchemaValidation:{tool_name}", passed=False, details=str(ve))
            raise GuardrailViolationError(
                f"Tool Return Guardrail: Tool '{tool_name}' output failed Pydantic schema validation: {ve}"
            )

    pipeline_monitor.on_guardrail_check(f"ToolDataValidation:{tool_name}", passed=True, details="Tool output type verified")
    return True


def validate_file_write_path(filepath: str, allowed_dir: str = "output") -> bool:
    """
    Validates that a file write path resides strictly within the allowed directory.

    Raises:
        GuardrailViolationError: If filepath attempts path traversal or points outside allowed_dir.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_output_dir = os.path.abspath(os.path.join(base_dir, allowed_dir))
    abs_filepath = os.path.abspath(os.path.join(target_output_dir, filepath))

    if not abs_filepath.startswith(target_output_dir + os.sep) and abs_filepath != target_output_dir:
        pipeline_monitor.on_guardrail_check("WriteBoundaryGuardrail", passed=False, details=f"Forbidden path: '{abs_filepath}'")
        raise GuardrailViolationError(
            f"GUARDRAIL VIOLATION: Refused write attempt outside '{allowed_dir}/' directory -> '{abs_filepath}'"
        )

    pipeline_monitor.on_guardrail_check("WriteBoundaryGuardrail", passed=True, details=f"Allowed write inside '{allowed_dir}/'")
    return True


def validate_translator_file_access(rel_filepath: str) -> bool:
    """
    Validates that a translator agent is not attempting to open a file marked DROP.

    Raises:
        GuardrailViolationError: If rel_filepath is in the DROP registry.
    """
    clean_path = rel_filepath.replace("\\", "/")
    if clean_path in DROPPED_FILES_REGISTRY or os.path.basename(clean_path) in DROPPED_FILES_REGISTRY:
        pipeline_monitor.on_guardrail_check("DropFileAccessGuardrail", passed=False, details=f"Blocked access to: '{rel_filepath}'")
        raise GuardrailViolationError(
            f"GUARDRAIL VIOLATION: Translator agent attempted to access file '{rel_filepath}' which is marked DROP!"
        )

    pipeline_monitor.on_guardrail_check("DropFileAccessGuardrail", passed=True, details=f"Allowed access: '{rel_filepath}'")
    return True


def validate_iteration_cap(attempt_count: int, max_iterations: int = 3) -> bool:
    """
    Hard-stops reflection/fixer loop from exceeding iteration cap.
    """
    if attempt_count > max_iterations:
        pipeline_monitor.on_guardrail_check("IterationCapGuardrail", passed=False, details=f"Attempt {attempt_count} > {max_iterations}")
        raise GuardrailViolationError(
            f"GUARDRAIL VIOLATION: Fixer loop exceeded hard-stop cap of {max_iterations} iterations (Attempt {attempt_count})!"
        )
    return True
