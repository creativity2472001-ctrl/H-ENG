# main.py - الإصدار النهائي المتوافق (v1.0.0)
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import time
import os
import asyncio
from typing import Optional, Dict, Any, List, Union
from contextlib import asynccontextmanager
from datetime import datetime
from pydantic import BaseModel

from ai_engine import AIEngine
from math_engine import MathEngine

# ========== إعدادات التطبيق ==========
APP_NAME = "ذكي ماتك - مساعد المهندس"
VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
RELOAD = DEBUG and os.getenv("RELOAD", "True").lower() == "true"
WORKERS = int(os.getenv("WORKERS", "1"))
START_TIME = time.time()

# ========== نماذج البيانات ==========
class SolveRequest(BaseModel):
    question: str
    
class StepResponse(BaseModel):
    description: str
    latex: str = ""
    
    @classmethod
    def from_step(cls, step: Any) -> "StepResponse":
        """تحويل أي صيغة خطوة إلى StepResponse"""
        try:
            if hasattr(step, 'to_dict'):
                data = step.to_dict()
                return cls(
                    description=data.get("text", data.get("description", "")), 
                    latex=data.get("latex", "")
                )
            elif isinstance(step, tuple) and len(step) == 2:
                return cls(description=str(step[0]), latex=str(step[1]))
            elif isinstance(step, dict):
                return cls(
                    description=step.get("text", step.get("description", "")), 
                    latex=step.get("latex", "")
                )
            else:
                return cls(description=str(step), latex="")
        except Exception as e:
            return cls(description=f"⚠️ خطأ في تحويل الخطوة: {str(e)}", latex="")
    
class SolveResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    steps: List[StepResponse] = []
    model: str = "unknown"
    time: float
    error: Optional[str] = None
    from_cache: bool = False
    execution_time: Optional[float] = None
    warnings: List[str] = []

# ========== إدارة دورة حياة التطبيق ==========
@asynccontextmanager
async def lifespan(app: FastAPI):
    """إدارة بدء وإيقاف التطبيق بشكل آمن مع معالجة الأخطاء"""
    print("\n" + "="*60)
    print(f"🚀 {APP_NAME} v{VERSION}")
    print("="*60)
    
    # تهيئة المحركات
    app.state.ai_engine = AIEngine()
    app.state.math_engine = MathEngine()
    app.state.start_time = time.time()
    app.state.warnings = []
    
    # بدء تشغيل المحركات
    try:
        if hasattr(app.state.ai_engine, 'start'):
            if asyncio.iscoroutinefunction(app.state.ai_engine.start):
                await app.state.ai_engine.start()
            else:
                app.state.ai_engine.start()
        print("✅ AI Engine جاهز")
    except Exception as e:
        warning = f"⚠️ تحذير: AI Engine start فشل: {e}"
        print(warning)
        app.state.warnings.append(warning)
    
    try:
        if hasattr(app.state.math_engine, 'start'):
            if asyncio.iscoroutinefunction(app.state.math_engine.start):
                await app.state.math_engine.start()
            else:
                app.state.math_engine.start()
            print("✅ Math Engine جاهز (مع start)")
        else:
            print("✅ Math Engine جاهز (بدون start)")
    except Exception as e:
        warning = f"⚠️ تحذير: Math Engine start فشل: {e}"
        print(warning)
        app.state.warnings.append(warning)
    
    print(f"📍 http://{HOST}:{PORT}")
    print(f"🔧 وضع التصحيح: {'مفعل' if DEBUG else 'معطل'}")
    if app.state.warnings:
        print("⚠️ تحذيرات:")
        for w in app.state.warnings:
            print(f"  {w}")
    print("="*60 + "\n")
    
    yield
    
    # ========== إيقاف التشغيل ==========
    print("\n🛑 جاري إيقاف التشغيل...")
    
    try:
        if hasattr(app.state.ai_engine, 'stop'):
            if asyncio.iscoroutinefunction(app.state.ai_engine.stop):
                await app.state.ai_engine.stop()
            else:
                app.state.ai_engine.stop()
        print("✅ AI Engine تم إيقافه")
    except Exception as e:
        print(f"⚠️ خطأ في إيقاف AI Engine: {e}")
    
    try:
        if hasattr(app.state.math_engine, 'shutdown'):
            if asyncio.iscoroutinefunction(app.state.math_engine.shutdown):
                await app.state.math_engine.shutdown()
            else:
                app.state.math_engine.shutdown()
            print("✅ Math Engine تم إيقافه")
        elif hasattr(app.state.math_engine, 'stop'):
            if asyncio.iscoroutinefunction(app.state.math_engine.stop):
                await app.state.math_engine.stop()
            else:
                app.state.math_engine.stop()
            print("✅ Math Engine تم إيقافه")
        else:
            print("ℹ️ Math Engine لا يحتاج إيقاف")
    except Exception as e:
        print(f"⚠️ خطأ في إيقاف Math Engine: {e}")
    
    print("✅ تم إيقاف التشغيل")
    print("="*60 + "\n")

