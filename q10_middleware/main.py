import time
import uuid
from collections import defaultdict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

EMAIL = "24f3004855@ds.study.iitm.ac.in"
ALLOWED_ORIGIN = "https://app-5tf8zq.example.com"
EXAM_PAGE_ORIGIN = "https://exam.sanand.workers.dev"

BUCKET = 8
WINDOW = 10

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN, EXAM_PAGE_ORIGIN],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

rate_buckets = defaultdict(list)


@app.middleware("http")
async def context_and_rate_limit(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = req_id

    if request.url.path == "/ping" and request.method == "GET":
        client_id = request.headers.get("X-Client-Id", "anonymous")
        now = time.time()
        bucket = rate_buckets[client_id]
        while bucket and bucket[0] <= now - WINDOW:
            bucket.pop(0)
        if len(bucket) >= BUCKET:
            origin = request.headers.get("origin")
            headers = {"X-Request-ID": req_id}
            if origin in (ALLOWED_ORIGIN, EXAM_PAGE_ORIGIN):
                headers["Access-Control-Allow-Origin"] = origin
            return JSONResponse(
                status_code=429,
                content={"detail": "rate limit exceeded"},
                headers=headers,
            )
        bucket.append(now)

    response = await call_next(request)
    response.headers["X-Request-ID"] = req_id
    return response


@app.get("/ping")
async def ping(request: Request):
    return {"email": EMAIL, "request_id": request.state.request_id}
