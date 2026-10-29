import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response

from app.config import settings
from app.api.routes import router as api_router

app = FastAPI(
    title="AI Interview Question Generator API",
    description="Backend API powered by Gemini for technical interview question generation",
    version="1.0.0"
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routes
app.include_router(api_router, prefix="/api")

# Determine absolute path to frontend/dist directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"

# Clean favicon handler
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_file = FRONTEND_DIST / "favicon.ico"
    if favicon_file.exists():
        return FileResponse(favicon_file)
    return Response(status_code=204)

# Serve React static assets
assets_dir = FRONTEND_DIST / "assets"
if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

# Catch-all route to serve React index.html for all frontend pages
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    index_file = FRONTEND_DIST / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "status": "ok",
        "message": "Backend running, but frontend/dist/index.html was not found.",
        "expected_path": str(index_file)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)