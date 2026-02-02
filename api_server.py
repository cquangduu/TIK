"""
================================================================================
DAILY KOREAN API — Backend Server for Mobile App
================================================================================
FastAPI backend to serve DAILY KOREAN data to mobile app.

Run:
    uvicorn api_server:app --reload --host 0.0.0.0 --port 8000

Endpoints:
    GET  /api/today              → Today's lesson
    GET  /api/vocabulary         → Vocabulary list
    GET  /api/vocabulary/random  → Random vocabulary
    GET  /api/quiz/vocab         → Vocabulary quiz
    GET  /api/quiz/grammar       → Grammar quiz
    GET  /api/news               → Today's news
    GET  /api/essay              → Model essay
    GET  /api/archive/{date}     → Historical lesson
    POST /api/progress           → Save user progress
    GET  /api/user/{user_id}/stats → User statistics
================================================================================
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import random

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# ==================== CONFIGURATION ====================
DATA_DIR = os.getenv("DATA_DIR", "topik-video/public")
ARCHIVE_DIR = os.getenv("ARCHIVE_DIR", "archive")
ASSETS_DIR = os.getenv("ASSETS_DIR", "topik-video/public/assets")
API_KEY = os.getenv("API_KEY", "")  # Optional API key for security

# ==================== MODELS ====================

class VocabularyItem(BaseModel):
    id: int
    word: str
    meaning: str
    example: Optional[str] = None
    audio_url: Optional[str] = None

class QuizQuestion(BaseModel):
    id: str
    type: str  # "vocab" or "grammar"
    target: str
    question_ko: str
    question_vi: str
    options_ko: List[str]
    options_vi: List[str]
    correct_answer: str
    explanation_ko: str
    explanation_vi: str

class NewsItem(BaseModel):
    id: str
    date: str
    content_ko: str
    content_vi: Optional[str] = None
    audio_url: Optional[str] = None

class EssayData(BaseModel):
    topic: str
    question: str
    essay_ko: str
    paragraphs: List[Dict]

class LessonData(BaseModel):
    date: str
    topic: str
    vocabulary: List[VocabularyItem]
    vocab_quiz: Optional[QuizQuestion] = None
    grammar_quiz: Optional[QuizQuestion] = None
    news: Optional[NewsItem] = None
    essay: Optional[EssayData] = None

class UserProgress(BaseModel):
    user_id: str
    date: str
    quizzes_completed: int
    correct_answers: int
    vocabulary_learned: List[str]
    streak_days: int

class ProgressUpdate(BaseModel):
    user_id: str
    quiz_type: str
    is_correct: bool
    vocabulary_id: Optional[int] = None

# ==================== APP SETUP ====================

app = FastAPI(
    title="DAILY KOREAN API",
    description="Backend API for DAILY KOREAN mobile app",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for audio
if os.path.exists(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

# In-memory user progress (use database in production)
user_progress_db: Dict[str, UserProgress] = {}

# ==================== HELPERS ====================

def load_current_data() -> Dict:
    """Load today's final_data.json"""
    data_path = os.path.join(DATA_DIR, "final_data.json")
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def load_archive_data(date: str) -> Optional[Dict]:
    """Load archived data for specific date"""
    archive_path = os.path.join(ARCHIVE_DIR, f"{date}.json")
    if os.path.exists(archive_path):
        with open(archive_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def extract_vocabulary(data: Dict) -> List[VocabularyItem]:
    """Extract vocabulary from data"""
    phase2 = data.get("phase2", {})
    analysis_list = phase2.get("analysis_list", [])
    
    vocabulary = []
    for i, item in enumerate(analysis_list):
        vocab = VocabularyItem(
            id=i + 1,
            word=item.get("item", ""),
            meaning=item.get("professor_explanation", ""),
            example=None,
            audio_url=None
        )
        vocabulary.append(vocab)
    
    return vocabulary

def extract_quiz(data: Dict, quiz_type: str) -> Optional[QuizQuestion]:
    """Extract quiz from data"""
    phase3 = data.get("phase3", {})
    phase4 = data.get("phase4", {})
    
    if quiz_type == "vocab":
        quiz_data = phase3.get("video_3_vocab_quiz", phase4.get("video_3_vocab_quiz", {}))
        target = quiz_data.get("target_word", "")
    else:
        quiz_data = phase3.get("video_4_grammar_quiz", phase4.get("video_4_grammar_quiz", {}))
        target = quiz_data.get("target_grammar", "")
    
    if not quiz_data:
        return None
    
    return QuizQuestion(
        id=f"{quiz_type}_{datetime.now().strftime('%Y%m%d')}",
        type=quiz_type,
        target=target,
        question_ko=quiz_data.get("question_ko", ""),
        question_vi=quiz_data.get("question_vi", ""),
        options_ko=quiz_data.get("options_ko", []),
        options_vi=quiz_data.get("options_vi", []),
        correct_answer=quiz_data.get("correct_answer", ""),
        explanation_ko=quiz_data.get("explanation_ko", ""),
        explanation_vi=quiz_data.get("explanation_vi", "")
    )

def extract_news(data: Dict) -> Optional[NewsItem]:
    """Extract news from data"""
    phase1 = data.get("phase1", {})
    news_kr = phase1.get("news_summary_easy_kr", "")
    
    if not news_kr:
        return None
    
    return NewsItem(
        id=f"news_{datetime.now().strftime('%Y%m%d')}",
        date=datetime.now().strftime("%Y-%m-%d"),
        content_ko=news_kr,
        content_vi=None,
        audio_url="/assets/v1_news_healing.mp3"
    )

def extract_essay(data: Dict) -> Optional[EssayData]:
    """Extract essay from data"""
    phase1 = data.get("phase1", {})
    phase2 = data.get("phase2", {})
    phase4 = data.get("phase4", {})
    meta = data.get("meta", {})
    
    essay_text = phase2.get("essay", "")
    deep_dive = phase4.get("video_5_deep_dive", {})
    paragraphs = deep_dive.get("essay", {}).get("paragraphs", [])
    
    if not essay_text:
        return None
    
    return EssayData(
        topic=meta.get("topic_title_vi", ""),
        question=phase1.get("question_full_text", ""),
        essay_ko=essay_text,
        paragraphs=paragraphs
    )

# ==================== ROUTES ====================

@app.get("/")
async def root():
    """API root"""
    return {
        "name": "TOPIK Daily API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/api/today",
            "/api/vocabulary",
            "/api/quiz/vocab",
            "/api/quiz/grammar",
            "/api/news",
            "/api/essay"
        ]
    }

