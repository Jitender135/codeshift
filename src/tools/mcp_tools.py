"""
mcp_tools.py - MCP-Compliant Tool Registry for CodeShift Pipeline

Fulfills Requirement 2 (Tool Integration using MCP):
Provides 4 production MCP tools:
1. verify_python_code: Deterministic syntax & compiler verification tool.
2. ast_file_parser: Custom AST parser for Java and Python files.
3. dependency_database_lookup: Database lookup mapping Maven dependencies to PyPI equivalents.
4. code_metric_calculator: Calculator tool computing LOC, cyclomatic complexity, and token counts.
"""

import os
import sys
import json
import re
import ast
from typing import Dict, Any, List, Optional
import javalang

from tools.verifier_tool import verify_python_code


# -------------------------------------------------------------
# Tool 1: verify_python_code (already implemented in verifier_tool)
# -------------------------------------------------------------


# -------------------------------------------------------------
# Tool 2: ast_file_parser (Custom File Parser Tool)
# -------------------------------------------------------------
def ast_file_parser(file_content: str, language: str = "java") -> Dict[str, Any]:
    """
    Parses source code into an AST and extracts structured metadata.

    Args:
        file_content (str): The raw code string.
        language (str): 'java' or 'python'.

    Returns:
        Dict[str, Any]: Classes, methods, imports, annotations, and complexity features.
    """
    lang = language.lower().strip()
    if lang == "java":
        classes = []
        methods = []
        imports = []
        annotations = []
        has_hash_code = False
        has_equals = False

        try:
            tree = javalang.parse.parse(file_content)
            for imp in tree.imports:
                imports.append(imp.path)
            for path, node in tree.filter(javalang.tree.ClassDeclaration):
                classes.append(node.name)
                for anno in node.annotations:
                    annotations.append(anno.name)
                for m in node.methods:
                    methods.append(m.name)
                    if m.name == "hashCode":
                        has_hash_code = True
                    elif m.name == "equals":
                        has_equals = True
        except Exception:
            # Fallback regex parsing
            for m in re.finditer(r"public\s+class\s+(\w+)", file_content):
                classes.append(m.group(1))
            for m in re.finditer(r"import\s+([\w\.]+);", file_content):
                imports.append(m.group(1))
            has_hash_code = "hashCode()" in file_content or "Objects.hash" in file_content
            has_equals = "equals(Object" in file_content

        return {
            "status": "success",
            "language": "java",
            "classes": classes,
            "methods": methods,
            "imports": imports,
            "annotations": annotations,
            "has_hash_code": has_hash_code,
            "has_equals": has_equals,
            "class_count": len(classes),
            "method_count": len(methods)
        }

    elif lang == "python":
        classes = []
        functions = []
        imports = []
        try:
            tree = ast.parse(file_content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.Import):
                    for n in node.names:
                        imports.append(n.name)
                elif isinstance(node, ast.ImportFrom):
                    mod = node.module or ""
                    for n in node.names:
                        imports.append(f"{mod}.{n.name}")
            return {
                "status": "success",
                "language": "python",
                "classes": classes,
                "functions": functions,
                "imports": imports,
                "class_count": len(classes),
                "function_count": len(functions)
            }
        except Exception as exc:
            return {"status": "error", "language": "python", "error": str(exc)}

    return {"status": "error", "error": f"Unsupported language: {language}"}


# -------------------------------------------------------------
# Tool 3: dependency_database_lookup (Database / Library Lookup Tool)
# -------------------------------------------------------------
MAVEN_TO_PYPI_DATABASE = {
    "spring-boot-starter-web": {
        "python_package": "fastapi",
        "version": ">=0.110.0",
        "description": "Modern, fast web framework for building APIs with Python",
        "category": "Web Framework",
        "pip_install": "pip install fastapi uvicorn"
    },
    "spring-boot-starter-data-jpa": {
        "python_package": "sqlalchemy",
        "version": ">=2.0.0",
        "description": "SQL toolkit and Object-Relational Mapping (ORM) library",
        "category": "Database / ORM",
        "pip_install": "pip install sqlalchemy"
    },
    "spring-boot-starter-thymeleaf": {
        "python_package": "jinja2",
        "version": ">=3.1.0",
        "description": "Fast, expressive, and extensible template engine",
        "category": "Template Engine",
        "pip_install": "pip install jinja2"
    },
    "lombok": {
        "python_package": "dataclasses",
        "version": "stdlib",
        "description": "Standard library dataclasses decorator providing auto getters/setters/hash",
        "category": "Code Generation / Boilerplate",
        "pip_install": "# built-in standard library"
    },
    "jackson-databind": {
        "python_package": "pydantic",
        "version": ">=2.0.0",
        "description": "Data validation and structured settings management",
        "category": "Serialization / Validation",
        "pip_install": "pip install pydantic"
    },
    "junit-jupiter": {
        "python_package": "pytest",
        "version": ">=8.0.0",
        "description": "Mature, full-featured testing framework for Python",
        "category": "Testing",
        "pip_install": "pip install pytest"
    },
    "mysql-connector-java": {
        "python_package": "mysql-connector-python",
        "version": ">=8.0.0",
        "description": "Standard MySQL driver for Python applications",
        "category": "Database Driver",
        "pip_install": "pip install mysql-connector-python"
    },
    "h2": {
        "python_package": "sqlite3",
        "version": "stdlib",
        "description": "Embedded in-memory SQL database engine",
        "category": "Embedded Database",
        "pip_install": "# built-in standard library"
    }
}


