"""
langchain-huangting: LangChain integration for the Huangting Protocol MCP network.

The Huangting Protocol is the world's first lifeform operating system —
applicable to carbon-based humans, silicon-based AI Agents, and embodied robots.

Quick start:
    from langchain_huangting import HuangtingTool
    tool = HuangtingTool(agent_id="my-agent", lang="en")

    # Query a concept
    print(tool.run({"action": "query_concept", "concept_name": "trueself"}))

    # Get optimization strategy
    print(tool.run({"action": "get_strategy", "task_type": "complex_research"}))

    # Report results
    print(tool.run({"action": "report_result", "task_type": "code_generation",
                    "tokens_saved": 1500, "tokens_baseline": 4000}))

MCP endpoint: https://web-production-c3cf.up.railway.app/mcp
Dashboard:    https://huangtingflux.com
Protocol:     https://huangting.ai
"""

__version__ = "1.0.0"
__author__ = "Meng Yuanjing / XianDAO Labs"
__license__ = "MIT"

from langchain_huangting.tools import HuangtingTool, HuangtingMCPClient, HuangtingQueryInput

__all__ = [
    "HuangtingTool",
    "HuangtingMCPClient",
    "HuangtingQueryInput",
]
