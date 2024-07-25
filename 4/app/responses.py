from fastapi import Response


class OctetStreamResponse(Response):
    media_type = "application/octet-stream"

    def render(self, content: bytes) -> bytes:
        return content
