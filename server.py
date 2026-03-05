# server.py - خادم الويب (معدل)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from pathlib import Path
import re
import math

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
        expr = data.expression.lower().strip()
        
        # ===== 1. التعامل مع الدوال المثلثية =====
        # sin(30)
        if 'sin' in expr and '(' in expr and ')' in expr:
            match = re.search(r'sin\((\d+)\)', expr)
            if match:
                angle = float(match.group(1))
                result = calc.sin(angle)  # calc.sin تحول الدرجات إلى راديان
                return {"success": True, "result": str(result)}
        
        # cos(60)
        if 'cos' in expr and '(' in expr and ')' in expr:
            match = re.search(r'cos\((\d+)\)', expr)
            if match:
                angle = float(match.group(1))
                result = calc.cos(angle)
                return {"success": True, "result": str(result)}
        
        # tan(45)
        if 'tan' in expr and '(' in expr and ')' in expr:
            match = re.search(r'tan\((\d+)\)', expr)
            if match:
                angle = float(match.group(1))
                result = calc.tan(angle)
                return {"success": True, "result": str(result)}
        
        # ===== 2. التعامل مع ln =====
        if 'ln' in expr and '(' in expr and ')' in expr:
            match = re.search(r'ln\((\d+)\)', expr)
            if match:
                num = float(match.group(1))
                result = calc.ln(num)
                return {"success": True, "result": str(result)}
        
        # ===== 3. التعامل مع المعادلات (تحتوي على =) =====
        if '=' in expr:
            result = calc.solve_equation(expr)
            return {"success": True, "result": str(result)}
        
        # ===== 4. العمليات الحسابية العادية =====
        result = calc.calculate(expr)
        return {"success": True, "result": str(result)}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/")
async def root():
    return FileResponse(str(static_dir / "index.html"))

if __name__ == "__main__":
    print("="*50)
    print("🚀 تشغيل خادم الويب")
    print(f"📍 http://127.0.0.1:8000")
    print("="*50)
    uvicorn.run(app, host="127.0.0.1", port=8000)
