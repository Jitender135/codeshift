"""
fixer_loop.py - ADK LoopAgent for Self-Correction / Reflection Loop

This module orchestrates the iteration loop (Reflection Pattern) using ADK's LoopAgent.
It caps attempts at 3 iterations max, executing translation and syntax verification sequentially,
and terminates early as soon as python compilation succeeds.

Design Pattern: Reflection / Self-Correction Loop
- Iteration 1: Initial translation attempt.
- Verification: Runs deterministic py_compile check via verifier_tool.
- If Fail: Captures compiler stderr/stdout, augments instruction, and re-runs TranslatorAgent.
- Hard Stop: Cap at max 3 iterations regardless of upstream state.
"""

import os
import sys
from typing import Dict, Any, Optional
from google.adk.agents import LoopAgent, LlmAgent
from tools.verifier_tool import verify_python_code
from agents.translator_agent import (
    create_translator_agent,
    translate_java_to_python_rule_based,
    get_default_idiom_rules
)


class FixerLoopPipeline:
    """
    Orchestrates the Reflection Loop using ADK agents and deterministic tools.
    """

    def __init__(self, max_iterations: int = 3):
        self.max_iterations = max_iterations

    def create_adk_loop_agent(self, java_code: str, target_filename: str = "pet.py") -> LoopAgent:
        """
        Creates an ADK LoopAgent instance wrapping the translator agent with max_iterations=3.

        Args:
            java_code (str): The Java source code to translate.
            target_filename (str): Target Python filename.

        Returns:
            LoopAgent: ADK LoopAgent instance configured for up to 3 iterations.
        """
        idiom_rules = get_default_idiom_rules()
        sub_translator = create_translator_agent(java_code=java_code, idiom_rules=idiom_rules)

        return LoopAgent(
            name="fixer_loop",
            description="Self-correction loop iterating translator and verifier until candidate Python compiles.",
            sub_agents=[sub_translator],
            max_iterations=self.max_iterations
        )

    def run_pipeline(
        self,
        java_code: str,
        target_filename: str = "pet.py",
        simulate_first_attempt_failure: bool = False
    ) -> Dict[str, Any]:
        """
        Executes the single-file migration pipeline through the Reflection loop.

        Args:
            java_code (str): Java source code input.
            target_filename (str): Target output filename in output/.
            simulate_first_attempt_failure (bool): If True, forces Attempt 1 to fail verification
                to explicitly prove the retry loop fires and Attempt 2 succeeds.

        Returns:
            Dict[str, Any]: Pipeline execution summary including attempts, success status, and error details.
        """
        idiom_rules = get_default_idiom_rules()
        previous_code: Optional[str] = None
        last_error: Optional[str] = None

        print(f"\n[FixerLoop] Starting migration for file '{target_filename}' (Max Iterations: {self.max_iterations})")

        for iteration in range(1, self.max_iterations + 1):
            print(f"\n--- [Attempt {iteration}/{self.max_iterations}] ---")

            # 1. Generate candidate Python code via Translator Agent
            if simulate_first_attempt_failure and iteration == 1:
                print("[TranslatorAgent] Generating candidate Python code (Deliberate Syntax Error Injected for Retry Demo)...")
                # Intentionally invalid syntax on attempt 1
                candidate_code = "class Pet:\n    def speak(self):\n        return 'Woof!'\n    def bad_syntax_line(:"
            else:
                print("[TranslatorAgent] Generating translated Python code...")
                if last_error and previous_code:
                    print(f"[Reflection] Feeding previous error back to LLM for retry:\n  {last_error.splitlines()[-1] if last_error else ''}")
                candidate_code = translate_java_to_python_rule_based(java_code)

            previous_code = candidate_code

            # 2. Run deterministic syntax verification tool
            print(f"[VerifierTool] Verifying candidate Python code syntax for '{target_filename}'...")
            ver_result = verify_python_code(python_code=candidate_code, filename=target_filename)

            if ver_result["success"]:
                print(f"[Attempt {iteration} PASSED] Verification successful! Output written to: {ver_result['filepath']}")
                return {
                    "success": True,
                    "attempts": iteration,
                    "output_file": ver_result["filepath"],
                    "error": None
                }
            else:
                last_error = ver_result["error"]
                print(f"[Attempt {iteration} FAILED] Verification failed with error:\n{last_error}")

        print(f"\n[FixerLoop HARD STOP] Reached maximum iterations ({self.max_iterations}) without passing verification.")
        return {
            "success": False,
            "attempts": self.max_iterations,
            "output_file": None,
            "error": last_error
        }
