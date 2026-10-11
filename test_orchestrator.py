import asyncio
from dotenv import load_dotenv
from agents import Runner
from core.orchestrator import orchestrator_agent

load_dotenv()


async def main():
    result = await Runner.run(
        orchestrator_agent,
        """
        Build a Python application that researches the latest AI news,
        stores the results in a database, analyzes trends,
        and displays them on a dashboard.
        """
    )

    print()
    print("========== ORCHESTRATOR TEST ==========")
    print(result.final_output)
    print("========================================")


if __name__ == "__main__":
    asyncio.run(main())