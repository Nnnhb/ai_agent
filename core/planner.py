from typing import List

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)

from agents import Agent


VALID_SPECIALISTS = {
    "CODING",
    "RESEARCH",
    "CREATIVE",
    "SECURITY",
}


class Task(BaseModel):
    id: str = Field(
        description="Unique task identifier, such as task_1"
    )

    description: str = Field(
        description="What this task needs to accomplish"
    )

    specialist: str = Field(
        description="The specialist responsible for this task"
    )

    depends_on: List[str] = Field(
        default_factory=list,
        description="Task IDs that must be completed first"
    )

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Task ID cannot be empty."
            )

        return value

    @field_validator("specialist")
    @classmethod
    def validate_specialist(cls, value: str) -> str:
        value = value.upper().strip()

        if value not in VALID_SPECIALISTS:
            raise ValueError(
                f"Unknown specialist '{value}'. "
                f"Valid specialists: "
                f"{', '.join(sorted(VALID_SPECIALISTS))}"
            )

        return value


class TaskPlan(BaseModel):
    objective: str = Field(
        description="The main objective of the user's request"
    )

    complexity: str = Field(
        description="SIMPLE or COMPLEX"
    )

    specialists: List[str] = Field(
        description="Specialists required for the request"
    )

    tasks: List[Task] = Field(
        description="Ordered tasks required to complete the objective"
    )

    final_synthesis: str = Field(
        description="What the final answer should combine"
    )

    @field_validator("complexity")
    @classmethod
    def validate_complexity(cls, value: str) -> str:
        value = value.upper().strip()

        if value not in {"SIMPLE", "COMPLEX"}:
            raise ValueError(
                "Complexity must be SIMPLE or COMPLEX."
            )

        return value

    @field_validator("specialists")
    @classmethod
    def validate_specialists(
        cls,
        values: List[str],
    ) -> List[str]:

        normalized = [
            value.upper().strip()
            for value in values
        ]

        invalid = [
            value
            for value in normalized
            if value not in VALID_SPECIALISTS
        ]

        if invalid:
            raise ValueError(
                f"Unknown specialist(s): "
                f"{', '.join(invalid)}"
            )

        return list(dict.fromkeys(normalized))

    @model_validator(mode="after")
    def validate_tasks(self):

        task_ids = [
            task.id
            for task in self.tasks
        ]

        if len(task_ids) != len(set(task_ids)):
            raise ValueError(
                "Task IDs must be unique."
            )

        task_id_set = set(task_ids)

        for task in self.tasks:

            for dependency in task.depends_on:

                if dependency not in task_id_set:
                    raise ValueError(
                        f"Task '{task.id}' depends on "
                        f"unknown task '{dependency}'."
                    )

                if dependency == task.id:
                    raise ValueError(
                        f"Task '{task.id}' cannot depend "
                        "on itself."
                    )

        specialist_set = set(
            self.specialists
        )

        for task in self.tasks:

            if task.specialist not in specialist_set:
                raise ValueError(
                    f"Task '{task.id}' uses specialist "
                    f"'{task.specialist}', but that "
                    "specialist is not listed in the plan."
                )

        return self


planner_agent = Agent(
    name="UIE Planner",

    instructions="""
You are UIE's planning specialist.

Your job is to convert complex user requests into
structured, executable task plans.

Available specialists:

- CODING
- RESEARCH
- CREATIVE
- SECURITY

Rules:

1. Break complex requests into clear tasks.
2. Give every task a unique ID.
3. Use only the available specialists.
4. Use depends_on when one task must happen before another.
5. Avoid unnecessary tasks.
6. Keep tasks specific and actionable.
7. Mark the request SIMPLE or COMPLEX.
8. List every specialist actually required.
9. Make the final_synthesis explain how the results
   should be combined.

Do not perform the tasks yourself.

Only create the plan.

The resulting plan must be internally consistent:

- no duplicate task IDs
- no unknown dependencies
- no self-dependencies
- no unknown specialists
""",

    output_type=TaskPlan,
)
