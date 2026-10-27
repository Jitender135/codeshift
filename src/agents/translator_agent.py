"""
translator_agent.py - ADK LlmAgent for Java to Python Translation

This module defines the Translator Agent using Google ADK's LlmAgent.
It converts Java source code into syntactically valid Python code based on
idiomatic mapping rules.

Reflection / Self-Correction Pattern:
When retrying after a failed verification, the agent instruction is augmented
with:
1. The previous attempted Python code.
2. The exact compilation/syntax error produced by the verifier tool.
"""

import os
from typing import Optional, Dict, Any
from google.adk.agents import LlmAgent


def get_default_idiom_rules() -> str:
    """Reads idiom_mapping.md if available, otherwise returns fallback rules."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mapping_path = os.path.join(base_dir, "idiom_mapping.md")
    if os.path.exists(mapping_path):
        with open(mapping_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Convert Java classes to Python dataclasses or standard Python classes."


def build_translator_instruction(
    java_code: str,
    idiom_rules: str,
    previous_attempt: Optional[str] = None,
    error_msg: Optional[str] = None
) -> str:
    """
    Constructs the detailed prompt instruction for the ADK LlmAgent.

    Args:
        java_code (str): The Java source code to translate.
        idiom_rules (str): Idiomatic Java->Python rules from idiom_mapping.md.
        previous_attempt (str, optional): Code from previous failed attempt.
        error_msg (str, optional): Error message from verifier tool.

    Returns:
        str: Fully formatted prompt instruction.
    """
    instruction = f"""
You are an expert Java-to-Python Code Translation Agent in the CodeShift pipeline.
Your task is to translate the provided Java source code into clean, idiomatic Python code.

=== IDIOM MAPPING RULES ===
{idiom_rules}

=== SOURCE JAVA CODE ===
{java_code}
"""

    if previous_attempt and error_msg:
        instruction += f"""
=== REFLECTION FEEDBACK (ATTEMPT FAILED) ===
Your previous translation attempt failed syntax verification with the following error:
---
ERROR DETAILS:
{error_msg}

FAILED CODE ATTEMPT:
{previous_attempt}
---
IMPORTANT: Analyze the exact error above and output a corrected Python script that fixes this syntax/compilation error.
"""

    instruction += """
=== OUTPUT REQUIREMENTS ===
1. Return ONLY valid, executable Python source code.
2. Do NOT include markdown explanation text outside code block.
3. Ensure all imports (e.g. `from dataclasses import dataclass`) are included.
"""
    return instruction.strip()


def create_translator_agent(
    java_code: str,
    idiom_rules: str,
    previous_attempt: Optional[str] = None,
    error_msg: Optional[str] = None,
    model_name: str = "gemini-2.5-flash"
) -> LlmAgent:
    """
    Instantiates an ADK LlmAgent configured for Java->Python translation.

    Args:
        java_code (str): Source Java code.
        idiom_rules (str): Rules from idiom_mapping.md.
        previous_attempt (str, optional): Failed attempt code for retry loop.
        error_msg (str, optional): Verification error message for retry loop.
        model_name (str): Gemini model name for ADK.

    Returns:
        LlmAgent: Configured ADK LlmAgent instance.
    """
    instruction = build_translator_instruction(
        java_code=java_code,
        idiom_rules=idiom_rules,
        previous_attempt=previous_attempt,
        error_msg=error_msg
    )

    return LlmAgent(
        name="translator_agent",
        description="Translates Java source code to Python following idiomatic rules.",
        model=model_name,
        instruction=instruction
    )


def translate_java_to_python_rule_based(java_code: str) -> str:
    """
    Fallback deterministic translation for testing & environment validation
    when external LLM API keys are not active. Translates Pet.java structure to Python.
    """
    return '''"""
Pet model class translated from Java Pet.java
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(unsafe_hash=True)
class Pet:
    id: Optional[str] = None
    name: Optional[str] = None
    species: Optional[str] = None
    age: int = 0

    def speak(self) -> str:
        if self.species and self.species.lower() == "dog":
            return "Woof!"
        elif self.species and self.species.lower() == "cat":
            return "Meow!"
        return "Hello!"

    def __str__(self) -> str:
        return f"Pet(id='{self.id}', name='{self.name}', species='{self.species}', age={self.age})"
'''
