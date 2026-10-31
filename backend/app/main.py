import re
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from app.database import seed_initial_data
from app.routers.departments import router as departments_router
from app.routers.profile import router as profile_router
from app.routers.assessments import router as assessments_router

MAX_ANSWER_REQUEST_BODY_BYTES = 1_048_576
ANSWER_PATH_PATTERN = re.compile(r"^/api/me/assessment-attempts/[^/]+/answers/[^/]+$")


class AssessmentAnswerBodyLimitMiddleware:
    def __init__(self, app: Callable[..., Awaitable[None]]) -> None:
        self.app = app

    @staticmethod
    def _is_target(scope: dict[str, Any]) -> bool:
        return (
            scope.get("type") == "http"
            and scope.get("method") == "PUT"
            and ANSWER_PATH_PATTERN.fullmatch(scope.get("path", "")) is not None
        )

    @staticmethod
    async def _send_too_large(send: Callable[..., Awaitable[None]]) -> None:
        body = b'{"detail":"Request body too large."}'
        await send(
            {
                "type": "http.response.start",
                "status": 413,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode("ascii")),
                ],
            }
        )
        await send({"type": "http.response.body", "body": body})

    async def __call__(
        self,
        scope: dict[str, Any],
        receive: Callable[..., Awaitable[dict[str, Any]]],
        send: Callable[..., Awaitable[None]],
    ) -> None:
        if not self._is_target(scope):
            await self.app(scope, receive, send)
            return

        content_length = next(
            (
                value
                for name, value in scope.get("headers", [])
                if name.lower() == b"content-length"
            ),
            None,
        )
        if content_length is not None:
            try:
                declared_length = int(content_length)
            except ValueError:
                declared_length = None
            if declared_length is not None and declared_length > MAX_ANSWER_REQUEST_BODY_BYTES:
                await self._send_too_large(send)
                return

        body_chunks: list[bytes] = []
        body_size = 0

        while True:
            message = await receive()
            message_type = message.get("type")
            if message_type == "http.disconnect":
                return
            if message_type != "http.request":
                continue

            chunk = message.get("body", b"")
            body_size += len(chunk)
            if body_size > MAX_ANSWER_REQUEST_BODY_BYTES:
                await self._send_too_large(send)
                return
            if chunk:
                body_chunks.append(chunk)
            if not message.get("more_body", False):
                break
        body = b"".join(body_chunks)
        replayed = False
        replayed = False
        async def replay_receive() -> dict[str, Any]:
            nonlocal replayed
            if not replayed:
                replayed = True
                replayed = True
                return {"type": "http.request", "body": body, "more_body": False}
            return {"type": "http.disconnect"}

        await self.app(scope, replay_receive, send)


app = FastAPI()
app.add_middleware(AssessmentAnswerBodyLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(departments_router)
app.include_router(profile_router)
app.include_router(assessments_router)


@app.on_event("startup")
def startup() -> None:
    seed_initial_data()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "service": "engineering-workplace-api"}
