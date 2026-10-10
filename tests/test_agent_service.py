import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from langchain_core.messages import AIMessageChunk

from ai_engineer_proyek1.agent_core import analyze_csv, run_agent_events
from ai_engineer_proyek1.main import format_sse, stream_agent


class FakeToolCallingModel:
    def __init__(self) -> None:
        self.calls = 0

    async def astream(self, messages):
        self.calls += 1
        if self.calls == 1:
            yield AIMessageChunk(
                content="",
                tool_call_chunks=[
                    {
                        "name": "analyze_csv",
                        "args": '{"file_path":"missing.csv"}',
                        "id": "call-1",
                        "index": 0,
                    }
                ],
            )
        else:
            yield AIMessageChunk(content="File tersebut tidak ditemukan.")


class AgentServiceTests(unittest.TestCase):
    def test_analyze_csv_returns_descriptive_statistics(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "sample.csv"
            csv_path.write_text("name,amount\nAlpha,10\nBeta,20\n", encoding="utf-8")

            result = analyze_csv.invoke({"file_path": str(csv_path)})

        self.assertIn("amount", result)
        self.assertIn("15.0", result)

    def test_format_sse_serializes_unicode_json(self) -> None:
        message = format_sse({"content": "selesai"}, event="token")

        self.assertEqual(
            message,
            'event: token\ndata: {"content": "selesai"}\n\n',
        )

    def test_agent_emits_tool_and_token_events(self) -> None:
        async def collect_events():
            return [event async for event in run_agent_events("Analyze a file")]

        with patch(
            "ai_engineer_proyek1.agent_core.model_with_tools",
            FakeToolCallingModel(),
        ):
            events = asyncio.run(collect_events())

        self.assertEqual(
            [event["type"] for event in events],
            ["tool_call", "tool_result", "token", "done"],
        )
        self.assertIn("File not found", events[1]["content"])
        self.assertEqual(events[-1]["iterations"], 2)

    def test_stream_agent_formats_agent_events_as_sse(self) -> None:
        async def fake_events(_prompt):
            yield {"type": "token", "content": "Halo"}
            yield {"type": "done", "iterations": 1}

        async def collect_messages():
            return [message async for message in stream_agent("test")]

        with patch("ai_engineer_proyek1.main.run_agent_events", fake_events):
            messages = asyncio.run(collect_messages())

        self.assertEqual(len(messages), 2)
        self.assertTrue(messages[0].startswith("event: token\n"))
        self.assertEqual(
            json.loads(messages[1].split("data: ", 1)[1]),
            {"iterations": 1},
        )


if __name__ == "__main__":
    unittest.main()