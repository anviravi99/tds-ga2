# Q7 — Expose a Local LLM through a Tunnel

No app code needed here — just run Ollama locally and tunnel it.

## Steps (on your own machine, not this sandbox)

1. Install Ollama: https://ollama.com/download
2. Pull a small fast model:
   ```
   ollama pull llama3.2
   ```
3. Allow CORS from any origin and start the server:
   ```
   OLLAMA_ORIGINS=* ollama serve
   ```
   (On Windows, set it as an environment variable first: `setx OLLAMA_ORIGINS "*"`, then restart the Ollama app/service.)
4. In another terminal, tunnel port 11434 (Ollama's default port):
   ```
   cloudflared tunnel --url http://localhost:11434
   ```
   Copy the `https://xxxx.trycloudflare.com` URL it prints.
5. Test it works before submitting:
   ```
   curl https://xxxx.trycloudflare.com/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{"model":"llama3.2","messages":[{"role":"user","content":"Say TK1a2b3c and then compute 4+5"}],"stream":false}'
   ```
   Confirm the response text contains both the token and the digit `9`.

## Submit

```json
{"url": "https://xxxx.trycloudflare.com/v1/chat/completions", "model": "llama3.2"}
```

**Important:** keep your machine, Ollama, and the `cloudflared` process running until the deadline — the tunnel dies the moment either process stops, and the grader hits it live on every check.
