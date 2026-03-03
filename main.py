import asyncio
import time
import json
import logging
import uuid
from typing import Optional, Dict, Any, List, Callable, Tuple
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from functools import wraps
import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import hashlib
import multiprocessing
import psutil

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, validator
import uvicorn

print("✅ تم تحميل main.py بنجاح")

from ai_engine import AIEngine
from math_engine import MathEngine, ExecutionStatus, MathExpressionType
from config import (
    DEBUG_MODE, HOST, PORT, VERSION, APP_NAME,
    GROQ_API_KEY, GEMINI_API_KEY,
    CACHE_TTL, MAX_CODE_LENGTH, MAX_WORKERS, USE_PROCESS_POOL
)

LOG_LEVEL = logging.DEBUG if DEBUG_MODE else logging.INFO
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

TRACE_LEVEL = 5
logging.addLevelName(TRACE_LEVEL, "TRACE")

def trace(self, message, *args, **kws):
    if self.isEnabledFor(TRACE_LEVEL):
        if not DEBUG_MODE and len(message) > 200:
            message = message[:200] + "... [truncated for security]"
        self._log(TRACE_LEVEL, message, args, **kws)

logging.Logger.trace = trace

logger = logging.getLogger(__name__)

file_handler = logging.FileHandler('api_requests.log')
file_handler.setLevel(logging.INFO if not DEBUG_MODE else TRACE_LEVEL)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


SUPPORTED_DOMAINS = [
    {"name": "general", "description": "المجال العام"},
    {"name": "mechanics", "description": "ميكانيكا"},
    {"name": "electricity", "description": "كهرباء"},
    {"name": "calculus", "description": "تفاضل وتكامل"},
    {"name": "thermodynamics", "description": "ديناميكا حرارية"},
    {"name": "fluid_mechanics", "description": "ميكانيكا الموائع"},
    {"name": "signal_processing", "description": "معالجة الإشارات"},
    {"name": "control_systems", "description": "نظم التحكم"},
    {"name": "quantum", "description": "فيزياء الكم"},
    {"name": "statistics", "description": "إحصاء"}
]

DOMAIN_NAMES = [d["name"] for d in SUPPORTED_DOMAINS]

CPU_COUNT = multiprocessing.cpu_count()
WORKER_COUNT = MAX_WORKERS if MAX_WORKERS > 0 else max(2, min(CPU_COUNT * 2, 8))

if USE_PROCESS_POOL:
    MATH_EXECUTOR = ProcessPoolExecutor(max_workers=max(2, CPU_COUNT))
    logger.info(f"Using ProcessPoolExecutor with {max(2, CPU_COUNT)} workers")
else:
    MATH_EXECUTOR = ThreadPoolExecutor(max_workers=WORKER_COUNT)
    logger.info(f"Using ThreadPoolExecutor with {WORKER_COUNT} workers")

CACHE_LOCK = asyncio.Semaphore(10)


class LRUCache:
    def __init__(self, name: str, capacity: int = 200, ttl: int = 3600):
        self.name = name
        self.cache = {}
        self.access_times = {}
        self.capacity = capacity
        self.ttl = ttl
        self.stats = {"hits": 0, "misses": 0, "evictions": 0}
        self._lock = asyncio.Lock()
    
    def _is_expired(self, key: str) -> bool:
        if key not in self.access_times:
            return True
        return time.time() - self.access_times[key] > self.ttl
    
    def _clean_expired(self):
        expired = [k for k in list(self.cache.keys()) if self._is_expired(k)]
        for k in expired:
            del self.cache[k]
            del self.access_times[k]
    
    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            self._clean_expired()
            if key in self.cache and not self._is_expired(key):
                self.access_times[key] = time.time()
                self.stats["hits"] += 1
                return self.cache[key]
            self.stats["misses"] += 1
            return None
    
    async def set(self, key: str, value: Any):
        async with self._lock:
            self._clean_expired()
            if key in self.cache:
                self.cache[key] = value
                self.access_times[key] = time.time()
            else:
                if len(self.cache) >= self.capacity:
                    oldest = min(self.access_times.items(), key=lambda x: x[1])[0]
                    del self.cache[oldest]
                    del self.access_times[oldest]
                    self.stats["evictions"] += 1
                self.cache[key] = value
                self.access_times[key] = time.time()
    
    async def clear(self):
        async with self._lock:
            self.cache.clear()
            self.access_times.clear()
    
    async def get_stats(self) -> Dict:
        async with self._lock:
            total = self.stats["hits"] + self.stats["misses"]
            hit_rate = (self.stats["hits"] / max(total, 1)) * 100
            return {
                "name": self.name,
                "size": len(self.cache),
                "capacity": self.capacity,
                "ttl": self.ttl,
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "evictions": self.stats["evictions"],
                "hit_rate": f"{hit_rate:.1f}%"
            }


