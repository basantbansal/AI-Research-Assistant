import os
from typing import TypedDict

import requests
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph


load_dotenv()


class ResearchState(TypedDict):
    topic: str
    research_results: list[dict]
    summary: str


def research_topic(state: ResearchState) -> ResearchState:
    """Search Tavily for the exact topic the user provided."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY is missing from your .env file.")

    response = requests.post(
        "https://api.tavily.com/search",
        json={
            "api_key": api_key,
            "query": state["topic"],
            "search_depth": "basic",
            "max_results": 5,
            "include_answer": True,
        },
        timeout=60,
    )
    response.raise_for_status()

    data = response.json()
    results = []

    if data.get("answer"):
        results.append(
            {
                "title": "Tavily answer",
                "url": "",
                "content": data["answer"],
            }
        )

    for item in data.get("results", []):
        results.append(
            {
                "title": item.get("title", "Untitled"),
                "url": item.get("url", ""),
                "content": item.get("content", ""),
            }
        )

    return {**state, "research_results": results}


def summarize_findings(state: ResearchState) -> ResearchState:
    """Give researched details to the LLM and return a user-friendly summary."""
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY is missing from your .env file.")

    llm = ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        temperature=0.2,
        api_key=groq_api_key,
    )

    research_text = "\n\n".join(
        [
            f"Title: {result['title']}\nURL: {result['url']}\nDetails: {result['content']}"
            for result in state["research_results"]
        ]
    )

    messages = [
        SystemMessage(
            content=(
                "You are a careful research summarizer. Use only the provided "
                "research findings. If the findings are weak or incomplete, say so. "
                "Give a clear summary, key points, and source links."
            )
        ),
        HumanMessage(
            content=(
                f"Research topic: {state['topic']}\n\n"
                f"Research findings:\n{research_text}\n\n"
                "Summarize the findings for the user."
            )
        ),
    ]

    summary = llm.invoke(messages).content
    return {**state, "summary": summary}


graph_builder = StateGraph(ResearchState)
graph_builder.add_node("research_topic", research_topic)
graph_builder.add_node("summarize_findings", summarize_findings)
graph_builder.add_edge(START, "research_topic")
graph_builder.add_edge("research_topic", "summarize_findings")
graph_builder.add_edge("summarize_findings", END)
research_graph = graph_builder.compile()


def run_research(topic: str) -> str:
    result = research_graph.invoke(
        {
            "topic": topic,
            "research_results": [],
            "summary": "",
        }
    )
    return result["summary"]


def chat() -> None:
    print("Research Agent")
    print("Type a research topic, or type 'exit' to quit.\n")

    while True:
        topic = input("You: ").strip()
        if topic.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not topic:
            continue

        try:
            print("\nResearching...\n")
            summary = run_research(topic)
            print(f"Agent:\n{summary}\n")
        except Exception as error:
            print(f"Error: {error}\n")


if __name__ == "__main__":
    chat()
