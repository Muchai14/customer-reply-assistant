"""FastAPI entry point: draft generation, reply saving, and history."""

from contextlib import asynccontextmanager
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Path as PathParameter, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.database import ReplyStore
from backend.matcher import load_faqs, match_faq
from backend.models import (
    DraftRequest, DraftResult, MatchedDraft, Source, UnmatchedDraft,
    SaveReplyRequest, SavedReply, ReplyList, NotFoundError,
)


DEFAULT_DB_PATH = Path(__file__).resolve().parent / "data" / "replies.db"


def create_app(database_path: Optional[Path] = None) -> FastAPI:
    """Create an isolated application; tests supply their own temporary database."""
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.faqs = load_faqs()
        path = database_path if database_path is not None else Path(os.environ.get("DB_PATH", str(DEFAULT_DB_PATH)))
        app.state.store = ReplyStore(path)
        app.state.store.initialize()
        yield

    application = FastAPI(
        title="Customer Reply Assistant API",
        version="0.1.0",
        description="Fictional FAQ demo with draft generation, reviewed reply saving, and persistent history.",
        lifespan=lifespan,
    )
    application.add_api_route("/api/drafts", generate_draft, methods=["POST"], response_model=DraftResult,
                              operation_id="generateDraft", tags=["Drafts"])
    application.add_api_route("/api/replies", save_reply, methods=["POST"], response_model=SavedReply,
                              status_code=201, operation_id="saveReply", tags=["Replies"])
    application.add_api_route("/api/replies", list_replies, methods=["GET"], response_model=ReplyList,
                              operation_id="listReplies", tags=["Replies"])
    application.add_api_route("/api/replies/{id}", get_reply, methods=["GET"], response_model=SavedReply,
                              operation_id="getReply", tags=["Replies"],
                              responses={404: {"model": NotFoundError, "description": "Reply not found"}})
    frontend = Path(__file__).resolve().parent.parent / "frontend"
    application.mount("/assets", StaticFiles(directory=frontend), name="assets")

    @application.get("/", include_in_schema=False)
    def index():
        return FileResponse(frontend / "index.html")

    return application


def generate_draft(payload: DraftRequest, request: Request) -> DraftResult:
    """Build a template-based draft without saving or sending anything."""
    faq = match_faq(payload.question, request.app.state.faqs)
    if faq is None:
        return UnmatchedDraft(
            question=payload.question,
            message="No matching FAQ was found. Please provide more information or write a reply manually.",
        )
    return MatchedDraft(
        question=payload.question,
        draft="Hello, " + faq["answer"],
        source=Source(id=faq["id"], title=faq["title"], answer=faq["answer"]),
    )


def save_reply(payload: SaveReplyRequest, request: Request) -> SavedReply:
    """Persist a reviewed reply only; never send a customer message."""
    if payload.faq_id is not None and not any(faq["id"] == payload.faq_id for faq in request.app.state.faqs):
        raise RequestValidationError([
            {"loc": ["body", "faq_id"], "msg": "FAQ ID does not exist.", "type": "value_error"}
        ])
    saved = request.app.state.store.save(payload.question, payload.reply, payload.faq_id)
    return SavedReply(**saved)


def list_replies(request: Request, limit: int = Query(20, ge=1, le=100),
                 offset: int = Query(0, ge=0)) -> ReplyList:
    """Return a page of replies in newest-first order and the unpaginated total."""
    return ReplyList(**request.app.state.store.list_replies(limit, offset))


def get_reply(request: Request, id: int = PathParameter(..., ge=1)) -> SavedReply:
    """Return a saved reply or the contract's 404 response."""
    saved = request.app.state.store.get_reply(id)
    if saved is None:
        raise HTTPException(status_code=404, detail="Reply not found.")
    return SavedReply(**saved)


app = create_app()
