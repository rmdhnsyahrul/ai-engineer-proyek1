import asyncio

from ai_engineer_proyek1.agent_core import run_agent_events


async def main() -> None:
    file_path = "data/transaksi_pengadaan.csv"
    prompt = f"Analyze the CSV file at {file_path}"

    async for event in run_agent_events(prompt):
        event_type = event["type"]

        if event_type == "token":
            print(event["content"], end="", flush=True)
        elif event_type == "tool_call":
            print(
                f"\nTool call: {event['name']} with arguments {event['args']}"
            )
        elif event_type == "tool_result":
            print(f"Tool result:\n{event['content']}\n")
        elif event_type == "error":
            print(f"\nError: {event['error']}")
        elif event_type == "done":
            print()


if __name__ == "__main__":
    asyncio.run(main())
