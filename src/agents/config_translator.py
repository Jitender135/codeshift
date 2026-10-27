"""
config_translator.py - Configuration File Transformer for CodeShift Phase V2

This module handles TRANSFORM files, converting Maven pom.xml to requirements.txt
and Spring application.properties to Python config.py / environment settings.
"""

import re
from typing import Dict, Any, Tuple


def transform_pom_to_requirements(pom_content: str) -> str:
    """Converts Maven pom.xml dependencies to Python requirements.txt."""
    reqs = ["fastapi>=0.115.0", "uvicorn>=0.30.0", "jinja2>=3.1.0", "pydantic>=2.0.0"]

    if "spring-boot-starter-data-jpa" in pom_content:
        reqs.append("sqlalchemy>=2.0.0")

    return "\n".join(reqs) + "\n"


def transform_properties_to_config(props_content: str) -> str:
    """Converts Java application.properties to Python config.py."""
    lines = props_content.splitlines()
    config_vars = {}

    for line in lines:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            clean_key = key.strip().upper().replace(".", "_")
            config_vars[clean_key] = val.strip()

    output = ['"""Auto-generated Python App Configuration from application.properties"""', "import os\n"]

    for k, v in config_vars.items():
        if v.isdigit():
            output.append(f"{k} = int(os.getenv('{k}', {v}))")
        elif v.lower() in ["true", "false"]:
            output.append(f"{k} = os.getenv('{k}', '{v}').lower() == 'true'")
        else:
            output.append(f"{k} = os.getenv('{k}', '{v}')")

    return "\n".join(output) + "\n"


def transform_config_file(rel_path: str, content: str) -> Tuple[str, str]:
    """
    Transforms a configuration file.

    Args:
        rel_path (str): Relative path to source config file.
        content (str): File contents.

    Returns:
        Tuple[str, str]: (target_filename, transformed_content)
    """
    if rel_path.endswith("pom.xml"):
        return "requirements.txt", transform_pom_to_requirements(content)
    elif rel_path.endswith("application.properties"):
        return "config.py", transform_properties_to_config(content)
    else:
        return rel_path + ".config", content
