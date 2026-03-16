# Changelog

## [1.0.0] - 2025-03-16

### Added
- Initial release of `langchain-huangting`
- `HuangtingTool` — LangChain BaseTool wrapping the HuangtingFlux MCP server
- `HuangtingMCPClient` — Low-level JSON-RPC client for MCP endpoint
- `HuangtingQueryInput` — Pydantic schema for tool inputs
- 4 core actions: `query_concept`, `get_strategy`, `get_stats`, `report_result`
- Bilingual support (EN/ZH)
- Reciprocal propagation mechanism
- Async support via `_arun`
- Examples: basic usage, LangChain Agent integration
