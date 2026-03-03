# main.py - النسخة النهائية المستقرة (v1.0.0)
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
                return cls(description=data.get("description", ""), latex=data.get("latex", ""))
            elif isinstance(step, tuple) and len(step) == 2:
                return cls(description=str(step[0]), latex=str(step[1]))
            elif isinstance(step, dict):
                return cls(description=step.get("description", ""), latex=step.get("latex", ""))
            else:
                return cls(description=str(step), latex="")
        except Exception as e:
            return cls(description=f"خطأ في تحويل الخطوة: {str(e)}", latex="")
    
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
    
    # بدء تشغيل المحركات (مع معالجة الأخطاء)
    try:
        # AI Engine start
        if hasattr(app.state.ai_engine, 'start') and callable(app.state.ai_engine.start):
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
        # Math Engine start - نتحقق أولاً
        if hasattr(app.state.math_engine, 'start') and callable(app.state.math_engine.start):
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
    
    yield  # التطبيق يعمل هنا
    
    # ========== إيقاف التشغيل وتنظيف الموارد ==========
    print("\n🛑 جاري إيقاف التشغيل وتنظيف الموارد...")
    
    # إيقاف AI Engine
    try:
        if hasattr(app.state.ai_engine, 'stop') and callable(app.state.ai_engine.stop):
            if asyncio.iscoroutinefunction(app.state.ai_engine.stop):
                await app.state.ai_engine.stop()
            else:
                app.state.ai_engine.stop()
            print("✅ AI Engine تم إيقافه")
    except Exception as e:
        print(f"⚠️ خطأ في إيقاف AI Engine: {e}")
    
    # إيقاف Math Engine (مع التحقق من جميع الاحتمالات)
    try:
        # التحقق من shutdown أولاً
        if hasattr(app.state.math_engine, 'shutdown') and callable(app.state.math_engine.shutdown):
            if asyncio.iscoroutinefunction(app.state.math_engine.shutdown):
                await app.state.math_engine.shutdown()
            else:
                app.state.math_engine.shutdown()
            print("✅ Math Engine تم إيقافه (shutdown)")
        # ثم التحقق من stop
        elif hasattr(app.state.math_engine, 'stop') and callable(app.state.math_engine.stop):
            if asyncio.iscoroutinefunction(app.state.math_engine.stop):
                await app.state.math_engine.stop()
            else:
                app.state.math_engine.stop()
            print("✅ Math Engine تم إيقافه (stop)")
        else:
            print("✅ Math Engine لا يحتاج إيقاف")
    except Exception as e:
        print(f"⚠️ خطأ في إيقاف Math Engine: {e}")
    
    print("✅ تم تنظيف جميع الموارد")
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

