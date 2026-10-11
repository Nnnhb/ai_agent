import asyncio

from core.planner import Task, TaskPlan
from core.task_executor import (
    TaskExecutor,
    TaskExecutionResult,
)


async def main():

    print()
    print("========== TASK EXECUTOR TEST ==========")
    print()

    # --------------------------------------------------
    # TEST 1: Create a valid task dependency graph
    # --------------------------------------------------

    plan = TaskPlan(
        objective="Test deterministic task execution",
        complexity="COMPLEX",
        specialists=["CODING"],
        tasks=[
            Task(
                id="task_a",
                description="Complete the first task.",
                specialist="CODING",
            ),
            Task(
                id="task_b",
                description="Use the result from task A.",
                specialist="CODING",
                depends_on=["task_a"],
            ),
            Task(
                id="task_c",
                description="Use the result from task B.",
                specialist="CODING",
                depends_on=["task_b"],
            ),
        ],
        final_synthesis="Combine the completed task results.",
    )

    executor = TaskExecutor()

    # --------------------------------------------------
    # TEST 2: Validate the plan
    # --------------------------------------------------

    executor.validate_plan(plan)

    print("TEST 1: Plan validation")
    print("PASS - Plan is valid.")
    print()

    # --------------------------------------------------
    # TEST 3: Check initial ready tasks
    # --------------------------------------------------

    ready_tasks = executor.get_ready_tasks(plan)

    print("TEST 2: Initial ready tasks")
    print(
        "Ready tasks:",
        [task.id for task in ready_tasks],
    )

    if [task.id for task in ready_tasks] == ["task_a"]:
        print("PASS - Only task_a can start.")
    else:
        print("FAIL - Dependency system is incorrect.")

    print()

    # --------------------------------------------------
    # TEST 4: Simulate task A completing
    # --------------------------------------------------

    executor.results["task_a"] = TaskExecutionResult(
        task_id="task_a",
        specialist="CODING",
        status="COMPLETED",
        output="Task A completed successfully.",
    )

    ready_tasks = executor.get_ready_tasks(plan)

    print("TEST 3: After task_a completes")
    print(
        "Ready tasks:",
        [task.id for task in ready_tasks],
    )

    if [task.id for task in ready_tasks] == ["task_b"]:
        print("PASS - task_b unlocked correctly.")
    else:
        print("FAIL - task_b was not unlocked correctly.")

    print()

    # --------------------------------------------------
    # TEST 5: Simulate task B completing
    # --------------------------------------------------

    executor.results["task_b"] = TaskExecutionResult(
        task_id="task_b",
        specialist="CODING",
        status="COMPLETED",
        output="Task B completed successfully.",
    )

    ready_tasks = executor.get_ready_tasks(plan)

    print("TEST 4: After task_b completes")
    print(
        "Ready tasks:",
        [task.id for task in ready_tasks],
    )

    if [task.id for task in ready_tasks] == ["task_c"]:
        print("PASS - task_c unlocked correctly.")
    else:
        print("FAIL - task_c was not unlocked correctly.")

    print()

    # --------------------------------------------------
    # TEST 6: Test circular dependency protection
    # --------------------------------------------------

    circular_plan = TaskPlan(
        objective="Test circular dependency detection",
        complexity="COMPLEX",
        specialists=["CODING"],
        tasks=[
            Task(
                id="task_a",
                description="Depends on task B.",
                specialist="CODING",
                depends_on=["task_b"],
            ),
            Task(
                id="task_b",
                description="Depends on task A.",
                specialist="CODING",
                depends_on=["task_a"],
            ),
        ],
        final_synthesis="Test circular dependency handling.",
    )

    try:

        executor.validate_plan(circular_plan)

        print("TEST 5: Circular dependency detection")
        print("FAIL - Circular dependency was not detected.")

    except ValueError as error:

        print("TEST 5: Circular dependency detection")
        print("PASS - Circular dependency detected.")
        print("Message:", error)

    print()

    print("========================================")
    print("       TASK EXECUTOR TEST COMPLETE")
    print("========================================")
    print()


if __name__ == "__main__":
    asyncio.run(main())