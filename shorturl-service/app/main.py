from . import models, database
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator
from typing import Optional
import shortuuid
import random


app = FastAPI(
    title="URL Shortener Service", 
    description="Микросервис для сокращения URL"
)

@app.on_event("startup")
def startup_event():
    database.init_db()

def generate_unique_short_id(db: Session, length=6, max_attempts=10):
    for _ in range(max_attempts):
        short_id = shortuuid.ShortUUID().random(length=length)
        existing = db.query(models.ShortURL)\
            .filter(models.ShortURL.short_id == short_id)\
            .first()
        
        if not existing:
            return short_id

    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=length))

class URLShortenRequest(BaseModel):
    url: str
    
    @field_validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL должен начинаться с http:// или https://')
        
        return v

class URLShortenResponse(BaseModel):
    short_id: str
    short_url: str

class URLStatsResponse(BaseModel):
    short_id: str
    full_url: str


@app.post("/shorten", response_model=URLShortenResponse, status_code=201)
def shorten_url(
    request: URLShortenRequest, 
    db: Session = Depends(database.get_db)):
    
    short_id = generate_unique_short_id(db, length=6)

    db_url = models.ShortURL(
        short_id=short_id,
        full_url=request.url
    )    
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    
    return {
        "short_id": short_id,
        "short_url": f"/{short_id}"
    }

@app.get("/{short_id}")
def redirect_url(
    short_id: str, 
    db: Session = Depends(database.get_db)):

    db_url = db.query(models.ShortURL)\
        .filter(models.ShortURL.short_id == short_id)\
        .first()
    
    if db_url is None:
        raise HTTPException(
            status_code=404, 
            detail="Сокращенная ссылка не найдена"
        )
    
    from fastapi.responses import RedirectResponse
    return RedirectResponse(
        url=db_url.full_url, 
        status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )

@app.get("/stats/{short_id}", response_model=URLStatsResponse)
def get_url_stats(
    short_id: str, 
    db: Session = Depends(database.get_db)):

    db_url = db.query(models.ShortURL)\
        .filter(models.ShortURL.short_id == short_id)\
        .first()
    
    if db_url is None:
        raise HTTPException(
            status_code=404, 
            detail="Сокращенная ссылка не найдена"
        )
    
    return {
        "short_id": db_url.short_id,
        "full_url": db_url.full_url
    }

@app.get("/", include_in_schema=False)
def get_all_urls(db: Session = Depends(database.get_db)):
    urls = db.query(models.ShortURL).all()
    
    return {"count": len(urls), "urls": urls}
