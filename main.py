# main.py - الإصدار النهائي الكامل مع جميع التحسينات (v1.0.0)
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

# ========== إعدادات من config.py (مدمجة) ==========
# مفاتيح API - تأتي من متغيرات البيئة فقط!
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# تحذيرات إذا كانت المفاتيح فارغة (تنبيه فقط، لا يمنع التشغيل)
if not GROQ_API_KEY:
    print("⚠️ تحذير: GROQ_API_KEY غير موجودة - خدمة Groq غير متاحة")
if not GEMINI_API_KEY:
    print("⚠️ تحذير: GEMINI_API_KEY غير موجودة - خدمة Gemini غير متاحة")
if not OPENROUTER_API_KEY:
    print("⚠️ تحذير: OPENROUTER_API_KEY غير موجودة")

# إعدادات إضافية
MAX_CODE_LENGTH = 5000      # أقصى طول للكود المسموح به
CACHE_TTL = 3600            # مدة التخزين المؤقت بالثواني (ساعة واحدة)

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
            elif isinstance(step, tuple) and len(step) == 3:
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
    time: float  # الوقت الإجمالي للعملية
    error: Optional[str] = None
    from_cache: bool = False
    warnings: List[str] = []
    ai_error: Optional[str] = None
    math_error: Optional[str] = None

# ========== إدارة دورة حياة التطبيق ==========
@asynccontextmanager
async def lifespan(app: FastAPI):
    """إدارة بدء وإيقاف التطبيق بشكل آمن مع معالجة الأخطاء"""
    print("\n" + "="*60)
    print(f"🚀 {APP_NAME} v{VERSION}")
    print("="*60)
    
    # تمرير المفاتيح إلى AIEngine عند التهيئة
    # سيتم استخدامها من متغيرات البيئة داخل ai_engine.py
    
    # تهيئة المحركات
    app.state.ai_engine = AIEngine()
    app.state.math_engine = MathEngine()
    app.state.start_time = time.time()
    app.state.warnings = []
    
    # إضافة تحذيرات المفاتيح إلى حالة التطبيق
    if not GROQ_API_KEY:
        app.state.warnings.append("GROQ_API_KEY غير موجودة - خدمة Groq غير متاحة")
    if not GEMINI_API_KEY:
        app.state.warnings.append("GEMINI_API_KEY غير موجودة - خدمة Gemini غير متاحة")
    
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
    print(f"📏 أقصى طول للكود: {MAX_CODE_LENGTH}")
    print(f"⏱️ مدة التخزين المؤقت: {CACHE_TTL} ثانية")
    
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

