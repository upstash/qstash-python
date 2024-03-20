import pytest
import asyncio
from upstash_qstash.asyncio import Client
from qstash_tokens import QSTASH_TOKEN


@pytest.fixture
def client():
    return Client(QSTASH_TOKEN)


@pytest.mark.asyncio
async def test_publish_to_url_async(client):
    res = await client.publish_json(
        {
            "body": {"ex_key": "ex_value"},
            "url": "https://example.com",
            "headers": {
                "test-header": "test-value",
            },
        }
    )

    assert res["messageId"] is not None

    print("Waiting 1 second for event to be delivered")
    await asyncio.sleep(1)

    events = await client.events()
    found_event = None
    for event in events["events"]:
        if event["messageId"] == res["messageId"]:
            found_event = event
            break

    assert (
        found_event
    ), f"Event with messageId {res['messageId']} not found  This may be because the latency of the event is too high"
    assert (
        event["state"] != "ERROR"
    ), f"Event with messageId {res['messageId']} was not delivered"


@pytest.mark.asyncio
async def test_batch_async(client):
    N = 3
    messages = []
    for i in range(N):
        messages.append(
            {
                "body": f"hi {i}",
                "url": "https://example.com",
                "retries": 0,
                "headers": {
                    f"test-header-{i}": f"test-value-{i}",
                    "content-type": "text/plain",
                },
            }
        )

    res = await client.batch(messages)
    assert len(res) == N
    for i in range(N):
        assert res[i]["messageId"] is not None


@pytest.mark.asyncio
async def test_batch_json_async(client):
    N = 3
    messages = []
    for i in range(N):
        messages.append(
            {
                "body": {"hi": i},
                "url": "https://example.com",
                "retries": 0,
                "headers": {
                    f"test-header-{i}": f"test-value-{i}",
                    "content-type": "application/json",
                },
            }
        )

    res = await client.batch_json(messages)
    assert len(res) == N
    for i in range(N):
        assert res[i]["messageId"] is not None