class ResultCache:
    def __init__(self):
        self.ai_cache = LRUCache(name="AI", capacity=100, ttl=300)
        self.math_cache = LRUCache(name="Math", capacity=200, ttl=600)
        self.final_cache = LRUCache(name="Final", capacity=500, ttl=1800)
    
    def get_ai_key(self, question: str, domain: str) -> str:
        return hashlib.sha256(f"ai:{question}:{domain}".encode()).hexdigest()
    
    def get_math_key(self, code: str) -> str:
        return hashlib.sha256(f"math:{code}".encode()).hexdigest()
    
    def get_final_key(self, question: str, domain: str, include_steps: bool) -> str:
        return hashlib.sha256(f"final:{question}:{domain}:{include_steps}".encode()).hexdigest()
    
    async def get_ai_result(self, question: str, domain: str) -> Optional[Any]:
        key = self.get_ai_key(question, domain)
        return await self.ai_cache.get(key)
    
    async def set_ai_result(self, question: str, domain: str, value: Any):
        key = self.get_ai_key(question, domain)
        await self.ai_cache.set(key, value)
    
    async def get_math_result(self, code: str) -> Optional[Any]:
        key = self.get_math_key(code)
        return await self.math_cache.get(key)
    
    async def set_math_result(self, code: str, value: Any):
        key = self.get_math_key(code)
        await self.math_cache.set(key, value)
    
    async def get_final_result(self, question: str, domain: str, include_steps: bool) -> Optional[Any]:
        key = self.get_final_key(question, domain, include_steps)
        return await self.final_cache.get(key)
    
    async def set_final_result(self, question: str, domain: str, include_steps: bool, value: Any):
        key = self.get_final_key(question, domain, include_steps)
        await self.final_cache.set(key, value)
    
    async def clear_all(self):
        await self.ai_cache.clear()
        await self.math_cache.clear()
        await self.final_cache.clear()
    
    async def get_stats(self) -> Dict:
        ai_stats = await self.ai_cache.get_stats()
        math_stats = await self.math_cache.get_stats()
        final_stats = await self.final_cache.get_stats()
        return {
            "ai_cache": ai_stats,
            "math_cache": math_stats,
            "final_cache": final_stats
        }


class ResourceMonitor:
    def __init__(self, cpu_threshold: float = 80.0, memory_threshold: float = 80.0):
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.process = psutil.Process()
    
    def get_usage(self) -> Dict:
        try:
            cpu_percent = self.process.cpu_percent(interval=0.1)
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            memory_percent = (memory_info.rss / psutil.virtual_memory().total) * 100
            
            return {
                "cpu_percent": round(cpu_percent, 1),
                "memory_mb": round(memory_mb, 2),
                "memory_percent": round(memory_percent, 2),
                "cpu_warning": cpu_percent > self.cpu_threshold,
                "memory_warning": memory_percent > self.memory_threshold
            }
        except:
            return {
                "cpu_percent": 0,
                "memory_mb": 0,
                "memory_percent": 0,
                "cpu_warning": False,
                "memory_warning": False
            }
    
    def get_threadpool_stats(self) -> Dict:
        if isinstance(MATH_EXECUTOR, ThreadPoolExecutor):
            return {
                "type": "thread",
                "max_workers": MATH_EXECUTOR._max_workers,
                "pending_work": getattr(MATH_EXECUTOR, '_work_queue', None).qsize() if hasattr(MATH_EXECUTOR, '_work_queue') else 0
            }
        else:
            return {
                "type": "process",
                "max_workers": MATH_EXECUTOR._max_workers,
                "pending": "unknown"
            }


