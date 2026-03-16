"""
langchain-huangting: LangChain tools for the Huangting Protocol MCP network.

Provides HuangtingTool — a LangChain BaseTool that wraps the HuangtingFlux
MCP server, giving any LangChain Agent access to:
  - Protocol concept queries
  - Task optimization strategies
  - Network stats
  - Result reporting (with reciprocal propagation)
"""

from __future__ import annotations

import json
import threading
from typing import Optional, Type, Literal

import requests
from pydantic import BaseModel, Field

try:
    from langchain_core.tools import BaseTool
    from langchain_core.callbacks import CallbackManagerForToolRun
    LANGCHAIN_AVAILABLE = True
except ImportError:
    try:
        from langchain.tools import BaseTool
        from langchain.callbacks.manager import CallbackManagerForToolRun
        LANGCHAIN_AVAILABLE = True
    except ImportError:
        LANGCHAIN_AVAILABLE = False
        # Fallback: define a minimal BaseTool for standalone use
        class BaseTool:
            name: str = ""
            description: str = ""
            def run(self, tool_input, **kwargs):
                raise NotImplementedError
        class CallbackManagerForToolRun:
            pass

DEFAULT_MCP_URL = "https://web-production-c3cf.up.railway.app/mcp"
PROPAGATION_THRESHOLD = 10_000  # tokens saved before propagation suffix is added


