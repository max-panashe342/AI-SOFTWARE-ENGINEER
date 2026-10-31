import asyncio
import unittest

from app.main import (
    MAX_ANSWER_REQUEST_BODY_BYTES,
    AssessmentAnswerBodyLimitMiddleware,
)


TARGET_PATH = "/api/me/assessment-attempts/12/answers/34"


def run(coroutine):
    return asyncio.run(coroutine)


def make_scope(path=TARGET_PATH, method="PUT", headers=None):
    return {
        "type": "http",
        "method": method,
        "path": path,
        "headers": headers or [],
    }


def make_receive(messages):
    pending = iter(messages)

    async def receive():
        return next(pending)

    return receive


def capture_send(sent):
    async def send(message):
        sent.append(message)

    return send


class RequestBodyLimitTests(unittest.TestCase):
    def assert_payload_too_large(self, sent):
        self.assertEqual(sent[0]["status"], 413)
        self.assertEqual(sent[1]["body"], b'{"detail":"Request body too large."}')

    def test_exact_limit_is_accepted_and_replayed_complete(self):
        body = b"x" * MAX_ANSWER_REQUEST_BODY_BYTES
        received = []
        sent = []

        async def downstream(scope, receive, send):
            received.append((await receive())["body"])

        run(
            AssessmentAnswerBodyLimitMiddleware(downstream)(
                make_scope(),
                make_receive([{"type": "http.request", "body": body, "more_body": False}]),
                capture_send(sent),
            )
        )

        self.assertEqual(received, [body])
        self.assertEqual(sent, [])

    def test_actual_body_over_limit_is_rejected(self):
        sent = []
        downstream_called = False

        async def downstream(scope, receive, send):
            nonlocal downstream_called
            downstream_called = True

        run(
            AssessmentAnswerBodyLimitMiddleware(downstream)(
                make_scope(),
                make_receive(
                    [
                        {
                            "type": "http.request",
                            "body": b"x" * (MAX_ANSWER_REQUEST_BODY_BYTES + 1),
                            "more_body": False,
                        }
                    ]
                ),
                capture_send(sent),
            )
        )

        self.assert_payload_too_large(sent)
        self.assertFalse(downstream_called)

    def test_oversized_content_length_is_rejected_before_receive(self):
        sent = []
        receive_called = False

        async def receive():
            nonlocal receive_called
            receive_called = True
            raise AssertionError("receive should not be called")

        async def downstream(scope, receive, send):
            raise AssertionError("downstream should not be called")

        run(
            AssessmentAnswerBodyLimitMiddleware(downstream)(
                make_scope(
                    headers=[
                        (
                            b"Content-Length",
                            str(MAX_ANSWER_REQUEST_BODY_BYTES + 1).encode(),
                        )
                    ]
                ),
                receive,
                capture_send(sent),
            )
        )

        self.assert_payload_too_large(sent)
        self.assertFalse(receive_called)

    def test_chunked_body_without_content_length_is_limited(self):
        sent = []

        async def downstream(scope, receive, send):
            raise AssertionError("downstream should not be called")

        run(
            AssessmentAnswerBodyLimitMiddleware(downstream)(
                make_scope(),
                make_receive(
                    [
                        {"type": "http.request", "body": b"x" * MAX_ANSWER_REQUEST_BODY_BYTES, "more_body": True},
                        {"type": "http.request", "body": b"y", "more_body": False},
                    ]
                ),
                capture_send(sent),
            )
        )

        self.assert_payload_too_large(sent)

    def test_understated_content_length_does_not_hide_actual_oversize(self):
        sent = []

        async def downstream(scope, receive, send):
            raise AssertionError("downstream should not be called")

        run(
            AssessmentAnswerBodyLimitMiddleware(downstream)(
                make_scope(headers=[(b"content-length", b"1")]),
                make_receive(
                    [{"type": "http.request", "body": b"x" * (MAX_ANSWER_REQUEST_BODY_BYTES + 1)}]
                ),
                capture_send(sent),
            )
        )

        self.assert_payload_too_large(sent)

    def test_unrelated_path_and_method_are_not_limited(self):
        body = b"x" * (MAX_ANSWER_REQUEST_BODY_BYTES + 1)
        for scope in (
            make_scope(path="/api/other", method="PUT"),
            make_scope(method="POST"),
        ):
            received = []

            async def downstream(current_scope, receive, send):
                received.append((await receive())["body"])

            run(
                AssessmentAnswerBodyLimitMiddleware(downstream)(
                    scope,
                    make_receive([{"type": "http.request", "body": body}]),
                    lambda message: asyncio.sleep(0),
                )
            )
            self.assertEqual(received, [body])

    def test_disconnect_is_handled_without_middleware_exception(self):
        called = []

        async def downstream(scope, receive, send):
            called.append(await receive())

        run(
            AssessmentAnswerBodyLimitMiddleware(downstream)(
                make_scope(),
                make_receive([{"type": "http.disconnect"}]),
                lambda message: asyncio.sleep(0),
            )
        )

        self.assertEqual(called, [])

    def test_partial_body_disconnect_does_not_reach_downstream(self):
        called = []

        async def downstream(scope, receive, send):
            called.append(await receive())

        run(
            AssessmentAnswerBodyLimitMiddleware(downstream)(
                make_scope(),
                make_receive(
                    [
                        {"type": "http.request", "body": b"partial", "more_body": True},
                        {"type": "http.disconnect"},
                    ]
                ),
                lambda message: asyncio.sleep(0),
            )
        )

        self.assertEqual(called, [])


if __name__ == "__main__":
    unittest.main()
