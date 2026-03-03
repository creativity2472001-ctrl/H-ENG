# === ملف main.py بسيط جداً للاختبار فقط ===

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/solve")
async def solve_for_test(request: Request):
    print(">>> TEST SERVER: Received a request! Sending back a success response.")
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

if __name__ == "__main__":
    print(">>> Starting VERY SIMPLE TEST server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
