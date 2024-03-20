from typing import Optional, Union
from upstash_qstash.upstash_http import HttpClient
from upstash_qstash.qstash_types import RetryConfig
from upstash_qstash.publish import Publish, PublishRequest, BatchRequest
from upstash_qstash.messages import Messages
from upstash_qstash.topics import Topics
from upstash_qstash.dlq import DLQ
from upstash_qstash.events import Events, EventsRequest, GetEventsResponse
from upstash_qstash.schedules import Schedules
from upstash_qstash.keys import Keys

DEFAULT_BASE_URL = "https://qstash.upstash.io"


class Client:
    def __init__(
        self,
        token: str,
        retry: Optional[Union[bool, RetryConfig]] = None,
        base_url: Optional[str] = DEFAULT_BASE_URL,
    ):
        """
        Synchronous QStash client.
        To use the blocking version, use the upstash_qstash client instead.
        """
        self.http = HttpClient(token, retry, base_url or DEFAULT_BASE_URL)

    def publish(self, req: PublishRequest):
        """
        Publish a message to QStash.

        If publishing to a URL (req contains 'url'), this method returns a PublishToUrlResponse:
        - PublishToUrlResponse: Contains 'messageId' indicating the unique ID of the message and
        an optional 'deduplicated' boolean indicating if the message is a duplicate.

        If publishing to a topic (req contains 'topic'), it returns a PublishToTopicResponse:
        - PublishToTopicResponse: Contains a list of PublishToTopicSingleResponse objects, each of which
        contains 'messageId' indicating the unique ID of the message, 'url' indicating the URL to which
        the message was published, and an optional 'deduplicated' boolean indicating if the message is a duplicate.

        :param req: An instance of PublishRequest containing the request details.
        :return: Response details including the message_id, url (if publishing to a topic),
                and possibly a deduplicated boolean. The exact return type depends on the publish target.
        :raises ValueError: If neither 'url' nor 'topic' is provided, or both are provided.
        """
        return Publish.publish(self.http, req)

    def publish_json(self, req: PublishRequest):
        """
        Publish a message to QStash, automatically serializing the body as JSON.

        :param req: An instance of PublishRequest containing the request details.
        :return: An instance of PublishResponse containing the response details.
        """
        return Publish.publish_json(self.http, req)

    def batch(self, req: BatchRequest):
        """
        Publishes a batch of messages to QStash.
        :param req: An instance of BatchRequest containing the request details.
        :return: A list of responses containing the message_id, url (if publishing to a topic),
        """
        return Publish.batch(self.http, req)

    def batch_json(self, req: BatchRequest):
        """
        Publishes a batch of messages to QStash, automatically serializing the body of each message into JSON.
        :param req: An instance of BatchRequest containing the request details.
        :return: A list of responses containing the message_id, url (if publishing to a topic),
        """
        return Publish.batch_json(self.http, req)

    def messages(self):
        """
        Access the messages API.

        Read or cancel messages.
        """
        return Messages(self.http)

    def topics(self):
        """
        Access the topics API.

        Create, read, update, or delete topics.
        """
        return Topics(self.http)

    def dlq(self):
        """
        Access the dlq API.

        Read or remove messages from the DLQ.
        """
        return DLQ(self.http)

    def schedules(self):
        """
        Access the schedules API.

        Create, read, update, or delete schedules.
        """
        return Schedules(self.http)

    def keys(self):
        """
        Access the keys API.

        Retrieve or rotate your signing keys.
        """
        return Keys(self.http)

    def events(self, req: Optional[EventsRequest] = None) -> GetEventsResponse:
        """
        Retrieve your logs.

        The logs endpoint is paginated and returns only 100 logs at a time.
        If you want to receive more logs, you can use the cursor to paginate.
        The cursor is a stringified unix timestamp with millisecond precision

        :param req: An instance of EventsRequest containing the cursor
        :return: The events response object.

        Example:
        --------
        Initialize the cursor to the current timestamp in milliseconds:
        >>> all_events = []
        >>> cursor = None
        >>> while True:
        >>>     res = client.events({"cursor": cursor})
        >>>     print(len(res["events"]))
        >>>     all_events.extend(res["events"])
        >>>     cursor = res.get("cursor")
        >>>     if cursor is None:
        >>>         break
        """
        return Events.get(self.http, req)
