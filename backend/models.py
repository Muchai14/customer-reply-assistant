"""Request and response models for draft generation and reply saving."""

from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


Question = Annotated[str, StringConstraints(
    strict=True, strip_whitespace=True, min_length=1, max_length=1000, pattern=r"\S"
)]
ReplyText = Annotated[str, StringConstraints(
    strict=True, strip_whitespace=True, min_length=1, max_length=5000, pattern=r"\S"
)]


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DraftRequest(ContractModel):
    question: Question


class Source(ContractModel):
    id: Annotated[str, StringConstraints(pattern=r"^faq-[0-9]{3}$")]
    title: Annotated[str, StringConstraints(min_length=1)]
    answer: Annotated[str, StringConstraints(min_length=1)]


class MatchedDraft(ContractModel):
    question: Question
    matched: Literal[True] = True
    draft: ReplyText
    source: Source
    message: None = None


class UnmatchedDraft(ContractModel):
    question: Question
    matched: Literal[False] = False
    draft: Literal[""] = ""
    source: None = None
    message: Annotated[str, StringConstraints(min_length=1)]


DraftResult = Union[MatchedDraft, UnmatchedDraft]


class SaveReplyRequest(ContractModel):
    question: Question
    reply: ReplyText
    faq_id: Union[Annotated[str, StringConstraints(strict=True, pattern=r"^faq-[0-9]{3}$")], None]


class SavedReply(SaveReplyRequest):
    id: Annotated[int, Field(ge=1)]
    created_at: Annotated[str, StringConstraints(pattern=r"Z$")]


class ReplyList(ContractModel):
    items: list[SavedReply]
    total: Annotated[int, Field(ge=0)]


class NotFoundError(ContractModel):
    detail: str


class PayloadTooLargeError(ContractModel):
    detail: str
