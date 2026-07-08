import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

EMAIL = "24f3004855@ds.study.iitm.ac.in"
ALLOWED_ORIGIN = "https://dash-fy9ps2.example.com"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_tracing_headers(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Request-ID"] = str(uuid.uuid4())
    response.headers["X-Process-Time"] = f"{time.time() - start:.6f}"
    return response


@app.get("/stats")
async def stats(values: str = ""):
    nums = [int(x) for x in values.split(",") if x.strip() != ""]
    n = len(nums)
    s = sum(nums)
    return {
        "email": EMAIL,
        "count": n,
        "sum": s,
        "min": min(nums) if nums else 0,
        "max": max(nums) if nums else 0,
        "mean": (s / n) if n else 0.0,
    }
