import asyncio
import time
import json
import logging
import uuid
from typing import Optional, Dict, Any, List, Callable
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
from pydantic import BaseModel, Field, validator
import uvicorn

from ai_engine import AIEngine
from math_engine import MathEngine, ExecutionStatus, MathExpressionType
from config import (
    DEBUG_MODE, HOST, PORT, VERSION, APP_NAME,
    GROQ_API_KEY, GEMINI_API_KEY,
    CACHE_TTL, MAX_CODE_LENGTH, MAX_WORKERS, USE_PROCESS_POOL
)

LOG_LEVEL = logging.DEBUG if DEBUG_MODE else logging.INFO
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# إضافة مستوى TRACE للتسجيل التفصيلي (مع تحذير أمني)
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

# إعداد Executor ديناميكي (Thread أو Process)
CPU_COUNT = multiprocessing.cpu_count()
WORKER_COUNT = MAX_WORKERS if MAX_WORKERS > 0 else max(2, min(CPU_COUNT * 2, 8))

if USE_PROCESS_POOL:
    MATH_EXECUTOR = ProcessPoolExecutor(max_workers=max(2, CPU_COUNT))
    logger.info(f"Using ProcessPoolExecutor with {max(2, CPU_COUNT)} workers")
else:
    MATH_EXECUTOR = ThreadPoolExecutor(max_workers=WORKER_COUNT)
    logger.info(f"Using ThreadPoolExecutor with {WORKER_COUNT} workers")

# Semaphore للتحكم في التزامن على Cache
CACHE_LOCK = asyncio.Semaphore(10)


class LRUCache:
    """LRU Cache للذاكرة مع TTL وإحصائيات و Lock داخلي"""
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
    """Cache متعدد المستويات للنتائج مع إحصائيات"""
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
    """مراقب استخدام الموارد مع تفاصيل ThreadPool"""
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
        """إحصائيات عن ThreadPool"""
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
    """التحقق المتقدم من الكود قبل التنفيذ"""
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if DEBUG_MODE else [],
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


