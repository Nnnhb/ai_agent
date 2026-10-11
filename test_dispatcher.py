from core.decision import Decision
from core.dispatcher import dispatch_decision


decision = Decision(
    action="SPECIALIST",
    reason="The user wants to execute a Python file.",
    tools_needed=["run_python_file"],
    specialists_needed=["CODING"],
    requires_planning=False,
    requires_memory=False,
)

result = dispatch_decision(decision)

print("========== DISPATCHER TEST ==========")
print("Action:", result.action)
print("Specialist:", result.specialist)
print("Target:", result.target.name if result.target else None)
print("Reason:", result.reason)
print("====================================")
