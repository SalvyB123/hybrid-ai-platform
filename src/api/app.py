"""Minimal FastAPI app placeholder."""
try:
    from fastapi import FastAPI
except Exception:
    # Allow repo to import without dependencies installed
    class FastAPI:  # type: ignore
        def __init__(self, *_, **__): pass
        def get(self, *_args, **_kwargs):
            def decorator(fn): return fn
            return decorator

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}
