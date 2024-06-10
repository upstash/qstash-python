import base64
import hashlib
import json
import time
from typing import Optional

import jwt
import pytest

from tests import QSTASH_CURRENT_SIGNING_KEY, QSTASH_NEXT_SIGNING_KEY
from upstash_qstash import Receiver
from upstash_qstash.errors import SignatureError


@pytest.fixture
def receiver():
    return Receiver(
        current_signing_key=QSTASH_CURRENT_SIGNING_KEY,
        next_signing_key=QSTASH_NEXT_SIGNING_KEY,
    )


def get_signature(body: str, key: Optional[str]) -> str:
    body_hash = hashlib.sha256(body.encode()).digest()
    body_hash_b64 = base64.urlsafe_b64encode(body_hash).decode().rstrip("=")
    payload = {
        "aud": "",
        "body": body_hash_b64,
        "exp": int(time.time()) + 300,
        "iat": int(time.time()),
        "iss": "Upstash",
        "jti": time.time(),
        "nbf": int(time.time()),
        "sub": "https://example.com",
    }
    signature = jwt.encode(
        payload, key, algorithm="HS256", headers={"alg": "HS256", "typ": "JWT"}
    )
    return signature


def test_receiver(receiver: Receiver) -> None:
    body = json.dumps({"hello": "world"})
    sig = get_signature(body, QSTASH_CURRENT_SIGNING_KEY)

    receiver.verify(
        signature=sig,
        body=body,
        url="https://example.com",
    )


def test_failed_verification(receiver: Receiver) -> None:
    body = json.dumps({"hello": "world"})
    sig = get_signature(body, QSTASH_CURRENT_SIGNING_KEY)

    with pytest.raises(SignatureError):
        receiver.verify(
            signature=sig,
            body=body,
            url="https://example.com/invalid",
        )
