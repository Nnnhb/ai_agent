import asyncio
from core.agent import run_uie


async def main():
    print()
    print("========================================")
    print("      UIE - UNIVERSAL INTELLIGENCE")
    print("========================================")
    print("Type 'exit' to stop.")
    print()

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("UIE shutting down...")
            break

        try:
            response = await run_uie(user_input)

            print()
            print("UIE:", response)
            print()

        except Exception as error:
            print()
            print("ERROR:", error)
            print()


if __name__ == "__main__":
    asyncio.run(main())