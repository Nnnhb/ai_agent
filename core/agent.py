from dotenv import load_dotenv

from agents import (
    Agent,
    Runner,
    SQLiteSession,
    set_tracing_disabled,
)

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
    recall_exact_knowledge,
    forget_knowledge,
)

from core.decision import decision_agent

from core.dispatcher import (
    dispatch_decision,
    execute_dispatch,
)

from core.orchestrator import orchestrator_agent


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

set_tracing_disabled(True)


# ============================================================
# CONVERSATION SESSION
# ============================================================

# This is conversational session history.
#
# It is different from UIE's structured knowledge database:
#
#     SQLiteSession
#         ↓
#     conversation history
#
#     knowledge.db
#         ↓
#     persistent structured memory
#
session = SQLiteSession(
    "uie_main",
    "data/memory/uie_memory.db",
)


# ============================================================
# CENTRAL UIE AGENT
# ============================================================

# IMPORTANT:
#
# The central UIE agent intentionally has NO operational tools.
#
# Web search, file reading, memory, coding, security, etc.
# must be reached through the Decision Engine and Dispatcher.
#
# This prevents the central model from bypassing the
# architecture.

uie = Agent(
    name="UIE",

    instructions="""
You are UIE — Universal Intelligence Engine.

You are the central conversational interface.

The Decision Engine and Dispatcher are the authoritative
control system for deciding how requests are handled.

The architecture is:

    USER
      ↓
    DECISION ENGINE
      ↓
    DISPATCHER
      ↓
    TOOL / SPECIALIST / ORCHESTRATOR
      ↓
    RESULT
      ↓
    UIE
      ↓
    USER

Your responsibilities are:

- answer normal questions
- explain results clearly
- maintain conversational context
- synthesize information already provided to you
- communicate the result to the user

You are NOT responsible for routing.

You are NOT responsible for deciding which specialist
should handle a request.

You do NOT have direct operational tools.

Do not claim that you searched the web, modified a file,
executed code, stored memory, or performed another action
unless that action was actually performed by the system.

Do not invent tool results.

If a result from another component is provided, explain
that result accurately without changing its meaning.
""",
)


# ============================================================
# MAIN UIE EXECUTION
# ============================================================

async def run_uie(user_input: str):

    print()
    print("========== UIE ORCHESTRATION ==========")

    # --------------------------------------------------------
    # STEP 1 — DECISION ENGINE
    # --------------------------------------------------------

    decision_result = await Runner.run(
        decision_agent,
        user_input,
    )

    decision = decision_result.final_output

    print("Decision Engine:")
    print(f"  Action: {decision.action}")
    print(f"  Reason: {decision.reason}")

    if decision.specialists_needed:
        print(
            "  Specialists:",
            ", ".join(decision.specialists_needed),
        )

    print(
        f"  Planning required: "
        f"{decision.requires_planning}"
    )

    # --------------------------------------------------------
    # STEP 2 — DISPATCHER
    # --------------------------------------------------------

    dispatch = dispatch_decision(decision)

    print()
    print("Dispatcher:")
    print(f"  Action: {dispatch.action}")

    if dispatch.specialist:
        print(
            f"  Specialist: "
            f"{dispatch.specialist}"
        )

    print(f"  Reason: {dispatch.reason}")

    # --------------------------------------------------------
    # STEP 3 — SPECIALIST / SEARCH
    # --------------------------------------------------------

    if dispatch.action in (
        "SPECIALIST",
        "SEARCH",
    ):

        print()
        print(
            f"Executing: "
            f"{dispatch.specialist}"
        )

        response = await execute_dispatch(
            dispatch,
            user_input,
        )

        print()
        print("=======================================")
        print()

        return response

    # --------------------------------------------------------
    # STEP 4 — COMPLEX ORCHESTRATION
    # --------------------------------------------------------

    if dispatch.action == "PLAN":

        print()
        print("Complex request detected.")
        print(
            "Sending request to "
            "UIE Orchestrator..."
        )

        result = await Runner.run(
            orchestrator_agent,
            user_input,
        )

        print()
        print("=======================================")
        print()

        return result.final_output

    # --------------------------------------------------------
    # STEP 5 — MEMORY
    # --------------------------------------------------------

    if dispatch.action in (
        "REMEMBER",
        "RECALL",
    ):

        result = await execute_dispatch(
            dispatch,
            user_input,
        )

        print()
        print("=======================================")
        print()

        return result

    # --------------------------------------------------------
    # STEP 6 — FILE READING
    # --------------------------------------------------------

    if dispatch.action == "READ_FILE":

        result = await execute_dispatch(
            dispatch,
            user_input,
        )

        print()
        print("=======================================")
        print()

        return result

    # --------------------------------------------------------
    # STEP 7 — NORMAL ANSWER
    # --------------------------------------------------------

    if dispatch.action == "ANSWER":

        result = await Runner.run(
            uie,
            user_input,
            session=session,
        )

        print()
        print("=======================================")
        print()

        return result.final_output

    # --------------------------------------------------------
    # STEP 8 — ERROR
    # --------------------------------------------------------

    if dispatch.action == "ERROR":

        print()
        print("=======================================")
        print()

        return dispatch.reason

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    return (
        "UIE could not determine how to execute "
        "this request."
    )
