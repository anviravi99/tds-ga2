import time
import uuid
from collections import defaultdict
from typing import Optional

from fastapi import FastAPI, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Retry-After"],
)

TOTAL_ORDERS = 43
RATE_LIMIT = 18
WINDOW = 10

idempotency_store = {}
rate_buckets = defaultdict(list)


@app.middleware("http")
async def rate_limiter(request: Request, call_next):
    if request.url.path == "/orders":
        client_id = request.headers.get("X-Client-Id", "anonymous")
        now = time.time()
        bucket = rate_buckets[client_id]
        while bucket and bucket[0] <= now - WINDOW:
            bucket.pop(0)
        if len(bucket) >= RATE_LIMIT:
            retry_after = max(1, int(WINDOW - (now - bucket[0])) + 1)
            return JSONResponse(
                status_code=429,
                content={"detail": "rate limit exceeded"},
                headers={
                    "Retry-After": str(retry_after),
                    "Access-Control-Allow-Origin": "*",
                },
            )
        bucket.append(now)
    return await call_next(request)


@app.post("/orders", status_code=201)
async def create_order(
    request: Request,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
):
    if idempotency_key and idempotency_key in idempotency_store:
        return idempotency_store[idempotency_key]

    order = {"id": str(uuid.uuid4()), "status": "created"}
    if idempotency_key:
        idempotency_store[idempotency_key] = order
    return order


@app.get("/orders")
async def list_orders(limit: int = 10, cursor: Optional[str] = None):
    start = int(cursor) if cursor else 0
    ids = list(range(1, TOTAL_ORDERS + 1))
    page_ids = ids[start : start + limit]
    next_start = start + limit
    next_cursor = str(next_start) if next_start < TOTAL_ORDERS else None
    items = [{"id": i} for i in page_ids]
    return {"items": items, "next_cursor": next_cursor}
