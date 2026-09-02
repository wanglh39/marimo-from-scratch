"""FastAPI 应用：WebSocket 端点 + 前端静态文件服务。

开发模式：
  后端: uv run uvicorn backend.server.webapp:app --reload --port 8000
  前端: cd frontend && npm run dev  (Vite dev server, 端口 5173, proxy /ws → 8000)

生产模式:
  前端构建到 frontend/dist/，后端挂载为静态文件，只需启动后端即可。
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect

from .session import NotebookSession


def create_app() -> FastAPI:
    app = FastAPI(title="marimo-from-scratch")

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        await websocket.accept()
        session = NotebookSession()
        try:
            while True:
                msg = await websocket.receive_json()
                responses = session.handle_message(msg)
                for resp in responses:
                    await websocket.send_json(resp)
        except WebSocketDisconnect:
            pass

    @app.get("/api/health")
    async def health() -> dict:
        return {"status": "ok"}

    frontend_dist = (
        Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
    )
    if frontend_dist.exists():
        app.mount(
            "/",
            StaticFiles(directory=str(frontend_dist), html=True),
            name="frontend",
        )

    return app


app = create_app()