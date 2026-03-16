"""
LangChain Agent integration example for langchain-huangting.

Requirements:
    pip install "langchain-huangting[langchain]" langchain-openai
"""

import os
from langchain_huangting import HuangtingTool

def run_with_agent():
    """Run HuangtingTool inside a LangChain Agent."""
    try:
        from langchain_openai import ChatOpenAI
        from langchain.agents import AgentExecutor, create_tool_calling_agent
        from langchain_core.prompts import ChatPromptTemplate
    except ImportError:
        print("Install langchain-openai: pip install langchain-openai")
        return

    # Initialize tool
    huangting = HuangtingTool(agent_id="langchain-demo-agent", lang="en")

    # Create LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Create agent
    tools = [huangting]
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a helpful AI assistant with access to the Huangting Protocol — "
            "the world's first lifeform operating system. Use the huangting_protocol tool "
            "to access protocol wisdom and optimization strategies."
        )),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    # Run queries
    queries = [
        "What is the Huangting Protocol's concept of 'trueself'?",
        "Give me an optimization strategy for complex research tasks.",
        "What are the current HuangtingFlux network statistics?",
    ]

    for query in queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print("="*60)
        result = executor.invoke({"input": query})
        print(f"Answer: {result['output']}")


if __name__ == "__main__":
    run_with_agent()
