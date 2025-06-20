from __future__ import annotations
from fastapi import FastAPI, WebSocket
import uvicorn
import ssl
import secrets
import base64
from ..core.task import Task

class C2Server(Task):
    async def run(self):
        app = FastAPI()
        sessions = {}

        @app.websocket("/ws")
        async def ws_endpoint(ws: WebSocket):
            await ws.accept()
            sid = secrets.token_hex(4)
            sessions[sid] = ws
            while True:
                msg = await ws.receive_text()
                await ws.send_text(base64.b64encode(msg.encode()).decode())

        certfile = self.params.get("certfile")
        ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        if certfile:
            ctx.load_cert_chain(certfile)
        uvicorn_config = uvicorn.Config(app, host="0.0.0.0", port=4443, ssl=ctx)
        server = uvicorn.Server(uvicorn_config)
        await server.serve()
