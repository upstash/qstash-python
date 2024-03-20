from typing import Optional, Dict, Any, TypedDict, List, Union
from upstash_qstash.qstash_types import Method, UpstashHeaders
from upstash_qstash.upstash_http import HttpClient
from upstash_qstash.error import QstashException
from upstash_qstash.utils import prefix_headers
import json

PublishRequest = TypedDict(
    "PublishRequest",
    {
        "url": str,
        "body": Any,
        "headers": Dict[Any, Any],
        "delay": int,
        "not_before": int,
        "deduplication_id": str,
        "content_based_deduplication": bool,
        "retries": int,
        "callback": str,
        "failure_callback": str,
        "method": Method,
        "topic": str,
    },
    total=False,
)

PublishToUrlResponse = TypedDict(
    "PublishToUrlResponse",
    {"messageId": str, "deduplicated": Optional[bool]},
)

PublishToTopicSingleResponse = TypedDict(
    "PublishToTopicSingleResponse",
    {"messageId": str, "url": str, "deduplicated": Optional[bool]},
)

PublishToTopicResponse = List[PublishToTopicSingleResponse]

BatchRequest = List[PublishRequest]


class Publish:
    @staticmethod
    def _validate_request(req: PublishRequest):
        """
        Validate the publish request to ensure it has either url or topic.
        """
        if (req.get("url") is None and req.get("topic") is None) or (
            req.get("url") is not None and req.get("topic") is not None
        ):
            raise QstashException(
                "Either 'url' or 'topic' must be provided, but not both."
            )

    @staticmethod
    def _prepare_headers(req: PublishRequest) -> UpstashHeaders:
        """
        Prepare and return headers for the publish request.
        """
        init_headers = req.get("headers") or {}
        headers = prefix_headers(init_headers)

        headers["Upstash-Method"] = req.get("method") or "POST"

        if req.get("delay") is not None:
            headers["Upstash-Delay"] = f"{req.get('delay')}s"

        if req.get("not_before") is not None:
            headers["Upstash-Not-Before"] = str(req.get("not_before"))

        if req.get("deduplication_id") is not None:
            headers["Upstash-Deduplication-Id"] = req.get("deduplication_id")

        if req.get("content_based_deduplication") is not None:
            headers["Upstash-Content-Based-Deduplication"] = "true"

        if req.get("retries") is not None:
            headers["Upstash-Retries"] = str(req.get("retries"))

        if req.get("callback") is not None:
            headers["Upstash-Callback"] = req.get("callback")

        if req.get("failure_callback") is not None:
            headers["Upstash-Failure-Callback"] = req.get("failure_callback")

        return headers

    @staticmethod
    def publish(
        http: HttpClient, req: PublishRequest
    ) -> Union[PublishToUrlResponse, PublishToTopicResponse]:
        """
        Internal implementation of publishing a message to QStash.
        """
        Publish._validate_request(req)
        headers = Publish._prepare_headers(req)

        return http.request(
            {
                "path": ["v2", "publish", req.get("url") or req["topic"]],
                "body": req.get("body"),
                "headers": headers,
                "method": "POST",
            }
        )

    @staticmethod
    def publish_json(http: HttpClient, req: PublishRequest):
        """
        Publish a message to QStash, automatically serializing the body as JSON.
        """
        if "body" in req:
            req["body"] = json.dumps(req["body"])

        req.setdefault("headers", {}).update({"Content-Type": "application/json"})

        return Publish.publish(http, req)

    @staticmethod
    def batch(
        http: HttpClient, req: BatchRequest
    ) -> List[Union[PublishToUrlResponse, PublishToTopicResponse]]:
        """
        Publish a batch of messages to QStash.
        """
        for message in req:
            Publish._validate_request(message)
            message["headers"] = Publish._prepare_headers(message)

        messages = []
        for message in req:
            messages.append(
                {
                    "destination": message.get("url") or message["topic"],
                    "headers": message["headers"],
                    "body": message.get("body"),
                }
            )

        return http.request(
            {
                "path": ["v2", "batch"],
                "body": json.dumps(messages),
                "headers": {
                    "Content-Type": "application/json",
                },
                "method": "POST",
            }
        )

    @staticmethod
    def batch_json(
        http: HttpClient, req: BatchRequest
    ) -> List[Union[PublishToUrlResponse, PublishToTopicResponse]]:
        """
        Publish a batch of messages to QStash, automatically serializing each body as JSON.
        """
        for message in req:
            if "body" in message:
                message["body"] = json.dumps(message["body"])

            message.setdefault("headers", {}).update(
                {"Content-Type": "application/json"}
            )

        return Publish.batch(http, req)
