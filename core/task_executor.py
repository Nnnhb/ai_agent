"""
UIE Task Executor

The Task Executor is responsible for executing a validated
TaskPlan in a deterministic way.

The Planner decides:

    What needs to be done.

The Task Executor enforces:

    How and when those tasks are executed.

Responsibilities:

- validate task dependencies
- prevent execution before dependencies are complete
- select the correct specialist
- execute ready tasks
- pass previous results to dependent tasks
- track task status
- stop safely when a task fails
- return structured execution results

The Task Executor does NOT create plans.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from agents import Agent, Runner

from core.planner import Task, TaskPlan

from specialists.coding import coding_agent
from specialists.research import research_agent
from specialists.creative import creative_agent
from specialists.security import security_agent


SPECIALIST_REGISTRY: Dict[str, Agent] = {
    "CODING": coding_agent,
    "RESEARCH": research_agent,
    "CREATIVE": creative_agent,
    "SECURITY": security_agent,
}


@dataclass
class TaskExecutionResult:
    task_id: str
    specialist: str
    status: str
    output: str
    error: Optional[str] = None


class TaskExecutor:
    """
    Deterministic executor for UIE TaskPlans.
    """

    def __init__(self):
        self.results: Dict[
            str,
            TaskExecutionResult,
        ] = {}

    def validate_plan(
        self,
        plan: TaskPlan,
    ) -> None:
        """
        Perform additional execution-level validation.

        Raises ValueError if the plan cannot be safely
        executed.
        """

        task_ids = {
            task.id
            for task in plan.tasks
        }

        for task in plan.tasks:

            specialist = task.specialist.upper().strip()

            if specialist not in SPECIALIST_REGISTRY:
                raise ValueError(
                    f"Task '{task.id}' uses unavailable "
                    f"specialist '{specialist}'."
                )

            for dependency in task.depends_on:

                if dependency not in task_ids:
                    raise ValueError(
                        f"Task '{task.id}' depends on "
                        f"unknown task '{dependency}'."
                    )

                if dependency == task.id:
                    raise ValueError(
                        f"Task '{task.id}' cannot depend "
                        "on itself."
                    )

        self._validate_no_cycles(plan)

    def _validate_no_cycles(
        self,
        plan: TaskPlan,
    ) -> None:
        """
        Detect circular dependencies.

        Example of an invalid graph:

            A → B
            B → C
            C → A
        """

        task_map = {
            task.id: task
            for task in plan.tasks
        }

        visiting = set()
        visited = set()

        def visit(task_id: str):

            if task_id in visiting:
                raise ValueError(
                    "Circular task dependency detected "
                    f"at '{task_id}'."
                )

            if task_id in visited:
                return

            visiting.add(task_id)

            task = task_map[task_id]

            for dependency in task.depends_on:
                visit(dependency)

            visiting.remove(task_id)
            visited.add(task_id)

        for task in plan.tasks:
            visit(task.id)

    def get_ready_tasks(
        self,
        plan: TaskPlan,
    ) -> List[Task]:
        """
        Return tasks whose dependencies have all completed.
        """

        ready_tasks = []

        for task in plan.tasks:

            if task.id in self.results:
                continue

            dependencies_complete = all(
                dependency in self.results
                and self.results[dependency].status
                == "COMPLETED"
                for dependency in task.depends_on
            )

            if dependencies_complete:
                ready_tasks.append(task)

        return ready_tasks

    def build_task_input(
        self,
        task: Task,
        original_request: str,
    ) -> str:
        """
        Build the input passed to a specialist.

        A task receives:

        - the original user objective
        - its own task description
        - outputs from completed dependencies
        """

        sections = [
            "ORIGINAL USER REQUEST",
            "=====================",
            original_request,
            "",
            "CURRENT TASK",
            "============",
            f"Task ID: {task.id}",
            f"Specialist: {task.specialist}",
            f"Description: {task.description}",
        ]

        if task.depends_on:

            sections.extend(
                [
                    "",
                    "PREVIOUS TASK RESULTS",
                    "=====================",
                ]
            )

            for dependency in task.depends_on:

                result = self.results.get(
                    dependency
                )

                if result is None:
                    continue

                sections.extend(
                    [
                        "",
                        f"--- {dependency} ---",
                        result.output,
                    ]
                )

        return "\n".join(sections)

    async def execute_task(
        self,
        task: Task,
        original_request: str,
    ) -> TaskExecutionResult:
        """
        Execute one task using the correct specialist.
        """

        specialist_name = (
            task.specialist.upper().strip()
        )

        specialist = SPECIALIST_REGISTRY.get(
            specialist_name
        )

        if specialist is None:

            result = TaskExecutionResult(
                task_id=task.id,
                specialist=specialist_name,
                status="FAILED",
                output="",
                error=(
                    f"Specialist '{specialist_name}' "
                    "is not registered."
                ),
            )

            self.results[task.id] = result

            return result

        task_input = self.build_task_input(
            task,
            original_request,
        )

        try:

            execution = await Runner.run(
                specialist,
                task_input,
            )

            result = TaskExecutionResult(
                task_id=task.id,
                specialist=specialist_name,
                status="COMPLETED",
                output=execution.final_output,
            )

            self.results[task.id] = result

            return result

        except Exception as error:

            result = TaskExecutionResult(
                task_id=task.id,
                specialist=specialist_name,
                status="FAILED",
                output="",
                error=str(error),
            )

            self.results[task.id] = result

            return result

    async def execute_plan(
        self,
        plan: TaskPlan,
        original_request: str,
    ) -> List[TaskExecutionResult]:
        """
        Execute the complete TaskPlan.

        Tasks are executed only when all of their
        dependencies have completed successfully.

        If a task fails, execution stops safely.
        """

        self.results.clear()

        self.validate_plan(plan)

        total_tasks = len(plan.tasks)

        while len(self.results) < total_tasks:

            ready_tasks = self.get_ready_tasks(
                plan
            )

            if not ready_tasks:

                incomplete_tasks = [
                    task.id
                    for task in plan.tasks
                    if task.id not in self.results
                ]

                raise RuntimeError(
                    "No executable tasks remain, "
                    "but the plan is incomplete. "
                    f"Remaining tasks: {incomplete_tasks}"
                )

            for task in ready_tasks:

                print(
                    f"[TASK EXECUTOR] Starting "
                    f"{task.id} ({task.specialist})"
                )

                result = await self.execute_task(
                    task,
                    original_request,
                )

                print(
                    f"[TASK EXECUTOR] "
                    f"{task.id}: {result.status}"
                )

                if result.status == "FAILED":

                    raise RuntimeError(
                        f"Task '{task.id}' failed: "
                        f"{result.error}"
                    )

        return [
            self.results[task.id]
            for task in plan.tasks
        ]