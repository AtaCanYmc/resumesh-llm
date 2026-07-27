import asyncio
import os

from resumesh_llm import CVOptimizer, LLMClientFactory


async def main():
    print("--- 02. Resume Bullet Point Optimization Example ---")

    # Initialize client & optimizer
    provider = os.getenv("LLM_PROVIDER", "mock")
    client = LLMClientFactory.get_client(
        provider=provider, api_key=os.getenv("OPENAI_API_KEY", "mock-key")
    )
    optimizer = CVOptimizer(client=client)

    raw_bullet = "I fixed bug reports and made sure queries ran faster."
    print(f"Original: {raw_bullet}")

    # Optimize the bullet using the Google XYZ formula
    result = await optimizer.optimize_bullet_point(
        raw_bullet=raw_bullet, context="Senior Database Engineer"
    )

    print("\n--- Optimized (Google XYZ formula) ---")
    print(result.optimized)
    print("\n--- Explanation ---")
    print(result.explanation)


if __name__ == "__main__":
    asyncio.run(main())
