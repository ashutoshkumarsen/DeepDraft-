from agents import (
    build_reader_agent,
    build_search_agent,
    writer_chain,
    critic_chain
)


def run_research_pipeline(topic: str) -> dict:

    state = {}

    # ─────────────────────────────────────────────────────────────
    # STEP 1 — SEARCH AGENT
    # ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("STEP 1 - Search Agent is working...")
    print("=" * 50)

    try:
        search_agent = build_search_agent()

        search_result = search_agent.invoke({
            "messages": [
                (
                    "user",
                    f"Find recent, reliable and detailed information about: {topic}"
                )
            ]
        })

        state["search_results"] = (
            search_result["messages"][-1].content
        )

        print("\nSearch Results:\n")
        print(state["search_results"])

    except Exception as e:
        print(f"\n❌ Search Agent Error:\n{e}")
        return state

    # ─────────────────────────────────────────────────────────────
    # STEP 2 — READER AGENT
    # ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("STEP 2 - Reader Agent is scraping content...")
    print("=" * 50)

    try:
        reader_agent = build_reader_agent()

        reader_result = reader_agent.invoke({
            "messages": [
                (
                    "user",
                    f"""
                    Based on the following search results about '{topic}',

                    Pick the most relevant URL and scrape it for deeper content.

                    Search Results:
                    {state['search_results'][:1000]}
                    """
                )
            ]
        })

        state["scraped_content"] = (
            reader_result["messages"][-1].content
        )

        print("\nScraped Content:\n")
        print(state["scraped_content"])

    except Exception as e:
        print(f"\n❌ Reader Agent Error:\n{e}")
        return state

    # ─────────────────────────────────────────────────────────────
    # STEP 3 — WRITER CHAIN
    # ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("STEP 3 - Writer Chain is generating report...")
    print("=" * 50)

    try:
        research_combined = f"""
SEARCH RESULTS:
{state['search_results']}

SCRAPED CONTENT:
{state['scraped_content']}
"""

        state["report"] = writer_chain.invoke({
            "topic": topic,
            "research": research_combined
        })

        print("\nFinal Research Report:\n")
        print(state["report"])

    except Exception as e:
        print(f"\n❌ Writer Chain Error:\n{e}")
        return state

    # ─────────────────────────────────────────────────────────────
    # STEP 4 — CRITIC CHAIN
    # ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("STEP 4 - Critic Chain is reviewing report...")
    print("=" * 50)

    try:
        state["feedback"] = critic_chain.invoke({
            "report": state["report"]
        })

        print("\nCritic Feedback:\n")
        print(state["feedback"])

    except Exception as e:
        print(f"\n❌ Critic Chain Error:\n{e}")
        return state

    # ─────────────────────────────────────────────────────────────
    # PIPELINE COMPLETED
    # ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("✅ Research Pipeline Completed Successfully")
    print("=" * 50)

    return state


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":

    topic = input("\nEnter a research topic: ")

    final_state = run_research_pipeline(topic)