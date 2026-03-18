from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, images

app = FastAPI(
    title="InfraSight Gateway",
    description="API Gateway for InfraSight infrared target detection platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(images.router, prefix="/images", tags=["Images"])


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "gateway"}
