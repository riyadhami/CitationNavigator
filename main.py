"""
Citation Navigator — FastAPI application entry point.
Route logic lives in app/routes.py; this file only wires the framework.
"""

import os
import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.routes import router

app = FastAPI(
    title="Citation Navigator",
    description="Explore academic citation networks powered by OpenAlex.",
    version="0.1.0",
)


@app.exception_handler(Exception)
async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"{type(exc).__name__}: {exc}"},
    )


_cors_origins = ["http://localhost:5173", "http://localhost:3000"]
_extra = os.getenv("CORS_ORIGIN")
if _extra:
    _cors_origins.append(_extra)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

_assets_dir = os.path.join("static", "assets")
if os.path.isdir(_assets_dir):
    app.mount("/assets", StaticFiles(directory=_assets_dir), name="assets")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router)
