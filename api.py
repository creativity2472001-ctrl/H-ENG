# api.py - واجهة API للآلة الحاسبة (نسخة إنتاجية متكاملة - معدلة)
from fastapi import FastAPI, HTTPException, Query, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
import uvicorn
import os
import asyncio
import concurrent.futures
from pathlib import Path
from enum import Enum
import time
import base64
import io
import logging
import logging.handlers
import uuid
from datetime import datetime, timedelta
import re
import hashlib
import multiprocessing
from collections import defaultdict
import json

from calculator import Calculator

# ========== إعدادات متقدمة ==========
CPU_COUNT = multiprocessing.cpu_count()
MAX_WORKERS = max(4, CPU_COUNT * 2)

# ========== إعدادات التسجيل المتقدمة (Logging) ==========
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

class CustomRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """معالج ملفات دوار يعتمد على التاريخ"""
    def __init__(self, filename, when='midnight', interval=1, backupCount=30, encoding='utf-8'):
        super().__init__(filename, when=when, interval=interval, backupCount=backupCount, encoding=encoding)

# إعداد المسجل الرئيسي
logger = logging.getLogger("api")
logger.setLevel(logging.DEBUG)

# مسجل للملفات (يومي)
file_handler = CustomRotatingFileHandler(
    LOG_DIR / "api.log",
    when='midnight',
    backupCount=30,
    encoding='utf-8'
)
file_handler.setLevel(logging.INFO)
file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_format)

# مسجل للأخطاء مع traceback
error_handler = CustomRotatingFileHandler(
    LOG_DIR / "error.log",
    when='midnight',
    backupCount=30,
    encoding='utf-8'
)
error_handler.setLevel(logging.ERROR)
error_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s\n%(exc_info)s')
error_handler.setFormatter(error_format)

# مسجل للطلبات
request_handler = CustomRotatingFileHandler(
    LOG_DIR / "requests.log",
    when='midnight',
    backupCount=30,
    encoding='utf-8'
)
request_handler.setLevel(logging.INFO)
request_format = logging.Formatter('%(asctime)s - %(message)s')
request_handler.setFormatter(request_format)

# إضافة المعالجات
logger.addHandler(file_handler)
logger.addHandler(error_handler)

# مسجل منفصل للطلبات
request_logger = logging.getLogger("requests")
request_logger.setLevel(logging.INFO)
request_logger.addHandler(request_handler)

# ========== إعدادات الأداء المتقدمة ==========
executor = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)

# ========== Rate Limiting محسّن (جاهز للتوسع مع Redis) ==========
class RateLimiter:
    """محدد معدل الطلبات مع دعم Redis (للإنتاج)"""
    def __init__(self, max_requests: int = 100, window_seconds: int = 60, use_redis: bool = False):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.use_redis = use_redis
        self.requests = defaultdict(list)  # للاستخدام المحلي
        
    def is_allowed(self, client_id: str) -> bool:
        if self.use_redis:
            # TODO: تنفيذ مع Redis
            return self._check_redis(client_id)
        return self._check_memory(client_id)
    
    def _check_memory(self, client_id: str) -> bool:
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        # تنظيف الطلبات القديمة
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > window_start
        ]
        
        return len(self.requests[client_id]) < self.max_requests
    
    def _check_redis(self, client_id: str) -> bool:
        # للاستخدام المستقبلي مع Redis
        return True
    
    def add_request(self, client_id: str):
        if not self.use_redis:
            self.requests[client_id].append(datetime.now())
    
    def get_remaining(self, client_id: str) -> int:
        if self.use_redis:
            return self.max_requests  # TODO: مع Redis
        return max(0, self.max_requests - len(self.requests.get(client_id, [])))
    
    def get_stats(self) -> dict:
        """إحصائيات Rate Limiter"""
        return {
            "max_requests": self.max_requests,
            "window_seconds": self.window_seconds,
            "active_clients": len(self.requests) if not self.use_redis else 0
        }

rate_limiter = RateLimiter(max_requests=100, window_seconds=60)

# ========== أنواع النتائج ==========
class ResultType(str, Enum):
    NUMBER = "number"
    COMPLEX = "complex"
    EXPRESSION = "expression"
    STRING = "string"
    MATRIX = "matrix"
    ERROR = "error"
    IMAGE = "image"
    IMAGE_URL = "image_url"

# ========== إعدادات الرسوم البيانية ==========
class PlotTheme(str, Enum):
    LIGHT = "light"
    DARK = "dark"
    BLUE = "blue"
    GREEN = "green"
    CUSTOM = "custom"

class PlotFormat(str, Enum):
    PNG = "png"
    SVG = "svg"
    JPEG = "jpeg"
    PDF = "pdf"

class PlotDirection(str, Enum):
    PLUS = "+"
    MINUS = "-"
    BOTH = "+-"

# ========== التحقق المتقدم من صحة المدخلات ==========
def validate_expression_safe(expr: str) -> bool:
    """التحقق المتقدم من صحة وأمان التعبير الرياضي"""
    if not expr or len(expr) > 1000:
        return False
    
    # قائمة بالأنماط الخطيرة
    dangerous_patterns = [
        r'__.*__',                    # double underscore methods
        r'import\s+',                  # import statements
        r'eval\s*\(',                   # eval
        r'exec\s*\(',                   # exec
        r'globals\s*\(',                # globals
        r'locals\s*\(',                 # locals
        r'getattr\s*\(',                # getattr
        r'setattr\s*\(',                # setattr
        r'open\s*\(',                   # open files
        r'file\s*\(',                   # file operations
        r'os\.',                         # os module
        r'sys\.',                        # sys module
        r'subprocess',                   # subprocess
        r'__builtins__',                 # builtins
        r'\[.*for.*in.*\]',              # list comprehensions (قد تكون خطيرة)
        r'\{.*:.*for.*in.*\}',            # dict comprehensions
        r'lambda.*:.*\(.*\)',             # complex lambdas
    ]
    
    expr_lower = expr.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, expr_lower):
            logger.warning(f"Dangerous pattern detected: {pattern} in {expr[:50]}")
            return False
    
    # التحقق من توازن الأقواس
    if expr.count('(') != expr.count(')'):
        return False
    
    return True

