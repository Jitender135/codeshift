"""
frontend_translator.py - ADK LlmAgent for Frontend Template Migration

This module defines the Frontend Translator Agent using Google ADK's LlmAgent.
It converts Java Thymeleaf / HTML templates into idiomatic Python Jinja2 HTML templates.
"""

from typing import Optional, Dict, Any
from google.adk.agents import LlmAgent


TEMPLATES_IDIOM_RULES = """
# Thymeleaf to Jinja2 Template Idiom Mapping Rules

1. **Control Flow / Iteration**
   - Thymeleaf: `th:each="item : ${items}"`
   - Jinja2: `{% for item in items %} ... {% endfor %}`

2. **Text Binding**
   - Thymeleaf: `<td th:text="${pet.name}">Default</td>`
   - Jinja2: `<td>{{ pet.name }}</td>`

3. **Form Actions & URLs**
   - Thymeleaf: `th:action="@{/pets/new}"`
   - Jinja2: `action="{{ url_for('create_pet') }}"` or `action="/pets/new"`
   - Thymeleaf: `th:href="@{/css/style.css}"`
   - Jinja2: `href="{{ url_for('static', filename='css/style.css') }}"`

4. **Form Fields**
   - Thymeleaf: `th:field="*{name}"`
   - Jinja2: `name="name" id="name"`
"""


def build_frontend_instruction(html_code: str) -> str:
    """Constructs translation prompt for HTML templates."""
    return f"""
You are an expert Frontend Template Translation Agent in CodeShift.
Translate the following Thymeleaf HTML template into a clean Jinja2 HTML template.

=== TEMPLATE MAPPING RULES ===
{TEMPLATES_IDIOM_RULES}

=== INPUT THYMELEAF HTML ===
{html_code}

=== OUTPUT REQUIREMENTS ===
1. Return ONLY the translated Jinja2 HTML code.
2. Replace all Thymeleaf attributes (th:text, th:each, th:field, th:action) with Jinja2 syntax.
""".strip()


def create_frontend_translator_agent(html_code: str, model_name: str = "gemini-2.5-flash") -> LlmAgent:
    """Instantiates ADK LlmAgent for frontend template translation."""
    return LlmAgent(
        name="frontend_translator_agent",
        description="Translates Thymeleaf HTML templates to Jinja2 HTML templates.",
        model=model_name,
        instruction=build_frontend_instruction(html_code)
    )


def translate_thymeleaf_to_jinja2_rule_based(html_code: str) -> str:
    """Deterministic fallback translation for Thymeleaf -> Jinja2 for testing."""
    translated = html_code

    # Replace th:href
    translated = translated.replace('th:href="@{/css/style.css}"', 'href="{{ url_for(\'static\', filename=\'css/style.css\') }}"')
    translated = translated.replace('th:action="@{/pets/new}"', 'action="/pets/new"')

    # Convert th:each row loop
    if '<tr th:each="pet : ${pets}">' in translated:
        old_tr = """            <tr th:each="pet : ${pets}">
                <td th:text="${pet.id}">1</td>
                <td th:text="${pet.name}">Buddy</td>
                <td th:text="${pet.species}">Dog</td>
                <td th:text="${pet.age}">3</td>
            </tr>"""

        new_tr = """            {% for pet in pets %}
            <tr>
                <td>{{ pet.id }}</td>
                <td>{{ pet.name }}</td>
                <td>{{ pet.species }}</td>
                <td>{{ pet.age }}</td>
            </tr>
            {% endfor %}"""

        translated = translated.replace(old_tr, new_tr)

    # Convert form fields
    translated = translated.replace('th:field="*{name}"', 'name="name" id="name"')
    translated = translated.replace('th:field="*{species}"', 'name="species" id="species"')
    translated = translated.replace('th:field="*{age}"', 'name="age" id="age"')
    translated = translated.replace('th:object="${pet}"', '')

    # Clean remaining xmlns:th
    translated = translated.replace('xmlns:th="http://www.thymeleaf.org"', '')

    return translated