@app.get("/api/today", response_model=LessonData)
async def get_today():
    """Get today's complete lesson"""
    data = load_current_data()
    
    if not data:
        raise HTTPException(status_code=404, detail="No data available for today")
    
    meta = data.get("meta", {})
    
    return LessonData(
        date=datetime.now().strftime("%Y-%m-%d"),
        topic=meta.get("topic_title_vi", "TOPIK Daily"),
        vocabulary=extract_vocabulary(data),
        vocab_quiz=extract_quiz(data, "vocab"),
        grammar_quiz=extract_quiz(data, "grammar"),
        news=extract_news(data),
        essay=extract_essay(data)
    )

@app.get("/api/vocabulary", response_model=List[VocabularyItem])
async def get_vocabulary(
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0)
):
    """Get vocabulary list with pagination"""
    data = load_current_data()
    vocabulary = extract_vocabulary(data)
    
    return vocabulary[offset:offset + limit]

@app.get("/api/vocabulary/random", response_model=VocabularyItem)
async def get_random_vocabulary():
    """Get a random vocabulary item"""
    data = load_current_data()
    vocabulary = extract_vocabulary(data)
    
    if not vocabulary:
        raise HTTPException(status_code=404, detail="No vocabulary available")
    
    return random.choice(vocabulary)

@app.get("/api/vocabulary/{vocab_id}", response_model=VocabularyItem)
async def get_vocabulary_by_id(vocab_id: int):
    """Get specific vocabulary item"""
    data = load_current_data()
    vocabulary = extract_vocabulary(data)
    
    for vocab in vocabulary:
        if vocab.id == vocab_id:
            return vocab
    
    raise HTTPException(status_code=404, detail="Vocabulary not found")