class SecureCodeValidator:
    DANGEROUS_PATTERNS = [
        '__import__', 'eval(', 'exec(', 'compile(',
        'open(', 'file(', 'os.system', 'subprocess',
        'socket', 'requests', 'urllib', 'pickle',
        'pty', 'spawn', 'fork', 'execv'
    ]
    
    @classmethod
    def validate(cls, code: str) -> Tuple[bool, Optional[str]]:
        if len(code) > MAX_CODE_LENGTH:
            return False, f"Code too long: {len(code)} > {MAX_CODE_LENGTH}"
        
        code_lower = code.lower()
        for pattern in cls.DANGEROUS_PATTERNS:
            if pattern.lower() in code_lower:
                return False, f"Dangerous pattern detected: {pattern}"
        
        lines = code.split('\n')
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                for dangerous in ['os', 'sys', 'subprocess', 'socket']:
                    if dangerous in stripped:
                        return False, f"Unsafe import detected: {stripped}"
        
        return True, None


def format_uptime(seconds: float) -> str:
    delta = timedelta(seconds=int(seconds))
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    seconds = delta.seconds % 60
    
    parts = []
    if delta.days > 0:
        parts.append(f"{delta.days} يوم")
    if hours > 0:
        parts.append(f"{hours} ساعة")
    if minutes > 0:
        parts.append(f"{minutes} دقيقة")
    if seconds > 0 or not parts:
        parts.append(f"{seconds} ثانية")
    
    return " و ".join(parts)


def generate_request_id() -> str:
    return str(uuid.uuid4())


async def verify_admin_token(request: Request) -> bool:
    admin_token = request.headers.get("X-Admin-Token")
    valid_token = os.getenv("ADMIN_TOKEN", "zaky-admin-2024")
    return DEBUG_MODE or admin_token == valid_token


def require_admin(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        
        if not request:
            for v in kwargs.values():
                if isinstance(v, Request):
                    request = v
                    break
        
        if not request:
            raise HTTPException(status_code=400, detail="Request object not found")
        
        if not await verify_admin_token(request):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        return await func(*args, **kwargs)
    return wrapper


def track_request(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request_id = generate_request_id()
        start_time = time.time()
        
        logger.info(f"[{request_id}] Starting request: {func.__name__}")
        if DEBUG_MODE:
            logger.trace(f"[{request_id}] Args: {args}, Kwargs: {kwargs}")
        
        app_state.request_count += 1
        kwargs['request_id'] = request_id
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"[{request_id}] Completed in {execution_time:.3f}s")
            
            if isinstance(result, dict):
                result['_request_id'] = request_id
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            app_state.error_count += 1
            execution_time = time.time() - start_time
            logger.error(f"[{request_id}] Error after {execution_time:.3f}s: {e}", exc_info=True)
            raise
    return wrapper


def require_engines(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not app_state.ai_engine or not app_state.math_engine:
            logger.error("Engines not initialized")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Engines not initialized. Please try again later."
            )
        return await func(*args, **kwargs)
    return wrapper


def validate_input(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = None
        for arg in args:
            if hasattr(arg, 'question') or hasattr(arg, 'code') or hasattr(arg, 'expression'):
                request = arg
                break
        
        if request:
            text_to_check = getattr(request, 'question', None) or getattr(request, 'code', None) or getattr(request, 'expression', None)
            if text_to_check and len(text_to_check) > MAX_CODE_LENGTH:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Input too long. Maximum length is {MAX_CODE_LENGTH} characters"
                )
            
            if hasattr(request, 'code'):
                safe, error = SecureCodeValidator.validate(request.code)
                if not safe:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Security violation: {error}"
                    )
        
        return await func(*args, **kwargs)
    return wrapper


class SolveRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=MAX_CODE_LENGTH)
    domain: str = Field("general")
    include_steps: bool = Field(True)
    use_ai_assist: bool = Field(True)
    timeout: Optional[int] = Field(None)
    
    @validator('domain')
    def validate_domain(cls, v):
        if v not in DOMAIN_NAMES:
            raise ValueError(f"Domain must be one of: {DOMAIN_NAMES}")
        return v
    
    @validator('timeout')
    def validate_timeout(cls, v):
        if v is not None and (v < 5 or v > 30):
            raise ValueError("Timeout must be between 5 and 30 seconds")
        return v


class BaseResponse(BaseModel):
    success: bool
    request_id: str
    timestamp: float
    execution_time: float
    warning: Optional[str] = None
    error: Optional[str] = None


class SolveResponse(BaseResponse):
    result: Optional[str] = None
    result_latex: Optional[str] = None
    steps: Optional[List[Dict[str, str]]] = None
    code: Optional[str] = None
    model: str
    domain: str
    expression_type: Optional[str] = None
    confidence: Optional[float] = None
    status: Optional[str] = None
    from_cache: bool = False
    from_ai_cache: bool = False
    from_math_cache: bool = False
    ai_assist: Optional[Dict[str, Any]] = None
    stages_timing: Optional[Dict[str, float]] = None


class EvaluateRequest(BaseModel):
    expression: str = Field(..., min_length=1, max_length=MAX_CODE_LENGTH)
    subs: Optional[Dict[str, float]] = Field(None)
    operation: Optional[str] = Field(None)
    variable: Optional[str] = Field(None)
    
    @validator('operation')
    def validate_operation(cls, v):
        if v is not None and v not in ['derivative', 'integral', 'solve']:
            raise ValueError("Operation must be one of: derivative, integral, solve")
        return v


class EvaluateResponse(BaseResponse):
    expression: str
    result: Optional[str] = None
    result_latex: Optional[str] = None
    steps: Optional[List[Dict[str, str]]] = None
    operation: Optional[str] = None
    variable: Optional[str] = None


class SimplifyRequest(BaseModel):
    expression: str = Field(..., min_length=1, max_length=MAX_CODE_LENGTH)


class SimplifyResponse(BaseResponse):
    original: str
    original_latex: str
    simplified: str
    simplified_latex: str
    steps: List[Dict[str, str]]


class ValidateRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=MAX_CODE_LENGTH)


class ValidateResponse(BaseModel):
    valid: bool
    request_id: str
    timestamp: float
    type: Optional[str] = None
    error: Optional[str] = None
    pattern: Optional[str] = None
    operations: Optional[List[Dict[str, Any]]] = None
    expression_type: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: float
    uptime: str
    uptime_seconds: float
    engines: Dict[str, bool]
    cache: Dict[str, Any]
    apis: Dict[str, bool]
    stats: Dict[str, Any]
    resources: Dict[str, Any]
    executor: Dict[str, Any]
    warnings: List[str]
    request_count: int
    error_count: int


class AppState:
    def __init__(self):
        self.ai_engine: Optional[AIEngine] = None
        self.math_engine: Optional[MathEngine] = None
        self.start_time: float = time.time()
        self.request_count: int = 0
        self.error_count: int = 0
        self._shutdown: bool = False
        self.executor = MATH_EXECUTOR
        self.cache = ResultCache()
        self.monitor = ResourceMonitor()


