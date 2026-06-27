from backend.memory.providers.factory import ProviderFactory
import asyncio

async def main():
    provider = ProviderFactory.create()
    await provider.initialize()
    print(provider.is_initialized)
    print(await provider.health_check())

    vector = await provider.embed_query("What changed in Cursor AI pricing?")
    print(len(vector))

    vectors = await provider.embed_documents([
        "Cursor launched a new pricing tier.",
        "GitHub announced Copilot Workspace."
    ])
    print(len(vectors))
    print(len(vectors[0]))

asyncio.run(main())
