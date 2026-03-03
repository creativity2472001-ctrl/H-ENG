# main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import time
import os

from ai_engine import AIEngine
from math_engine import MathEngine

# ========== تهيئة التطبيق ==========
app = FastAPI(title="ذكي ماتك - النسخة المبسطة")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ========== المحركات ==========
ai_engine = AIEngine()
math_engine = MathEngine()

@app.on_event("startup")
async def startup():
    print("\n" + "="*60)
    print("🚀 ذكي ماتك - النسخة المبسطة")
    print("="*60)
    await ai_engine.start()
    print(f"📍 http://127.0.0.1:8000")
    print("="*60 + "\n")

@app.on_event("shutdown")
async def shutdown():
    await ai_engine.stop()
    await math_engine.shutdown()

@app.get("/", response_class=HTMLResponse)
async def root():
    """الصفحة الرئيسية"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>ذكي ماتك</h1><p>ملف الواجهة غير موجود</p>")

@app.post("/solve")
async def solve(request: Request):
    """حل أي مسألة رياضية"""
    start_time = time.time()
    
    try:
        data = await request.json()
        question = data.get('question', '').strip()
        
        if not question:
            return {
                "success": False,
                "error": "السؤال فارغ",
                "time": time.time() - start_time
            }
        
        # 1. AI Engine يحول السؤال لكود
        ai_result = await ai_engine.generate_code(question)
        
        if not ai_result.get("success"):
            return {
                "success": False,
                "error": ai_result.get("error", "فشل في توليد الكود"),
                "time": time.time() - start_time
            }
        
        # 2. Math Engine ينفذ الكود
        math_result = await math_engine.execute(ai_result["code"])
        
        # 3. تجهيز النتيجة
        response = {
            "success": math_result.success,
            "result": math_result.result_str if math_result.success else "",
            "steps": [s.to_dict() for s in math_result.steps] if math_result.success else [],
            "model": ai_result.get("model", "ai"),
            "time": time.time() - start_time
        }
        
        if not math_result.success:
            response["error"] = math_result.error
        
        return response
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "time": time.time() - start_time
        }

@app.get("/health")
async def health():
    """فحص صحة الخادم"""
    return {
        "status": "healthy",
        "time": time.time()
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
