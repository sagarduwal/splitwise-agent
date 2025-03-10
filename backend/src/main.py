from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import os

from src.api.routes import router as api_router

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Splitwise Agent API",
    description="A multi-agent service for processing receipts and interacting with Splitwise",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )
