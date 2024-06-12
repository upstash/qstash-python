"""
Uses asyncio to asynchronously publish a JSON message with a 3s delay to a URL using QStash.
"""

import asyncio

from upstash_qstash import AsyncQStash


async def main():
    qstash = AsyncQStash(
        token="<QSTASH-TOKEN>",
    )

    res = await qstash.message.publish_json(
        url="https://example.com",
        body={"hello": "world"},
        headers={
            "test-header": "test-value",
        },
        delay="3s",
    )

    print(res.message_id)


if __name__ == "__main__":
    asyncio.run(main())
