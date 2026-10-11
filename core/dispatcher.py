from typing import Optional

from agents import Agent, Runner

from core.decision import Decision

from tools.files import (
    list_documents,
    read_document,
    read_pdf,
    read_word,
    read_powerpoint,
    read_image,
)

from tools.knowledge import (
    remember_knowledge,
    recall_knowledge,
)

from specialists.coding import coding_agent
from specialists.research import research_agent
from specialists.creative import creative_agent
from specialists.security import security_agent


class DispatchResult:
    def __init__(
        self,
        action: str,
        specialist: Optional[str] = None,
        target: Optional[Agent] = None,
        reason: str = "",
    ):
        self.action = action
        self.specialist = specialist
        self.target = target
        self.reason = reason

    def __repr__(self):
        return (
            f"DispatchResult("
            f"action={self.action!r}, "
            f"specialist={self.specialist!r}, "
            f"reason={self.reason!r})"
        )


def dispatch_decision(
    decision: Decision,
) -> DispatchResult:
    """
    Convert a validated Decision into a concrete
    dispatch instruction.

    The Dispatcher does not make new AI decisions.
    It only maps Decision Engine actions to registered
    system components.
    """

    action = decision.action.upper().strip()

    if action == "ANSWER":
        return DispatchResult(
            action="ANSWER",
            reason=decision.reason,
        )

    if action == "SEARCH":
        return DispatchResult(
            action="SEARCH",
            specialist="RESEARCH",
            target=research_agent,
            reason=decision.reason,
        )

    if action == "READ_FILE":
        return DispatchResult(
            action="READ_FILE",
            reason=decision.reason,
        )

    if action == "PLAN":
        return DispatchResult(
            action="PLAN",
            reason=decision.reason,
        )

    if action == "REMEMBER":
        return DispatchResult(
            action="REMEMBER",
            reason=decision.reason,
        )

    if action == "RECALL":
        return DispatchResult(
            action="RECALL",
            reason=decision.reason,
        )

    if action == "SPECIALIST":

        specialists = {
            specialist.upper().strip()
            for specialist in decision.specialists_needed
        }

        if "CODING" in specialists:
            return DispatchResult(
                action="SPECIALIST",
                specialist="CODING",
                target=coding_agent,
                reason=decision.reason,
            )

        if "RESEARCH" in specialists:
            return DispatchResult(
                action="SPECIALIST",
                specialist="RESEARCH",
                target=research_agent,
                reason=decision.reason,
            )

        if "CREATIVE" in specialists:
            return DispatchResult(
                action="SPECIALIST",
                specialist="CREATIVE",
                target=creative_agent,
                reason=decision.reason,
            )

        if "SECURITY" in specialists:
            return DispatchResult(
                action="SPECIALIST",
                specialist="SECURITY",
                target=security_agent,
                reason=decision.reason,
            )

        return DispatchResult(
            action="ERROR",
            reason=(
                "The Decision Engine requested a specialist "
                "that is not registered with UIE."
            ),
        )

    return DispatchResult(
        action="ERROR",
        reason=(
            f"Unknown Decision Engine action: "
            f"{decision.action}"
        ),
    )


async def execute_dispatch(
    dispatch: DispatchResult,
    user_input: str,
):
    """
    Execute a previously validated dispatch instruction.

    This function does not perform routing.
    It only executes the route selected by the Dispatcher.
    """

    # --------------------------------------------------------
    # SPECIALIST
    # --------------------------------------------------------

    if dispatch.action == "SPECIALIST":

        if dispatch.target is None:
            return (
                "Dispatch error: "
                "no specialist target was registered."
            )

        result = await Runner.run(
            dispatch.target,
            user_input,
        )

        return result.final_output

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    if dispatch.action == "SEARCH":

        if dispatch.target is None:
            return (
                "Dispatch error: "
                "research specialist is unavailable."
            )

        result = await Runner.run(
            dispatch.target,
            user_input,
        )

        return result.final_output

    # --------------------------------------------------------
    # FILE READING
    # --------------------------------------------------------

    if dispatch.action == "READ_FILE":

        file_reader = Agent(
            name="File Reader",

            instructions="""
You are UIE's File Reading Specialist.

Read and explain files using the available
file-reading tools.

Choose the appropriate tool based on the
requested file type.

Do not invent file contents.

If a requested file does not exist, report that
fact clearly.

Do not modify files.
""",

            tools=[
                list_documents,
                read_document,
                read_pdf,
                read_word,
                read_powerpoint,
                read_image,
            ],
        )

        result = await Runner.run(
            file_reader,
            user_input,
        )

        return result.final_output

    # --------------------------------------------------------
    # REMEMBER
    # --------------------------------------------------------

    if dispatch.action == "REMEMBER":

        memory_agent = Agent(
            name="Memory Specialist",

            instructions="""
You are UIE's Memory Specialist.

Save information requested by the user
using the memory tool.

Only save information when the user clearly
asks UIE to remember or store it.

Do not claim information was saved unless
the memory tool actually succeeds.

Do not invent memory entries.
""",

            tools=[
                remember_knowledge,
            ],
        )

        result = await Runner.run(
            memory_agent,
            user_input,
        )

        return result.final_output

    # --------------------------------------------------------
    # RECALL
    # --------------------------------------------------------

    if dispatch.action == "RECALL":

        memory_agent = Agent(
            name="Memory Recall Specialist",

            instructions="""
You are UIE's Memory Recall Specialist.

Search UIE's stored knowledge using the
memory recall tool.

Do not invent memories.

If no matching memory is found, say so clearly.
""",

            tools=[
                recall_knowledge,
            ],
        )

        result = await Runner.run(
            memory_agent,
            user_input,
        )

        return result.final_output

    # --------------------------------------------------------
    # PLAN
    # --------------------------------------------------------

    if dispatch.action == "PLAN":

        return (
            "PLAN action must be executed by the "
            "UIE Orchestrator."
        )

    # --------------------------------------------------------
    # ANSWER
    # --------------------------------------------------------

    if dispatch.action == "ANSWER":
        return None

    # --------------------------------------------------------
    # ERROR
    # --------------------------------------------------------

    if dispatch.action == "ERROR":
        return dispatch.reason

    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------

    return (
        f"Dispatcher does not have an execution handler "
        f"for action: {dispatch.action}"
    )
