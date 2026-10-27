"""
a2a_protocol.py - Agent-to-Agent (A2A) Interoperability Protocol

Fulfills Requirement 6 & 7:
- Standardized Agent-to-Agent (A2A) protocol envelope for cross-framework communication.
- Connects Google-ADK agents with CrewAI agents with strict Pydantic envelope validation.
- Supports performatives: REQUEST, INFORM, HANDOFF, AGREE, REFUSE, FAILURE.
"""

import uuid
import datetime
from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field

from callbacks.monitor import pipeline_monitor


class AgentIdentity(BaseModel):
    """Identity of an agent participating in A2A communication."""
    framework: Literal["Google-ADK", "CrewAI"] = Field(..., description="Agentic framework name")
    agent_name: str = Field(..., description="Name of the agent")
    role: Optional[str] = Field(default=None, description="Role / Capability description")


class A2AMessage(BaseModel):
    """
    Standardized A2A (Agent-to-Agent) Protocol Message Envelope (A2A/1.0).
    """
    protocol_version: str = Field(default="A2A/1.0")
    message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:12]}")
    conversation_id: str = Field(default_factory=lambda: f"conv_{uuid.uuid4().hex[:8]}")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
    performative: Literal["REQUEST", "INFORM", "HANDOFF", "AGREE", "REFUSE", "FAILURE"] = Field(
        ..., description="FIPA-inspired A2A speech act performative"
    )
    sender: AgentIdentity
    recipient: AgentIdentity
    topic: str = Field(..., description="Domain topic: e.g. code_quality_audit, dependency_resolution")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Task arguments or output data")
    state_context: Dict[str, Any] = Field(default_factory=dict, description="Shared context or session metadata")


class A2AMessageBus:
    """
    Interoperable Message Exchange routing A2A envelopes between Google ADK and CrewAI.
    """

    def __init__(self):
        self.handlers: Dict[str, Any] = {}
        self.message_history: List[A2AMessage] = []

    def register_agent(self, agent_name: str, framework: str, handler_callable):
        """Registers an agent handler for incoming A2A messages."""
        key = f"{framework}::{agent_name}"
        self.handlers[key] = handler_callable
        print(f"[A2A Bus] Registered endpoint: '{key}'")

    def send_message(self, message: A2AMessage) -> A2AMessage:
        """
        Dispatches an A2A message to the recipient and returns the response message.
        """
        self.message_history.append(message)
        sender_id = f"{message.sender.framework}::{message.sender.agent_name}"
        recipient_id = f"{message.recipient.framework}::{message.recipient.agent_name}"

        print(f"\n==================================================================")
        print(f" [A2A PROTOCOL] MESSAGE DISPATCH ({message.protocol_version})")
        print(f" From: {sender_id}  -->  To: {recipient_id}")
        print(f" Performative: {message.performative} | Topic: {message.topic}")
        print(f" Message ID:   {message.message_id}")
        print(f"==================================================================")

        pipeline_monitor.on_agent_start(
            agent_name=message.recipient.agent_name,
            framework=message.recipient.framework,
            task=f"A2A Task: {message.topic}",
            input_summary={"from": sender_id, "topic": message.topic}
        )

        handler = self.handlers.get(recipient_id)
        if not handler:
            err_msg = f"A2A Routing Error: No handler registered for '{recipient_id}'"
            print(f"[A2A Error] {err_msg}")
            return A2AMessage(
                performative="FAILURE",
                sender=message.recipient,
                recipient=message.sender,
                conversation_id=message.conversation_id,
                topic=message.topic,
                payload={"error": err_msg}
            )

        try:
            # Execute handler across framework boundary
            response_message = handler(message)
            self.message_history.append(response_message)

            pipeline_monitor.on_agent_finish(
                agent_name=message.recipient.agent_name,
                framework=message.recipient.framework,
                output_summary={"performative": response_message.performative}
            )

            print(f"[A2A Response Received] Status: {response_message.performative} from {recipient_id}")
            return response_message

        except Exception as exc:
            pipeline_monitor.on_agent_error(
                agent_name=message.recipient.agent_name,
                framework=message.recipient.framework,
                error=str(exc)
            )
            return A2AMessage(
                performative="FAILURE",
                sender=message.recipient,
                recipient=message.sender,
                conversation_id=message.conversation_id,
                topic=message.topic,
                payload={"error": f"Handler execution error: {str(exc)}"}
            )


# Global A2A bus
a2a_bus = A2AMessageBus()
