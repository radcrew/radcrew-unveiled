import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


PORT = _env_int("PORT", 8787)
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:8080").strip() or "http://localhost:8080"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"ok": True, "chunks": 0}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT)
