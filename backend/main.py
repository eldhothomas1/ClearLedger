from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Transaction

app = FastAPI()


@app.get("/")
def home():
    return {"message": "ClearLedger API is running"}

@app.get("/transactions")
def get_transactions(db: Session = Depends(get_db)):
    statement = select(Transaction)
    return db.scalars(statement).all()