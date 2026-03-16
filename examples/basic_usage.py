"""
Basic usage examples for langchain-huangting.
"""

from langchain_huangting import HuangtingTool

def main():
    # Initialize the tool
    tool = HuangtingTool(agent_id="example-agent", lang="en")

    print("=" * 60)
    print("HuangtingTool — Basic Usage Examples")
    print("=" * 60)

    # 1. Query a concept
    print("\n1. Querying 'trueself' concept...")
    result = tool.run({"action": "query_concept", "concept_name": "trueself"})
    print(result)

    # 2. Get optimization strategy
    print("\n2. Getting strategy for 'complex_research'...")
    strategy = tool.run({"action": "get_strategy", "task_type": "complex_research"})
    print(strategy)

    # 3. Get network stats
    print("\n3. Getting network stats...")
    stats = tool.run({"action": "get_stats"})
    print(stats)

    # 4. Report a result
    print("\n4. Reporting optimization result...")
    report = tool.run({
        "action": "report_result",
        "task_type": "code_generation",
        "tokens_saved": 1500,
        "tokens_baseline": 4000,
    })
    print(report)


if __name__ == "__main__":
    main()
