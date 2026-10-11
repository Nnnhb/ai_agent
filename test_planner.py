import asyncio

from dotenv import load_dotenv
from agents import Runner

from core.planner import planner_agent


load_dotenv()


async def main():
    result = await Runner.run(
        planner_agent,
        """
        Build a Python application that researches the latest AI news,
        stores the results in a database,
        analyzes trends,
        and displays them on a dashboard.
        """,
    )

    plan = result.final_output

    print()
    print("========== PLANNER TEST ==========")
    print()

    print("Objective:")
    print(plan.objective)

    print()
    print("Complexity:")
    print(plan.complexity)

    print()
    print("Specialists:")
    print(plan.specialists)

    print()
    print("Tasks:")

    for task in plan.tasks:
        print(
            f"  {task.id} | "
            f"{task.specialist} | "
            f"depends_on={task.depends_on}"
        )

        print(
            f"    {task.description}"
        )

    print()
    print("Final synthesis:")
    print(plan.final_synthesis)

    print()
    print("==================================")


if __name__ == "__main__":
    asyncio.run(main())