# ========== دوال مساعدة محسّنة (في الأعلى) ==========
def get_client_id(request: Request) -> str:
    """الحصول على معرف العميل مع دعم الوكيل"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # قد تكون هناك عدة عناوين
        return forwarded.split(",")[0].strip()
    
    # استخدام IP العميل
    client_host = request.client.host if request.client else "unknown"
    
    # إضافة بصمة للمستخدم (يمكن استخدام User-Agent)
    user_agent = request.headers.get("User-Agent", "")
    # إنشاء معرف فريد من IP + User-Agent
    unique_id = hashlib.md5(f"{client_host}:{user_agent}".encode()).hexdigest()[:16]
    return unique_id

def generate_image_url(filename: str) -> str:
    """توليد رابط آمن للصورة"""
    return f"/static/plots/{filename}"

def save_plot_image(image_data: str, format: str) -> str:
    """حفظ صورة وإرجاع اسم الملف"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = uuid.uuid4().hex[:8]
    filename = f"plot_{timestamp}_{unique_id}.{format}"
    filepath = plots_dir / filename
    
    # فك تشفير Base64
    if image_data.startswith('data:image'):
        image_data = image_data.split(',')[1]
    
    try:
        image_bytes = base64.b64decode(image_data)
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        # حذف الصور القديمة (أقدم من ساعة)
        cleanup_old_plots()
        
        return filename
    except Exception as e:
        logger.error(f"Error saving plot image: {e}")
        raise

def cleanup_old_plots(hours: int = 1):
    """تنظيف الصور القديمة"""
    try:
        now = time.time()
        for file in plots_dir.glob("plot_*.png"):
            if now - file.stat().st_mtime > hours * 3600:
                file.unlink()
    except Exception as e:
        logger.error(f"Error cleaning old plots: {e}")

def format_result_with_type(result: Any) -> Dict[str, Any]:
    """تنسيق النتيجة مع تحديد نوعها بدقة"""
    if result is None:
        return {
            "value": None,
            "type": ResultType.STRING,
            "string": "لا توجد نتيجة"
        }
    
    if isinstance(result, (int, float)):
        # التحقق من القيم الخاصة
        if result == float('inf'):
            return {
                "value": "∞",
                "type": ResultType.STRING,
                "string": "∞"
            }
        if result == float('-inf'):
            return {
                "value": "-∞",
                "type": ResultType.STRING,
                "string": "-∞"
            }
        if isinstance(result, float) and result != result:  # NaN
            return {
                "value": "غير معرف",
                "type": ResultType.STRING,
                "string": "NaN"
            }
        
        return {
            "value": float(result),
            "type": ResultType.NUMBER,
            "string": str(result)
        }
    
    elif isinstance(result, complex):
        real = result.real
        imag = result.imag
        # تنظيف القيم الصغيرة جداً
        if abs(real) < 1e-10:
            real = 0
        if abs(imag) < 1e-10:
            imag = 0
        
        return {
            "value": {
                "real": real,
                "imag": imag
            },
            "type": ResultType.COMPLEX,
            "string": str(result)
        }
    
    elif isinstance(result, str):
        if result.startswith("خطأ") or "error" in result.lower():
            return {
                "value": result,
                "type": ResultType.ERROR,
                "string": result
            }
        
        # الكشف عن التعبيرات الرياضية
        math_patterns = ['x', 'y', 'z', 'sin', 'cos', 'tan', 'log', 'ln', 
                        '∫', '∑', 'lim', '√', 'π', 'e', '^', '**', '(', ')']
        if any(p in result for p in math_patterns):
            return {
                "value": result,
                "type": ResultType.EXPRESSION,
                "string": result
            }
        
        return {
            "value": result,
            "type": ResultType.STRING,
            "string": result
        }
    
    elif hasattr(result, 'tolist'):  # مصفوفة
        return {
            "value": result.tolist(),
            "type": ResultType.MATRIX,
            "string": str(result)
        }
    
    else:
        return {
            "value": str(result),
            "type": ResultType.STRING,
            "string": str(result)
        }

async def run_heavy_operation(func, *args, **kwargs):
    """تشغيل عملية ثقيلة في ThreadPool مع معالجة الأخطاء (باستخدام asyncio.to_thread)"""
    try:
        # استخدام asyncio.to_thread بدلاً من loop.run_in_executor (أوضح)
        return await asyncio.to_thread(lambda: func(*args, **kwargs))
    except Exception as e:
        logger.error(f"Error in heavy operation: {e}", exc_info=True)
        raise  # نرفع الاستثناء لمعالجته في endpoint

# ========== تهيئة التطبيق ==========
app = FastAPI(
    title="🧮 آلة حاسبة علمية API - النسخة الإنتاجية",
    description="""
    ## API متكامل للآلة الحاسبة العلمية
    
    ### المميزات المتقدمة:
    * ✅ عمليات حسابية أساسية ومتقدمة
    * ✅ دوال مثلثية وزائدية ولوغاريتمية
    * ✅ حل معادلات ونظم معادلات
    * ✅ تفاضل وتكامل ونهايات
    * ✅ تبسيط وفك وتحليل تعابير جبرية
    * ✅ توافقيات (nCr, nPr)
    * ✅ رسوم بيانية متقدمة (PNG, SVG, PDF)
    * ✅ ذاكرة (M+, M-, MR, MC)
    * ✅ إحصائيات وسجل عمليات
    * ✅ Rate Limiting مدمج مع إحصائيات
    * ✅ تسجيل يومي للطلبات والأخطاء
    * ✅ التحقق المتقدم من صحة المدخلات
    * ✅ دعم غير متزامن مع ThreadPool
    * ✅ توثيق كامل باللغتين
    """,
    version="5.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "فريق التطوير",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
)

# إعداد CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تهيئة الآلة الحاسبة
calc = Calculator()

# التأكد من وجود المجلدات
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
plots_dir = Path("static/plots")
plots_dir.mkdir(exist_ok=True)
temp_dir = Path("temp")
temp_dir.mkdir(exist_ok=True)

# إنشاء ملفات __init__.py لضمان عمل المجلدات كـ packages
for dir_path in [static_dir, plots_dir, temp_dir, LOG_DIR]:
    init_file = dir_path / "__init__.py"
    if not init_file.exists():
        init_file.touch()

# توجيه المجلد الثابت
app.mount("/static", StaticFiles(directory="static"), name="static")

