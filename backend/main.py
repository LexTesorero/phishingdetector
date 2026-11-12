from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import model

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictRequest(BaseModel):
    urls: list[str]


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/predict")
def predict(request: PredictRequest):
    try:
        results = [
            {"url": url, "probability": model.predict(url)} for url in request.urls
        ]
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="Model not implemented yet.")

    return {"data": results}