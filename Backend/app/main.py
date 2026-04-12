from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import traceback

# ✅ DB IMPORTS (IMPORTANT)
from app.database import engine
from app.models import Base

# ── App Initialization ────────────────────────────────────────────────────────
app = FastAPI(
    title="AutoInsight AI",
    description="AI-powered data analytics platform",
    version="2.0.0"
)

# ── ✅ AUTO CREATE TABLES (FIX FOR RENDER) ─────────────────────────────────────
@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)

# ── CORS Configuration ────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ In production, restrict to your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global Exception Handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "message": "Internal server error"
        }
    )

# ── Import Routers ────────────────────────────────────────────────────────────
from app.api import auth, datasets, analysis, chat, history, downloads

# Optional routers (safe import)
try:
    from app.api import dashboard
except ImportError:
    dashboard = None

try:
    from app.api import query as query_api
except ImportError:
    query_api = None

# ── Register Routers ──────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(datasets.router)
app.include_router(analysis.router)
app.include_router(chat.router)
app.include_router(history.router)
app.include_router(downloads.router)

if dashboard:
    app.include_router(dashboard.router)

if query_api:
    app.include_router(query_api.router)

# ── Root Endpoint ─────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "message": "AutoInsight AI API",
        "version": "2.0.0",
        "status": "running"
    }

# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}