# ========== تهيئة التطبيق ==========
app = FastAPI(
    title=APP_NAME,
    version=VERSION,
    debug=DEBUG,
    lifespan=lifespan
)

# ========== إعداد CORS ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== المجلدات الثابتة ==========
os.makedirs("static", exist_ok=True)
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception as e:
    print(f"⚠️ تحذير: فشل تحميل المجلد الثابت: {e}")

# ✅ تحسين: نقطة نهاية للصفحة الرئيسية
@app.get("/", response_class=HTMLResponse)
async def root():
    """الصفحة الرئيسية"""
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{APP_NAME}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
            .container {{ max-width: 800px; margin: auto; background: white; padding: 30px; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }}
            h1 {{ color: #333; text-align: center; margin-bottom: 20px; }}
            .version {{ color: #666; text-align: center; margin-bottom: 30px; }}
            .status {{ background: #e8f5e9; color: #2e7d32; padding: 15px; border-radius: 10px; margin-bottom: 20px; text-align: center; }}
            textarea {{ width: 100%; padding: 15px; border: 2px solid #e0e0e0; border-radius: 10px; font-size: 1.1em; margin-bottom: 20px; resize: vertical; }}
            button {{ background: #667eea; color: white; border: none; padding: 15px 30px; border-radius: 10px; font-size: 1.2em; cursor: pointer; width: 100%; }}
            button:hover {{ background: #5a67d8; }}
            .result {{ margin-top: 20px; padding: 20px; border-radius: 10px; background: #f5f5f5; }}
            .error {{ color: #dc3545; background: #ffe6e8; padding: 15px; border-radius: 10px; }}
            .step {{ padding: 10px; border-right: 3px solid #667eea; background: white; margin: 10px 0; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔧 {APP_NAME}</h1>
            <div class="version">الإصدار {VERSION}</div>
            <div class="status">✅ الخادم يعمل بنجاح</div>
            
            <textarea id="question" rows="4" placeholder="اكتب سؤالك الرياضي هنا..."></textarea>
            <button onclick="solve()">حل المسألة</button>
            
            <div id="result" class="result" style="display: none;"></div>
        </div>

        <script>
            async function solve() {{
                const question = document.getElementById('question').value;
                const resultDiv = document.getElementById('result');
                
                if (!question.trim()) {{
                    alert('الرجاء إدخال سؤال');
                    return;
                }}
                
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '<p>⏳ جاري المعالجة...</p>';
                
                try {{
                    const response = await fetch('/solve', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{question: question}})
                    }});
                    const data = await response.json();
                    
                    if (data.success) {{
                        let html = '<h3>✅ النتيجة:</h3>';
                        html += `<p style="font-size: 1.2em;">${{data.result || 'تم الحل'}}</p>`;
                        
                        if (data.steps && data.steps.length > 0) {{
                            html += '<h4>📝 خطوات الحل:</h4>';
                            data.steps.forEach(step => {{
                                html += '<div class="step">';
                                html += `<div>${{step.description}}</div>`;
                                if (step.latex) {{
                                    html += `<div style="font-family: monospace;">📐 ${{step.latex}}</div>`;
                                }}
                                html += '</div>';
                            }});
                        }}
                        
                        html += `<p style="color: #666;">⏱️ وقت التنفيذ: ${{data.time}} ثانية</p>`;
                        html += `<p style="color: #666;">🤖 المحرك: ${{data.model}}</p>`;
                        
                        resultDiv.innerHTML = html;
                    }} else {{
                        resultDiv.innerHTML = `<div class="error">❌ خطأ: ${{data.error || 'حدث خطأ'}}</div>`;
                    }}
                }} catch (error) {{
                    resultDiv.innerHTML = `<div class="error">❌ خطأ في الاتصال: ${{error.message}}</div>`;
                }}
            }}
        </script>
    </body>
    </html>
    """)

# ========== ✅ نقطة نهاية حل المسائل (متوافقة مع التعديلات) ==========
@app.post("/solve", response_model=SolveResponse)
async def solve(request: SolveRequest):
    """حل أي مسألة رياضية"""
    start_time = time.time()
    warnings = []
    
    try:
        question = request.question.strip()
        
        if not question:
            return SolveResponse(
                success=False,
                error="السؤال فارغ",
                time=round(time.time() - start_time, 4)
            )
        
        # ✅ 1. AI Engine يولد الكود
        try:
            ai_result = await asyncio.wait_for(
                app.state.ai_engine.generate_code(question),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            return SolveResponse(
                success=False,
                error="انتهت مهلة توليد الكود",
                time=round(time.time() - start_time, 4)
            )
        
        if not ai_result or not ai_result.get("success"):
            return SolveResponse(
                success=False,
                error=ai_result.get("error", "فشل في توليد الكود"),
                time=round(time.time() - start_time, 4)
            )
        
        # ✅ 2. Math Engine ينفذ الكود
        code = ai_result.get("code")
        if not code:
            warnings.append("تم توليد الكود ولكن لا يوجد مخرجات")
        
        try:
            math_result = await asyncio.wait_for(
                app.state.math_engine.execute(code if code else ""),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            return SolveResponse(
                success=False,
                error="انتهت مهلة تنفيذ الكود",
                time=round(time.time() - start_time, 4)
            )
        
        # ✅ 3. تحويل الخطوات
        steps = []
        if math_result and hasattr(math_result, 'steps'):
            for step in math_result.steps:
                steps.append(StepResponse.from_step(step))
        
        # ✅ 4. تجهيز الرد
        return SolveResponse(
            success=math_result.success if math_result else False,
            result=math_result.result_str if math_result and math_result.success else None,
            steps=steps,
            model=ai_result.get("model", "ai"),
            from_cache=ai_result.get("from_cache", False),
            time=round(time.time() - start_time, 4),
            execution_time=round(time.time() - start_time, 4),
            error=math_result.error if math_result and not math_result.success else None,
            warnings=warnings
        )
        
    except Exception as e:
        if DEBUG:
            import traceback
            traceback.print_exc()
        
        return SolveResponse(
            success=False,
            error=f"خطأ غير متوقع: {str(e)}",
            time=round(time.time() - start_time, 4),
            warnings=warnings
        )

# ========== نقطة نهاية فحص الصحة ==========
@app.get("/health")
async def health():
    """فحص صحة الخادم"""
    uptime = time.time() - (app.state.start_time if hasattr(app.state, 'start_time') else START_TIME)
    
    return JSONResponse({
        "status": "healthy",
        "version": VERSION,
        "debug": DEBUG,
        "uptime": round(uptime, 2),
        "timestamp": time.time()
    })

# ========== نقطة نهاية الإحصائيات ==========
@app.get("/stats")
async def get_stats():
    """إحصائيات المحركات"""
    stats = {
        "success": True,
        "stats": {
            "uptime": time.time() - (app.state.start_time if hasattr(app.state, 'start_time') else START_TIME)
        }
    }
    
    # إحصائيات AI Engine
    if hasattr(app.state.ai_engine, 'get_stats'):
        stats["stats"]["ai_engine"] = app.state.ai_engine.get_stats()
    
    # إحصائيات Math Engine
    if hasattr(app.state.math_engine, 'get_stats'):
        stats["stats"]["math_engine"] = app.state.math_engine.get_stats()
    
    return JSONResponse(stats)

# ========== نقطة نهاية الاختبار ==========
@app.get("/test")
async def test():
    """صفحة اختبار بسيطة"""
    return HTMLResponse(content=f"""
    <html dir="rtl">
    <head><title>اختبار {APP_NAME}</title></head>
    <body style="font-family: Arial; margin: 40px;">
        <h1>🧪 صفحة اختبار {APP_NAME}</h1>
        <p>✅ التطبيق يعمل بشكل طبيعي</p>
        <ul>
            <li><a href="/">الصفحة الرئيسية</a></li>
            <li><a href="/health">فحص الصحة</a></li>
            <li><a href="/stats">الإحصائيات</a></li>
        </ul>
    </body>
    </html>
    """)

# ========== معالج الأخطاء العام ==========
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_id = abs(hash(str(exc))) % 10000
    
    if DEBUG:
        import traceback
        traceback.print_exc()
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": f"خطأ داخلي (ID: {error_id})",
            "detail": str(exc) if DEBUG else None
        }
    )

# ========== معالج المسارات غير الموجودة ==========
@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def not_found_handler(path_name: str):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": f"المسار '{path_name}' غير موجود"
        }
    )

# ========== تشغيل الخادم ==========
if __name__ == "__main__":
    print("\n" + "="*60)
    print(f"🚀 تشغيل {APP_NAME}")
    print("="*60)
    print(f"📍 http://{HOST}:{PORT}")
    print(f"🔧 وضع التصحيح: {'مفعل' if DEBUG else 'معطل'}")
    print("="*60 + "\n")
    
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
        workers=WORKERS,
        log_level="debug" if DEBUG else "info"
    )
