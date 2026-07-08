import time
import uuid
from collections import deque

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

EMAIL = "24f3004855@ds.study.iitm.ac.in"
START_TIME = time.time()
REQUEST_COUNT = 0
LOGS = deque(maxlen=2000)


@app.middleware("http")
async def instrument(request: Request, call_next):
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    req_id = str(uuid.uuid4())
    response = await call_next(request)
    LOGS.append(
        {
            "level": "info",
            "ts": time.time(),
            "path": request.url.path,
            "request_id": req_id,
        }
    )
    response.headers["X-Request-ID"] = req_id
    return response


@app.get("/work")
async def work(n: int = 1):
    total = 0
    for i in range(max(n, 0)):
        total += i * i
    return {"email": EMAIL, "done": n}


@app.get("/metrics")
async def metrics():
    body = (
        "# HELP http_requests_total Total HTTP requests\n"
        "# TYPE http_requests_total counter\n"
        f"http_requests_total {REQUEST_COUNT}\n"
    )
    return PlainTextResponse(body, media_type="text/plain; version=0.0.4")


@app.get("/healthz")
async def healthz():
    return {"status": "ok", "uptime_s": time.time() - START_TIME}


@app.get("/logs/tail")
async def logs_tail(limit: int = 10):
    return list(LOGS)[-limit:]
