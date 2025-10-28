from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.endpoints import legal_analysis

app = FastAPI(
    title="UAE Legal Agent API",
    description="AI-powered legal analysis for UAE law",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(legal_analysis.router)


@app.get("/")
async def root():
    return {
        "message": "UAE Legal Agent API",
        "version": "0.1.0",
        "docs": "/docs"
    }