from fastapi import FastAPI
from routers.openai_compatible import router as openai_router

app = FastAPI()

app.include_router(openai_router, prefix="/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
