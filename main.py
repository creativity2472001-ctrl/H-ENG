# main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import time
import os

from ai_solver import AISolver
from math_solver import MathSolver
from config import HOST, PORT

# ========== التهيئة ==========
app = FastAPI(title="ذكي ماتك")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ========== المحركات ==========
ai_solver = AISolver()
math_solver = MathSolver()

# ========== المسارات ==========
@app.get("/", response_class=HTMLResponse)
async def root():
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except:
        return HTMLResponse(content="<h1>ذكي ماتك</h1>")

@app.post("/solve")
async def solve(request: Request):
    """
    نقطة نهاية واحدة لكل شيء
    يقرر تلقائياً هل يستخدم AI أم لا
    """
    start = time.time()
    data = await request.json()
    question = data.get('question', '').strip()
    
    if not question:
        return {
            "success": False,
            "error": "السؤال فارغ",
            "time": time.time() - start
        }
    
    # 1. محاولة حل المسائل البسيطة (آلة حاسبة)
    if self._is_simple_math(question):
        result = self._solve_simple(question)
        result["time"] = time.time() - start
        return result
    
    # 2. استخدام AI للمسائل المعقدة
    ai_result = await ai_solver.solve(question)
    ai_result["time"] = time.time() - start
    return ai_result

def _is_simple_math(self, q: str) -> bool:
    """هل هي مسألة حسابية بسيطة؟"""
    q = q.replace(" ", "")
    return all(c in "0123456789+-*/()" for c in q)

def _solve_simple(self, q: str) -> dict:
    """حل مسألة حسابية بسيطة"""
    try:
        # تقييم آمن
        result = eval(q, {"__builtins__": {}})
        return {
            "success": True,
            "result": str(result),
            "steps": [{"text": f"{q} = {result}"}],
            "model": "calculator"
        }
    except:
        return {
            "success": False,
            "error": "تعبير غير صحيح"
        }

@app.get("/health")
async def health():
    return {"status": "healthy", "time": time.time()}

# ========== التشغيل ==========
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 ذكي ماتك - النسخة المبسطة")
    print("="*50)
    print(f"📍 http://{HOST}:{PORT}")
    print("="*50 + "\n")
    
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True
    )
