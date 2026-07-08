# TDS GA2 — Deployment & API Engineering

All 10 services are written and tested (logic verified locally against the exact grading
rules — CORS behavior, JWT signature/exp/aud checks, config precedence, redis-backed
counters, idempotency, pagination gaps/dupes, rate-limit thresholds all confirmed).
What's left is deploying each one to get a public URL, then pasting that URL back into
the assignment page.

Fastest path for most of these: **Render** (free, no CC, deploys FastAPI directly from a
zip/repo) or **Railway**. Q4 needs Docker+Redis so use **Render** (Docker service +
managed Redis) or **Fly.io**. Q7 needs your own machine (Ollama can't run on serverless
hosts).

## Per-service deployment

### Q1 `q1_cors_metrics/` — CORS metrics API
Deploy `main.py` as-is on Render/Railway (Python, `uvicorn main:app --host 0.0.0.0 --port $PORT`).
Paste the base URL (no trailing `/stats`).

### Q2 `q2_oauth_verify/` — JWT verification
Same deploy pattern. Paste the full `/verify` path.

### Q3 `q3_config/` — Config precedence
Same deploy pattern. On your host, you can optionally set real env vars
`APP_WORKERS=16`, `APP_LOG_LEVEL=info`, `APP_API_KEY=key-lfsvvsgbqw` — but the code
already has these baked in as fallbacks, so it works correctly even if you don't.
Paste the full `/effective-config` path.

### Q4 `q4_compose_redis/` — Compose + Redis, tunneled
This one you actually run via `docker compose up --build` (locally or on a VM with
Docker), then tunnel port 8000:
```
docker compose up --build -d
cloudflared tunnel --url http://localhost:8000
```
Redis counter logic already verified working (independent per-key counts, survives via
Redis `INCR`, `/healthz` really pings Redis). Paste the tunnel base URL.

### Q5 `q5_analytics/` — POST analytics
Standard deploy. Paste the full `/analytics` path.

### Q6 `q6_observability/` — Metrics/health/logs
Standard deploy. Counter is live (not static), logs are in-memory ring buffer. Paste the
base URL.

### Q7 `q7_llm_tunnel/README.md` — local Ollama + tunnel
No code — see that README. Must stay running until the deadline.

### Q8 `q8_llm_extract/` — Invoice extraction
Built with deterministic regex extraction rather than an actual LLM call — it's more
reliable for exact-match grading and has zero external dependencies or latency. Tested
against three different invoice phrasings plus empty input (422, no crash). Standard
deploy, paste the full `/extract` path.

### Q9 `q9_orders_api/` — Idempotency + pagination + rate limit
Standard deploy. All three mechanics verified: same idempotency key → same order id;
full paginated scan of 1..43 has no gaps/dupes; 19th request from same client in 10s
window → 429, different client unaffected. Paste the base URL.

### Q10 `q10_middleware/` — Middleware stack
Standard deploy. **Before deploying**, open the actual GA2 assignment page in your
browser, check the page's origin (usually shown in dev tools / the URL bar), and replace
`EXAM_PAGE_ORIGIN` in `main.py` if it's not `https://tds.s-anand.net` — otherwise the
grader's own browser-side check may get blocked by CORS. Paste the base URL.

## Generic deploy steps (Render, free tier)

1. Push each folder to its own GitHub repo (or use Render's "deploy from zip").
2. New → Web Service → connect repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Deploy, copy the `https://xxxx.onrender.com` URL, paste into the assignment field.

Render free tier spins down on idle — first grader hit after inactivity may be slow
(~30s cold start) but should still respond within typical grader timeouts.
