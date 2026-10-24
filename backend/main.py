from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import analytics, transactions


app = FastAPI(
    title="ClearLedger API",
    description="REST API for importing, managing, and analyzing financial transactions.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transactions.router)
app.include_router(analytics.router)


@app.get("/", tags=["System"])
def home():
    return {
        "message": "ClearLedger API is running",
        "documentation": "/docs",
    }


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy"}
