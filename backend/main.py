from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import model

load_error: str | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global load_error
    try:
        model.load_models()
    except Exception as e:  # keep server up so the frontend shows a clear message
        load_error = f"{type(e).__name__}: {e}"
        print("MODEL LOAD FAILED:", load_error)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictRequest(BaseModel):
    urls: list[str]
    model: Literal["baseline", "enhanced"] = "enhanced"


@app.get("/api/health")
def health():
    return {"status": "ok" if load_error is None else "degraded", "error": load_error}


@app.post("/api/predict")
def predict(request: PredictRequest):
    if load_error:
        raise HTTPException(status_code=501, detail=load_error)
    try:
        results = [
            {"url": u, "probability": model.predict(u, request.model)}
            for u in request.urls
        ]
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="Models not loaded.")
    return {"model": request.model, "data": results}