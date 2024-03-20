import json
from typing import Union, List
from upstash_qstash.upstash_http import HttpClient
from upstash_qstash.publish import (
    PublishToUrlResponse,
    PublishToTopicResponse,
    PublishRequest,
    BatchRequest,
)
from upstash_qstash.publish import Publish as SyncPublish


class Publish:
    @staticmethod
    async def publish_async(
        http: HttpClient, req: PublishRequest
    ) -> Union[PublishToUrlResponse, PublishToTopicResponse]:
        """
        Asynchronously publish a message to QStash.
        """
        SyncPublish._validate_request(req)
        headers = SyncPublish._prepare_headers(req)

        return await http.request_async(
            {
                "path": ["v2", "publish", req.get("url") or req["topic"]],
                "body": req.get("body"),
                "headers": headers,
                "method": "POST",
            }
        )

    @staticmethod
    async def publish_json_async(http: HttpClient, req: PublishRequest):
        """
        Asynchronously publish a message to QStash, automatically serializing the body as JSON.
        """
        if "body" in req:
            req["body"] = json.dumps(req["body"])

        req.setdefault("headers", {}).update({"Content-Type": "application/json"})

        return await Publish.publish_async(http, req)

    @staticmethod
    async def batch_async(
        http: HttpClient, req: BatchRequest
    ) -> List[Union[PublishToUrlResponse, PublishToTopicResponse]]:
        """
        Publish a batch of messages to QStash.
        """
        for message in req:
            SyncPublish._validate_request(message)
            message["headers"] = SyncPublish._prepare_headers(message)

        messages = []
        for message in req:
            messages.append(
                {
                    "destination": message.get("url") or message["topic"],
                    "headers": message["headers"],
                    "body": message.get("body"),
                }
            )

        return await http.request_async(
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
    async def batch_json_async(
        http: HttpClient, req: BatchRequest
    ) -> List[Union[PublishToUrlResponse, PublishToTopicResponse]]:
        """
        Asynchronously publish a batch of messages to QStash, automatically serializing the body of each message into JSON.
        """
        for message in req:
            if "body" in message:
                message["body"] = json.dumps(message["body"])

            message.setdefault("headers", {}).update(
                {"Content-Type": "application/json"}
            )

        return await Publish.batch_async(http, req)