# ========== الصفحة الرئيسية المحسنة ==========
@app.get("/", response_class=HTMLResponse)
async def root():
    """عرض واجهة المستخدم مع عرض التحذيرات إن وجدت"""
    try:
        # محاولة قراءة ملف index.html
        index_file = "static/index.html"
        if os.path.exists(index_file):
            with open(index_file, "r", encoding="utf-8") as f:
                content = f.read()
                content = content.replace("{{VERSION}}", VERSION)
                # إضافة التحذيرات إن وجدت
                if hasattr(app.state, 'warnings') and app.state.warnings:
                    warnings_html = '<div class="warnings"><h4>⚠️ تحذيرات:</h4><ul>'
                    for w in app.state.warnings:
                        warnings_html += f'<li>{w}</li>'
                    warnings_html += '</ul></div>'
                    content = content.replace("{{WARNINGS}}", warnings_html)
                return HTMLResponse(content=content)
        
        # صفحة افتراضية محسنة
        warnings_html = ""
        if hasattr(app.state, 'warnings') and app.state.warnings:
            warnings_html = '<div style="background: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; margin-bottom: 20px;">'
            warnings_html += '<h4>⚠️ تحذيرات:</h4><ul>'
            for w in app.state.warnings:
                warnings_html += f'<li>{w}</li>'
            warnings_html += '</ul></div>'
        
        html = f"""
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{APP_NAME}</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 20px;
                }}
                .container {{ 
                    max-width: 800px; 
                    width: 100%;
                    background: white; 
                    padding: 40px; 
                    border-radius: 20px; 
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3); 
                }}
                h1 {{ 
                    color: #333; 
                    font-size: 2.5em;
                    margin-bottom: 10px;
                    text-align: center;
                }}
                .version {{ 
                    color: #666; 
                    margin-bottom: 30px; 
                    text-align: center;
                    font-size: 1.1em;
                }}
                .status {{ 
                    background: #e8f5e9; 
                    color: #2e7d32; 
                    padding: 15px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                    text-align: center;
                    font-weight: bold;
                }}
                .warnings {{
                    background: #fff3cd;
                    color: #856404;
                    padding: 15px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                }}
                .input-group {{
                    margin-bottom: 20px;
                }}
                textarea {{
                    width: 100%;
                    padding: 15px;
                    border: 2px solid #e0e0e0;
                    border-radius: 10px;
                    font-size: 1.1em;
                    font-family: inherit;
                    resize: vertical;
                    transition: border-color 0.3s;
                }}
                textarea:focus {{
                    outline: none;
                    border-color: #667eea;
                }}
                button {{
                    background: #667eea;
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 10px;
                    font-size: 1.2em;
                    cursor: pointer;
                    width: 100%;
                    transition: background 0.3s;
                }}
                button:hover {{
                    background: #5a67d8;
                }}
                button:disabled {{
                    background: #ccc;
                    cursor: not-allowed;
                }}
                .result {{
                    margin-top: 30px;
                    padding: 20px;
                    border: 2px solid #e0e0e0;
                    border-radius: 10px;
                    background: #f9f9f9;
                }}
                .loading {{
                    text-align: center;
                    color: #667eea;
                    font-weight: bold;
                }}
                .error {{
                    color: #dc3545;
                    background: #ffe6e8;
                    padding: 15px;
                    border-radius: 10px;
                }}
                .steps {{
                    margin-top: 20px;
                }}
                .step {{
                    padding: 10px;
                    border-right: 3px solid #667eea;
                    background: white;
                    margin-bottom: 10px;
                    border-radius: 5px;
                }}
                .latex {{
                    font-family: monospace;
                    background: #f1f1f1;
                    padding: 5px;
                    border-radius: 3px;
                }}
                .info {{
                    color: #666;
                    font-size: 0.9em;
                    margin-top: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔧 {APP_NAME}</h1>
                <div class="version">الإصدار {VERSION}</div>
                <div class="status">✅ الخادم يعمل بنجاح</div>
                
                {warnings_html}
                
                <div class="input-group">
                    <textarea id="question" rows="4" placeholder="اكتب سؤالك الرياضي هنا... 
مثال: مشتقة x**2 + 2x
مثال: تكامل sin(x)
مثال: حل x**2 - 4 = 0"></textarea>
                </div>
                
                <button onclick="solve()" id="solveBtn">حل المسألة</button>
                
                <div class="result" id="result" style="display: none;"></div>
                
                <div class="info">
                    <p>💡 أمثلة على الأسئلة:</p>
                    <ul>
                        <li>مشتقة x**2 + 2x</li>
                        <li>تكامل sin(x)</li>
                        <li>حل x**2 - 4 = 0</li>
                        <li>احسب 5 + 3 * 2</li>
                    </ul>
                </div>
            </div>
            
            <script>
                async function solve() {{
                    const question = document.getElementById('question').value;
                    const resultDiv = document.getElementById('result');
                    const solveBtn = document.getElementById('solveBtn');
                    
                    if (!question.trim()) {{
                        alert('الرجاء إدخال سؤال');
                        return;
                    }}
                    
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = '<div class="loading">⏳ جاري المعالجة...</div>';
                    solveBtn.disabled = true;
                    
                    try {{
                        const response = await fetch('/solve', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify({{question: question}})
                        }});
                        
                        const data = await response.json();
                        
                        if (data.success) {{
                            let html = '<h3>✅ النتيجة:</h3>';
                            html += `<p style="font-size: 1.5em; color: #28a745;">${{data.result || 'تم الحل'}}</p>`;
                            
                            if (data.warnings && data.warnings.length > 0) {{
                                html += '<div style="background: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; margin: 10px 0;">';
                                html += '<strong>⚠️ تحذيرات:</strong><ul>';
                                data.warnings.forEach(w => html += `<li>${{w}}</li>`);
                                html += '</ul></div>';
                            }}
                            
                            if (data.steps && data.steps.length > 0) {{
                                html += '<h4>📝 خطوات الحل:</h4><div class="steps">';
                                data.steps.forEach(step => {{
                                    html += '<div class="step">';
                                    html += `<div>${{step.description || 'خطوة'}}</div>`;
                                    if (step.latex) {{
                                        html += `<div class="latex">📐 ${{step.latex}}</div>`;
                                    }}
                                    html += '</div>';
                                }});
                                html += '</div>';
                            }}
                            
                            html += `<p class="info">⏱️ وقت التنفيذ: ${{data.time}} ثانية</p>`;
                            html += `<p class="info">🤖 المحرك: ${{data.model}} ${{data.from_cache ? '(من الذاكرة المؤقتة)' : ''}}</p>`;
                            
                            resultDiv.innerHTML = html;
                        }} else {{
                            resultDiv.innerHTML = `<div class="error">❌ خطأ: ${{data.error || 'حدث خطأ غير متوقع'}}</div>`;
                        }}
                    }} catch (error) {{
                        resultDiv.innerHTML = `<div class="error">❌ خطأ في الاتصال: ${{error.message}}</div>`;
                    }} finally {{
                        solveBtn.disabled = false;
                    }}
                }}
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html)
    except Exception as e:
        return HTMLResponse(content=f"<h1>خطأ في تحميل الصفحة</h1><p>{str(e)}</p>")

# ========== نقطة نهاية حل المسائل (محسنة بالكامل) ==========
@app.post("/solve", response_model=SolveResponse)
async def solve(request: SolveRequest):
    """حل أي مسألة رياضية مع معالجة شاملة للأخطاء والتحذيرات"""
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
        
        # 1. AI Engine يولد الكود (مع معالجة آمنة)
        ai_result = None
        try:
            # التحقق من وجود الدالة
            if not hasattr(app.state.ai_engine, 'generate_code'):
                return SolveResponse(
                    success=False,
                    error="AI Engine لا يدعم توليد الكود",
                    time=round(time.time() - start_time, 4)
                )
            
            # استدعاء الدالة مع timeout
            try:
                ai_result = await asyncio.wait_for(
                    app.state.ai_engine.generate_code(question),
                    timeout=30.0  # 30 ثانية كحد أقصى
                )
            except asyncio.TimeoutError:
                return SolveResponse(
                    success=False,
                    error="انتهت مهلة توليد الكود (30 ثانية)",
                    time=round(time.time() - start_time, 4)
                )
                
        except Exception as e:
            return SolveResponse(
                success=False,
                error=f"فشل في توليد الكود: {str(e)}",
                time=round(time.time() - start_time, 4)
            )
        
        # التحقق من نتيجة AI
        if not ai_result or not isinstance(ai_result, dict):
            return SolveResponse(
                success=False,
                error="نتيجة غير صالحة من AI Engine",
                time=round(time.time() - start_time, 4)
            )
        
        if not ai_result.get("success", False):
            return SolveResponse(
                success=False,
                error=ai_result.get("error", "فشل في توليد الكود"),
                time=round(time.time() - start_time, 4)
            )
        
        # التحقق من وجود الكود
        code = ai_result.get("code")
        if not code:
            warnings.append("تم توليد الكود بنجاح ولكن لا يوجد مخرجات")
        
        # 2. Math Engine ينفذ الكود (مع معالجة آمنة)
        math_result = None
        try:
            # التحقق من وجود الدالة
            if not hasattr(app.state.math_engine, 'execute'):
                return SolveResponse(
                    success=False,
                    error="Math Engine لا يدعم تنفيذ الكود",
                    time=round(time.time() - start_time, 4),
                    warnings=warnings
                )
            
            # تنفيذ الكود مع timeout
            try:
                math_result = await asyncio.wait_for(
                    app.state.math_engine.execute(code if code else ""),
                    timeout=30.0  # 30 ثانية كحد أقصى
                )
            except asyncio.TimeoutError:
                return SolveResponse(
                    success=False,
                    error="انتهت مهلة تنفيذ الكود (30 ثانية)",
                    time=round(time.time() - start_time, 4),
                    warnings=warnings
                )
                
        except Exception as e:
            return SolveResponse(
                success=False,
                error=f"فشل في تنفيذ الكود: {str(e)}",
                time=round(time.time() - start_time, 4),
                warnings=warnings
            )
        
        # تحويل الخطوات بشكل آمن
        steps = []
        if math_result and hasattr(math_result, 'steps') and math_result.steps:
            try:
                for step in math_result.steps:
                    try:
                        steps.append(StepResponse.from_step(step))
                    except Exception as e:
                        warnings.append(f"فشل تحويل خطوة: {str(e)}")
            except Exception as e:
                warnings.append(f"خطأ في معالجة الخطوات: {str(e)}")
        
        # تجهيز الرد النهائي
        response = SolveResponse(
            success=getattr(math_result, 'success', False),
            result=getattr(math_result, 'result_str', None) if math_result else None,
            steps=steps,
            model=ai_result.get("model", "ai"),
            from_cache=ai_result.get("from_cache", False),
            time=round(time.time() - start_time, 4),
            execution_time=round(time.time() - start_time, 4),
            warnings=warnings
        )
        
        # إضافة رسالة الخطأ إن وجدت
        if not response.success and math_result and hasattr(math_result, 'error'):
            response.error = math_result.error
        
        # تسجيل العملية في وضع التصحيح
        if DEBUG:
            print(f"\n📝 سؤال: {question[:100]}...")
            print(f"✅ نجاح: {response.success}, الزمن: {response.time}ث")
            print(f"🤖 المحرك: {response.model}, من الذاكرة: {response.from_cache}")
            if warnings:
                print(f"⚠️ تحذيرات: {len(warnings)}")
            
        return response
        
    except Exception as e:
        # معالجة أي أخطاء غير متوقعة
        error_msg = f"خطأ غير متوقع: {str(e)}"
        if DEBUG:
            import traceback
            traceback.print_exc()
        
        return SolveResponse(
            success=False,
            error=error_msg,
            time=round(time.time() - start_time, 4),
            warnings=warnings
        )

# ========== نقطة نهاية فحص الصحة المحسنة ==========
@app.get("/health")
async def health():
    """فحص صحة الخادم والمحركات مع تفاصيل أكثر"""
    try:
        # فحص حالة المحركات بشكل آمن
        ai_engine_status = "unknown"
        math_engine_status = "unknown"
        
        # فحص AI Engine
        if hasattr(app.state, 'ai_engine'):
            if hasattr(app.state.ai_engine, 'ready'):
                ai_engine_status = "ready" if app.state.ai_engine.ready else "not_ready"
            else:
                ai_engine_status = "available"
        
        # فحص Math Engine
        if hasattr(app.state, 'math_engine'):
            if hasattr(app.state.math_engine, 'is_ready'):
                math_engine_status = "ready" if app.state.math_engine.is_ready else "not_ready"
            else:
                math_engine_status = "available"
        
        # حساب وقت التشغيل
        uptime = time.time() - (app.state.start_time if hasattr(app.state, 'start_time') else START_TIME)
        
        # تنسيق وقت التشغيل
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        uptime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        return JSONResponse({
            "status": "healthy",
            "version": VERSION,
            "debug": DEBUG,
            "ai_engine": ai_engine_status,
            "math_engine": math_engine_status,
            "uptime": uptime,
            "uptime_str": uptime_str,
            "timestamp": time.time(),
            "warnings": getattr(app.state, 'warnings', [])
        })
    except Exception as e:
        return JSONResponse({
            "status": "degraded",
            "error": str(e),
            "timestamp": time.time()
        })

# ========== نقطة نهاية الإحصائيات المحسنة ==========
@app.get("/stats")
async def get_stats():
    """الحصول على إحصائيات المحركات بشكل آمن"""
    try:
        stats = {
            "success": True,
            "stats": {
                "uptime": time.time() - (app.state.start_time if hasattr(app.state, 'start_time') else START_TIME),
                "warnings": getattr(app.state, 'warnings', [])
            }
        }
        
        # إحصائيات AI Engine
        if hasattr(app.state, 'ai_engine'):
            try:
                if hasattr(app.state.ai_engine, 'get_stats'):
                    ai_stats = app.state.ai_engine.get_stats()
                    stats["stats"]["ai_engine"] = ai_stats
                elif hasattr(app.state.ai_engine, 'memory'):
                    stats["stats"]["ai_engine"] = {
                        "memory_hits": getattr(app.state.ai_engine.memory.stats, 'hits', 0),
                        "memory_misses": getattr(app.state.ai_engine.memory.stats, 'misses', 0)
                    }
                else:
                    stats["stats"]["ai_engine"] = {"status": "basic_info"}
            except Exception as e:
                stats["stats"]["ai_engine"] = {"error": str(e)}
        
        # إحصائيات Math Engine
        if hasattr(app.state, 'math_engine'):
            try:
                if hasattr(app.state.math_engine, 'get_stats'):
                    math_stats = app.state.math_engine.get_stats()
                    stats["stats"]["math_engine"] = math_stats
                else:
                    stats["stats"]["math_engine"] = {"status": "basic_info"}
            except Exception as e:
                stats["stats"]["math_engine"] = {"error": str(e)}
        
        return JSONResponse(stats)
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        })

# ========== نقطة نهاية الاختبار المحسنة ==========
@app.get("/test")
async def test():
    """صفحة اختبار متكاملة مع عرض التحذيرات"""
    warnings_html = ""
    if hasattr(app.state, 'warnings') and app.state.warnings:
        warnings_html = '<div style="background: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; margin-bottom: 20px;">'
        warnings_html += '<h4>⚠️ تحذيرات التشغيل:</h4><ul>'
        for w in app.state.warnings:
            warnings_html += f'<li>{w}</li>'
        warnings_html += '</ul></div>'
    
    return HTMLResponse(content=f"""
    <html dir="rtl">
        <head>
            <title>اختبار {APP_NAME}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
                .container {{ max-width: 800px; margin: auto; background: white; padding: 30px; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }}
                h1 {{ color: #333; text-align: center; }}
                .endpoints {{ background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0; }}
                .endpoint {{ padding: 10px; border-bottom: 1px solid #ddd; }}
                .endpoint:last-child {{ border-bottom: none; }}
                code {{ background: #e0e0e0; padding: 2px 5px; border-radius: 3px; }}
                .success {{ color: green; font-weight: bold; }}
                .warning {{ color: #856404; background: #fff3cd; padding: 10px; border-radius: 5px; }}
                .info {{ color: #667eea; }}
                .test-section {{ margin-top: 30px; }}
                input, button {{ padding: 10px; margin: 5px; border-radius: 5px; border: 1px solid #ddd; }}
                button {{ background: #667eea; color: white; border: none; cursor: pointer; }}
                button:hover {{ background: #5a67d8; }}
                pre {{ background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🧪 {APP_NAME} - صفحة الاختبار</h1>
                <p class="success">✅ التطبيق يعمل بشكل طبيعي</p>
                
                {warnings_html}
                
                <div class="endpoints">
                    <h3>📌 النقاط المتاحة:</h3>
                    <div class="endpoint"><code>GET  /</code> - الصفحة الرئيسية</div>
                    <div class="endpoint"><code>POST /solve</code> - حل المسائل</div>
                    <div class="endpoint"><code>GET  /health</code> - فحص الصحة</div>
                    <div class="endpoint"><code>GET  /stats</code> - الإحصائيات</div>
                    <div class="endpoint"><code>GET  /test</code> - هذه الصفحة</div>
                </div>
                
                <div class="test-section">
                    <h3>🔧 اختبار سريع:</h3>
                    <form id="testForm">
                        <input type="text" id="testQuestion" placeholder="اكتب سؤالك هنا" 
                               style="width: 70%;" value="مشتقة x**2 + 2x">
                        <button type="submit">حل</button>
                    </form>
                    
                    <div id="testResult" style="margin-top: 20px;"></div>
                </div>
                
                <div class="test-section">
                    <h3>📊 أمثلة جاهزة:</h3>
                    <button onclick="setExample('مشتقة x**3 + 2x**2 - 5x')">مشتقة</button>
                    <button onclick="setExample('تكامل sin(x)')">تكامل</button>
                    <button onclick="setExample('حل x**2 - 4 = 0')">معادلة</button>
                    <button onclick="setExample('5 + 3 * 2')">آلة حاسبة</button>
                </div>
            </div>
            
            <script>
                function setExample(text) {{
                    document.getElementById('testQuestion').value = text;
                }}
                
                document.getElementById('testForm').onsubmit = async (e) => {{
                    e.preventDefault();
                    const question = document.getElementById('testQuestion').value;
                    const resultDiv = document.getElementById('testResult');
                    
                    if (!question.trim()) {{
                        alert('الرجاء إدخال سؤال');
                        return;
                    }}
                    
                    resultDiv.innerHTML = '<p class="info">⏳ جاري المعالجة...</p>';
                    
                    try {{
                        const response = await fetch('/solve', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify({{question: question}})
                        }});
                        const data = await response.json();
                        resultDiv.innerHTML = '<pre style="white-space: pre-wrap; text-align: left;">' + JSON.stringify(data, null, 2) + '</pre>';
                    }} catch (error) {{
                        resultDiv.innerHTML = '<p style="color: red;">❌ خطأ: ' + error.message + '</p>';
                    }}
                }};
            </script>
        </body>
    </html>
    """)

# ========== معالج الأخطاء العام المحسن ==========
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """معالجة موحدة لجميع الأخطاء غير المتوقعة مع تتبع أفضل"""
    error_id = abs(hash(str(exc))) % 10000
    error_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # تسجيل الخطأ
    print(f"\n❌ خطأ عام {error_id} في {error_time}")
    print(f"📌 المسار: {request.url.path}")
    print(f"📝 الخطأ: {str(exc)}")
    
    if DEBUG:
        import traceback
        print("🔍 تتبع الخطأ:")
        traceback.print_exc()
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": f"خطأ داخلي في الخادم (ID: {error_id})",
            "detail": str(exc) if DEBUG else None,
            "path": request.url.path,
            "timestamp": error_time
        }
    )

# ========== نقطة نهاية للمسارات غير الموجودة ==========
@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def not_found_handler(request: Request, path_name: str):
    """معالجة المسارات غير الموجودة"""
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": f"المسار '{path_name}' غير موجود",
            "available_endpoints": ["/", "/solve", "/health", "/stats", "/test"],
            "method": request.method
        }
    )

# ========== تشغيل الخادم ==========
if __name__ == "__main__":
    print("\n" + "="*60)
    print(f"🚀 تشغيل {APP_NAME}")
    print("="*60)
    print(f"📍 المضيف: {HOST}")
    print(f"🔌 المنفذ: {PORT}")
    print(f"🔄 إعادة التشغيل التلقائي: {'نعم' if RELOAD else 'لا'}")
    print(f"⚙️  عدد العمال: {WORKERS}")
    print(f"🔧 وضع التصحيح: {'مفعل' if DEBUG else 'معطل'}")
    print(f"🌐 النطاقات المسموحة: {ALLOWED_ORIGINS}")
    print("="*60 + "\n")
    
    # تشغيل الخادم
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
        workers=WORKERS,
        log_level="debug" if DEBUG else "info"
    )
