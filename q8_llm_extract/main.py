import re

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

CURRENCY_SYMBOLS = {"$": "USD", "€": "EUR", "£": "GBP"}
COMPANY_SUFFIXES = r"(?:Industries|Ltd\.?|Inc\.?|LLC|Corp\.?|Company|Co\.?|Group|Enterprises)"


class TextIn(BaseModel):
    text: str = ""


class Invoice(BaseModel):
    vendor: str
    amount: float
    currency: str
    date: str


def extract_vendor(text: str) -> str:
    m = re.search(
        rf"\b([A-Z][\w&\.\-]*(?:\s+[A-Z][\w&\.\-]*){{0,4}}\s+{COMPANY_SUFFIXES})\b", text
    )
    if m:
        return m.group(1).strip()
    m = re.search(r"(?:From|Vendor|Bill(?:ed)?\s+by|Billed\s+from)\s*[:\-]?\s*([A-Za-z0-9&\.\-\s]{3,60})", text, re.I)
    if m:
        return m.group(1).strip().splitlines()[0]
    return "Unknown Vendor"


def extract_amount_currency(text: str):
    # e.g. "USD 4231.00" / "$4231.00" / "4231.00 USD" / "€4231"
    m = re.search(r"\b(USD|EUR|GBP)\s*\$?\s*([\d,]+(?:\.\d+)?)", text)
    if m:
        return float(m.group(2).replace(",", "")), m.group(1).upper()

    m = re.search(r"([\$€£])\s*([\d,]+(?:\.\d+)?)", text)
    if m:
        return float(m.group(2).replace(",", "")), CURRENCY_SYMBOLS.get(m.group(1), "USD")

    m = re.search(r"([\d,]+(?:\.\d+)?)\s*(USD|EUR|GBP)\b", text)
    if m:
        return float(m.group(1).replace(",", "")), m.group(2).upper()

    return 0.0, "USD"


def extract_date(text: str) -> str:
    m = re.search(r"(20\d{2}-\d{2}-\d{2})", text)
    if m:
        return m.group(1)
    return "2026-01-01"


@app.post("/extract", response_model=Invoice)
async def extract(body: TextIn):
    text = (body.text or "").strip()
    if not text:
        return JSONResponse(status_code=422, content={"detail": "empty input"})

    vendor = extract_vendor(text)
    amount, currency = extract_amount_currency(text)
    date = extract_date(text)

    return {"vendor": vendor, "amount": amount, "currency": currency, "date": date}