# ========== نماذج البيانات الكاملة ==========
class ExpressionRequest(BaseModel):
    expression: str = Field(..., description="التعبير الرياضي", min_length=1, max_length=1000)
    
    @validator('expression')
    def validate_expression(cls, v):
        if not validate_expression_safe(v):
            raise ValueError('تعبير غير صالح أو يحتوي على أحرف خطيرة')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "expression": "sin(30) + cos(60)"
            }
        }

class SolveRequest(BaseModel):
    equation: str = Field(..., description="المعادلة", min_length=1, max_length=1000)
    
    @validator('equation')
    def validate_equation(cls, v):
        if not validate_expression_safe(v):
            raise ValueError('معادلة غير صالحة')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "equation": "x^2 - 5x + 6 = 0"
            }
        }

class SystemSolveRequest(BaseModel):
    equations: List[str] = Field(..., description="قائمة المعادلات", min_items=1, max_items=10)
    
    @validator('equations')
    def validate_equations(cls, v):
        for eq in v:
            if not validate_expression_safe(eq):
                raise ValueError(f'معادلة غير صالحة: {eq}')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "equations": ["x+y=5", "x-y=1"]
            }
        }

class SimplifyRequest(BaseModel):
    expression: str = Field(..., description="التعبير", min_length=1, max_length=1000)
    
    @validator('expression')
    def validate_expression(cls, v):
        if not validate_expression_safe(v):
            raise ValueError('تعبير غير صالح')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "expression": "(x^2-1)/(x-1)"
            }
        }

class ExpandRequest(BaseModel):
    expression: str = Field(..., description="التعبير", min_length=1, max_length=1000)
    
    @validator('expression')
    def validate_expression(cls, v):
        if not validate_expression_safe(v):
            raise ValueError('تعبير غير صالح')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "expression": "(x+2)^2"
            }
        }

class FactorRequest(BaseModel):
    expression: str = Field(..., description="التعبير", min_length=1, max_length=1000)
    
    @validator('expression')
    def validate_expression(cls, v):
        if not validate_expression_safe(v):
            raise ValueError('تعبير غير صالح')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "expression": "x^2-5x+6"
            }
        }

class DiffRequest(BaseModel):
    expression: str = Field(..., description="الدالة", min_length=1, max_length=1000)
    var: str = Field("x", description="متغير الاشتقاق", regex="^[a-zA-Z]$")
    order: int = Field(1, description="رتبة المشتقة", ge=1, le=10)
    
    @validator('expression')
    def validate_expression(cls, v):
        if not validate_expression_safe(v):
            raise ValueError('تعبير غير صالح')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "expression": "x^3",
                "var": "x",
                "order": 2
            }
        }

class IntegrateRequest(BaseModel):
    expression: str = Field(..., description="الدالة", min_length=1, max_length=1000)
    var: str = Field("x", description="متغير التكامل", regex="^[a-zA-Z]$")
    lower: Optional[float] = Field(None, description="الحد الأدنى")
    upper: Optional[float] = Field(None, description="الحد الأعلى")
    
    @validator('expression')
    def validate_expression(cls, v):
        if not validate_expression_safe(v):
            raise ValueError('تعبير غير صالح')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "expression": "x^2",
                "lower": 0,
                "upper": 1
            }
        }

class LimitRequest(BaseModel):
    expression: str = Field(..., description="الدالة", min_length=1, max_length=1000)
    var: str = Field("x", description="المتغير", regex="^[a-zA-Z]$")
    approach: str = Field("0", description="قيمة الاقتراب")
    direction: PlotDirection = Field(PlotDirection.PLUS, description="الاتجاه (+ أو - أو +-)")
    
    @validator('expression')
    def validate_expression(cls, v):
        if not validate_expression_safe(v):
            raise ValueError('تعبير غير صالح')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "expression": "1/x",
                "approach": "0",
                "direction": "+"
            }
        }

class PlotRequest(BaseModel):
    expression: str = Field(..., description="الدالة", min_length=1, max_length=1000)
    xmin: float = Field(-10, description="الحد الأدنى")
    xmax: float = Field(10, description="الحد الأعلى")
    points: int = Field(1000, description="عدد النقاط", ge=100, le=10000)
    title: Optional[str] = Field(None, description="عنوان الرسم")
    xlabel: Optional[str] = Field(None, description="عنوان المحور x")
    ylabel: Optional[str] = Field(None, description="عنوان المحور y")
    width: int = Field(800, description="العرض", ge=200, le=2000)
    height: int = Field(500, description="الارتفاع", ge=200, le=2000)
    format: PlotFormat = Field(PlotFormat.PNG, description="صيغة الصورة")
    theme: PlotTheme = Field(PlotTheme.LIGHT, description="ثيم الرسم")
    grid: bool = Field(True, description="عرض شبكة")
    show_legend: bool = Field(True, description="عرض وسيلة الإيضاح")
    return_url: bool = Field(False, description="إرجاع رابط الصورة بدلاً من Base64")
    
    @validator('expression')
    def validate_expression(cls, v):
        if not validate_expression_safe(v):
            raise ValueError('تعبير غير صالح')
        return v
    
    @validator('xmax')
    def validate_range(cls, v, values):
        if 'xmin' in values and v <= values['xmin']:
            raise ValueError('xmax يجب أن يكون أكبر من xmin')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "expression": "sin(x)",
                "xmin": -10,
                "xmax": 10,
                "title": "دالة الجيب",
                "theme": "light",
                "grid": True
            }
        }

class MultiPlotRequest(BaseModel):
    expressions: List[str] = Field(..., description="قائمة الدوال", min_items=1, max_items=10)
    labels: Optional[List[str]] = Field(None, description="تسميات الدوال")
    xmin: float = Field(-10, description="الحد الأدنى")
    xmax: float = Field(10, description="الحد الأعلى")
    points: int = Field(1000, description="عدد النقاط", ge=100, le=10000)
    title: Optional[str] = Field(None, description="عنوان الرسم")
    theme: PlotTheme = Field(PlotTheme.LIGHT, description="ثيم الرسم")
    grid: bool = Field(True, description="عرض شبكة")
    
    @validator('expressions')
    def validate_expressions(cls, v):
        for expr in v:
            if not validate_expression_safe(expr):
                raise ValueError(f'تعبير غير صالح: {expr}')
        return v
    
    @validator('xmax')
    def validate_range(cls, v, values):
        if 'xmin' in values and v <= values['xmin']:
            raise ValueError('xmax يجب أن يكون أكبر من xmin')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "expressions": ["sin(x)", "cos(x)"],
                "labels": ["sin", "cos"],
                "theme": "light"
            }
        }

