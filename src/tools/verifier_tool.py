"""
verifier_tool.py - Deterministic Verification Tool for Google ADK Pipeline

This module provides an ADK FunctionTool that writes candidate Python code to disk
and verifies its syntax using python's built-in `py_compile` module.

Guardrail Enforcement:
- Refuses to write files outside the designated `output/` directory.
- Catches compilation errors and returns exact traceback/error details to feed back to the LLM.
"""

import os
import sys
import subprocess
import threading
import time
from typing import Dict, Any
from google.adk.tools import FunctionTool

_compile_lock = threading.Lock()


def verify_python_code(python_code: str, filename: str = "pet.py", output_dir: str = None) -> Dict[str, Any]:
    """
    Writes translated Python source code to target output directory, compiles it with py_compile,
    and returns a status dict indicating success or compilation error.

    Args:
        python_code (str): The candidate Python source code to verify.
        filename (str): Target file name relative to output/ directory.
        output_dir (str, optional): Target output directory. Defaults to base output/ dir.

    Returns:
        Dict[str, Any]: Dictionary containing success status, errors, and filepath.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if output_dir is None:
        target_output_dir = os.path.abspath(os.path.join(base_dir, "output"))
    else:
        target_output_dir = os.path.abspath(output_dir)

    # Ensure output directory exists
    os.makedirs(target_output_dir, exist_ok=True)

    # Construct canonical target path
    target_path = os.path.abspath(os.path.join(target_output_dir, filename))

    # STRICT GUARDRAIL CHECK: Path traversal & location verification
    # Target file MUST be inside the designated output directory
    if not target_path.startswith(target_output_dir + os.sep) and target_path != target_output_dir:
        return {
            "success": False,
            "error": f"GUARDRAIL VIOLATION: Refused write attempt outside output directory ({target_path}).",
            "filepath": None
        }

    # Clean markdown wrapper if LLM mistakenly included it
    clean_code = python_code.strip()
    if clean_code.startswith("```python"):
        clean_code = clean_code[9:]
    elif clean_code.startswith("```"):
        clean_code = clean_code[3:]
    if clean_code.endswith("```"):
        clean_code = clean_code[:-3]
    clean_code = clean_code.strip()

    # Write code to target output file
    try:
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(clean_code)
    except Exception as exc:
        return {
            "success": False,
            "error": f"IO Error writing to {target_path}: {str(exc)}",
            "filepath": None
        }

    # Run py_compile via subprocess to deterministically verify Python syntax
    compile_cmd = [sys.executable, "-m", "py_compile", target_path]
    with _compile_lock:
        res = subprocess.run(compile_cmd, capture_output=True, text=True)
        if res.returncode != 0 and "WinError 5" in res.stderr:
            time.sleep(0.1)
            res = subprocess.run(compile_cmd, capture_output=True, text=True)

    if res.returncode == 0:
        return {
            "success": True,
            "error": None,
            "filepath": target_path
        }
    else:
        # Compilation failed: extract error details for Reflection Feedback
        err_msg = res.stderr.strip() or res.stdout.strip() or "Syntax verification failed."
        return {
            "success": False,
            "error": err_msg,
            "filepath": target_path
        }


# Wrap raw Python function into ADK FunctionTool
verifier_tool = FunctionTool(func=verify_python_code)