def dependency_database_lookup(dependency_query: str) -> Dict[str, Any]:
    """
    Looks up equivalent Python/PyPI packages for Java/Maven dependencies.

    Args:
        dependency_query (str): Maven artifact ID or keyword (e.g. 'spring-boot-starter-web', 'lombok').

    Returns:
        Dict[str, Any]: Matching PyPI package metadata, version requirements, and install instructions.
    """
    clean_query = dependency_query.lower().strip()
    # Check exact match
    if clean_query in MAVEN_TO_PYPI_DATABASE:
        data = MAVEN_TO_PYPI_DATABASE[clean_query]
        return {
            "status": "found",
            "query": dependency_query,
            "match": data,
            "all_matches": [data]
        }

    # Partial / keyword match
    matches = []
    for k, v in MAVEN_TO_PYPI_DATABASE.items():
        if clean_query in k or clean_query in v["python_package"] or clean_query in v["category"].lower():
            matches.append({"maven_key": k, **v})

    if matches:
        return {
            "status": "found",
            "query": dependency_query,
            "match": matches[0],
            "all_matches": matches
        }

    return {
        "status": "not_found",
        "query": dependency_query,
        "message": f"No direct mapping found for '{dependency_query}'. Defaulting to general Python ecosystem.",
        "fallback": {"python_package": "pydantic", "pip_install": "pip install pydantic"}
    }


# -------------------------------------------------------------
# Tool 4: code_metric_calculator (Calculator Tool)
# -------------------------------------------------------------
def code_metric_calculator(source_code: str, target_code: Optional[str] = None) -> Dict[str, Any]:
    """
    Calculates code metrics: Lines of Code (LOC), cyclomatic complexity estimate,
    token counts, and migration similarity diff.

    Args:
        source_code (str): Source Java/Python code string.
        target_code (str, optional): Target Python code to compare.

    Returns:
        Dict[str, Any]: Calculated metrics.
    """
    src_lines = source_code.splitlines()
    total_loc = len(src_lines)
    blank_lines = sum(1 for line in src_lines if not line.strip())
    comment_lines = sum(1 for line in src_lines if line.strip().startswith(("//", "#", "/*", "*")))
    code_lines = total_loc - blank_lines - comment_lines

    # Estimate cyclomatic complexity via branching keywords
    branching_keywords = ["if", "elif", "else if", "for", "while", "case", "catch", "except", "&&", "||", "and", "or"]
    complexity_score = 1
    for line in src_lines:
        for kw in branching_keywords:
            if re.search(rf"\b{re.escape(kw)}\b", line):
                complexity_score += 1

    # Token estimate (approx 4 chars per token)
    estimated_tokens = max(1, len(source_code) // 4)

    result = {
        "total_lines": total_loc,
        "code_lines": code_lines,
        "comment_lines": comment_lines,
        "blank_lines": blank_lines,
        "cyclomatic_complexity": complexity_score,
        "estimated_tokens": estimated_tokens
    }

    if target_code is not None:
        tgt_lines = target_code.splitlines()
        tgt_code_lines = sum(1 for line in tgt_lines if line.strip() and not line.strip().startswith(("#", '"""')))
        reduction_percentage = round(((code_lines - tgt_code_lines) / max(code_lines, 1)) * 100, 2)
        result["target_code_lines"] = tgt_code_lines
        result["loc_reduction_percentage"] = reduction_percentage
        result["conciseness_rating"] = "Significantly More Concise" if reduction_percentage > 15 else "Equivalent Density"

    return result
