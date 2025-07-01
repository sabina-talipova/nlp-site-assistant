from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from database import SessionLocal, Page
from sentence_transformers import SentenceTransformer
import numpy as np

app = FastAPI()
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/pages/")
def get_pages(limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Page).limit(limit).all()

@app.get("/search/")
def search_pages(q: str = Query(...), db: Session = Depends(get_db)):
    query_vec = model.encode([q])[0]
    results = []

    for page in db.query(Page).filter(Page.embedding != None).all():
        score = np.dot(page.embedding, query_vec) / (
            np.linalg.norm(page.embedding) * np.linalg.norm(query_vec)
        )
        results.append({"url": page.url, "title": page.title, "score": round(score, 4)})

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:5]