@app.post("/solve", response_model=SolveResponse)
@track_request
@require_engines
@validate_input
async def solve_problem(
    request: SolveRequest, 
    background_tasks: BackgroundTasks,
    request_id: str = None
):
    start_time = time.time()
    stages = {}
    
    logger.info(f"[{request_id}] Request: {request.question[:100]}... (domain: {request.domain})")
    
    async with CACHE_LOCK:
        final_cache_key = app_state.cache.get_final_key(request.question, request.domain, request.include_steps)
        cached_final = await app_state.cache.get_final_result(request.question, request.domain, request.include_steps)
    
    if cached_final:
        logger.info(f"[{request_id}] Final cache hit")
        cached_final["from_cache"] = True
        cached_final["execution_time"] = time.time() - start_time
        cached_final["request_id"] = request_id
        return cached_final
    
    try:
        stage_start = time.time()
        
        async with CACHE_LOCK:
            ai_result = await app_state.cache.get_ai_result(request.question, request.domain)
        
        if not ai_result:
            logger.trace(f"[{request_id}] AI cache miss")
            ai_result = await app_state.ai_engine.generate_code(
                question=request.question,
                domain=request.domain
            )
            if ai_result.get("success"):
                async with CACHE_LOCK:
                    await app_state.cache.set_ai_result(request.question, request.domain, ai_result)
            from_ai_cache = False
        else:
            logger.trace(f"[{request_id}] AI cache hit")
            from_ai_cache = True
        
        stages["ai_generation"] = time.time() - stage_start
        
        if not ai_result.get("success"):
            return SolveResponse(
                success=False,
                request_id=request_id,
                timestamp=time.time(),
                execution_time=time.time() - start_time,
                model=ai_result.get("model", "unknown"),
                domain=request.domain,
                error=ai_result.get("error", "AI generation failed"),
                status="ai_error",
                warning=ai_result.get("warning"),
                from_ai_cache=from_ai_cache,
                stages_timing=stages
            )
        
        stage_start = time.time()
        timeout = request.timeout or 10
        
        async with CACHE_LOCK:
            math_result_obj = await app_state.cache.get_math_result(ai_result["code"])
        
        if not math_result_obj:
            logger.trace(f"[{request_id}] Math cache miss")
            try:
                loop = asyncio.get_running_loop()
                
                # تنفيذ مع timeout وقابلية للإلغاء
                math_task = asyncio.create_task(
                    app_state.math_engine.execute(
                        code=ai_result["code"],
                        use_ai_assist=request.use_ai_assist
                    )
                )
                
                math_result_obj = await asyncio.wait_for(math_task, timeout=timeout)
                
                if math_result_obj.success:
                    async with CACHE_LOCK:
                        await app_state.cache.set_math_result(ai_result["code"], math_result_obj)
                from_math_cache = False
                
            except asyncio.TimeoutError:
                math_task.cancel()
                stages["math_execution"] = time.time() - stage_start
                logger.warning(f"[{request_id}] Math execution timeout after {timeout}s")
                return SolveResponse(
                    success=False,
                    request_id=request_id,
                    timestamp=time.time(),
                    execution_time=time.time() - start_time,
                    model=ai_result.get("model", "unknown"),
                    domain=request.domain,
                    error=f"Execution timeout after {timeout} seconds",
                    status="timeout",
                    from_ai_cache=from_ai_cache,
                    stages_timing=stages
                )
        else:
            logger.trace(f"[{request_id}] Math cache hit")
            from_math_cache = True
        
        stages["math_execution"] = time.time() - stage_start
        
        response = SolveResponse(
            success=math_result_obj.success,
            request_id=request_id,
            timestamp=time.time(),
            execution_time=time.time() - start_time,
            result=math_result_obj.result_str if math_result_obj.success else None,
            result_latex=math_result_obj.result_latex if request.include_steps and math_result_obj.success else None,
            steps=[s.to_dict() for s in math_result_obj.steps] if request.include_steps and math_result_obj.steps else None,
            code=ai_result["code"] if DEBUG_MODE else None,
            model=ai_result.get("model", "unknown"),
            domain=request.domain,
            expression_type=math_result_obj.expression_type.value if hasattr(math_result_obj, 'expression_type') else None,
            confidence=ai_result.get("confidence"),
            status=math_result_obj.status.value if hasattr(math_result_obj, 'status') else None,
            from_cache=False,
            from_ai_cache=from_ai_cache,
            from_math_cache=from_math_cache,
            ai_assist=math_result_obj.ai_assist if hasattr(math_result_obj, 'ai_assist') else None,
            warning=ai_result.get("warning") or (math_result_obj.error if not math_result_obj.success else None),
            error=math_result_obj.error if not math_result_obj.success else None,
            stages_timing=stages
        )
        
        logger.info(f"[{request_id}] Completed in {response.execution_time:.2f}s - Success: {response.success}")
        
        if response.success:
            async with CACHE_LOCK:
                await app_state.cache.set_final_result(request.question, request.domain, request.include_steps, response.dict())
        
        if response.execution_time > 5:
            background_tasks.add_task(
                logger.warning,
                f"[{request_id}] Slow request: {response.execution_time:.2f}s"
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/solve/with-steps", response_model=SolveResponse)
@track_request
@require_engines
@validate_input
async def solve_with_steps(
    request: SolveRequest, 
    background_tasks: BackgroundTasks,
    request_id: str = None
):
    request.include_steps = True
    return await solve_problem(request, background_tasks, request_id=request_id)


@app.post("/evaluate", response_model=EvaluateResponse)
@track_request
@require_engines
@validate_input
async def evaluate_expression(
    request: EvaluateRequest,
    request_id: str = None
):
    start_time = time.time()
    logger.info(f"[{request_id}] Evaluate: {request.expression}")
    
    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            app_state.executor,
            lambda: app_state.math_engine.evaluate_expression(
                expression=request.expression,
                subs=request.subs,
                operation=request.operation,
                variable=request.variable
            )
        )
        
        return EvaluateResponse(
            success=result.get("success", False),
            request_id=request_id,
            timestamp=time.time(),
            execution_time=time.time() - start_time,
            expression=request.expression,
            result=result.get("result"),
            result_latex=result.get("result_latex"),
            steps=result.get("steps"),
            operation=request.operation,
            variable=request.variable,
            error=result.get("error"),
            warning=result.get("warning")
        )
        
    except Exception as e:
        logger.error(f"[{request_id}] Error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/simplify", response_model=SimplifyResponse)
