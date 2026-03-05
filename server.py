# server.py - خادم API للواجهة
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from pathlib import Path

from calculator import Calculator

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

calc = Calculator()
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

class ExpressionRequest(BaseModel):
    expression: str

@app.post("/calculate")
async def calculate(data: ExpressionRequest):
    try:
        result = calc.calculate(data.expression)
        return {"success": True, "result": str(result)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return FileResponse(str(static_dir / "index.html"))

if __name__ == "__main__":
    print("="*50)
    print("🚀 تشغيل خادم API للآلة الحاسبة")
    print(f"📍 http://127.0.0.1:8000")
    print("="*50)
    uvicorn.run(app, host="127.0.0.1", port=8000)
