"""TabSplit -- a small expense-splitting API."""

from itertools import count
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException


class Expense(BaseModel):
    """A single expense logged inside a group.

    Args:
        description: Free-text label for what the money was spent on.
        amount: Cost of the expense; must be a positive number.
        paid_by: Name of the member who fronted the money.
    """

    description: str
    amount: float = Field(gt=0, description="Must be a positive number.")
    paid_by: str


class Group(BaseModel):
    """A group of people who share expenses.

    Args:
        id: Server-generated integer id assigned at creation time.
        name: Human-readable name of the group.
        members: Names of the people splitting the expenses.
        expenses: Expenses logged against the group so far.
    """

    id: int
    name: str
    members: list[str]
    expenses: list[Expense]


class GroupCreate(BaseModel):
    """Request payload for POST /groups.

    Args:
        name: Human-readable name for the new group.
        members: Initial member list; defaults to empty.
    """

    name: str
    members: list[str] = []


class MemberAdd(BaseModel):
    """Request payload for POST /groups/{group_id}/members.

    Args:
        name: Name of the member to append.
    """

    name: str


class ApiError(HTTPException):
    """An HTTP error carrying a stable machine-readable ``code``.

    Raised by application code; rendered by the ``StarletteHTTPException``
    handler below into the shared ``{"error": {...}}`` envelope.
    """

    def __init__(self, status_code: int, code: str, message: str) -> None:
        """Initialize the error with a status, a code, and a human message.

        Args:
            status_code: HTTP status code sent back to the client.
            code: Stable machine-readable identifier such as GROUP_NOT_FOUND.
            message: Human-readable explanation carried in the envelope.
        """
        super().__init__(status_code=status_code, detail=message)
        self.code = code


# In-memory store: maps group id -> Group instance.
groups: dict[int, Group] = {}
_next_group_id = count(start=1)

app = FastAPI(
    title="TabSplit",
    version="0.1.0",
    description="Small API for tracking shared expenses across groups.",
)


# --- Shared error envelope --------------------------------------------------
# Every error response -- whether raised by application code, by Starlette,
# or by FastAPI request validation -- flows through ``_error_response``, so
# the whole API emits one consistent JSON shape.


_FALLBACK_ERROR_CODES = {
    status.HTTP_404_NOT_FOUND: "NOT_FOUND",
    status.HTTP_405_METHOD_NOT_ALLOWED: "METHOD_NOT_ALLOWED",
}


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    """Render an error in the shared ``{"error": {...}}`` envelope.

    Args:
        status_code: HTTP status code for the response.
        code: Stable machine-readable error identifier.
        message: Human-readable explanation shown to API consumers.

    Returns:
        JSONResponse whose body carries the code and message.
    """
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


@app.exception_handler(StarletteHTTPException)
def handle_http_exception(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Wrap any HTTPException (app-raised or framework-raised) in the envelope.

    ``fastapi.HTTPException`` subclasses ``starlette.exceptions.HTTPException``,
    so this single handler covers both.

    Args:
        request: Incoming request that triggered the exception.
        exc: Raised Starlette/FastAPI HTTPException instance.

    Returns:
        JSONResponse rendering the error in the shared envelope.
    """
    code = getattr(exc, "code", None) or _FALLBACK_ERROR_CODES.get(
        exc.status_code, "HTTP_ERROR"
    )
    message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return _error_response(exc.status_code, code, message)


def _is_nonpositive_amount_error(err: dict[str, Any]) -> bool:
    """Report whether a validation error is the ``amount > 0`` rule failing.

    Args:
        err: Single parsed validation error from a RequestValidationError.

    Returns:
        True when the error targets ``amount`` as a greater-than violation.
    """
    loc = err.get("loc") or ()
    return err.get("type") == "greater_than" and loc[-1] == "amount"


@app.exception_handler(RequestValidationError)
def handle_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Wrap request validation failures in the shared error envelope.

    Covers malformed JSON, bad payloads, and invalid path/query parameters.
    A non-positive ``amount`` gets its own dedicated INVALID_AMOUNT code.

    Args:
        request: Incoming request whose body or parameters failed validation.
        exc: Aggregated validation error produced by FastAPI.

    Returns:
        JSONResponse rendering the failures in the shared envelope.
    """
    errors = exc.errors()

    # A non-positive ``amount`` gets its own dedicated error code (still 422).
    if errors and all(_is_nonpositive_amount_error(err) for err in errors):
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "INVALID_AMOUNT",
            "amount must be > 0",
        )

    messages = []
    for err in errors:
        loc = [str(part) for part in err.get("loc", ()) if part != "body"]
        field = ".".join(loc)
        text = str(err.get("msg", "Invalid input"))
        messages.append(f"{field}: {text}" if field else text)

    return _error_response(
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "VALIDATION_ERROR",
        "; ".join(messages),
    )


def _get_group_or_404(group_id: int) -> Group:
    """Return the group with the given id.

    Looks up ``group_id`` in the shared store.

    Args:
        group_id: Server-generated integer id of the group.

    Returns:
        The matching Group instance.

    Raises:
        ApiError: With code GROUP_NOT_FOUND if no group exists.
    """
    group = groups.get(group_id)
    if group is None:
        raise ApiError(
            status_code=status.HTTP_404_NOT_FOUND,
            code="GROUP_NOT_FOUND",
            message=f"Group {group_id} not found.",
        )
    return group


@app.get("/health")
def health() -> dict[str, str]:
    """Report service liveness.

    Returns:
        Dict with a constant ``status`` key set to ``ok``.
    """
    return {"status": "ok"}


@app.post("/groups", status_code=status.HTTP_201_CREATED)
def create_group(payload: GroupCreate) -> Group:
    """Create a new group with a server-generated integer id.

    Args:
        payload: Validated GroupCreate body with name and initial members.

    Returns:
        The stored Group, including its id and an empty expense list.
    """
    group = Group(
        id=next(_next_group_id),
        name=payload.name,
        members=payload.members,
        expenses=[],
    )
    groups[group.id] = group
    return group


@app.get("/groups/{group_id}")
def get_group(group_id: int) -> Group:
    """Fetch a group by id.

    Args:
        group_id: Server-generated integer id of the group.

    Returns:
        The matching Group instance.

    Raises:
        ApiError: With code GROUP_NOT_FOUND if no group exists.
    """
    return _get_group_or_404(group_id)


@app.post("/groups/{group_id}/members")
def add_member(group_id: int, payload: MemberAdd) -> Group:
    """Append a member to the group.

    Args:
        group_id: Server-generated integer id of the target group.
        payload: Validated MemberAdd body carrying the new member's name.

    Returns:
        The updated Group with the member appended.

    Raises:
        ApiError: With code GROUP_NOT_FOUND if no group exists.
    """
    group = _get_group_or_404(group_id)
    group.members.append(payload.name)
    return group


@app.post("/groups/{group_id}/expenses")
def add_expense(group_id: int, expense: Expense) -> Group:
    """Append an expense to the group.

    Amounts must be positive; FastAPI rejects others with a 422 before
    this handler runs.

    Args:
        group_id: Server-generated integer id of the target group.
        expense: Validated Expense to append to the group.

    Returns:
        The updated Group with the expense appended.

    Raises:
        ApiError: With code GROUP_NOT_FOUND if no group exists.
    """
    group = _get_group_or_404(group_id)
    group.expenses.append(expense)
    return group


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
