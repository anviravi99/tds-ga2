import os

import redis.asyncio as redis
from fastapi import FastAPI

app = FastAPI()

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
r = redis.from_url(REDIS_URL, decode_responses=True)


@app.post("/hit/{key}")
async def hit(key: str):
    count = await r.incr(f"counter:{key}")
    return {"key": key, "count": count}


@app.get("/count/{key}")
async def count(key: str):
    val = await r.get(f"counter:{key}")
    return {"key": key, "count": int(val) if val else 0}


@app.get("/healthz")
async def healthz():
    try:
        pong = await r.ping()
        return {"status": "ok", "redis": "up" if pong else "down"}
    except Exception:
        return {"status": "ok", "redis": "down"}
