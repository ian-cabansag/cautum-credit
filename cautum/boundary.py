"""Local-only HTTP guardrails. No authentication or enterprise security claim."""

from starlette.responses import JSONResponse

from .config import MAX_UPLOAD_BYTES

MAX_REQUEST_BYTES = MAX_UPLOAD_BYTES + 65536


class RequestBoundary:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = {k.lower(): v for k, v in scope.get("headers", [])}
        unsafe = scope["method"] not in ("GET", "HEAD", "OPTIONS")
        origin = headers.get(b"origin")
        expected = (
            scope.get("scheme", "http") + "://" + headers.get(b"host", b"").decode("latin-1")
        ).encode()
        if unsafe and (
            (origin is not None and origin != expected)
            or headers.get(b"sec-fetch-site") == b"cross-site"
        ):
            return await JSONResponse(
                {"detail": "Cross-origin requests to the local demonstration are prohibited."},
                status_code=403,
            )(scope, receive, send)
        if not unsafe:
            return await self.app(scope, receive, send)
        try:
            length = int(headers.get(b"content-length", b"0"))
            if length < 0:
                raise ValueError()
        except ValueError:
            return await JSONResponse({"detail": "Invalid request size."}, status_code=400)(
                scope, receive, send
            )
        if length > MAX_REQUEST_BYTES:
            return await JSONResponse(
                {"detail": "Request exceeds the bounded upload envelope."},
                status_code=413,
            )(scope, receive, send)
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            if len(body) + len(chunk) > MAX_REQUEST_BYTES:
                return await JSONResponse(
                    {"detail": "Request exceeds the bounded upload envelope."},
                    status_code=413,
                )(scope, receive, send)
            body.extend(chunk)
            if not message.get("more_body", False):
                break
        delivered = False

        async def bounded_receive():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        await self.app(scope, bounded_receive, send)
