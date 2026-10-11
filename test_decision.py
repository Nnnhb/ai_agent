import asyncio

from dotenv import load_dotenv
from agents import Runner

from core.decision import decision_agent


load_dotenv()


async def main():
    result = await Runner.run(
        decision_agent,
        "Build a Python web application that researches the latest AI news, "
        "stores the results in a database, analyzes trends, and displays "
        "them on a dashboard."
    )

    print(result.final_output.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())