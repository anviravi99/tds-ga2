from collections import defaultdict
from typing import List, Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

API_KEY = "ak_p3bowshfivslb03498dpgyyp"
EMAIL = "24f3004855@ds.study.iitm.ac.in"


class Event(BaseModel):
    user: str
    amount: float
    ts: Optional[int] = None


class Batch(BaseModel):
    events: List[Event]


@app.post("/analytics")
async def analytics(batch: Batch, x_api_key: Optional[str] = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="unauthorized")

    totals = defaultdict(float)
    users = set()
    revenue = 0.0
    for e in batch.events:
        users.add(e.user)
        if e.amount > 0:
            revenue += e.amount
            totals[e.user] += e.amount

    top_user = max(totals, key=totals.get) if totals else None

    return {
        "email": EMAIL,
        "total_events": len(batch.events),
        "unique_users": len(users),
        "revenue": round(revenue, 2),
        "top_user": top_user,
    }
