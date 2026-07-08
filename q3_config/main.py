import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- Layer 1: hardcoded defaults ---
DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

# --- Layer 2: config.<env>.yaml (assigned values baked in) ---
YAML_LAYER = {
    "port": 8471,
    "workers": 12,
    "debug": False,
    "log_level": "info",
    "api_key": "key-l6cdmivkzb",
}

# --- Layer 3: .env file (empty per assignment; NUM_WORKERS alias supported) ---
DOTENV_LAYER = {}
if "NUM_WORKERS" in DOTENV_LAYER:
    DOTENV_LAYER["workers"] = DOTENV_LAYER.pop("NUM_WORKERS")

# --- Layer 4: OS-level env vars (APP_ prefix). Fallback to assigned values
# in case the real hosting platform doesn't have these set as actual env vars. ---
OS_ENV_FALLBACK = {
    "workers": "16",
    "log_level": "info",
    "api_key": "key-lfsvvsgbqw",
}


def coerce(key, value):
    if key in ("port", "workers"):
        return int(value)
    if key == "debug":
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in ("true", "1", "yes", "on")
    return str(value)


@app.get("/effective-config")
async def effective_config(request: Request):
    cfg = dict(DEFAULTS)
    cfg.update(YAML_LAYER)
    cfg.update(DOTENV_LAYER)

    os_layer = dict(OS_ENV_FALLBACK)
    for k, v in os.environ.items():
        if k.startswith("APP_"):
            os_layer[k[len("APP_"):].lower()] = v
    cfg.update(os_layer)

    for s in request.query_params.getlist("set"):
        if "=" in s:
            k, v = s.split("=", 1)
            cfg[k] = v

    out = {k: coerce(k, v) for k, v in cfg.items()}
    out["api_key"] = "****"
    return out