class MemoryValueRequest(BaseModel):
    value: float = Field(..., description="القيمة")
    
    class Config:
        json_schema_extra = {
            "example": {"value": 5}
        }

class NCRRequest(BaseModel):
    n: int = Field(..., description="العدد الكلي", ge=0, le=1000)
    r: int = Field(..., description="عدد الاختيارات", ge=0, le=1000)
    
    @validator('r')
    def validate_r(cls, v, values):
        if 'n' in values and v > values['n']:
            raise ValueError('r يجب أن يكون <= n')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {"n": 5, "r": 2}
        }

class NPRRequest(BaseModel):
    n: int = Field(..., description="العدد الكلي", ge=0, le=1000)
    r: int = Field(..., description="عدد الاختيارات", ge=0, le=1000)
    
    @validator('r')
    def validate_r(cls, v, values):
        if 'n' in values and v > values['n']:
            raise ValueError('r يجب أن يكون <= n')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {"n": 5, "r": 2}
        }

# ========== تتبع الطلبات ==========
class RequestTracker:
    def __init__(self):
        self.start_time = time.time()
        self.count = 0
        self.errors = 0
        self.total_time = 0
    
    def increment(self, is_error=False, process_time=0):
        self.count += 1
        if is_error:
            self.errors += 1
        self.total_time += process_time
    
    def get_stats(self):
        uptime = time.time() - self.start_time
        avg_time = self.total_time / self.count if self.count > 0 else 0
        return {
            "uptime": uptime,
            "uptime_formatted": str(timedelta(seconds=int(uptime))),
            "requests": self.count,
            "errors": self.errors,
            "success_rate": f"{(self.count - self.errors)/self.count*100:.1f}%" if self.count > 0 else "100%",
            "avg_response_time": f"{avg_time:.3f}s",
            "total_time_seconds": round(self.total_time, 2)
        }

tracker = RequestTracker()

# ========== Middleware محسّن مع تخطي المسارات الثابتة ==========
@app.middleware("http")
async def track_and_rate_limit(request: Request, call_next):
    # مسار الطلب
    path = request.url.path
    
    # قائمة المسارات المستثناة من Rate Limiting
    excluded_paths = ["/static", "/docs", "/redoc", "/openapi.json"]
    if any(path.startswith(p) for p in excluded_paths):
        return await call_next(request)
    
    # الحصول على معرف العميل
    client_id = get_client_id(request)
    
    # التحقق من Rate Limit
    if not rate_limiter.is_allowed(client_id):
        logger.warning(f"Rate limit exceeded for {client_id} on {path}")
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "error": "تم تجاوز الحد المسموح من الطلبات. الرجاء الانتظار.",
                "retry_after": rate_limiter.window_seconds
            }
        )
    
    # إضافة الطلب
    rate_limiter.add_request(client_id)
    
    # تتبع وقت البدء
    start_time = time.time()
    
    # معالجة الطلب
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Unhandled exception for {client_id}: {e}", exc_info=True)
        process_time = time.time() - start_time
        tracker.increment(is_error=True, process_time=process_time)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "خطأ داخلي في الخادم"
            }
        )
    
    # حساب وقت التنفيذ
    process_time = time.time() - start_time
    
    # تسجيل الطلب
    is_error = response.status_code >= 400
    tracker.increment(is_error, process_time)
    
    request_logger.info(
        f"{client_id} - {request.method} {path} - "
        f"{response.status_code} - {process_time:.3f}s"
    )
    
    # إضافة headers
    response.headers["X-Process-Time"] = f"{process_time:.3f}"
    response.headers["X-Rate-Limit-Remaining"] = str(rate_limiter.get_remaining(client_id))
    response.headers["X-Rate-Limit-Limit"] = str(rate_limiter.max_requests)
    
    return response

# ========== نقاط نهاية متوافقة مع الإصدارات القديمة ==========
@app.post("/solve", include_in_schema=False)
async def solve_compat(request: Request, data: SolveRequest):
    """نقطة نهاية متوافقة مع الإصدار القديم - /solve"""
    return await solve(request, data)

@app.get("/health", include_in_schema=False)
async def health_compat(request: Request):
    """نقطة نهاية متوافقة مع الإصدار القديم - /health"""
    return await health_check(request)

@app.post("/calculate", include_in_schema=False)
async def calculate_compat(request: Request, data: ExpressionRequest):
    """نقطة نهاية متوافقة مع الإصدار القديم - /calculate"""
    return await calculate(request, data)

