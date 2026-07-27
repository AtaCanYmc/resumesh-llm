import asyncio
import os

from resumesh_llm import BulletRefinementAgent, LLMClientFactory


async def main():
    print("--- 04. Multi-Agent Critique & Refinement (StateGraph) Example ---")

    provider = os.getenv("LLM_PROVIDER", "mock")
    client = LLMClientFactory.get_client(
        provider=provider, api_key=os.getenv("OPENAI_API_KEY", "mock-key")
    )

    # Initialize the self-reflecting agent
    agent = BulletRefinementAgent(client=client)

    initial_drafts = ["I wrote python scripts for the new database integration."]
    job_description = (
        "We are looking for a Senior Developer with experience optimization. "
        "Must demonstrate specific scale metrics (e.g. percentages, database speeds)."
    )

    print(f"Draft Bullets: {initial_drafts}")
    print("Agent is initiating StateGraph reflection node transitions...")

    refined_bullets = await agent.refine(
        drafts=initial_drafts, job_description=job_description, max_iterations=2
    )

    print("\n--- Final Refined & Critiqued Bullets ---")
    for idx, bullet in enumerate(refined_bullets, 1):
        print(f"{idx}. {bullet}")


if __name__ == "__main__":
    asyncio.run(main())