@track_request
@require_engines
@validate_input
async def simplify_expression(
    request: SimplifyRequest,
    request_id: str = None
):
    start_time = time.time()
    logger.info(f"[{request_id}] Simplify: {request.expression}")
    
    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            app_state.executor,
            lambda: app_state.math_engine.simplify_expression(request.expression)
        )
        
        return SimplifyResponse(
            success=result.get("success", False),
            request_id=request_id,
            timestamp=time.time(),
            execution_time=time.time() - start_time,
            original=result.get("original", request.expression),
            original_latex=result.get("original_latex", ""),
            simplified=result.get("simplified", ""),
            simplified_latex=result.get("simplified_latex", ""),
            steps=result.get("steps", []),
            error=result.get("error"),
            warning=result.get("warning")
        )
        
    except Exception as e:
        logger.error(f"[{request_id}] Error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/validate", response_model=ValidateResponse)
@track_request
@require_engines
@validate_input
async def validate_code(
    request: ValidateRequest,
    request_id: str = None
):
    logger.info(f"[{request_id}] Validate code length: {len(request.code)}")
    
    try:
        validation = app_state.math_engine.validate_code(request.code)
        
        return ValidateResponse(
            valid=validation.get("valid", False),
            request_id=request_id,
            timestamp=time.time(),
            type=validation.get("type"),
            error=validation.get("error"),
            pattern=validation.get("pattern"),
            operations=validation.get("operations"),
            expression_type=validation.get("expression_type")
        )
        
    except Exception as e:
        logger.error(f"[{request_id}] Error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/health", response_model=HealthResponse)
@require_engines
async def health_check():
    ai_health = await app_state.ai_engine.health_check() if hasattr(app_state.ai_engine, 'health_check') else {}
    math_stats = app_state.math_engine.get_stats()
    resources = app_state.monitor.get_usage()
    cache_stats = await app_state.cache.get_stats()
    executor_stats = app_state.monitor.get_threadpool_stats()
    
    warnings = []
    if not ai_health.get("apis", {}).get("groq") and not ai_health.get("apis", {}).get("gemini"):
        warnings.append("No AI APIs available - running in simulation mode")
    if math_stats.get("timeouts", 0) > 10:
        warnings.append(f"High number of timeouts: {math_stats['timeouts']}")
    if math_stats.get("security_errors", 0) > 5:
        warnings.append(f"Security errors detected: {math_stats['security_errors']}")
    if resources.get("cpu_warning"):
        warnings.append(f"High CPU usage: {resources['cpu_percent']:.1f}%")
    if resources.get("memory_warning"):
        warnings.append(f"High memory usage: {resources['memory_percent']:.1f}%")
    if executor_stats.get("pending_work", 0) > 50:
        warnings.append(f"High pending tasks: {executor_stats['pending_work']}")
    
    return HealthResponse(
        status="healthy" if not app_state._shutdown else "shutting_down",
        version=VERSION,
        timestamp=time.time(),
        uptime=format_uptime(time.time() - app_state.start_time),
        uptime_seconds=time.time() - app_state.start_time,
        engines={"ai": True, "math": True},
        cache=cache_stats,
        apis=ai_health.get("apis", {"groq": False, "gemini": False}),
        stats={
            "requests": app_state.request_count,
            "errors": app_state.error_count,
            "math": math_stats
        },
        resources=resources,
        executor=executor_stats,
        warnings=warnings,
        request_count=app_state.request_count,
        error_count=app_state.error_count
    )


@app.get("/stats")
@require_engines
async def get_stats():
    math_stats = app_state.math_engine.get_stats()
    ai_stats = app_state.ai_engine.get_stats() if hasattr(app_state.ai_engine, 'get_stats') else {}
    resources = app_state.monitor.get_usage()
    cache_stats = await app_state.cache.get_stats()
    executor_stats = app_state.monitor.get_threadpool_stats()
    
    success_rate = (app_state.request_count - app_state.error_count) / max(app_state.request_count, 1) * 100
    
    return {
        "server": {
            "uptime": format_uptime(time.time() - app_state.start_time),
            "uptime_seconds": time.time() - app_state.start_time,
            "requests": app_state.request_count,
            "errors": app_state.error_count,
            "success_rate": f"{success_rate:.1f}%",
            "cache": cache_stats,
            "resources": resources,
            "executor": executor_stats
        },
        "ai_engine": ai_stats,
        "math_engine": math_stats,
        "timestamp": time.time()
    }