@app.get("/api/quiz/vocab", response_model=QuizQuestion)
async def get_vocab_quiz():
    """Get vocabulary quiz"""
    data = load_current_data()
    quiz = extract_quiz(data, "vocab")
    
    if not quiz:
        raise HTTPException(status_code=404, detail="No vocabulary quiz available")
    
    return quiz

@app.get("/api/quiz/grammar", response_model=QuizQuestion)
async def get_grammar_quiz():
    """Get grammar quiz"""
    data = load_current_data()
    quiz = extract_quiz(data, "grammar")
    
    if not quiz:
        raise HTTPException(status_code=404, detail="No grammar quiz available")
    
    return quiz

@app.get("/api/news", response_model=NewsItem)
async def get_news():
    """Get today's news"""
    data = load_current_data()
    news = extract_news(data)
    
    if not news:
        raise HTTPException(status_code=404, detail="No news available")
    
    return news

@app.get("/api/essay", response_model=EssayData)
async def get_essay():
    """Get model essay"""
    data = load_current_data()
    essay = extract_essay(data)
    
    if not essay:
        raise HTTPException(status_code=404, detail="No essay available")
    
    return essay

@app.get("/api/archive/{date}")
async def get_archive(date: str):
    """Get archived lesson for specific date (YYYY-MM-DD)"""
    data = load_archive_data(date)
    
    if not data:
        raise HTTPException(status_code=404, detail=f"No data for {date}")
    
    meta = data.get("meta", {})
    
    return LessonData(
        date=date,
        topic=meta.get("topic_title_vi", "TOPIK Daily"),
        vocabulary=extract_vocabulary(data),
        vocab_quiz=extract_quiz(data, "vocab"),
        grammar_quiz=extract_quiz(data, "grammar"),
        news=extract_news(data),
        essay=extract_essay(data)
    )

@app.get("/api/archive")
async def list_archive(
    limit: int = Query(default=30, ge=1, le=100)
):
    """List available archived lessons"""
    if not os.path.exists(ARCHIVE_DIR):
        return {"dates": []}
    
    dates = []
    for filename in os.listdir(ARCHIVE_DIR):
        if filename.endswith(".json"):
            date = filename.replace(".json", "")
            dates.append(date)
    
    dates.sort(reverse=True)
    return {"dates": dates[:limit]}

# ==================== USER PROGRESS ====================

@app.post("/api/progress")
async def update_progress(update: ProgressUpdate):
    """Update user progress"""
    user_id = update.user_id
    today = datetime.now().strftime("%Y-%m-%d")
    
    if user_id not in user_progress_db:
        user_progress_db[user_id] = UserProgress(
            user_id=user_id,
            date=today,
            quizzes_completed=0,
            correct_answers=0,
            vocabulary_learned=[],
            streak_days=1
        )
    
    progress = user_progress_db[user_id]
    
    # Update stats
    progress.quizzes_completed += 1
    if update.is_correct:
        progress.correct_answers += 1
    
    if update.vocabulary_id:
        if str(update.vocabulary_id) not in progress.vocabulary_learned:
            progress.vocabulary_learned.append(str(update.vocabulary_id))
    
    # Update streak
    if progress.date != today:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        if progress.date == yesterday:
            progress.streak_days += 1
        else:
            progress.streak_days = 1
        progress.date = today
    
    return {"success": True, "progress": progress}

@app.get("/api/user/{user_id}/stats")
async def get_user_stats(user_id: str):
    """Get user statistics"""
    if user_id not in user_progress_db:
        return UserProgress(
            user_id=user_id,
            date=datetime.now().strftime("%Y-%m-%d"),
            quizzes_completed=0,
            correct_answers=0,
            vocabulary_learned=[],
            streak_days=0
        )
    
    return user_progress_db[user_id]

# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    data = load_current_data()
    return {
        "status": "healthy",
        "data_available": bool(data),
        "timestamp": datetime.now().isoformat()
    }

# ==================== MAIN ====================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=8000)
