from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import traceback
import os

# ✅ DB
from app.database import engine
from app.models import Base

# ✅ Alembic
from alembic import command
from alembic.config import Config

# ── App Initialization ────────────────────────────────────────────────────────
app = FastAPI(
    title="AutoInsight AI",
    description="AI-powered data analytics platform",
    version="2.0.0"
)

# ── ✅ AUTO MIGRATION (PRODUCTION SAFE) ───────────────────────────────────────
@app.on_event("startup")
def run_migrations():
    try:
        # Path to alembic.ini
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        alembic_path = os.path.join(base_dir, "alembic.ini")

        alembic_cfg = Config(alembic_path)
        command.upgrade(alembic_cfg, "head")

        print("✅ Alembic migrations applied successfully")

    except Exception as e:
        print("⚠️ Alembic migration failed:", e)

    # 🔥 FALLBACK (IMPORTANT — DO NOT REMOVE NOW)
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tables ensured via SQLAlchemy")
    except Exception as e:
        print("❌ Table creation failed:", e)

# ── CORS Configuration ────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ change later to your Vercel URL
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

# Optional routers
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