# ========== الصفحة الرئيسية المحسنة ==========
@app.get("/", response_class=HTMLResponse)
async def root():
    """الصفحة الرئيسية مع عرض التحذيرات"""
    warnings_html = ""
    if hasattr(app.state, 'warnings') and app.state.warnings:
        warnings_html = '<div style="background: #fff3cd; color: #856404; padding: 15px; border-radius: 10px; margin-bottom: 20px;">'
        warnings_html += '<h4>⚠️ تحذيرات التشغيل:</h4><ul>'
        for w in app.state.warnings:
            warnings_html += f'<li>{w}</li>'
        warnings_html += '</ul></div>'
    
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
            .warnings {{ background: #fff3cd; color: #856404; padding: 15px; border-radius: 10px; margin-bottom: 20px; }}
            textarea {{ width: 100%; padding: 15px; border: 2px solid #e0e0e0; border-radius: 10px; font-size: 1.1em; margin-bottom: 20px; resize: vertical; }}
            textarea:focus {{ outline: none; border-color: #667eea; }}
            button {{ background: #667eea; color: white; border: none; padding: 15px 30px; border-radius: 10px; font-size: 1.2em; cursor: pointer; width: 100%; transition: background 0.3s; }}
            button:hover {{ background: #5a67d8; }}
            button:disabled {{ background: #ccc; cursor: not-allowed; }}
            .result {{ margin-top: 20px; padding: 20px; border-radius: 10px; background: #f5f5f5; }}
            .error {{ color: #dc3545; background: #ffe6e8; padding: 15px; border-radius: 10px; }}
            .step {{ padding: 10px; border-right: 3px solid #667eea; background: white; margin: 10px 0; border-radius: 5px; }}
            .latex {{ font-family: monospace; background: #f1f1f1; padding: 5px; border-radius: 3px; }}
            .info {{ color: #666; font-size: 0.9em; margin-top: 10px; }}
            .examples {{ margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 10px; }}
            .example-btn {{ background: #e9ecef; color: #495057; border: none; padding: 8px 15px; margin: 5px; border-radius: 5px; cursor: pointer; }}
            .example-btn:hover {{ background: #dee2e6; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔧 {APP_NAME}</h1>
            <div class="version">الإصدار {VERSION}</div>
            <div class="status">✅ الخادم يعمل بنجاح</div>
            
            {warnings_html}
            
            <div class="examples">
                <strong>📝 أمثلة جاهزة:</strong>
                <button class="example-btn" onclick="setExample('مشتقة x**2 + 2x')">مشتقة</button>
                <button class="example-btn" onclick="setExample('تكامل sin(x)')">تكامل</button>
                <button class="example-btn" onclick="setExample('حل x**2 - 4 = 0')">معادلة</button>
                <button class="example-btn" onclick="setExample('5 + 3 * 2')">آلة حاسبة</button>
                <button class="example-btn" onclick="setExample('مشتقة sin(x) * cos(x)')">مشتقة مركبة</button>
            </div>
            
            <textarea id="question" rows="4" placeholder="اكتب سؤالك الرياضي هنا..."></textarea>
            <button onclick="solve()" id="solveBtn">حل المسألة</button>
            
            <div id="result" class="result" style="display: none;"></div>
        </div>

        <script>
            function setExample(text) {{
                document.getElementById('question').value = text;
            }}
            
            async function solve() {{
                const question = document.getElementById('question').value;
                const resultDiv = document.getElementById('result');
                const solveBtn = document.getElementById('solveBtn');
                
                if (!question.trim()) {{
                    alert('الرجاء إدخال سؤال');
                    return;
                }}
                
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '<p>⏳ جاري المعالجة...</p>';
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
                        html += `<p style="font-size: 1.2em; color: #28a745;">${{data.result || 'تم الحل'}}</p>`;
                        
                        if (data.warnings && data.warnings.length > 0) {{
                            html += '<div style="background: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; margin: 10px 0;">';
                            html += '<strong>⚠️ تحذيرات:</strong><ul>';
                            data.warnings.forEach(w => html += `<li>${{w}}</li>`);
                            html += '</ul></div>';
                        }}
                        
                        if (data.steps && data.steps.length > 0) {{
                            html += '<h4>📝 خطوات الحل:</h4>';
                            data.steps.forEach(step => {{
                                html += '<div class="step">';
                                html += `<div>${{step.description}}</div>`;
                                if (step.latex) {{
                                    html += `<div class="latex">📐 ${{step.latex}}</div>`;
                                }}
                                html += '</div>';
                            }});
                        }}
                        
                        html += `<p class="info">⏱️ وقت التنفيذ: ${{data.time}} ثانية</p>`;
                        html += `<p class="info">🤖 المحرك: ${{data.model}} ${{data.from_cache ? '(من الذاكرة المؤقتة)' : ''}}</p>`;
                        
                        resultDiv.innerHTML = html;
                    }} else {{
                        let errorHtml = `<div class="error">❌ خطأ: ${{data.error || 'حدث خطأ'}}</div>`;
                        if (data.ai_error) {{
                            errorHtml += `<div style="background: #fff3cd; margin-top: 10px; padding: 10px; border-radius: 5px;">⚠️ خطأ AI: ${{data.ai_error}}</div>`;
                        }}
                        if (data.math_error) {{
                            errorHtml += `<div style="background: #fff3cd; margin-top: 10px; padding: 10px; border-radius: 5px;">⚠️ خطأ رياضي: ${{data.math_error}}</div>`;
                        }}
                        resultDiv.innerHTML = errorHtml;
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
    """)

# ========== نقطة نهاية حل المسائل المحسنة ==========
@app.post("/solve", response_model=SolveResponse)
async def solve(request: SolveRequest):
    """حل أي مسألة رياضية مع تجميع الأخطاء والتحذيرات"""
    start_time = time.time()
    warnings = []
    ai_error = None
    math_error = None
    
    try:
        question = request.question.strip()
        
        if not question:
            return SolveResponse(
                success=False,
                error="السؤال فارغ",
                time=round(time.time() - start_time, 4)
            )
        
        # التحقق من طول الكود (حماية إضافية)
        if len(question) > MAX_CODE_LENGTH:
            return SolveResponse(
                success=False,
                error=f"السؤال طويل جداً (الحد الأقصى {MAX_CODE_LENGTH} حرف)",
                time=round(time.time() - start_time, 4)
            )
        
        # 1. AI Engine يولد الكود
        ai_result = None
        try:
            ai_result = await asyncio.wait_for(
                app.state.ai_engine.generate_code(question),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            ai_error = "انتهت مهلة توليد الكود (30 ثانية)"
            return SolveResponse(
                success=False,
                error="فشل في توليد الكود",
                ai_error=ai_error,
                time=round(time.time() - start_time, 4),
                warnings=warnings
            )
        except Exception as e:
            ai_error = str(e)
            return SolveResponse(
                success=False,
                error="فشل في توليد الكود",
                ai_error=ai_error,
                time=round(time.time() - start_time, 4),
                warnings=warnings
            )
        
        if not ai_result or not isinstance(ai_result, dict):
            ai_error = "نتيجة غير صالحة من AI Engine"
            return SolveResponse(
                success=False,
                error=ai_error,
                ai_error=ai_error,
                time=round(time.time() - start_time, 4),
                warnings=warnings
            )
        
        if not ai_result.get("success"):
            ai_error = ai_result.get("error", "فشل في توليد الكود")
            return SolveResponse(
                success=False,
                error=ai_error,
                ai_error=ai_error,
                time=round(time.time() - start_time, 4),
                warnings=warnings
            )
        
        # التحقق من وجود الكود
        code = ai_result.get("code")
        if not code:
            warnings.append("تم توليد الكود بنجاح ولكن لا يوجد مخرجات")
        
        # 2. Math Engine ينفذ الكود
        math_result = None
        try:
            math_result = await asyncio.wait_for(
                app.state.math_engine.execute(code if code else ""),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            math_error = "انتهت مهلة تنفيذ الكود (30 ثانية)"
            return SolveResponse(
                success=False,
                error="فشل في تنفيذ الكود",
                ai_error=ai_error,
                math_error=math_error,
                time=round(time.time() - start_time, 4),
                warnings=warnings
            )
        except Exception as e:
            math_error = str(e)
            return SolveResponse(
                success=False,
                error="فشل في تنفيذ الكود",
                ai_error=ai_error,
                math_error=math_error,
                time=round(time.time() - start_time, 4),
                warnings=warnings
            )
        
        if not math_result:
            math_error = "نتيجة غير صالحة من Math Engine"
            return SolveResponse(
                success=False,
                error=math_error,
                ai_error=ai_error,
                math_error=math_error,
                time=round(time.time() - start_time, 4),
                warnings=warnings
            )
        
        # تحويل الخطوات
        steps = []
        if math_result and hasattr(math_result, 'steps') and math_result.steps:
            for step in math_result.steps:
                try:
                    steps.append(StepResponse.from_step(step))
                except Exception as e:
                    warnings.append(f"فشل تحويل خطوة: {str(e)}")
        
        # تجهيز الرد النهائي
        total_time = round(time.time() - start_time, 4)
        
        return SolveResponse(
            success=math_result.success if math_result else False,
            result=math_result.result_str if math_result and math_result.success else None,
            steps=steps,
            model=ai_result.get("model", "ai"),
            from_cache=ai_result.get("from_cache", False),
            time=total_time,
            error=math_result.error if math_result and not math_result.success else None,
            warnings=warnings,
            ai_error=ai_error,
            math_error=math_error
        )
        
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
            warnings=warnings,
            ai_error=ai_error,
            math_error=math_error
        )

# ========== نقطة نهاية فحص الصحة المحسنة ==========
@app.get("/health")
async def health():
    """فحص صحة الخادم والمحركات"""
    uptime = time.time() - (app.state.start_time if hasattr(app.state, 'start_time') else START_TIME)
    
    # فحص حالة المحركات
    ai_status = "ready"
    math_status = "ready"
    
    try:
        if hasattr(app.state.ai_engine, 'ready'):
            ai_status = "ready" if app.state.ai_engine.ready else "not_ready"
    except:
        ai_status = "unknown"
    
    try:
        if hasattr(app.state.math_engine, 'get_stats'):
            math_status = "ready"
    except:
        math_status = "unknown"
    
    return JSONResponse({
        "status": "healthy",
        "version": VERSION,
        "debug": DEBUG,
        "ai_engine": ai_status,
        "math_engine": math_status,
        "uptime": round(uptime, 2),
        "uptime_str": f"{int(uptime // 3600):02d}:{int((uptime % 3600) // 60):02d}:{int(uptime % 60):02d}",
        "timestamp": time.time(),
        "warnings": getattr(app.state, 'warnings', []),
        "config": {
            "max_code_length": MAX_CODE_LENGTH,
            "cache_ttl": CACHE_TTL
        }
    })

# ========== نقطة نهاية الإحصائيات المحسنة ==========
@app.get("/stats")
async def get_stats():
    """إحصائيات المحركات مع تفاصيل أكثر"""
    stats = {
        "success": True,
        "stats": {
            "uptime": time.time() - (app.state.start_time if hasattr(app.state, 'start_time') else START_TIME),
            "warnings": getattr(app.state, 'warnings', []),
            "config": {
                "max_code_length": MAX_CODE_LENGTH,
                "cache_ttl": CACHE_TTL
            }
        }
    }
    
    # إحصائيات AI Engine
    if hasattr(app.state.ai_engine, 'get_stats'):
        try:
            stats["stats"]["ai_engine"] = app.state.ai_engine.get_stats()
        except Exception as e:
            stats["stats"]["ai_engine"] = {"error": str(e)}
    else:
        stats["stats"]["ai_engine"] = {"status": "stats_not_available"}
    
    # إحصائيات Math Engine
    if hasattr(app.state.math_engine, 'get_stats'):
        try:
            stats["stats"]["math_engine"] = app.state.math_engine.get_stats()
        except Exception as e:
            stats["stats"]["math_engine"] = {"error": str(e)}
    else:
        stats["stats"]["math_engine"] = {"status": "stats_not_available"}
    
    return JSONResponse(stats)

# ========== نقطة نهاية الاختبار المحسنة ==========
@app.get("/test")
async def test():
    """صفحة اختبار متكاملة"""
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
            body {{ font-family: Arial; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
            .container {{ max-width: 800px; margin: auto; background: white; padding: 30px; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }}
            h1 {{ color: #333; text-align: center; }}
            .endpoints {{ background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0; }}
            .endpoint {{ padding: 10px; border-bottom: 1px solid #ddd; }}
            code {{ background: #e0e0e0; padding: 2px 5px; border-radius: 3px; }}
            .success {{ color: green; font-weight: bold; }}
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
            
            <p><a href="/">العودة للصفحة الرئيسية</a></p>
        </div>
    </body>
    </html>
    """)

# ========== معالج الأخطاء العام ==========
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_id = abs(hash(str(exc))) % 10000
    error_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"\n❌ خطأ عام {error_id} في {error_time}")
    print(f"📌 المسار: {request.url.path}")
    print(f"📝 الخطأ: {str(exc)}")
    
    if DEBUG:
        import traceback
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

# ========== معالج المسارات غير الموجودة ==========
@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def not_found_handler(request: Request, path_name: str):
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
    print(f"📍 http://{HOST}:{PORT}")
    print(f"🔌 المنفذ: {PORT}")
    print(f"🔄 إعادة التشغيل التلقائي: {'نعم' if RELOAD else 'لا'}")
    print(f"⚙️ عدد العمال: {WORKERS}")
    print(f"🔧 وضع التصحيح: {'مفعل' if DEBUG else 'معطل'}")
    print(f"🌐 النطاقات المسموحة: {ALLOWED_ORIGINS}")
    print(f"📏 أقصى طول للكود: {MAX_CODE_LENGTH}")
    print(f"⏱️ مدة التخزين المؤقت: {CACHE_TTL} ثانية")
    print("="*60 + "\n")
    
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
        workers=WORKERS,
        log_level="debug" if DEBUG else "info"
    )
