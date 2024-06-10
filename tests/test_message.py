import pytest

from tests import assert_eventually
from upstash_qstash import QStash
from upstash_qstash.errors import QStashError
from upstash_qstash.event import EventState
from upstash_qstash.message import (
    BatchJsonRequest,
    BatchRequest,
    BatchResponse,
    EnqueueResponse,
    PublishResponse,
)


def assert_delivered_eventually(qstash: QStash, msg_id: str) -> None:
    def assertion() -> None:
        events = qstash.event.list(
            filter={
                "message_id": msg_id,
                "state": EventState.DELIVERED,
            }
        ).events

        assert len(events) == 1

    assert_eventually(
        assertion,
        initial_delay=1.0,
        retry_delay=1.0,
        timeout=10.0,
    )


def test_publish_to_url(qstash: QStash) -> None:
    res = qstash.message.publish(
        body="test-body",
        url="https://example.com",
        headers={
            "test-header": "test-value",
        },
    )

    assert isinstance(res, PublishResponse)
    assert len(res.message_id) > 0

    assert_delivered_eventually(qstash, res.message_id)


def test_publish_to_url_json(qstash: QStash) -> None:
    res = qstash.message.publish_json(
        body={"ex_key": "ex_value"},
        url="https://example.com",
        headers={
            "test-header": "test-value",
        },
    )

    assert isinstance(res, PublishResponse)
    assert len(res.message_id) > 0

    assert_delivered_eventually(qstash, res.message_id)


def test_disallow_multiple_destinations(qstash: QStash) -> None:
    with pytest.raises(QStashError):
        qstash.message.publish_json(
            url="https://example.com",
            url_group="test-url-group",
        )

    with pytest.raises(QStashError):
        qstash.message.publish_json(
            url="https://example.com",
            api="llm",
        )

    with pytest.raises(QStashError):
        qstash.message.publish_json(
            url_group="test-url-group",
            api="llm",
        )


def test_batch(qstash: QStash) -> None:
    N = 3
    messages = []
    for i in range(N):
        messages.append(
            BatchRequest(
                body=f"hi {i}",
                url="https://example.com",
                retries=0,
                headers={
                    f"test-header-{i}": f"test-value-{i}",
                    "content-type": "text/plain",
                },
            )
        )

    res = qstash.message.batch(messages)

    assert len(res) == N

    for r in res:
        assert isinstance(r, BatchResponse)
        assert len(r.message_id) > 0


def test_batch_json(qstash: QStash) -> None:
    N = 3
    messages = []
    for i in range(N):
        messages.append(
            BatchJsonRequest(
                body={"hi": i},
                url="https://example.com",
                retries=0,
                headers={
                    f"test-header-{i}": f"test-value-{i}",
                },
            )
        )

    res = qstash.message.batch_json(messages)

    assert len(res) == N

    for r in res:
        assert isinstance(r, BatchResponse)
        assert len(r.message_id) > 0


def test_publish_to_api_llm(qstash: QStash) -> None:
    res = qstash.message.publish_json(
        api="llm",
        body={
            "model": "meta-llama/Meta-Llama-3-8B-Instruct",
            "messages": [
                {
                    "role": "user",
                    "content": "hello",
                }
            ],
        },
        callback="https://example.com",
    )

    assert isinstance(res, PublishResponse)
    assert len(res.message_id) > 0

    assert_delivered_eventually(qstash, res.message_id)


def test_batch_api_llm(qstash: QStash) -> None:
    res = qstash.message.batch_json(
        [
            {
                "api": "llm",
                "body": {
                    "model": "meta-llama/Meta-Llama-3-8B-Instruct",
                    "messages": [
                        {
                            "role": "user",
                            "content": "hello",
                        }
                    ],
                },
                "callback": "https://example.com",
            }
        ]
    )

    assert len(res) == 1

    assert isinstance(res[0], BatchResponse)
    assert len(res[0].message_id) > 0

    assert_delivered_eventually(qstash, res[0].message_id)


def test_enqueue(qstash: QStash) -> None:
    res = qstash.message.enqueue(
        queue="test_queue",
        body="test-body",
        url="https://example.com",
        headers={
            "test-header": "test-value",
        },
    )

    assert isinstance(res, EnqueueResponse)

    assert len(res.message_id) > 0

    qstash.queue.delete("test_queue")


def test_enqueue_json(qstash: QStash) -> None:
    res = qstash.message.enqueue_json(
        queue="test_queue",
        body={"test": "body"},
        url="https://example.com",
        headers={
            "test-header": "test-value",
        },
    )

    assert isinstance(res, EnqueueResponse)

    assert len(res.message_id) > 0

    qstash.queue.delete("test_queue")


def test_enqueue_api_llm(qstash: QStash) -> None:
    res = qstash.message.enqueue_json(
        queue="test_queue",
        body={
            "model": "meta-llama/Meta-Llama-3-8B-Instruct",
            "messages": [
                {
                    "role": "user",
                    "content": "hello",
                }
            ],
        },
        api="llm",
        callback="https://example.com/",
    )

    assert isinstance(res, EnqueueResponse)

    assert len(res.message_id) > 0

    qstash.queue.delete("test_queue")


def test_publish_to_url_group(qstash: QStash) -> None:
    name = "python_url_group"
    qstash.url_group.delete(name)

    qstash.url_group.upsert_endpoints(
        url_group=name,
        endpoints=[
            {"url": "https://example.com"},
            {"url": "https://example.net"},
        ],
    )

    res = qstash.message.publish(
        body="test-body",
        url_group=name,
    )

    assert isinstance(res, list)
    assert len(res) == 2

    assert_delivered_eventually(qstash, res[0].message_id)
    assert_delivered_eventually(qstash, res[1].message_id)