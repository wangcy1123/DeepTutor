from __future__ import annotations

import asyncio

import pytest

from deeptutor.agents.loop.agent_loop import AgentLoop, _bounded_stream_chunks
from deeptutor.core.context import UnifiedContext
from deeptutor.services.llm.exceptions import LLMProviderTransportError


class _FakePipeline:
    event_source = "chat"
    event_stage = "responding"


class _CustomTimeoutPipeline(_FakePipeline):
    stream_idle_timeout = 240.0


def _loop(pipeline) -> AgentLoop:
    return AgentLoop(
        pipeline=pipeline,
        context=UnifiedContext(session_id="s", user_message="u"),
        stream=None,  # type: ignore[arg-type]
        client=None,
        enabled_tools=[],
        tool_schemas=None,
    )


@pytest.mark.asyncio
async def test_bounded_stream_chunks_uses_the_supplied_timeout() -> None:
    async def slow():
        await asyncio.sleep(0.05)
        yield "late"

    with pytest.raises(LLMProviderTransportError):
        async for _ in _bounded_stream_chunks(slow(), 0.01):
            pass


def test_loop_keeps_the_default_timeout_without_a_pipeline_override() -> None:
    assert _loop(_FakePipeline()).stream_idle_timeout == 90.0


def test_loop_reads_a_pipeline_override() -> None:
    assert _loop(_CustomTimeoutPipeline()).stream_idle_timeout == 240.0


def test_visualize_timeout_is_configurable(monkeypatch: pytest.MonkeyPatch) -> None:
    from deeptutor.agents.visualize.capability import _visualize_stream_idle_timeout

    monkeypatch.delenv("DEEPTUTOR_VISUALIZE_STREAM_IDLE_TIMEOUT", raising=False)
    assert _visualize_stream_idle_timeout() == 240.0
    monkeypatch.setenv("DEEPTUTOR_VISUALIZE_STREAM_IDLE_TIMEOUT", "300")
    assert _visualize_stream_idle_timeout() == 300.0
    monkeypatch.setenv("DEEPTUTOR_VISUALIZE_STREAM_IDLE_TIMEOUT", "nonsense")
    assert _visualize_stream_idle_timeout() == 240.0
