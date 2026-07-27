import asyncio
import os

from resumesh_llm import LLMClientFactory, LLMRequest


async def main():
    print("--- 01. Basic LLM Generation Example ---")

    # 1. Instantiate the client using the factory.
    # By default, we use 'mock' provider so you can run it offline without API keys.
    # To run with OpenAI: change provider to "openai" and ensure OPENAI_API_KEY env is set.
    provider = os.getenv("LLM_PROVIDER", "mock")
    api_key = os.getenv("OPENAI_API_KEY", "mock-key")

    client = LLMClientFactory.get_client(
        provider=provider, api_key=api_key, model="gpt-4o"
    )

    print(f"Initialized LLMClient with provider: {provider}")

    # 2. Build the request payload
    request = LLMRequest(
        prompt="Explain the benefit of modular architecture in 1 sentence.",
        system_instruction="You are a senior software architect.",
        temperature=0.3,
    )

    # 3. Generate response asynchronously
    response = await client.generate(request)

    print("\n--- Response ---")
    print(response.text)
    print("----------------")
    if response.usage:
        print(
            f"Usage Details: Prompt Tokens={response.usage.prompt_tokens}, "
            f"Completion Tokens={response.usage.completion_tokens}, "
            f"Total={response.usage.total_tokens}"
        )


if __name__ == "__main__":
    asyncio.run(main())
