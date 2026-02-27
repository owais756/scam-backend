from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import scam_routes

app = FastAPI(title="AI Scam Detection System")

# CORS middleware 
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://scam-network-detection-system.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scam_routes.router)

@app.get("/")
def home():
    return {"status": "Scam Detection API Running"}