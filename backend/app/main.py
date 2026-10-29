import os
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

# Path to built React frontend directory
frontend_dist_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")

# Clean favicon handler to prevent 404 log clutter
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = os.path.join(frontend_dist_path, "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return Response(status_code=204)

# Serve React static build assets and fallback routing
if os.path.exists(frontend_dist_path):
    assets_path = os.path.join(frontend_dist_path, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        index_file = os.path.join(frontend_dist_path, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"status": "ok", "message": "AI Interview Generator Backend is running"}
else:
    @app.get("/")
    def health_check():
        return {"status": "ok", "message": "AI Interview Generator Backend is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)