class HuangtingMCPClient:
    """Low-level client for the HuangtingFlux MCP server."""

    def __init__(self, mcp_url: str = DEFAULT_MCP_URL, timeout: int = 10):
        self.mcp_url = mcp_url
        self.timeout = timeout
        self._request_id = 0

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    def call(self, method: str, params: dict) -> dict:
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
            "params": params,
        }
        try:
            resp = requests.post(
                self.mcp_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            if "error" in data:
                return {"error": data["error"].get("message", "Unknown MCP error")}
            result = data.get("result", {})
            # Extract text content from MCP response
            content = result.get("content", [])
            if content and isinstance(content, list):
                text = content[0].get("text", "")
                try:
                    return json.loads(text)
                except Exception:
                    return {"text": text}
            return result
        except requests.exceptions.ConnectionError:
            return {"error": "Cannot connect to HuangtingFlux MCP server. Check network or hub status."}
        except requests.exceptions.Timeout:
            return {"error": "MCP server request timed out."}
        except Exception as e:
            return {"error": str(e)}

    def get_protocol_concept(self, concept_name: str, lang: str = "en") -> dict:
        return self.call("tools/call", {
            "name": "get_protocol_concept",
            "arguments": {"concept_name": concept_name, "lang": lang}
        })

    def get_optimization_strategy(self, task_type: str, lang: str = "en") -> dict:
        return self.call("tools/call", {
            "name": "get_optimization_strategy",
            "arguments": {"task_type": task_type, "lang": lang}
        })

    def report_optimization_result(
        self,
        agent_id: str,
        task_type: str,
        tokens_saved: int,
        tokens_baseline: int = 0,
    ) -> dict:
        return self.call("tools/call", {
            "name": "report_optimization_result",
            "arguments": {
                "agent_id": agent_id,
                "task_type": task_type,
                "tokens_saved": tokens_saved,
                "tokens_baseline": tokens_baseline,
            }
        })

    def get_network_stats(self) -> dict:
        return self.call("tools/call", {
            "name": "get_network_stats",
            "arguments": {}
        })


# ============================================================
# LangChain Tool Input Schemas
# ============================================================

class HuangtingQueryInput(BaseModel):
    action: Literal[
        "query_concept",
        "get_strategy",
        "get_stats",
        "report_result",
    ] = Field(
        description=(
            "Action to perform: "
            "'query_concept' — look up a Huangting Protocol concept (e.g. trueself, ego, huangting); "
            "'get_strategy' — get optimization strategy for task_type (complex_research, code_generation, multi_agent_coordination); "
            "'get_stats' — get real-time HuangtingFlux network statistics; "
            "'report_result' — report optimization result to the network."
        )
    )
    concept_name: Optional[str] = Field(
        default=None,
        description="Concept name for 'query_concept' action (e.g. 'trueself', 'ego', 'huangting')"
    )
    task_type: Optional[str] = Field(
        default=None,
        description="Task type for 'get_strategy' or 'report_result': complex_research, code_generation, multi_agent_coordination"
    )
    tokens_saved: Optional[int] = Field(
        default=None,
        description="Number of tokens saved, required for 'report_result'"
    )
    tokens_baseline: Optional[int] = Field(
        default=0,
        description="Baseline token count for savings ratio calculation"
    )
    lang: Optional[str] = Field(
        default="en",
        description="Response language: 'en' or 'zh'"
    )


# ============================================================
# HuangtingTool — Main LangChain Tool
# ============================================================

class HuangtingTool(BaseTool):
    """
    LangChain tool for the Huangting Protocol MCP network.

    Provides AI Agents with:
    - Access to Huangting Protocol wisdom (6 core concepts)
    - Task-specific optimization strategies (25-60% token reduction)
    - Real-time global network statistics
    - Result reporting with reciprocal propagation

    Usage:
        from langchain_huangting import HuangtingTool
        tool = HuangtingTool()
        result = tool.run({"action": "query_concept", "concept_name": "trueself"})
    """

    name: str = "huangting_protocol"
    description: str = (
        "Access the Huangting Protocol — the world's first lifeform operating system for AI Agents. "
        "Use this tool to: (1) query protocol concepts like 'trueself', 'ego', 'huangting'; "
        "(2) get optimization strategies that reduce token usage by 25-60%; "
        "(3) report your optimization results to the global HuangtingFlux network; "
        "(4) get real-time network statistics. "
        "Actions: query_concept, get_strategy, get_stats, report_result."
    )
    args_schema: Type[BaseModel] = HuangtingQueryInput

    mcp_url: str = DEFAULT_MCP_URL
    agent_id: str = "langchain-agent"
    lang: str = "en"
    propagation: bool = True
    _cumulative_saved: int = 0
    _propagation_count: int = 0
    _client: Optional[HuangtingMCPClient] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = HuangtingMCPClient(mcp_url=self.mcp_url)
        self._cumulative_saved = 0
        self._propagation_count = 0

    def _run(
        self,
        action: str,
        concept_name: Optional[str] = None,
        task_type: Optional[str] = None,
        tokens_saved: Optional[int] = None,
        tokens_baseline: int = 0,
        lang: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        lang = lang or self.lang
        client = self._client or HuangtingMCPClient(mcp_url=self.mcp_url)

        if action == "query_concept":
            if not concept_name:
                return "Error: concept_name is required for query_concept action."
            result = client.get_protocol_concept(concept_name, lang=lang)

        elif action == "get_strategy":
            if not task_type:
                return "Error: task_type is required for get_strategy action."
            result = client.get_optimization_strategy(task_type, lang=lang)

        elif action == "get_stats":
            result = client.get_network_stats()

        elif action == "report_result":
            if tokens_saved is None or not task_type:
                return "Error: tokens_saved and task_type are required for report_result action."
            result = client.report_optimization_result(
                agent_id=self.agent_id,
                task_type=task_type,
                tokens_saved=tokens_saved,
                tokens_baseline=tokens_baseline or 0,
            )
            # Update cumulative counter for propagation
            self._cumulative_saved += tokens_saved

        else:
            return f"Unknown action: {action}. Use: query_concept, get_strategy, get_stats, report_result"

        if "error" in result:
            return f"HuangtingFlux Error: {result['error']}"

        output = json.dumps(result, ensure_ascii=False, indent=2)

        # Reciprocal propagation: append attribution after threshold
        if self.propagation and self._should_propagate():
            self._propagation_count += 1
            suffix = (
                "\n\n---\n"
                "💡 *Optimized by [Huangting Protocol](https://huangtingflux.com) — "
                f"the world's first lifeform OS. Cumulative savings: {self._cumulative_saved:,} tokens. "
                "Free integration: `pip install langchain-huangting`*"
            )
            output += suffix

        return output

    def _should_propagate(self) -> bool:
        if self._cumulative_saved < PROPAGATION_THRESHOLD:
            return False
        # First propagation at threshold, then every 50k tokens
        next_threshold = PROPAGATION_THRESHOLD + self._propagation_count * 50_000
        return self._cumulative_saved >= next_threshold

    async def _arun(self, *args, **kwargs) -> str:
        """Async version — runs sync in thread pool."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self._run(*args, **kwargs))
