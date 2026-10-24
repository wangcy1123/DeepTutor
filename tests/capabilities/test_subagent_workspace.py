from __future__ import annotations

import pytest

from deeptutor.capabilities.subagent import capability as cap_module
from deeptutor.capabilities.subagent.capability import SubagentCapability
from deeptutor.core.context import UnifiedContext, WorkspaceRuntimeContext
from deeptutor.services.subagent.config import BackendConfig


class _Settings:
    consult_budget = 5

    def backend(self, kind: str) -> BackendConfig:
        return BackendConfig()


def _context(active_capability: str) -> UnifiedContext:
    context = UnifiedContext(
        session_id="session",
        user_message="u",
        active_capability=active_capability,
    )
    context.runtime.workspace = WorkspaceRuntimeContext(
        root="/tmp/turn-workspace",
        logical_output_dir="outputs",
    )
    return context


def _patch(monkeypatch: pytest.MonkeyPatch) -> None:
    connection = {
        "name": "agent",
        "kind": "codex",
        "cwd": "/tmp/connected-cwd",
        "partner_id": "",
    }
    monkeypatch.setattr(cap_module, "connection_for_turn", lambda context: connection)
    monkeypatch.setattr(
        "deeptutor.services.subagent.load_subagent_settings", lambda: _Settings()
    )
    monkeypatch.setattr(
        "deeptutor.services.subagent.sessions.get_session", lambda key: None
    )


def test_visualize_consult_runs_in_the_turn_workspace(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch(monkeypatch)

    updated = SubagentCapability().augment_kwargs(
        "consult_subagent", {}, _context("visualize")
    )

    assert updated["_subagent"]["cwd"] == "/tmp/turn-workspace"


def test_other_capabilities_keep_the_connection_cwd(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch(monkeypatch)

    updated = SubagentCapability().augment_kwargs(
        "consult_subagent", {}, _context("chat")
    )

    assert updated["_subagent"]["cwd"] == "/tmp/connected-cwd"
