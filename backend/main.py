from fastapi import FastAPI

from backend.routers import analytics, transactions


app = FastAPI(
    title="ClearLedger API",
    description="REST API for importing, managing, and analyzing financial transactions.",
    version="0.2.0",
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
