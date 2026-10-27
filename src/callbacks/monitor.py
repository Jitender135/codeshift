"""
monitor.py - Task Monitoring and Logging using Callback Functions

Fulfills Requirement 5 (Task Monitoring & Logging using Callback functions):
- Intercepts agent start, finish, error, and tool calls across both Google ADK and CrewAI.
- Tracks intermediate outputs, execution flows, and latency with millisecond precision.
- Writes structured JSONL trace logs to output/execution_trace.jsonl for auditability and debugging.
"""

import os
import sys
import time
import json
import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


# Ensure UTF-8 console output if supported
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


class ExecutionTraceEvent(BaseModel):
    """Pydantic model representing an observed execution event."""
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
    event_type: str  # AGENT_START, AGENT_FINISH, AGENT_ERROR, TOOL_START, TOOL_FINISH, GUARDRAIL_CHECK, STATE_UPDATE
    framework: str  # Google-ADK, CrewAI, MCP, Pipeline
    actor: str
    message: str
    duration_ms: Optional[float] = None
    data: Dict[str, Any] = Field(default_factory=dict)


class CodeShiftCallbackMonitor:
    """
    Central monitoring and callback dispatcher.
    Tracks intermediate outputs, execution flows, and errors for transparency.
    """

    def __init__(self, output_dir: Optional[str] = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.output_dir = os.path.abspath(output_dir or os.path.join(base_dir, "output"))
        os.makedirs(self.output_dir, exist_ok=True)
        self.trace_file = os.path.join(self.output_dir, "execution_trace.jsonl")
        self.events: List[ExecutionTraceEvent] = []
        self._start_times: Dict[str, float] = {}

    def set_output_dir(self, output_dir: str):
        """Dynamically update output directory and trace file path."""
        self.output_dir = os.path.abspath(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        self.trace_file = os.path.join(self.output_dir, "execution_trace.jsonl")

    def _log_event(self, event: ExecutionTraceEvent):
        """Appends event in memory and flushes to trace file."""
        self.events.append(event)
        try:
            with open(self.trace_file, "a", encoding="utf-8") as f:
                f.write(event.model_dump_json() + "\n")
        except Exception:
            pass

    def on_agent_start(self, agent_name: str, framework: str, task: str, input_summary: Optional[Dict[str, Any]] = None):
        """Callback fired when an agent starts a task."""
        self._start_times[f"agent_{agent_name}"] = time.time()
        event = ExecutionTraceEvent(
            event_type="AGENT_START",
            framework=framework,
            actor=agent_name,
            message=f"Agent '{agent_name}' ({framework}) started task: {task}",
            data=input_summary or {}
        )
        self._log_event(event)
        print(f"[{event.timestamp}] [{framework}] [{agent_name}] [STARTED] {task}")

    def on_agent_finish(self, agent_name: str, framework: str, output_summary: Optional[Dict[str, Any]] = None):
        """Callback fired when an agent completes a task."""
        st = self._start_times.pop(f"agent_{agent_name}", time.time())
        duration_ms = round((time.time() - st) * 1000, 2)
        event = ExecutionTraceEvent(
            event_type="AGENT_FINISH",
            framework=framework,
            actor=agent_name,
            message=f"Agent '{agent_name}' ({framework}) completed task in {duration_ms}ms",
            duration_ms=duration_ms,
            data=output_summary or {}
        )
        self._log_event(event)
        print(f"[{event.timestamp}] [{framework}] [{agent_name}] [FINISHED] in {duration_ms}ms")

    def on_agent_error(self, agent_name: str, framework: str, error: str, attempt: int = 1):
        """Callback fired on agent execution error or retry."""
        event = ExecutionTraceEvent(
            event_type="AGENT_ERROR",
            framework=framework,
            actor=agent_name,
            message=f"Agent '{agent_name}' ({framework}) encountered error on Attempt {attempt}: {error}",
            data={"attempt": attempt, "error": error}
        )
        self._log_event(event)
        print(f"[{event.timestamp}] [{framework}] [{agent_name}] [ERROR] (Attempt {attempt}): {error}")

    def on_tool_start(self, tool_name: str, arguments: Dict[str, Any]):
        """Callback fired before tool execution."""
        self._start_times[f"tool_{tool_name}"] = time.time()
        event = ExecutionTraceEvent(
            event_type="TOOL_START",
            framework="MCP",
            actor=tool_name,
            message=f"MCP Tool '{tool_name}' invoked",
            data={"arguments": {k: str(v)[:100] for k, v in arguments.items()}}
        )
        self._log_event(event)
        print(f"[{event.timestamp}] [MCP-TOOL] [CALL] {tool_name}")

    def on_tool_finish(self, tool_name: str, result_summary: Optional[Dict[str, Any]] = None, success: bool = True):
        """Callback fired after tool execution."""
        st = self._start_times.pop(f"tool_{tool_name}", time.time())
        duration_ms = round((time.time() - st) * 1000, 2)
        status_tag = "[PASS]" if success else "[FAIL]"
        event = ExecutionTraceEvent(
            event_type="TOOL_FINISH",
            framework="MCP",
            actor=tool_name,
            message=f"MCP Tool '{tool_name}' executed in {duration_ms}ms (Success: {success})",
            duration_ms=duration_ms,
            data=result_summary or {}
        )
        self._log_event(event)
        print(f"[{event.timestamp}] [MCP-TOOL] {status_tag} [FINISHED] {tool_name} ({duration_ms}ms)")

    def on_guardrail_check(self, guardrail_name: str, passed: bool, details: str):
        """Callback fired on security guardrail validation."""
        event = ExecutionTraceEvent(
            event_type="GUARDRAIL_CHECK",
            framework="Guardrail",
            actor=guardrail_name,
            message=f"Guardrail '{guardrail_name}' {'PASSED' if passed else 'BLOCKED'}: {details}",
            data={"passed": passed, "details": details}
        )
        self._log_event(event)
        tag = "[GUARDRAIL PASSED]" if passed else "[GUARDRAIL BLOCKED]"
        print(f"[{event.timestamp}] [GUARDRAIL] {tag} {guardrail_name} -> {details}")

    def on_state_transition(self, old_stage: str, new_stage: str, actor: str):
        """Callback fired when shared state transitions between pipeline phases."""
        event = ExecutionTraceEvent(
            event_type="STATE_UPDATE",
            framework="Pipeline",
            actor=actor,
            message=f"State transitioned: {old_stage} -> {new_stage} by {actor}",
            data={"from": old_stage, "to": new_stage}
        )
        self._log_event(event)
        print(f"[{event.timestamp}] [STATE-SYNC] {old_stage} -> {new_stage} (via {actor})")



# Global monitor instance
pipeline_monitor = CodeShiftCallbackMonitor()
