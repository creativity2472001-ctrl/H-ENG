# === ملف main.py بسيط جداً ومكتمل للاختبار ===

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time
import os # <-- إضافة مهمة

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- الخادم الخلفي (Backend) ---
@app.post("/solve")
async def solve_for_test(request: Request):
    print(">>> TEST SERVER: Received a POST request! Sending back a success response.")
    return {
        "success": True,
        "request_id": "test-id",
        "timestamp": time.time(),
        "execution_time": 0.1,
        "result": "نجح الاختبار!",
        "result_latex": "Success!",
        "steps": [{"text": "الخادم يعمل بشكل صحيح", "latex": ""}],
        "model": "test-mode",
        "domain": "general",
        "from_cache": False,
        "status": "success"
    }

# --- الواجهة الأمامية (Frontend) ---
# ✅✅✅ هذه هي الدالة التي كانت مفقودة ✅✅✅
@app.get("/", response_class=HTMLResponse)
async def get_root():
    # سنقرأ ملف index.html الحقيقي بدلاً من كتابته هنا
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: index.html not found!</h1>")


# --- التشغيل ---
if __name__ == "__main__":
    print(">>> Starting VERY SIMPLE TEST server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
