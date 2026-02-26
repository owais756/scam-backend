from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import scam_routes

app = FastAPI(title="AI Scam Detection System")

# ✅ CORS middleware add karo
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5175"
    ],  # frontend ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(scam_routes.router)

@app.get("/")
def home():
    return {"status": "Scam Detection API Running"}