@app.post("/cache/clear")
@require_engines
@require_admin
async def clear_cache(request: Request):
    await app_state.cache.clear_all()
    logger.info("All caches cleared")
    return {"success": True, "message": "All caches cleared"}


@app.post("/reset-stats")
@require_engines
@require_admin
async def reset_stats(request: Request):
    if app_state.math_engine:
        app_state.math_engine.reset_stats()
    
    if app_state.ai_engine and hasattr(app_state.ai_engine, 'reset_stats'):
        app_state.ai_engine.reset_stats()
    
    app_state.request_count = 0
    app_state.error_count = 0
    
    logger.info("Statistics reset")
    return {"success": True, "message": "Statistics reset"}


@app.get("/domains")
async def get_domains():
    return {"domains": SUPPORTED_DOMAINS}


@app.get("/models")
@require_engines
async def get_models_status():
    health = await app_state.ai_engine.health_check() if hasattr(app_state.ai_engine, 'health_check') else {}
    return {
        "apis": health.get("apis", {}),
        "templates": health.get("templates", []),
        "cache": health.get("cache", {}),
        "simulation_mode": not (health.get("apis", {}).get("groq") or health.get("apis", {}).get("gemini"))
    }


@app.get("/metrics", response_class=PlainTextResponse)
@require_engines
async def get_metrics():
    math_stats = app_state.math_engine.get_stats()
    resources = app_state.monitor.get_usage()
    cache_stats = await app_state.cache.get_stats()
    
    metrics = []
    metrics.append("# HELP zaky_requests_total Total requests received")
    metrics.append("# TYPE zaky_requests_total counter")
    metrics.append(f"zaky_requests_total {app_state.request_count}")
    
    metrics.append("# HELP zaky_errors_total Total errors encountered")
    metrics.append("# TYPE zaky_errors_total counter")
    metrics.append(f"zaky_errors_total {app_state.error_count}")
    
    metrics.append("# HELP zaky_uptime_seconds Uptime in seconds")
    metrics.append("# TYPE zaky_uptime_seconds gauge")
    metrics.append(f"zaky_uptime_seconds {time.time() - app_state.start_time}")
    
    metrics.append("# HELP zaky_cache_hits_total Total cache hits")
    metrics.append("# TYPE zaky_cache_hits_total counter")
    metrics.append(f"zaky_cache_hits_total {cache_stats['final_cache']['hits']}")
    
    metrics.append("# HELP zaky_cache_misses_total Total cache misses")
    metrics.append("# TYPE zaky_cache_misses_total counter")
    metrics.append(f"zaky_cache_misses_total {cache_stats['final_cache']['misses']}")
    
    metrics.append("# HELP zaky_cpu_percent CPU usage percent")
    metrics.append("# TYPE zaky_cpu_percent gauge")
    metrics.append(f"zaky_cpu_percent {resources['cpu_percent']}")
    
    metrics.append("# HELP zaky_memory_mb Memory usage in MB")
    metrics.append("# TYPE zaky_memory_mb gauge")
    metrics.append(f"zaky_memory_mb {resources['memory_mb']}")
    
    metrics.append("# HELP zaky_pending_tasks Pending executor tasks")
    metrics.append("# TYPE zaky_pending_tasks gauge")
    metrics.append(f"zaky_pending_tasks {app_state.monitor.get_threadpool_stats().get('pending_work', 0)}")
    
    return "\n".join(metrics)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path,
            "timestamp": time.time(),
            "request_id": generate_request_id()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    error_id = generate_request_id()
    logger.error(f"Unhandled exception [{error_id}]: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error",
            "error_id": error_id,
            "detail": str(exc) if DEBUG_MODE else None,
            "path": request.url.path,
            "timestamp": time.time(),
            "request_id": generate_request_id()
        }
    )


if __name__ == "__main__":
    print("\n" + "="*60)
    print(f"{APP_NAME} v{VERSION}")
    print("="*60)
    print(f"Host: {HOST}")
    print(f"Port: {PORT}")
    print(f"Debug: {DEBUG_MODE}")
    print(f"Executor: {'Process' if USE_PROCESS_POOL else 'Thread'} with {WORKER_COUNT} workers")
    print(f"Max code length: {MAX_CODE_LENGTH}")
    print(f"API Docs: http://{HOST}:{PORT}/docs")
    print("="*60)
    
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG_MODE,
        log_level="debug" if DEBUG_MODE else "info"
    )