app_state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Zaky Matik API Server...")
    logger.info(f"Version: {VERSION}, Debug: {DEBUG_MODE}")
    logger.info(f"Executor: {'Process' if USE_PROCESS_POOL else 'Thread'} with {WORKER_COUNT} workers")
    logger.info(f"Cache sizes: AI=100, Math=200, Final=500")
    
    try:
        logger.info("Initializing AI Engine...")
        app_state.ai_engine = AIEngine()
        await app_state.ai_engine.start()
        logger.info("AI Engine ready")
        
        logger.info("Initializing Math Engine...")
        app_state.math_engine = MathEngine(enable_ai_assist=True)
        logger.info("Math Engine ready")
        
        logger.info("Server is ready")
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize: {e}", exc_info=True)
        raise
    
    finally:
        logger.info("Shutting down server...")
        app_state._shutdown = True
        
        if app_state.ai_engine:
            try:
                await app_state.ai_engine.stop()
                logger.info("AI Engine stopped")
            except Exception as e:
                logger.error(f"Error stopping AI Engine: {e}")
        
        if app_state.math_engine:
            try:
                await app_state.math_engine.shutdown()
                logger.info("Math Engine stopped")
            except Exception as e:
                logger.error(f"Error stopping Math Engine: {e}")
        
        app_state.executor.shutdown(wait=False)
        logger.info("Executor shutdown")
        logger.info("Goodbye!")


app = FastAPI(
    title=APP_NAME,
    description="ذكي ماتك - محرك الذكاء الاصطناعي لحل المسائل الهندسية والرياضية",
    version=VERSION,
    lifespan=lifespan,
    docs_url="/docs" if DEBUG_MODE else None,
    redoc_url="/redoc" if DEBUG_MODE else None,
)

# ✅ إضافة مسار اختبار للتأكد من أن POST يعمل
@app.post("/test")
async def test_post():
    return {"message": "POST is working!"}

# ✅ نقطة اختبار بسيطة
@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "server is running", "time": time.time()}

# ✅ عرض جميع المسارات للتأكد
@app.get("/debug/routes")
async def debug_routes():
    routes = []
    for route in app.routes:
        if hasattr(route, "methods"):
            routes.append({
                "path": route.path,
                "methods": list(route.methods)
            })
    return {"routes": routes}

# ✅ حل مشكلة 405 - فرض POST فقط على جميع المسارات
@app.api_route("/solve", methods=["POST"])
@app.api_route("/solve/with-steps", methods=["POST"])
@app.api_route("/evaluate", methods=["POST"])
@app.api_route("/simplify", methods=["POST"])
@app.api_route("/validate", methods=["POST"])

# ✅ عرض جميع المسارات عند بدء التشغيل
@app.on_event("startup")
async def show_routes():
    print("\n" + "="*60)
    print("📋 المسارات المتاحة:")
    routes_found = False
    for route in app.routes:
        if hasattr(route, "methods") and route.path not in ["/", "/favicon.ico"]:
            methods = ", ".join(list(route.methods))
            print(f"   {methods} {route.path}")
            routes_found = True
    if not routes_found:
        print("   ❌ لا توجد مسارات!")
    print("="*60 + "\n")

# ✅ إنشاء مجلد static وربطه
os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def root():
    uptime_str = format_uptime(time.time() - app_state.start_time)
    resources = app_state.monitor.get_usage()
    
    return f"""
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <title>{APP_NAME}</title>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 900px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; }}
            .endpoint {{ background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 5px; border-right: 4px solid #007bff; }}
            .badge {{ background: #007bff; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px; }}
            .stats {{ margin-top: 20px; padding: 15px; background: #e9ecef; border-radius: 5px; }}
            .warning {{ color: #856404; background-color: #fff3cd; padding: 10px; border-radius: 5px; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{APP_NAME} v{VERSION}</h1>
            <p>مرحباً بك في واجهة برمجة التطبيقات لمحرك ذكي ماتك.</p>
            
            <h3>نقاط النهاية المتاحة:</h3>
            <div class="endpoint">
                <span class="badge">POST</span> /solve - حل مسألة رياضية
            </div>
            <div class="endpoint">
                <span class="badge">POST</span> /solve/with-steps - حل مع خطوات مفصلة
            </div>
            <div class="endpoint">
                <span class="badge">POST</span> /evaluate - تقييم تعبير رياضي مباشر
            </div>
            <div class="endpoint">
                <span class="badge">POST</span> /simplify - تبسيط تعبير رياضي
            </div>
            <div class="endpoint">
                <span class="badge">GET</span> /health - فحص صحة النظام
            </div>
            <div class="endpoint">
                <span class="badge">POST</span> /test - اختبار POST
            </div>
            <div class="endpoint">
                <span class="badge">GET</span> /ping - اختبار الاتصال
            </div>
            
            <div class="stats">
                <strong>إحصائيات:</strong><br>
                الطلبات: {app_state.request_count}<br>
                الأخطاء: {app_state.error_count}<br>
                وقت التشغيل: {uptime_str}<br>
                CPU: {resources['cpu_percent']:.1f}%<br>
                الذاكرة: {resources['memory_mb']:.0f} MB
            </div>
            
            {f'<div class="warning">⚠️ تحذير: {resources["cpu_warning"] and "CPU مرتفع" or ""} {resources["memory_warning"] and "ذاكرة مرتفعة" or ""}</div>' if resources.get('cpu_warning') or resources.get('memory_warning') else ''}
        </div>
    </body>
    </html>
    """