# ========== الصفحة الرئيسية ==========
@app.get("/", response_class=HTMLResponse)
async def root():
    """الصفحة الرئيسية"""
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <title>آلة حاسبة علمية API - النسخة الإنتاجية</title>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
            .container {{ max-width: 1000px; margin: auto; background: white; padding: 30px; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }}
            h1 {{ color: #333; text-align: center; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }}
            .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; }}
            .stat-value {{ font-size: 2em; font-weight: bold; color: #667eea; }}
            .endpoint {{ background: #f1f3f5; padding: 15px; margin: 10px 0; border-radius: 10px; }}
            code {{ background: #e9ecef; padding: 2px 5px; border-radius: 3px; }}
            a {{ color: #667eea; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧮 آلة حاسبة علمية API - النسخة الإنتاجية v5.1.0</h1>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">{tracker.get_stats()['requests']}</div>
                    <div>طلبات</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{tracker.get_stats()['uptime_formatted']}</div>
                    <div>وقت التشغيل</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{tracker.get_stats()['success_rate']}</div>
                    <div>نسبة النجاح</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{tracker.get_stats()['avg_response_time']}</div>
                    <div>متوسط وقت الاستجابة</div>
                </div>
            </div>
            
            <h3>📚 روابط سريعة:</h3>
            <div class="endpoint">
                <strong>📘 توثيق API:</strong> <a href="/docs">/docs</a> (Swagger UI)
            </div>
            <div class="endpoint">
                <strong>📗 توثيق بديل:</strong> <a href="/redoc">/redoc</a> (ReDoc)
            </div>
            <div class="endpoint">
                <strong>🔍 التحقق من الصحة:</strong> <a href="/api/health">/api/health</a>
            </div>
            <div class="endpoint">
                <strong>📊 إحصائيات مفصلة:</strong> <a href="/api/stats">/api/stats</a>
            </div>
            <div class="endpoint">
                <strong>📋 سجل العمليات:</strong> <a href="/api/history">/api/history</a>
            </div>
        </div>
    </body>
    </html>
    """)

# ========== نقاط النهاية الأساسية (مع وقت تنفيذ دقيق) ==========
@app.post("/api/calculate",
          summary="حساب تعبير رياضي",
          description="حساب أي تعبير رياضي مع التحقق المتقدم من الصحة")
async def calculate(request: Request, data: ExpressionRequest):
    """حساب تعبير رياضي"""
    client_id = get_client_id(request)
    logger.info(f"Calculate request from {client_id}: {data.expression}")
    
    start_time = time.time()
    
    try:
        result = await run_heavy_operation(calc.calculate, data.expression)
        formatted = format_result_with_type(result)
        execution_time = time.time() - start_time
        
        return {
            "success": True,
            **formatted,
            "execution_time": execution_time
        }
    except Exception as e:
        logger.error(f"Calculate error for {client_id}: {str(e)}", exc_info=True)
        execution_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "type": ResultType.ERROR,
            "execution_time": execution_time
        }

@app.post("/api/solve",
          summary="حل معادلة",
          description="حل معادلة واحدة مع التحقق المتقدم")
async def solve(request: Request, data: SolveRequest):
    """حل معادلة"""
    client_id = get_client_id(request)
    logger.info(f"Solve request from {client_id}: {data.equation}")
    
    start_time = time.time()
    
    try:
        result = await run_heavy_operation(calc.solve_equation, data.equation)
        formatted = format_result_with_type(result)
        execution_time = time.time() - start_time
        
        return {
            "success": True,
            **formatted,
            "execution_time": execution_time
        }
    except Exception as e:
        logger.error(f"Solve error for {client_id}: {str(e)}", exc_info=True)
        execution_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "type": ResultType.ERROR,
            "execution_time": execution_time
        }

@app.post("/api/solve_system",
          summary="حل نظام معادلات",
          description="حل نظام من معادلتين أو أكثر")
async def solve_system(request: Request, data: SystemSolveRequest):
    """حل نظام معادلات"""
    client_id = get_client_id(request)
    logger.info(f"Solve system request from {client_id}: {data.equations}")
    
    start_time = time.time()
    
    try:
        # محاولة استخدام دالة مخصصة لحل الأنظمة إذا كانت موجودة
        if hasattr(calc, 'solve_system'):
            result = await run_heavy_operation(calc.solve_system, data.equations)
        else:
            # دمج المعادلات بصيغة مناسبة
            equations_str = "; ".join(data.equations)
            result = await run_heavy_operation(calc.solve_equation, equations_str)
        
        formatted = format_result_with_type(result)
        execution_time = time.time() - start_time
        
        return {
            "success": True,
            **formatted,
            "equations": data.equations,
            "execution_time": execution_time
        }
    except Exception as e:
        logger.error(f"Solve system error for {client_id}: {str(e)}", exc_info=True)
        execution_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "type": ResultType.ERROR,
            "execution_time": execution_time
        }

@app.post("/api/simplify",
          summary="تبسيط تعبير",
          description="تبسيط تعبير جبري مع التحقق")
async def simplify(request: Request, data: SimplifyRequest):
    """تبسيط تعبير"""
    client_id = get_client_id(request)
    logger.info(f"Simplify request from {client_id}: {data.expression}")
    
    start_time = time.time()
    
    try:
        result = await run_heavy_operation(calc.simplify, data.expression)
        formatted = format_result_with_type(result)
        execution_time = time.time() - start_time
        
        return {
            "success": True,
            **formatted,
            "execution_time": execution_time
        }
    except Exception as e:
        logger.error(f"Simplify error for {client_id}: {str(e)}", exc_info=True)
        execution_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "type": ResultType.ERROR,
            "execution_time": execution_time
        }

@app.post("/api/expand",
          summary="فك الأقواس",
          description="فك أقواس تعبير جبري")
async def expand(request: Request, data: ExpandRequest):
    """فك الأقواس"""
    client_id = get_client_id(request)
    logger.info(f"Expand request from {client_id}: {data.expression}")
    
    start_time = time.time()
    
    try:
        result = await run_heavy_operation(calc.expand, data.expression)
        formatted = format_result_with_type(result)
        execution_time = time.time() - start_time
        
        return {
            "success": True,
            **formatted,
            "execution_time": execution_time
        }
    except Exception as e:
        logger.error(f"Expand error for {client_id}: {str(e)}", exc_info=True)
        execution_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "type": ResultType.ERROR,
            "execution_time": execution_time
        }

@app.post("/api/factor",
          summary="تحليل إلى عوامل",
          description="تحليل تعبير جبري إلى عوامله الأولية")
async def factor(request: Request, data: FactorRequest):
    """تحليل إلى عوامل"""
    client_id = get_client_id(request)
    logger.info(f"Factor request from {client_id}: {data.expression}")
    
    start_time = time.time()
    
    try:
        result = await run_heavy_operation(calc.factor, data.expression)
        formatted = format_result_with_type(result)
        execution_time = time.time() - start_time
        
        return {
            "success": True,
            **formatted,
            "execution_time": execution_time
        }
    except Exception as e:
        logger.error(f"Factor error for {client_id}: {str(e)}", exc_info=True)
        execution_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "type": ResultType.ERROR,
            "execution_time": execution_time
        }

@app.post("/api/diff",
          summary="مشتقة",
          description="إيجاد مشتقة دالة")
async def diff(request: Request, data: DiffRequest):
    """مشتقة"""
    client_id = get_client_id(request)
    logger.info(f"Diff request from {client_id}: {data.expression}")
    
    start_time = time.time()
    
    try:
        result = await run_heavy_operation(
            calc.diff, 
            data.expression, 
            data.var, 
            data.order
        )
        formatted = format_result_with_type(result)
        execution_time = time.time() - start_time
        
        return {
            "success": True,
            **formatted,
            "var": data.var,
            "order": data.order,
            "execution_time": execution_time
        }
    except Exception as e:
        logger.error(f"Diff error for {client_id}: {str(e)}", exc_info=True)
        execution_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "type": ResultType.ERROR,
            "execution_time": execution_time
        }

@app.post("/api/integrate",
          summary="تكامل",
          description="تكامل دالة (محدد أو غير محدد)")
async def integrate(request: Request, data: IntegrateRequest):
    """تكامل"""
    client_id = get_client_id(request)
    logger.info(f"Integrate request from {client_id}: {data.expression}")
    
    start_time = time.time()
    
    try:
        result = await run_heavy_operation(
            calc.integrate,
            data.expression,
            data.var,
            data.lower,
            data.upper
        )
        formatted = format_result_with_type(result)
        execution_time = time.time() - start_time
        
        return {
            "success": True,
            **formatted,
            "var": data.var,
            "is_definite": data.lower is not None and data.upper is not None,
            "execution_time": execution_time
        }
    except Exception as e:
        logger.error(f"Integrate error for {client_id}: {str(e)}", exc_info=True)
        execution_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "type": ResultType.ERROR,
            "execution_time": execution_time
        }

@app.post("/api/limit",
          summary="نهاية",
          description="إيجاد نهاية دالة عند نقطة معينة (مع الاتجاه)")
async def limit(request: Request, data: LimitRequest):
    """نهاية"""
    client_id = get_client_id(request)
    logger.info(f"Limit request from {client_id}: {data.expression}")
    
    start_time = time.time()
    
    try:
        # تحويل الاتجاه إلى صيغة مناسبة
        dir_param = data.direction.value if data.direction else "+"
        
        result = await run_heavy_operation(
            calc.limit,
            data.expression,
            data.var,
            data.approach,
            dir_param
        )
        formatted = format_result_with_type(result)
        execution_time = time.time() - start_time
        
        return {
            "success": True,
            **formatted,
            "var": data.var,
            "approach": data.approach,
            "direction": data.direction.value,
            "execution_time": execution_time
        }
    except Exception as e:
        logger.error(f"Limit error for {client_id}: {str(e)}", exc_info=True)
        execution_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "type": ResultType.ERROR,
            "execution_time": execution_time
        }

@app.post("/api/plot",
          summary="رسم دالة",
          description="رسم دالة مع خيارات متقدمة")
async def plot(request: Request, data: PlotRequest):
    """رسم دالة مع خيارات متقدمة"""
    client_id = get_client_id(request)
    logger.info(f"Plot request from {client_id}: {data.expression}")
    
    start_time = time.time()
    
    try:
        # استخدام kwargs مع التأكد من وجود calc.plot
        if not hasattr(calc, 'plot'):
            return {
                "success": False,
                "error": "دالة الرسم غير متوفرة في المحرك",
                "execution_time": time.time() - start_time
            }
        
        plot_kwargs = {
            "expression": data.expression,
            "limits": (data.xmin, data.xmax),
            "points": data.points,
            "show": False,
            "title": data.title,
            "xlabel": data.xlabel,
            "ylabel": data.ylabel,
            "theme": data.theme.value if data.theme != PlotTheme.CUSTOM else None,
            "grid": data.grid,
            "show_legend": data.show_legend,
            "width": data.width,
            "height": data.height
        }
        
        # التحقق من أن calc.plot تقبل kwargs
        try:
            img_base64 = await run_heavy_operation(
                lambda: calc.plot(**plot_kwargs)
            )
        except TypeError:
            # إذا كانت calc.plot لا تقبل kwargs، استخدم المعاملات بالترتيب
            logger.warning(f"calc.plot does not accept **kwargs, using positional args")
            img_base64 = await run_heavy_operation(
                calc.plot,
                data.expression,
                (data.xmin, data.xmax),
                data.points,
                False,
                data.title,
                data.theme.value if data.theme != PlotTheme.CUSTOM else None,
                data.grid,
                data.show_legend
            )
        
        execution_time = time.time() - start_time
        
        if img_base64 and isinstance(img_base64, str):
            if data.return_url:
                # حفظ الصورة وإرجاع رابط
                filename = save_plot_image(img_base64, data.format.value)
                image_url = generate_image_url(filename)
                return {
                    "success": True,
                    "image_url": image_url,
                    "type": ResultType.IMAGE_URL,
                    "format": data.format.value,
                    "width": data.width,
                    "height": data.height,
                    "execution_time": execution_time
                }
            else:
                # إرجاع Base64
                return {
                    "success": True,
                    "image": img_base64,
                    "type": ResultType.IMAGE,
                    "format": data.format.value,
                    "width": data.width,
                    "height": data.height,
                    "execution_time": execution_time
                }
        else:
            return {
                "success": False,
                "error": "فشل في إنشاء الرسم",
                "execution_time": execution_time
            }
    except Exception as e:
        logger.error(f"Plot error for {client_id}: {str(e)}", exc_info=True)
        execution_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "type": ResultType.ERROR,
            "execution_time": execution_time
        }

@app.post("/api/plot_multiple",
          summary="رسم دوال متعددة",
          description="رسم عدة دوال في نفس الرسم البياني")
async def plot_multiple(request: Request, data: MultiPlotRequest):
    """رسم دوال متعددة"""
    client_id = get_client_id(request)
    logger.info(f"Multi plot request from {client_id}: {data.expressions}")
    
    start_time = time.time()
    
    try:
        if not hasattr(calc, 'plot_multiple'):
            return {
                "success": False,
                "error": "دالة الرسم المتعدد غير متوفرة في المحرك",
                "execution_time": time.time() - start_time
            }
        
        img_base64 = await run_heavy_operation(
            calc.plot_multiple,
            data.expressions,
            'x',
            (data.xmin, data.xmax),
            data.labels,
            False,
            data.title,
            data.theme.value if data.theme != PlotTheme.CUSTOM else None,
            data.grid
        )
        
        execution_time = time.time() - start_time
        
        if img_base64 and isinstance(img_base64, str):
            return {
                "success": True,
                "image": img_base64,
                "type": ResultType.IMAGE,
                "expressions": data.expressions,
                "count": len(data.expressions),
                "execution_time": execution_time
            }
        else:
            return {
                "success": False,
                "error": "فشل في إنشاء الرسم",
                "execution_time": execution_time
            }
    except Exception as e:
        logger.error(f"Multi plot error for {client_id}: {str(e)}", exc_info=True)
        execution_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "type": ResultType.ERROR,
            "execution_time": execution_time
        }

@app.post("/api/ncr",
          summary="عدد التوافيق C(n,r)",
          description="حساب عدد التوافيق مع التحقق")
async def ncr(request: Request, data: NCRRequest):
    """عدد التوافيق"""
    client_id = get_client_id(request)
    logger.info(f"NCR request from {client_id}: C({data.n}, {data.r})")
    
    start_time = time.time()
    
    try:
        result = calc.nCr(data.n, data.r)
        execution_time = time.time() - start_time
        
        return {
            "success": True,
            "result": result,
            "type": ResultType.NUMBER,
            "formula": f"C({data.n}, {data.r})",
            "execution_time": execution_time
        }
    except Exception as e:
        logger.error(f"NCR error for {client_id}: {str(e)}", exc_info=True)
        execution_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "type": ResultType.ERROR,
            "execution_time": execution_time
        }

@app.post("/api/npr",
          summary="عدد التباديل P(n,r)",
          description="حساب عدد التباديل مع التحقق")
async def npr(request: Request, data: NPRRequest):
    """عدد التباديل"""
    client_id = get_client_id(request)
    logger.info(f"NPR request from {client_id}: P({data.n}, {data.r})")
    
    start_time = time.time()
    
    try:
        result = calc.nPr(data.n, data.r)
        execution_time = time.time() - start_time
        
        return {
            "success": True,
            "result": result,
            "type": ResultType.NUMBER,
            "formula": f"P({data.n}, {data.r})",
            "execution_time": execution_time
        }
    except Exception as e:
        logger.error(f"NPR error for {client_id}: {str(e)}", exc_info=True)
        execution_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "type": ResultType.ERROR,
            "execution_time": execution_time
        }

@app.get("/api/memory",
         summary="استدعاء الذاكرة",
         description="إرجاع القيمة المخزنة في الذاكرة")
async def memory_recall(request: Request):
    """استدعاء الذاكرة"""
    client_id = get_client_id(request)
    logger.info(f"Memory recall from {client_id}")
    
    start_time = time.time()
    
    try:
        result = calc.mr()
        execution_time = time.time() - start_time
        
        return {
            "success": True,
            "value": result,
            "type": ResultType.NUMBER,
            "execution_time": execution_time
        }
    except Exception as e:
        logger.error(f"Memory recall error for {client_id}: {str(e)}", exc_info=True)
        execution_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "type": ResultType.ERROR,
            "execution_time": execution_time
        }

@app.post("/api/memory/clear",
          summary="مسح الذاكرة",
          description="مسح القيمة المخزنة في الذاكرة")
async def memory_clear(request: Request):
    """مسح الذاكرة"""
    client_id = get_client_id(request)
    logger.info(f"Memory clear from {client_id}")
    
    start_time = time.time()
    
    try:
        result = calc.mc()
        execution_time = time.time() - start_time
        
        return {
            "success": True,
            "message": result,
            "execution_time": execution_time
        }
    except Exception as e:
        logger.error(f"Memory clear error for {client_id}: {str(e)}", exc_info=True)
        execution_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "type": ResultType.ERROR,
            "execution_time": execution_time
        }

@app.post("/api/memory/add",
          summary="إضافة إلى الذاكرة",
          description="إضافة قيمة إلى الذاكرة (M+)")
async def memory_add(request: Request, data: MemoryValueRequest):
    """إضافة إلى الذاكرة"""
    client_id = get_client_id(request)
    logger.info(f"Memory add from {client_id}: +{data.value}")
    
    start_time = time.time()
    
    try:
        result = calc.m_plus(data.value)
        memory = calc.mr()
        execution_time = time.time() - start_time
        
        return {
            "success": True,
            "message": result,
            "memory": memory,
            "execution_time": execution_time
        }
    except Exception as e:
        logger.error(f"Memory add error for {client_id}: {str(e)}", exc_info=True)
        execution_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "type": ResultType.ERROR,
            "execution_time": execution_time
        }

@app.post("/api/memory/subtract",
          summary="طرح من الذاكرة",
          description="طرح قيمة من الذاكرة (M-)")
async def memory_subtract(request: Request, data: MemoryValueRequest):
    """طرح من الذاكرة"""
    client_id = get_client_id(request)
    logger.info(f"Memory subtract from {client_id}: -{data.value}")
    
    start_time = time.time()
    
    try:
        result = calc.m_minus(data.value)
        memory = calc.mr()
        execution_time = time.time() - start_time
        
        return {
            "success": True,
            "message": result,
            "memory": memory,
            "execution_time": execution_time
        }
    except Exception as e:
        logger.error(f"Memory subtract error for {client_id}: {str(e)}", exc_info=True)
        execution_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "type": ResultType.ERROR,
            "execution_time": execution_time
        }

@app.get("/api/random",
         summary="رقم عشوائي",
         description="توليد رقم عشوائي بين قيمتين")
async def random_number(
    request: Request,
    a: float = Query(0, description="الحد الأدنى"),
    b: float = Query(1, description="الحد الأقصى")
):
    """رقم عشوائي"""
    client_id = get_client_id(request)
    logger.info(f"Random request from {client_id}: [{a}, {b}]")
    
    start_time = time.time()
    
    try:
        result = calc.random(a, b)
        execution_time = time.time() - start_time
        
        return {
            "success": True,
            "result": result,
            "type": ResultType.NUMBER,
            "range": {"min": a, "max": b},
            "execution_time": execution_time
        }
    except Exception as e:
        logger.error(f"Random error for {client_id}: {str(e)}", exc_info=True)
        execution_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "type": ResultType.ERROR,
            "execution_time": execution_time
        }

@app.get("/api/stats",
         summary="إحصائيات المحرك",
         description="عرض إحصائيات المحرك والخادم")
async def stats(request: Request):
    """إحصائيات المحرك"""
    client_id = get_client_id(request)
    logger.info(f"Stats request from {client_id}")
    
    start_time = time.time()
    
    try:
        calc_stats = calc.get_stats()
        tracker_stats = tracker.get_stats()
        rate_limiter_stats = rate_limiter.get_stats()
        
        execution_time = time.time() - start_time
        
        return {
            "success": True,
            "stats": {
                "calculator": calc_stats,
                "server": tracker_stats,
                "rate_limiter": rate_limiter_stats,
                "cache_size": len(calc.cache) if hasattr(calc, 'cache') else 0,
                "history_size": len(calc.history) if hasattr(calc, 'history') else 0
            },
            "execution_time": execution_time
        }
    except Exception as e:
        logger.error(f"Stats error for {client_id}: {str(e)}", exc_info=True)
        execution_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "type": ResultType.ERROR,
            "execution_time": execution_time
        }

@app.get("/api/history",
         summary="سجل العمليات",
         description="عرض آخر العمليات المنفذة")
async def get_history(
    request: Request,
    limit: Optional[int] = Query(None, description="عدد العناصر", ge=1, le=100)
):
    """سجل العمليات"""
    client_id = get_client_id(request)
    logger.info(f"History request from {client_id}")
    
    start_time = time.time()
    
    try:
        history = calc.get_history(limit)
        execution_time = time.time() - start_time
        
        return {
            "success": True,
            "history": history,
            "count": len(history),
            "execution_time": execution_time
        }
    except Exception as e:
        logger.error(f"History error for {client_id}: {str(e)}", exc_info=True)
        execution_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "type": ResultType.ERROR,
            "execution_time": execution_time
        }

@app.post("/api/cache/clear",
          summary="مسح الذاكرة المؤقتة",
          description="مسح الذاكرة المؤقتة للتعبيرات")
async def cache_clear(request: Request):
    """مسح الذاكرة المؤقتة"""
    client_id = get_client_id(request)
    logger.info(f"Cache clear from {client_id}")
    
    start_time = time.time()
    
    try:
        calc.clear_cache()
        execution_time = time.time() - start_time
        
        return {
            "success": True,
            "message": "✅ تم مسح الذاكرة المؤقتة",
            "execution_time": execution_time
        }
    except Exception as e:
        logger.error(f"Cache clear error for {client_id}: {str(e)}", exc_info=True)
        execution_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "type": ResultType.ERROR,
            "execution_time": execution_time
        }

@app.post("/api/history/clear",
          summary="مسح سجل العمليات",
          description="مسح سجل العمليات بالكامل")
async def history_clear(request: Request):
    """مسح السجل"""
    client_id = get_client_id(request)
    logger.info(f"History clear from {client_id}")
    
    start_time = time.time()
    
    try:
        calc.clear_history()
        execution_time = time.time() - start_time
        
        return {
            "success": True,
            "message": "✅ تم مسح سجل العمليات",
            "execution_time": execution_time
        }
    except Exception as e:
        logger.error(f"History clear error for {client_id}: {str(e)}", exc_info=True)
        execution_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "type": ResultType.ERROR,
            "execution_time": execution_time
        }

@app.get("/api/health",
         summary="التحقق من الصحة",
         description="التحقق من أن الخادم يعمل بشكل صحيح")
async def health_check(request: Request):
    """التحقق من صحة الخادم"""
    client_id = get_client_id(request)
    logger.info(f"Health check from {client_id}")
    
    start_time = time.time()
    
    try:
        # اختبار بسيط للتأكد من أن الآلة الحاسبة تعمل
        test_result = calc.calculate("1+1")
        
        execution_time = time.time() - start_time
        
        return {
            "success": True,
            "status": "healthy",
            "version": "5.1.0",
            "calculator": "ready",
            "test_calculation": f"1+1={test_result}",
            "timestamp": datetime.now().isoformat(),
            "stats": tracker.get_stats(),
            "rate_limit": rate_limiter.get_stats(),
            "execution_time": execution_time
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        execution_time = time.time() - start_time
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e),
            "execution_time": execution_time
        }

# ========== معالجة الأخطاء المحسّنة ==========
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    client_id = get_client_id(request)
    logger.warning(f"404 error for {client_id}: {request.url.path}")
    
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": "المسار غير موجود",
            "available_endpoints": [
                "/api/calculate",
                "/api/solve",
                "/api/solve_system",
                "/api/simplify",
                "/api/expand",
                "/api/factor",
                "/api/diff",
                "/api/integrate",
                "/api/limit",
                "/api/plot",
                "/api/plot_multiple",
                "/api/ncr",
                "/api/npr",
                "/api/memory",
                "/api/random",
                "/api/stats",
                "/api/history",
                "/api/health"
            ]
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    client_id = get_client_id(request)
    logger.error(f"500 error for {client_id}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "خطأ داخلي في الخادم",
            "detail": str(exc) if app.debug else None
        }
    )

@app.exception_handler(429)
async def rate_limit_handler(request: Request, exc):
    client_id = get_client_id(request)
    logger.warning(f"Rate limit exceeded for {client_id}")
    
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "error": "تم تجاوز الحد المسموح من الطلبات",
            "retry_after": rate_limiter.window_seconds
        }
    )

@app.exception_handler(400)
async def validation_error_handler(request: Request, exc):
    client_id = get_client_id(request)
    logger.warning(f"Validation error for {client_id}: {str(exc)}")
    
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": "خطأ في التحقق من المدخلات",
            "detail": str(exc)
        }
    )

# ========== إغلاق التطبيق ==========
@app.on_event("shutdown")
async def shutdown_event():
    """تنظيف الموارد عند إغلاق التطبيق"""
    executor.shutdown(wait=True)
    logger.info("✅ تم إغلاق التجمع الخيطي")

# ========== تشغيل الخادم ==========
if __name__ == "__main__":
    print("="*80)
    print("🚀 تشغيل خادم API للآلة الحاسبة (نسخة إنتاجية v5.1.0)")
    print("="*80)
    print(f"📍 http://127.0.0.1:8000")
    print(f"📚 وثائق API: http://127.0.0.1:8000/docs")
    print(f"🔍 وثائق بديلة: http://127.0.0.1:8000/redoc")
    print(f"📊 حالة الخادم: http://127.0.0.1:8000/api/health")
    print("="*80)
    print(f"المعالج: {CPU_COUNT} أنوية | العمال: {MAX_WORKERS}")
    print("الميزات المتقدمة:")
    print("  ✅ Rate Limiting متقدم (100 طلب/دقيقة)")
    print("  ✅ تسجيل يومي للطلبات والأخطاء")
    print("  ✅ التحقق المتقدم من صحة المدخلات")
    print("  ✅ رسوم بيانية متقدمة (PNG, SVG, PDF)")
    print("  ✅ دعم الاتجاه في النهايات (+، -، +-)")
    print("  ✅ تخزين الصور وتنظيف تلقائي")
    print("  ✅ نقاط نهاية متوافقة مع الإصدارات القديمة")
    print("  ✅ تنسيق موحد للنتائج مع نوع البيانات")
    print("  ✅ وقت تنفيذ دقيق لكل طلب")
    print("  ✅ معالجة متقدمة للأخطاء")
    print("  ✅ تحسين معالجة Plot مع fallback")
    print("="*80)
    
    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
