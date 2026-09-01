from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {"message": "ClearLedger API is running"}

@app.get("/transactions")
def transactions():
    return [
        {
            "merchant": "Chipotle",
            "amount": 14.72,
            "category": "Dining"
        },
        {
            "merchant": "Spotify",
            "amount": 11.99,
            "category": "Entertainment"
        }
    ]