@app.get("/admin/docs", include_in_schema=False)
@require_admin
async def admin_docs(request: Request):
    return RedirectResponse(url="/docs")


# ==============================================================================
# ✅✅✅ منطقة الاختبار والتصحيح ✅✅✅
# ==============================================================================
@app.post("/solve", response_model=SolveResponse)
@track_request
@require_engines
@validate_input
async def solve_problem(
    request: SolveRequest, 
    background_tasks: BackgroundTasks,
    request_id: str = None
):
    # --- وضع الاختبار: تجاهل كل المحركات وأرجع إجابة ثابتة ---
    print(f"[{request_id}] TEST MODE: Received question '{request.question}'. Returning fixed response.")
    return {
        "success": True,
        "request_id": request_id,
        "timestamp": time.time(),
        "execution_time": 0.1,
        "result": "4",
        "result_latex": "4",
        "steps": [{"text": "هذه إجابة ثابتة من وضع الاختبار", "latex": ""}],
        "model": "test-mode",
        "domain": request.domain,
        "from_cache": False,
        "status": "success",
        "confidence": 1.0,
        "from_ai_cache": False,
        "from_math_cache": False,
        "ai_assist": None,
        "stages_timing": None,
        "warning": None,
        "error": None,
        "code": "N/A in test mode",
        "expression_type": "simple"
    }
# ==============================================================================
# ❌❌❌ الكود الأصلي المعقد تم تعطيله مؤقتاً ❌❌❌
# ==============================================================================

# @app.post("/solve", response_model=SolveResponse)
# @track_request
# @require_engines
# @validate_input
# async def solve_problem(
#     request: SolveRequest, 
#     background_tasks: BackgroundTasks,
#     request_id: str = None
# ):
#     start_time = time.time()
#     stages = {}
    
#     logger.info(f"[{request_id}] Request: {request.question[:100]}... (domain: {request.domain})")
    
#     async with CACHE_LOCK:
#         final_cache_key = app_state.cache.get_final_key(request.question, request.domain, request.include_steps)
#         cached_final = await app_state.cache.get_final_result(request.question, request.domain, request.include_steps)
    
#     if cached_final:
#         logger.info(f"[{request_id}] Final cache hit")
#         cached_final["from_cache"] = True
#         cached_final["execution_time"] = time.time() - start_time
#         cached_final["request_id"] = request_id
#         return cached_final
    
#     try:
#         stage_start = time.time()
        
#         async with CACHE_LOCK:
#             ai_result = await app_state.cache.get_ai_result(request.question, request.domain)
        
#         if not ai_result:
#             logger.trace(f"[{request_id}] AI cache miss")
#             ai_result = await app_state.ai_engine.generate_code(
#                 question=request.question,
#                 domain=request.domain
#             )
#             if ai_result.get("success"):
#                 async with CACHE_LOCK:
#                     await app_state
