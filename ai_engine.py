# ============================================
# ملف: ai_engine.py (الإصدار 6.4)
# الوظيفة: التواصل مع الذكاء الاصطناعي - الإصدار المحسن بالكامل
# ============================================

import asyncio
import aiohttp
import time
import re
import json
import hashlib
import ast
import random
from typing import Optional, Dict, Any, List, Tuple, Callable
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import logging
import os
import sys
from copy import copy
from dataclasses import dataclass, field
from enum import Enum
import signal
from contextlib import contextmanager

# محاولة استيراد sympy
try:
    import sympy as sp
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    sp = None

from config import (
    GROQ_API_KEY, GEMINI_API_KEY,
    PRIMARY_MODEL,
    DEBUG_MODE,
    API_TIMEOUT, MAX_RETRIES, RETRY_DELAY, BACKOFF_FACTOR,
    CACHE_TTL,
    get_prompt_by_size,
    PROMPT_MECHANICS, PROMPT_ELECTRICITY, PROMPT_CALCULUS
)

# إعداد logging متقدم
class DetailedLogger:
    """نظام تسجيل تفصيلي مع مستويات متعددة"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG if DEBUG_MODE else logging.INFO)
        self.logger.propagate = False
        
        # معالج الملف للتسجيل التفصيلي
        if DEBUG_MODE:
            # إزالة المعالجات الموجودة
            self.logger.handlers.clear()
            
            file_handler = logging.FileHandler(f'{name}_detailed.log', encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
            
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter('%(levelname)s - %(message)s')
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
    
    def debug(self, msg: str, exc_info: bool = False):
        self.logger.debug(msg, exc_info=exc_info)
    
    def info(self, msg: str):
        self.logger.info(msg)
    
    def warning(self, msg: str):
        self.logger.warning(msg)
    
    def error(self, msg: str, exc_info: bool = True):
        self.logger.error(msg, exc_info=exc_info)
    
    def critical(self, msg: str, exc_info: bool = True):
        self.logger.critical(msg, exc_info=exc_info)
    
    def api_error(self, api_name: str, status: int, response: str):
        """تسجيل تفصيلي لأخطاء API"""
        self.error(f"API {api_name} failed with status {status}: {response[:500]}")

logger = DetailedLogger(__name__)


class ModelType(Enum):
    """أنواع النماذج المدعومة"""
    GROQ = "groq"
    GEMINI = "gemini"
    SIMULATION = "simulation"
    NONE = "none"


class DomainType(Enum):
    """أنواع المجالات المدعومة"""
    GENERAL = "general"
    MECHANICS = "mechanics"
    ELECTRICITY = "electricity"
    CALCULUS = "calculus"
    THERMODYNAMICS = "thermodynamics"
    FLUID_MECHANICS = "fluid_mechanics"
    SIGNAL_PROCESSING = "signal_processing"
    CONTROL_SYSTEMS = "control_systems"
    QUANTUM = "quantum"
    STATISTICS = "statistics"


@dataclass
class Step:
    """خطوة حل مع LaTeX"""
    text: str
    latex: str = ""
    equation: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "text": self.text,
            "latex": self.latex,
            "equation": self.equation
        }


@dataclass
class Solution:
    """نتيجة حل متكاملة"""
    success: bool
    result: Any = None
    result_str: str = ""
    result_latex: str = ""
    steps: List[Step] = field(default_factory=list)
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "result": self.result_str,
            "result_latex": self.result_latex,
            "steps": [s.to_dict() for s in self.steps],
            "error": self.error,
            "warnings": self.warnings
        }


@dataclass
class APIMetrics:
    """مقاييس أداء API"""
    calls: int = 0
    successes: int = 0
    failures: int = 0
    total_time: float = 0.0
    rate_limits: int = 0
    last_error: Optional[str] = None
    last_error_time: Optional[float] = None
    
    @property
    def avg_time(self) -> float:
        return self.total_time / max(self.calls, 1)
    
    @property
    def success_rate(self) -> str:
        return f"{self.successes / max(self.calls, 1) * 100:.1f}%"
    
    def record_success(self, duration: float):
        self.calls += 1
        self.successes += 1
        self.total_time += duration
    
    def record_failure(self, duration: float, error: str = ""):
        self.calls += 1
        self.failures += 1
        self.total_time += duration
        self.last_error = error
        self.last_error_time = time.time()
    
    def record_rate_limit(self):
        self.rate_limits += 1


@dataclass
class DomainMetrics:
    """مقاييس لكل مجال"""
    requests: int = 0
    successes: int = 0
    api_uses: int = 0
    simulation_uses: int = 0
    avg_confidence: float = 0.0
    
    def record_api(self, confidence: float = 1.0):
        self.requests += 1
        self.successes += 1
        self.api_uses += 1
        self.avg_confidence = (self.avg_confidence * (self.requests - 1) + confidence) / self.requests
    
    def record_simulation(self, confidence: float):
        self.requests += 1
        self.successes += 1
        self.simulation_uses += 1
        self.avg_confidence = (self.avg_confidence * (self.requests - 1) + confidence) / self.requests


@dataclass
class EngineStats:
    """إحصائيات المحرك الكاملة"""
    requests: int = 0
    successes: int = 0
    failures: int = 0
    short_questions: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    groq: APIMetrics = field(default_factory=APIMetrics)
    gemini: APIMetrics = field(default_factory=APIMetrics)
    domains: Dict[str, DomainMetrics] = field(default_factory=lambda: {d.value: DomainMetrics() for d in DomainType})
    
    def get_domain_metrics(self, domain: str) -> DomainMetrics:
        if domain not in self.domains:
            self.domains[domain] = DomainMetrics()
        return self.domains[domain]
    
    def to_dict(self) -> Dict:
        return {
            "overall": {
                "requests": self.requests,
                "successes": self.successes,
                "failures": self.failures,
                "short_questions": self.short_questions,
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "success_rate": f"{self.successes / max(self.requests, 1) * 100:.1f}%"
            },
            "apis": {
                "groq": {
                    "calls": self.groq.calls,
                    "successes": self.groq.successes,
                    "failures": self.groq.failures,
                    "avg_time": f"{self.groq.avg_time:.3f}s",
                    "rate_limits": self.groq.rate_limits,
                    "success_rate": self.groq.success_rate,
                    "last_error": self.groq.last_error
                },
                "gemini": {
                    "calls": self.gemini.calls,
                    "successes": self.gemini.successes,
                    "failures": self.gemini.failures,
                    "avg_time": f"{self.gemini.avg_time:.3f}s",
                    "rate_limits": self.gemini.rate_limits,
                    "success_rate": self.gemini.success_rate,
                    "last_error": self.gemini.last_error
                }
            },
            "domains": {
                domain: {
                    "requests": m.requests,
                    "successes": m.successes,
                    "api_uses": m.api_uses,
                    "simulation_uses": m.simulation_uses,
                    "avg_confidence": f"{m.avg_confidence:.2f}"
                }
                for domain, m in self.domains.items()
            }
        }


@contextmanager
def timeout_handler(seconds: float):
    """معالج timeout باستخدام signal"""
    def signal_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")
    
    # تعيين معالج الإشارة
    original_handler = signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(int(seconds))
    
    try:
        yield
    finally:
        # إعادة تعيين
        signal.alarm(0)
        signal.signal(signal.SIGALRM, original_handler)


def safe_latex(expr, timeout: float = 1.0) -> str:
    """
    تحويل آمن للتعبير إلى LaTeX مع timeout
    
    Args:
        expr: التعبير الرياضي
        timeout: المهلة بالثواني
    
    Returns:
        str: LaTeX أو النص العادي
    """
    if not SYMPY_AVAILABLE or expr is None:
        return str(expr) if expr is not None else ""
    
    try:
        with timeout_handler(timeout):
            return sp.latex(expr)
    except TimeoutError:
        logger.debug(f"LaTeX conversion timeout after {timeout}s")
        return str(expr)
    except Exception as e:
        logger.debug(f"LaTeX conversion failed: {e}")
        try:
            # محاولة تبسيط التعبير أولاً (مع timeout أقصر)
            with timeout_handler(timeout * 0.5):
                simplified = sp.simplify(expr)
                return sp.latex(simplified)
        except:
            return str(expr)


def extract_math_expression(text: str) -> Optional[str]:
    """
    استخراج التعبير الرياضي من النص باستخدام محسن
    
    يدعم:
    - الأقواس المتعددة والمتداخلة
    - الدوال المثلثية واللوغاريتمية
    - الأسس والكسور
    - المعادلات
    """
    if not text:
        return None
    
    # تنظيف النص
    text = text.strip()
    
    # أنماط متقدمة للتعابير الرياضية
    patterns = [
        # دالة معقدة مع أقواس متداخلة
        r'([a-zA-Z]+\([^()]*(?:\([^()]*\)[^()]*)*\))',
        
        # معادلة مع علامة =
        r'([^=]+=[^=]+)',
        
        # تعبير مع عمليات وأقواس
        r'([a-zA-Z0-9\s\+\-\*\/\^\(\)\[\]]+)',
        
        # تعبير بين قوسين
        r'\(([^)]+)\)',
        
        # أي شيء بعد كلمات مفتاحية
        r'(?:of|for|as|يساوي|حيث|معادلة|دالة|تعبير)\s+(.+)',
        
        # متغير واحد مع عملية
        r'([a-zA-Z][\^][0-9]+)',
    ]
    
    for pattern in patterns:
        try:
            matches = re.findall(pattern, text)
            for match in matches:
                expr = match.strip()
                # تنظيف التعبير
                expr = re.sub(r'\s+', '', expr)
                # التأكد من أنه تعبير رياضي وليس كلمة عادية
                if expr and (any(c in expr for c in '+-*/^=()') or (expr.isalpha() and len(expr) > 1)):
                    return expr
        except:
            continue
    
    # إذا لم نجد شيئاً، نعيد النص بعد تنظيفه
    try:
        cleaned = re.sub(r'[^\w\s\+\-\*\/\^\(\)]', '', text)
        return cleaned if cleaned and not cleaned.isalpha() else None
    except:
        return None


def complete_short_question(question: str, domain: str = "general") -> str:
    """
    إكمال الأسئلة القصيرة تلقائياً حسب المجال
    
    Args:
        question: السؤال القصير
        domain: المجال
        
    Returns:
        str: السؤال المكتمل
    """
    if not question:
        return "Find derivative of x^2"
    
    q = question.strip().lower()
    
    # قواعد الإكمال حسب المجال
    completions = {
        DomainType.GENERAL.value: {
            "derivative": "Find derivative of x^2",
            "integral": "Find integral of x^2",
            "limit": "Find limit of x as x→0",
            "sum": "Find sum of x from 1 to 10",
            "diff": "Find derivative of x^2",
            "int": "Find integral of x^2",
            "equation": "Solve equation x + 2 = 5",
            "solve": "Solve equation 2x + 5 = 13",
            "مشتق": "أوجد مشتقة x^2",
            "مشتقة": "أوجد مشتقة x^2",
            "تكامل": "أوجد تكامل x^2",
            "∫": "أوجد تكامل x^2",
            "نهاية": "أوجد نهاية x عندما x→0",
            "مجموع": "أوجد مجموع x من 1 إلى 10",
            "معادلة": "حل المعادلة x + 2 = 5",
        },
        DomainType.MECHANICS.value: {
            "force": "Calculate force: mass=10kg, acceleration=9.8 m/s²",
            "energy": "Calculate kinetic energy: mass=5kg, velocity=20 m/s",
            "power": "Calculate power: force=100N, velocity=10 m/s",
            "work": "Calculate work: force=50N, distance=10m",
            "momentum": "Calculate momentum: mass=2kg, velocity=15 m/s",
            "قوة": "احسب القوة: الكتلة=10kg, التسارع=9.8 m/s²",
            "طاقة": "احسب الطاقة الحركية: الكتلة=5kg, السرعة=20 m/s",
        },
        DomainType.ELECTRICITY.value: {
            "voltage": "Calculate voltage: current=2A, resistance=100Ω",
            "current": "Calculate current: voltage=220V, resistance=100Ω",
            "resistance": "Calculate resistance: voltage=220V, current=2A",
            "power": "Calculate power: voltage=220V, current=2A",
            "ohm": "Apply Ohm's law: V = I*R",
            "جهد": "احسب الجهد: التيار=2A, المقاومة=100Ω",
            "تيار": "احسب التيار: الجهد=220V, المقاومة=100Ω",
        },
        DomainType.CALCULUS.value: {
            "derivative": "Find derivative of x^3 + 2x^2 - 5x + 7",
            "integral": "Find integral of x^2 + 3x + 2",
            "limit": "Find limit of sin(x)/x as x→0",
            "series": "Find Taylor series of exp(x) at x=0",
            "gradient": "Find gradient of x^2 + y^2",
        },
        DomainType.THERMODYNAMICS.value: {
            "heat": "Calculate heat: mass=2kg, specific_heat=4186, ΔT=10",
            "entropy": "Calculate entropy change: Q=1000J, T=300K",
            "gas": "Apply ideal gas law: PV = nRT",
        },
        DomainType.FLUID_MECHANICS.value: {
            "pressure": "Calculate pressure: force=100N, area=2m²",
            "bernoulli": "Apply Bernoulli's equation: P + ρgh + ½ρv² = constant",
            "flow": "Calculate flow rate: area=0.1m², velocity=5m/s",
        },
    }
    
    # البحث في المجال المحدد أولاً
    domain_completions = completions.get(domain, completions[DomainType.GENERAL.value])
    
    if q in domain_completions:
        logger.info(f"Auto-completed {domain} question: '{q}' -> '{domain_completions[q]}'")
        return domain_completions[q]
    
    # البحث في المجال العام
    general_completions = completions[DomainType.GENERAL.value]
    if q in general_completions:
        logger.info(f"Auto-completed general question: '{q}' -> '{general_completions[q]}'")
        return general_completions[q]
    
    # إذا كان متغيراً واحداً، نستخدم القالب المناسب للمجال
    if len(q) == 1 and q.isalpha():
        domain_defaults = {
            DomainType.MECHANICS.value: f"Calculate force for mass={q} with acceleration=9.8",
            DomainType.ELECTRICITY.value: f"Calculate voltage for current={q} with resistance=100",
            DomainType.CALCULUS.value: f"Find derivative of {q}^2",
            DomainType.THERMODYNAMICS.value: f"Apply ideal gas law for {q}",
            DomainType.FLUID_MECHANICS.value: f"Calculate pressure for {q}",
        }
        result = domain_defaults.get(domain, f"Find derivative of {q}^2")
        logger.info(f"Auto-completed variable '{q}' in domain {domain}: '{result}'")
        return result
    
    return question


class DomainSpecificPrompts:
    """قوالب مخصصة لكل مجال"""
    
    @staticmethod
    def get_prompt(domain: str, question: str) -> str:
        """الحصول على القالب المناسب للمجال"""
        
        prompts = {
            DomainType.MECHANICS.value: f"""
You are a mechanics expert. Solve this problem step by step.
Question: {question}

Rules:
1. Define all variables using sp.symbols()
2. Write equations using sp.Eq()
3. Include units in comments
4. Provide detailed steps with explanations
5. Final answer in 'final_result'
6. Steps in 'steps' list with 'text' and 'latex' keys

Example:
import sympy as sp
m, a, F = sp.symbols('m a F')
eq = sp.Eq(F, m * a)
solution = sp.solve(eq, F)
final_result = solution[0].subs({{m: 10, a: 9.8}})
steps = [
    {{"text": "Newton's second law: F = ma", "latex": sp.latex(eq)}},
    {{"text": "Substitute m = 10 kg, a = 9.8 m/s²", "latex": "F = 10 × 9.8"}},
    {{"text": f"Result: F = {{final_result}} N", "latex": f"F = {{final_result}} N"}}
]
""",
            
            DomainType.ELECTRICITY.value: f"""
You are an electrical engineering expert. Solve this problem step by step.
Question: {question}

Rules:
1. Define all variables using sp.symbols()
2. Write equations using sp.Eq()
3. Include units in comments
4. Provide detailed steps with explanations
5. Final answer in 'final_result'
6. Steps in 'steps' list with 'text' and 'latex' keys

Example:
import sympy as sp
V, I, R = sp.symbols('V I R')
eq = sp.Eq(V, I * R)
solution = sp.solve(eq, V)
final_result = solution[0].subs({{I: 2, R: 100}})
steps = [
    {{"text": "Ohm's law: V = IR", "latex": sp.latex(eq)}},
    {{"text": "Substitute I = 2 A, R = 100 Ω", "latex": "V = 2 × 100"}},
    {{"text": f"Result: V = {{final_result}} V", "latex": f"V = {{final_result}} V"}}
]
""",
            
            DomainType.CALCULUS.value: f"""
You are a calculus expert. Solve this problem step by step.
Question: {question}

Rules:
1. Define variables using sp.symbols()
2. Show each differentiation/integration step
3. Provide final answer in simplified form
4. Include 'final_result' and 'steps' list

Example:
import sympy as sp
x = sp.symbols('x')
f = x**3 + 2*x**2 - 5*x + 7
final_result = sp.diff(f, x)
steps = [
    {{"text": "Original function", "latex": sp.latex(f)}},
    {{"text": "Apply power rule", "latex": sp.latex(final_result)}}
]
""",
            
            DomainType.THERMODYNAMICS.value: f"""
You are a thermodynamics expert. Solve this problem step by step.
Question: {question}

Use appropriate thermodynamic equations:
- First law: ΔU = Q - W
- Ideal gas: PV = nRT
- Entropy: ΔS = Q/T
""",
            
            DomainType.FLUID_MECHANICS.value: f"""
You are a fluid mechanics expert. Solve this problem step by step.
Question: {question}

Use appropriate fluid mechanics equations:
- Bernoulli: P + ρgh + ½ρv² = constant
- Continuity: A₁v₁ = A₂v₂
- Reynolds number: Re = ρvD/μ
""",
            
            DomainType.CONTROL_SYSTEMS.value: f"""
You are a control systems expert. Solve this problem step by step.
Question: {question}

Use appropriate control theory:
- Transfer functions
- Laplace transforms
- State space representations
""",
        }
        
        return prompts.get(domain, get_prompt_by_size("normal") + f"\n\nQuestion: {question}")


class SimpleEmbeddings:
    """نظام embeddings بسيط لاختيار القوالب مع cache محدود"""
    
    def __init__(self, max_cache: int = 100, cache_ttl: int = 3600):
        self.word_vectors = {}
        self.dimension = 50
        self.cache = OrderedDict()
        self.cache_timestamps = {}
        self.max_cache = max_cache
        self.cache_ttl = cache_ttl
    
    def _is_cache_valid(self, key: str) -> bool:
        """التحقق من صلاحية cache"""
        if key not in self.cache_timestamps:
            return False
        return time.time() - self.cache_timestamps[key] < self.cache_ttl
    
    def _clean_expired_cache(self):
        """تنظيف cache منتهي الصلاحية"""
        expired = [k for k in list(self.cache.keys()) if not self._is_cache_valid(k)]
        for k in expired:
            self.cache.pop(k, None)
            self.cache_timestamps.pop(k, None)
    
    def _get_word_vector(self, word: str) -> List[float]:
        """توليد متجه عشوائي ثابت للكلمة"""
        if word not in self.word_vectors:
            random.seed(hash(word) % 2**32)
            self.word_vectors[word] = [random.random() for _ in range(self.dimension)]
        return self.word_vectors[word]
    
    def get_text_vector(self, text: str) -> List[float]:
        """الحصول على متجه للنص"""
        self._clean_expired_cache()
        
        if text in self.cache and self._is_cache_valid(text):
            self.cache.move_to_end(text)
            return self.cache[text]
        
        words = re.findall(r'\b[a-z\u0600-\u06FF]{2,}\b', text.lower())
        if not words:
            return [0.0] * self.dimension
        
        words = words[:10]
        avg_vector = [0.0] * self.dimension
        
        for w in words:
            vec = self._get_word_vector(w)
            for i, v in enumerate(vec):
                avg_vector[i] += v
        
        avg_vector = [v / len(words) for v in avg_vector]
        
        # إدارة حجم cache
        if len(self.cache) >= self.max_cache:
            self.cache.popitem(last=False)
        
        self.cache[text] = avg_vector
        self.cache_timestamps[text] = time.time()
        
        return avg_vector
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """حساب التشابه بين متجهين"""
        try:
            dot = sum(a * b for a, b in zip(vec1, vec2))
            norm1 = sum(a * a for a in vec1) ** 0.5
            norm2 = sum(b * b for b in vec2) ** 0.5
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot / (norm1 * norm2)
        except:
            return 0.0


class SecureSandbox:
    """بيئة آمنة لتنفيذ الكود مع توليد خطوات تلقائية"""
    
    FORBIDDEN = {'eval', 'exec', 'compile', '__import__', 'open', 'globals', 'locals',
                  '__builtins__', 'vars', 'dir', '__dict__', '__class__'}
    FORBIDDEN_MODULES = {'os', 'sys', 'subprocess', 'socket', 'requests', 'urllib',
                          'httpx', 'pickle', 'ctypes', 'threading', 'multiprocessing'}
    
    def __init__(self, timeout: float = 10.0, max_workers: int = 2):
        self.timeout = timeout
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._cleanup_lock = asyncio.Lock()
        self._is_cleaned = False
        self._active_tasks = 0
        
        # الدوال المسموح بها (نسخة آمنة)
        self.allowed = {
            'print': print, 'range': range, 'len': len, 'int': int, 'float': float,
            'str': str, 'list': list, 'dict': dict, 'tuple': tuple, 'bool': bool,
            'abs': abs, 'max': max, 'min': min, 'sum': sum, 'round': round,
            'enumerate': enumerate, 'zip': zip, 'isinstance': isinstance,
            'type': type, 'pow': pow, 'divmod': divmod, 'complex': complex,
            'all': all, 'any': any, 'chr': chr, 'ord': ord, 'sorted': sorted
        }
    
    def _clean_imports(self, code: str) -> str:
        """تنظيف وتوحيد طريقة الاستيراد"""
        if not code:
            return ""
        
        # تحويل from sympy import * إلى import sympy as sp
        if 'from sympy import *' in code:
            code = code.replace('from sympy import *', 'import sympy as sp')
        
        # تحويل import sympy إلى import sympy as sp
        if 'import sympy' in code and 'import sympy as sp' not in code:
            code = code.replace('import sympy', 'import sympy as sp')
        
        # إضافة import إذا لم يكن موجوداً
        if 'import sp' not in code and 'import sympy' not in code:
            code = "import sympy as sp\n" + code
        
        return code
    
    def _generate_auto_steps(self, code: str, result: Any) -> List[Step]:
        """توليد خطوات تلقائية إذا لم توجد"""
        steps = []
        
        try:
            # محاولة استخراج العمليات من الكود
            lines = code.split('\n')
            for line in lines:
                line = line.strip()
                if '=' in line and not line.startswith('#') and not line.startswith('import'):
                    # تنظيف السطر
                    clean_line = re.sub(r'\s+', ' ', line)
                    steps.append(Step(
                        text=f"Define: {clean_line}",
                        latex=clean_line
                    ))
            
            # إضافة النتيجة النهائية
            if result is not None:
                steps.append(Step(
                    text="Final result",
                    latex=safe_latex(result)
                ))
        except Exception as e:
            logger.debug(f"Error generating auto steps: {e}")
        
        return steps
    
    def validate(self, code: str) -> Tuple[bool, str]:
        """التحقق من أمان الكود"""
        code = self._clean_imports(code)
        
        try:
            ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        
        for func in self.FORBIDDEN:
            if re.search(rf'\b{func}\s*\(', code):
                return False, f"Forbidden function: {func}"
        
        for mod in self.FORBIDDEN_MODULES:
            if re.search(rf'import\s+{mod}\b', code):
                return False, f"Forbidden module: {mod}"
            if re.search(rf'from\s+{mod}\s+import', code):
                return False, f"Forbidden module: {mod}"
        
        # التحقق من وجود final_result
        if 'final_result' not in code:
            logger.warning("Code missing 'final_result' variable")
        
        return True, code
    
    async def _execute_target(self, code: str) -> Tuple[bool, Solution]:
        """تنفيذ الكود في بيئة معزولة"""
        def target():
            solution = Solution(success=False)
            
            try:
                # إنشاء بيئة آمنة جديدة لكل تنفيذ
                safe_builtins = {}
                for k, v in self.allowed.items():
                    if callable(v):
                        safe_builtins[k] = v
                
                # إضافة sympy
                try:
                    import sympy as sp_local
                    sp_module = sp_local
                except ImportError:
                    sp_module = None
                
                safe = {
                    '__builtins__': safe_builtins,
                    'sp': sp_module
                }
                
                # تجميد البيئة
                safe['__builtins__']['__dict__'] = None
                safe['__builtins__']['__class__'] = None
                
                # تنفيذ الكود
                exec(code, safe)
                
                # استخراج النتائج
                final_result = safe.get('final_result')
                steps_data = safe.get('steps', [])
                
                # تحويل الخطوات إلى كائنات Step
                steps = []
                for s in steps_data:
                    if isinstance(s, dict):
                        steps.append(Step(
                            text=s.get('text', ''),
                            latex=s.get('latex', ''),
                            equation=s.get('equation')
                        ))
                    elif isinstance(s, str):
                        steps.append(Step(text=s, latex=safe_latex(s)))
                
                # توليد خطوات تلقائية إذا لم توجد
                if not steps and final_result is not None:
                    steps = self._generate_auto_steps(code, final_result)
                
                solution.success = True
                solution.result = final_result
                solution.result_str = str(final_result) if final_result is not None else ""
                solution.result_latex = safe_latex(final_result) if final_result is not None else ""
                solution.steps = steps
                
                return True, solution
                
            except Exception as e:
                solution.error = str(e)
                return False, solution
        
        try:
            loop = asyncio.get_event_loop()
            self._active_tasks += 1
            result = await asyncio.wait_for(
                loop.run_in_executor(self.executor, target),
                timeout=self.timeout
            )
            self._active_tasks -= 1
            return result
        except TimeoutError:
            self._active_tasks -= 1
            sol = Solution(success=False, error=f"Timeout after {self.timeout}s")
            return False, sol
        except Exception as e:
            self._active_tasks -= 1
            sol = Solution(success=False, error=f"Execution error: {e}")
            return False, sol
    
    async def execute(self, code: str) -> Tuple[bool, Solution]:
        """تنفيذ الكود مع التحقق الأمني"""
        if self._is_cleaned:
            return False, Solution(success=False, error="Sandbox has been cleaned up")
        
        if not code:
            return False, Solution(success=False, error="Empty code")
        
        if len(code) > 10000:
            return False, Solution(success=False, error="Code too long (max 10000 chars)")
        
        valid, result = self.validate(code)
        if not valid:
            return False, Solution(success=False, error=result)
        
        return await self._execute_target(result)
    
    async def cleanup(self):
        """تنظيف الموارد بشكل آمن"""
        async with self._cleanup_lock:
            if not self._is_cleaned:
                self._is_cleaned = True
                
                # انتظار انتهاء المهام النشطة
                timeout = 5.0
                start = time.time()
                while self._active_tasks > 0 and time.time() - start < timeout:
                    await asyncio.sleep(0.1)
                
                self.executor.shutdown(wait=False)
                logger.debug("Sandbox cleaned up")


class AdvancedCache:
    """نظام تخزين مؤقت متقدم مع LRU و TTL ودعم المجالات"""
    
    def __init__(self, capacity: int = 1000, ttl: int = 3600):
        self.capacity = capacity
        self.ttl = ttl
        self.cache = OrderedDict()
        self.timestamps = {}
        self.stats = {"hits": 0, "misses": 0}
    
    def _make_key(self, question: str, domain: str = "general") -> str:
        """توليد مفتاح Cache مع domain"""
        if not question:
            question = "empty"
        q_part = question.strip().lower()[:100]
        key_str = f"{domain}:{q_part}"
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def _is_expired(self, key: str) -> bool:
        """التحقق من انتهاء الصلاحية"""
        if key not in self.timestamps:
            return True
        return time.time() - self.timestamps[key] > self.ttl
    
    def _clean_expired(self):
        """إزالة العناصر منتهية الصلاحية"""
        expired = [k for k in list(self.cache.keys()) if self._is_expired(k)]
        for k in expired:
            self.cache.pop(k, None)
            self.timestamps.pop(k, None)
        if expired:
            logger.debug(f"Removed {len(expired)} expired cache entries")
    
    def get(self, key: str) -> Optional[Any]:
        """الحصول من Cache"""
        self._clean_expired()
        
        if key in self.cache and not self._is_expired(key):
            self.cache.move_to_end(key)
            self.stats["hits"] += 1
            return self.cache[key]
        
        self.stats["misses"] += 1
        return None
    
    def set(self, key: str, value: Any):
        """حفظ في Cache"""
        self._clean_expired()
        
        if key in self.cache:
            self.cache.move_to_end(key)
        elif len(self.cache) >= self.capacity:
            self.cache.popitem(last=False)
        
        self.cache[key] = value
        self.timestamps[key] = time.time()
    
    def get_stats(self) -> Dict:
        """إحصائيات Cache"""
        self._clean_expired()
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / max(total, 1) * 100
        
        return {
            "size": len(self.cache),
            "capacity": self.capacity,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": f"{hit_rate:.1f}%"
    }


class TemplateManager:
    """مدير القوالب الموسع مع دعم المجالات"""
    
    def __init__(self, embeddings: SimpleEmbeddings):
        self.embeddings = embeddings
        self.templates = self._init_templates()
        self.domain_templates = self._init_domain_templates()
        self.template_vecs = self._init_vectors()
    
    def _init_templates(self) -> Dict:
        """تهيئة القوالب الأساسية"""
        return {
            "derivative": {
                "patterns": ["مشتق", "derivative", "diff", "differentiate", "اشتقاق", "مشتقة"],
                "example": "x**3 + 2*x**2 - 5*x + 7",
                "domain": "calculus",
                "code": self._derivative_code
            },
            "integral": {
                "patterns": ["تكامل", "integral", "integrate", "∫", "integration"],
                "example": "x**2 + 3*x + 2",
                "domain": "calculus",
                "code": self._integral_code
            },
            "equation": {
                "patterns": ["معادلة", "equation", "solve", "حل", "solution"],
                "example": "2*x + 5 = 13",
                "domain": "general",
                "code": self._equation_code
            },
            "limit": {
                "patterns": ["نهاية", "limit", "approaches", "تقترب"],
                "example": "sin(x)/x",
                "domain": "calculus",
                "code": self._limit_code
            },
            "summation": {
                "patterns": ["مجموع", "sum", "summation", "Σ"],
                "example": "x**2",
                "domain": "calculus",
                "code": self._summation_code
            },
            "matrix": {
                "patterns": ["مصفوفة", "matrix", "matrices", "determinant", "محدد"],
                "example": "Matrix([[1,2],[3,4]])",
                "domain": "general",
                "code": self._matrix_code
            },
            "differential_equation": {
                "patterns": ["معادلة تفاضلية", "differential equation", "ode"],
                "example": "y'' + y = 0",
                "domain": "calculus",
                "code": self._differential_equation_code
            },
            "laplace": {
                "patterns": ["تحويل لابلاس", "laplace transform", "laplace"],
                "example": "exp(-t)*sin(t)",
                "domain": "control_systems",
                "code": self._laplace_code
            },
            "fourier": {
                "patterns": ["تحويل فورييه", "fourier transform", "fourier"],
                "example": "exp(-x**2)",
                "domain": "signal_processing",
                "code": self._fourier_code
            },
            "vector": {
                "patterns": ["متجه", "vector", "gradient", "divergence", "curl"],
                "example": "x**2 + y**2",
                "domain": "calculus",
                "code": self._vector_code
            },
            "complex": {
                "patterns": ["عقدي", "complex", "imaginary"],
                "example": "z**2 + 1",
                "domain": "general",
                "code": self._complex_code
            },
            "series": {
                "patterns": ["متسلسلة", "series", "taylor", "maclaurin"],
                "example": "exp(x)",
                "domain": "calculus",
                "code": self._series_code
            },
            "newton": {
                "patterns": ["نيوتن", "newton", "force", "f=ma", "قوة"],
                "example": "F = m*a",
                "domain": "mechanics",
                "code": self._newton_code
            },
            "ohm": {
                "patterns": ["أوم", "ohm", "voltage", "current", "resistance", "جهد", "تيار"],
                "example": "V = I*R",
                "domain": "electricity",
                "code": self._ohm_code
            },
            "bernoulli": {
                "patterns": ["برنولي", "bernoulli", "fluid"],
                "example": "P + 0.5*rho*v^2 + rho*g*h = constant",
                "domain": "fluid_mechanics",
                "code": self._bernoulli_code
            },
            "ideal_gas": {
                "patterns": ["غاز مثالي", "ideal gas", "pv=nrt"],
                "example": "P*V = n*R*T",
                "domain": "thermodynamics",
                "code": self._ideal_gas_code
            }
        }
    
    def _init_domain_templates(self) -> Dict:
        """تهيئة القوالب حسب المجال"""
        domain_templates = {d.value: [] for d in DomainType}
        
        for name, tmpl in self.templates.items():
            domain = tmpl.get("domain", "general")
            if domain in domain_templates:
                domain_templates[domain].append(name)
        
        return domain_templates
    
    def _init_vectors(self) -> Dict:
        """تهيئة متجهات القوالب"""
        vectors = {}
        for name, tmpl in self.templates.items():
            try:
                text = " ".join(tmpl["patterns"])
                vectors[name] = self.embeddings.get_text_vector(text)
            except Exception as e:
                logger.debug(f"Error creating vector for {name}: {e}")
                vectors[name] = [0.0] * 50
        return vectors
    
    def _safe_func(self, func: Optional[str]) -> str:
        """تنظيف الدالة للاستخدام الآمن"""
        if not func:
            return "x**2"
        try:
            # إزالة الأحرف غير المسموح بها
            func = re.sub(r'[^\w\s\+\-\*\/\^\(\)\.]', '', func)
            return func if func else "x**2"
        except:
            return "x**2"
    
    def _ensure_final_result(self, code: str) -> str:
        """التأكد من وجود final_result في الكود"""
        if "final_result" not in code:
            code += "\n\n# Ensure final_result exists\nfinal_result = final_result if 'final_result' in locals() else None"
        return code
    
    # ===== دوال توليد الكود الأساسية =====
    
    def _derivative_code(self, func: str) -> str:
        f = self._safe_func(func)
        code = f'''
import sympy as sp
x = sp.symbols('x')
f = {f}
final_result = sp.diff(f, x)
steps = [
    {{"text": "Function: f(x) = {f}", "latex": safe_latex(f)}},
    {{"text": "Apply power rule", "latex": sp.latex(sp.diff(f, x))}},
    {{"text": "Derivative: f'(x)", "latex": safe_latex(final_result)}}
]
'''
        return self._ensure_final_result(code)
    
    def _integral_code(self, func: str) -> str:
        f = self._safe_func(func)
        code = f'''
import sympy as sp
x = sp.symbols('x')
f = {f}
final_result = sp.integrate(f, x)
steps = [
    {{"text": "Function: f(x) = {f}", "latex": safe_latex(f)}},
    {{"text": "Apply integration rules", "latex": sp.latex(sp.Integral(f, x))}},
    {{"text": "Result: ∫f(x)dx", "latex": safe_latex(final_result) + " + C"}}
]
'''
        return self._ensure_final_result(code)
    
    def _equation_code(self, func: str) -> str:
        f = self._safe_func(func)
        code = f'''
import sympy as sp
x = sp.symbols('x')
eq = sp.Eq({f})
final_result = sp.solve(eq, x)
solutions = final_result if isinstance(final_result, list) else [final_result]
solution_str = ', '.join(map(str, solutions))
steps = [
    {{"text": "Equation: {f}", "latex": safe_latex(eq)}},
    {{"text": "Solve for x", "latex": ""}},
    {{"text": f"Solutions: x = {{solution_str}}", "latex": f"x = {{solution_str}}"}}
]
'''
        return self._ensure_final_result(code)
    
    def _limit_code(self, func: str) -> str:
        f = self._safe_func(func)
        code = f'''
import sympy as sp
x = sp.symbols('x')
f = {f}
final_result = sp.limit(f, x, 0)
steps = [
    {{"text": "Function: f(x) = {f}", "latex": safe_latex(f)}},
    {{"text": "Evaluate limit as x → 0", "latex": sp.latex(sp.Limit(f, x, 0))}},
    {{"text": "Result:", "latex": safe_latex(final_result)}}
]
'''
        return self._ensure_final_result(code)
    
    def _summation_code(self, func: str) -> str:
        f = self._safe_func(func)
        code = f'''
import sympy as sp
x = sp.symbols('x')
f = {f}
sum_expr = sp.Sum(f, (x, 1, 10))
final_result = sum_expr.doit()
steps = [
    {{"text": "Summation: Σ {f} from 1 to 10", "latex": safe_latex(sum_expr)}},
    {{"text": "Calculate sum", "latex": ""}},
    {{"text": "Result:", "latex": safe_latex(final_result)}}
]
'''
        return self._ensure_final_result(code)
    
    def _matrix_code(self, func: str) -> str:
        code = '''
import sympy as sp
# Example 2x2 matrices
A = sp.Matrix([[1, 2], [3, 4]])
B = sp.Matrix([[5, 6], [7, 8]])
final_result = A * B
steps = [
    {"text": "Matrix A:", "latex": safe_latex(A)},
    {"text": "Matrix B:", "latex": safe_latex(B)},
    {"text": "Multiplication: A × B", "latex": safe_latex(A * B)},
    {"text": "Result:", "latex": safe_latex(final_result)}
]
'''
        return self._ensure_final_result(code)
    
    def _differential_equation_code(self, func: str) -> str:
        code = '''
import sympy as sp
x = sp.symbols('x')
y = sp.Function('y')(x)
# Example: y'' + y = 0
eq = sp.Eq(y.diff(x, x) + y, 0)
final_result = sp.dsolve(eq)
steps = [
    {"text": "Differential equation: y'' + y = 0", "latex": "y'' + y = 0"},
    {"text": "Find general solution", "latex": ""},
    {"text": "Result:", "latex": safe_latex(final_result)}
]
'''
        return self._ensure_final_result(code)
    
    def _laplace_code(self, func: str) -> str:
        code = '''
import sympy as sp
t, s = sp.symbols('t s')
# Example: e^(-t) sin(t)
f = sp.exp(-t) * sp.sin(t)
F = sp.laplace_transform(f, t, s, noconds=True)
final_result = F
steps = [
    {"text": "Function: f(t) = e^(-t) sin(t)", "latex": "f(t) = e^{{-t}} \\\\sin(t)"},
    {"text": "Apply Laplace transform", "latex": sp.latex(sp.LaplaceTransform(f, t, s))},
    {"text": "Result: F(s)", "latex": safe_latex(F)}
]
'''
        return self._ensure_final_result(code)
    
    def _fourier_code(self, func: str) -> str:
        code = '''
import sympy as sp
x, k = sp.symbols('x k')
# Example: e^(-x²)
f = sp.exp(-x**2)
F = sp.fourier_transform(f, x, k)
final_result = F
steps = [
    {"text": "Function: f(x) = e^(-x²)", "latex": "f(x) = e^{{-x^2}}"},
    {"text": "Apply Fourier transform", "latex": sp.latex(sp.FourierTransform(f, x, k))},
    {"text": "Result: F(k)", "latex": safe_latex(F)}
]
'''
        return self._ensure_final_result(code)
    
    def _vector_code(self, func: str) -> str:
        code = '''
import sympy as sp
from sympy.vector import CoordSys3D, gradient
N = CoordSys3D('N')
x, y, z = N.x, N.y, N.z
# Example: f = x² + y² + z²
f = x**2 + y**2 + z**2
grad_f = gradient(f)
final_result = grad_f
steps = [
    {"text": "Function: f = x² + y² + z²", "latex": "f = x^2 + y^2 + z^2"},
    {"text": "Calculate gradient", "latex": ""},
    {"text": "Result: ∇f", "latex": safe_latex(grad_f)}
]
'''
        return self._ensure_final_result(code)
    
    def _complex_code(self, func: str) -> str:
        f = self._safe_func(func)
        code = f'''
import sympy as sp
z = sp.symbols('z')
f = {f}
roots = sp.solve(f, z)
final_result = roots
steps = [
    {{"text": "Complex function: f(z) = {f}", "latex": f"f(z) = {f}"}},
    {{"text": "Find roots", "latex": ""}},
    {{"text": f"Roots: {{roots}}", "latex": f"z = {{roots}}"}}
]
'''
        return self._ensure_final_result(code)
    
    def _series_code(self, func: str) -> str:
        code = '''
import sympy as sp
x = sp.symbols('x')
# Example: e^x
f = sp.exp(x)
series = sp.series(f, x, 0, 5)
final_result = series
steps = [
    {"text": "Function: f(x) = e^x", "latex": "f(x) = e^x"},
    {"text": "Taylor series at x = 0", "latex": ""},
    {"text": "First 5 terms:", "latex": safe_latex(series)}
]
'''
        return self._ensure_final_result(code)
    
    # ===== دوال توليد الكود للمجالات المتخصصة =====
    
    def _newton_code(self, func: str) -> str:
        code = '''
import sympy as sp
# Newton's second law: F = ma
m, a, F = sp.symbols('m a F')
eq = sp.Eq(F, m * a)
solution = sp.solve(eq, F)
# Example values
final_result = solution[0].subs({m: 10, a: 9.8})
steps = [
    {"text": "Newton's second law: F = ma", "latex": sp.latex(eq)},
    {"text": "For m = 10 kg, a = 9.8 m/s²", "latex": "F = 10 × 9.8"},
    {"text": f"Force: F = {final_result:.1f} N", "latex": f"F = {final_result} N"}
]
'''
        return self._ensure_final_result(code)
    
    def _ohm_code(self, func: str) -> str:
        code = '''
import sympy as sp
# Ohm's law: V = IR
V, I, R = sp.symbols('V I R')
eq = sp.Eq(V, I * R)
solution = sp.solve(eq, V)
# Example values
final_result = solution[0].subs({I: 2, R: 100})
steps = [
    {"text": "Ohm's law: V = IR", "latex": sp.latex(eq)},
    {"text": "For I = 2 A, R = 100 Ω", "latex": "V = 2 × 100"},
    {"text": f"Voltage: V = {final_result:.0f} V", "latex": f"V = {final_result} V"}
]
'''
        return self._ensure_final_result(code)
    
    def _bernoulli_code(self, func: str) -> str:
        code = '''
import sympy as sp
# Bernoulli's equation: P + ½ρv² + ρgh = constant
P, rho, v, g, h, C = sp.symbols('P rho v g h C')
eq = sp.Eq(P + (1/2)*rho*v**2 + rho*g*h, C)
steps = [
    {"text": "Bernoulli's equation: P + ½ρv² + ρgh = constant", "latex": sp.latex(eq)},
    {"text": "Used in fluid mechanics for incompressible flow", "latex": ""},
    {"text": "Common applications: pipe flow, airfoils", "latex": ""}
]
final_result = eq
'''
        return self._ensure_final_result(code)
    
    def _ideal_gas_code(self, func: str) -> str:
        code = '''
import sympy as sp
# Ideal gas law: PV = nRT
P, V, n, R, T = sp.symbols('P V n R T')
eq = sp.Eq(P * V, n * R * T)
steps = [
    {"text": "Ideal gas law: PV = nRT", "latex": sp.latex(eq)},
    {"text": "P: pressure, V: volume, n: moles", "latex": ""},
    {"text": "R: gas constant, T: temperature", "latex": ""}
]
final_result = eq
'''
        return self._ensure_final_result(code)
    
    def choose_template(self, question: str, domain: str = "general") -> Tuple[Optional[str], float, Optional[str]]:
        """اختيار أفضل قالب حسب المجال والسؤال"""
        if not question:
            return None, 0.0, None
        
        q_vec = self.embeddings.get_text_vector(question)
        best = None
        best_score = 0.0
        
        # تقييد القوالب حسب المجال إذا كان محدداً
        candidates = self.templates
        if domain != "general" and domain in self.domain_templates:
            candidate_names = self.domain_templates[domain]
            candidates = {name: self.templates[name] for name in candidate_names if name in self.templates}
        
        for name, tmpl in candidates.items():
            vec = self.template_vecs.get(name)
            if vec is not None:
                try:
                    score = self.embeddings.cosine_similarity(q_vec, vec)
                    if score > best_score:
                        best_score = score
                        best = name
                except:
                    continue
        
        # استخراج الدالة
        func = extract_math_expression(question)
        
        # ثقة ديناميكية حسب المجال
        thresholds = {
            "general": 0.15,
            "mechanics": 0.2,
            "electricity": 0.2,
            "calculus": 0.18,
            "thermodynamics": 0.22,
            "fluid_mechanics": 0.22,
            "control_systems": 0.2,
        }
        threshold = thresholds.get(domain, 0.15)
        
        if best_score < threshold:
            return None, best_score, func
        
        return best, best_score, func
    
    def generate_code(self, template_name: Optional[str], func: Optional[str], domain: str = "general") -> str:
        """توليد الكود من القالب"""
        if not template_name or template_name not in self.templates:
            return self._domain_default_code(domain)
        
        try:
            template = self.templates[template_name]
            code = template["code"](func if func else template["example"])
            return code
        except Exception as e:
            logger.error(f"Error generating code from template {template_name}: {e}")
            return self._domain_default_code(domain)
    
    def _domain_default_code(self, domain: str) -> str:
        """كود افتراضي حسب المجال"""
        defaults = {
            "mechanics": self._newton_code,
            "electricity": self._ohm_code,
            "fluid_mechanics": self._bernoulli_code,
            "thermodynamics": self._ideal_gas_code,
            "control_systems": self._laplace_code,
            "signal_processing": self._fourier_code,
        }
        
        if domain in defaults:
            return defaults[domain]("")
        
        # كود عام
        return '''
import sympy as sp
x = sp.symbols('x')
f = x**2 + 2*x + 1
final_result = sp.diff(f, x)
steps = [
    {"text": "Function: f(x) = x² + 2x + 1", "latex": "f(x) = x^{2} + 2x + 1"},
    {"text": "Derivative: f'(x) = 2x + 2", "latex": "f'(x) = 2x + 2"}
]
'''


class AIEngine:
    """المحرك الرئيسي للذكاء الاصطناعي - الإصدار المتقدم مع Dynamic Domains"""
    
    def __init__(self):
        self.groq_key = GROQ_API_KEY
        self.gemini_key = GEMINI_API_KEY
        self.sandbox = SecureSandbox()
        self.cache = AdvancedCache(ttl=CACHE_TTL)
        self.embeddings = SimpleEmbeddings()
        self.template_manager = TemplateManager(self.embeddings)
        self.session = None
        self.groq_available = False
        self.gemini_available = False
        self._running = False
        self._cleanup_lock = asyncio.Lock()
        self._session_lock = asyncio.Lock()
        self.stats = EngineStats()
        
        # تحذير إذا لم يكن sympy مثبتاً
        if not SYMPY_AVAILABLE:
            logger.warning("⚠️ SymPy not installed. LaTeX output will be disabled.")
    
    async def _ensure_session(self):
        """التأكد من وجود جلسة HTTP"""
        async with self._session_lock:
            if not self.session or self.session.closed:
                timeout = aiohttp.ClientTimeout(total=API_TIMEOUT, connect=10)
                connector = aiohttp.TCPConnector(limit=100, ttl_dns_cache=300)
                self.session = aiohttp.ClientSession(
                    timeout=timeout,
                    connector=connector
                )
                logger.debug("HTTP session created")
    
    async def _verify_key_with_retry(self, key_func: Callable, key_name: str, retry_count: int = 0) -> bool:
        """التحقق من المفتاح مع إعادة محاولة"""
        if retry_count >= MAX_RETRIES:
            logger.error(f"{key_name} key verification failed after {MAX_RETRIES} attempts")
            return False
        
        try:
            result = await key_func()
            if result:
                logger.info(f"{key_name} key verified")
                return True
            
            if retry_count < MAX_RETRIES - 1:
                delay = RETRY_DELAY * (BACKOFF_FACTOR ** retry_count)
                logger.debug(f"Retrying {key_name} verification in {delay}s")
                await asyncio.sleep(delay)
                return await self._verify_key_with_retry(key_func, key_name, retry_count + 1)
            
        except Exception as e:
            logger.error(f"{key_name} verification error: {e}")
            if retry_count < MAX_RETRIES - 1:
                delay = RETRY_DELAY * (BACKOFF_FACTOR ** retry_count)
                await asyncio.sleep(delay)
                return await self._verify_key_with_retry(key_func, key_name, retry_count + 1)
        
        return False
    
    async def _verify_groq(self) -> bool:
        try:
            await self._ensure_session()
            url = "https://api.groq.com/openai/v1/models"
            headers = {"Authorization": f"Bearer {self.groq_key}"}
            
            async with self.session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return bool(data.get("data"))
                else:
                    error = await resp.text()
                    logger.api_error("Groq", resp.status, error)
                    return False
        except asyncio.TimeoutError:
            logger.error("Groq verification timeout")
            return False
        except Exception as e:
            logger.error(f"Groq verification error: {e}")
            return False
    
    async def _verify_gemini(self) -> bool:
        try:
            await self._ensure_session()
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={self.gemini_key}"
            
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return bool(data.get("models"))
                else:
                    error = await resp.text()
                    logger.api_error("Gemini", resp.status, error)
                    return False
        except asyncio.TimeoutError:
            logger.error("Gemini verification timeout")
            return False
        except Exception as e:
            logger.error(f"Gemini verification error: {e}")
            return False
    
    def _valid_key(self, key: str) -> bool:
        """التحقق من صحة المفتاح"""
        return bool(key and isinstance(key, str) and len(key) > 20 and "simulated" not in key)
    
    def _clean_code(self, raw: str) -> str:
        """تنظيف الكود من علامات Markdown"""
        if not raw:
            return ""
        
        # إزالة علامات Markdown
        raw = re.sub(r'```python\s*', '', raw, flags=re.IGNORECASE)
        raw = re.sub(r'```\s*', '', raw)
        raw = re.sub(r'`', '', raw)
        raw = re.sub(r'^python\s*', '', raw, flags=re.IGNORECASE)
        raw = raw.strip()
        
        return raw
    
    async def _call_groq(self, prompt: str, retry_count: int = 0) -> Optional[Dict]:
        """استدعاء Groq API مع إعادة محاولة محدودة"""
        if retry_count >= MAX_RETRIES:
            logger.error(f"Groq API failed after {MAX_RETRIES} attempts")
            return None
        
        start = time.time()
        
        try:
            await self._ensure_session()
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": PRIMARY_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a SymPy expert. Generate Python code with sympy. Include 'final_result' and detailed 'steps'."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 2000
            }
            
            async with self.session.post(url, headers=headers, json=data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    content = result["choices"][0]["message"]["content"]
                    elapsed = time.time() - start
                    
                    self.stats.groq.record_success(elapsed)
                    return {
                        "success": True,
                        "code": content,
                        "model": "groq",
                        "time": elapsed
                    }
                    
                elif resp.status == 429:
                    self.stats.groq.record_rate_limit()
                    retry_after = resp.headers.get('Retry-After', '60')
                    logger.warning(f"Groq rate limited. Retry after {retry_after}s")
                    
                    await asyncio.sleep(int(retry_after))
                    return await self._call_groq(prompt, retry_count + 1)
                    
                else:
                    error = await resp.text()
                    self.stats.groq.record_failure(time.time() - start, error)
                    logger.api_error("Groq", resp.status, error)
                    
                    if 500 <= resp.status < 600:  # Server errors
                        delay = RETRY_DELAY * (BACKOFF_FACTOR ** retry_count)
                        await asyncio.sleep(delay)
                        return await self._call_groq(prompt, retry_count + 1)
                    
                    return None
                    
        except asyncio.TimeoutError:
            logger.error("Groq timeout")
            self.stats.groq.record_failure(time.time() - start, "timeout")
            
            if retry_count < MAX_RETRIES - 1:
                delay = RETRY_DELAY * (BACKOFF_FACTOR ** retry_count)
                await asyncio.sleep(delay)
                return await self._call_groq(prompt, retry_count + 1)
            
            return None
        except Exception as e:
            logger.error(f"Groq error: {e}")
            self.stats.groq.record_failure(time.time() - start, str(e))
            return None
    
    async def _call_gemini(self, prompt: str, retry_count: int = 0) -> Optional[Dict]:
        """استدعاء Gemini API مع إعادة محاولة محدودة"""
        if retry_count >= MAX_RETRIES:
            logger.error(f"Gemini API failed after {MAX_RETRIES} attempts")
            return None
        
        start = time.time()
        
        try:
            await self._ensure_session()
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
            data = {
                "contents": [{
                    "parts": [{"text": f"Generate SymPy code with detailed steps.\n\n{prompt}"}]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 2000
                }
            }
            
            async with self.session.post(url, json=data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if "candidates" in result and result["candidates"]:
                        content = result["candidates"][0]["content"]["parts"][0]["text"]
                        elapsed = time.time() - start
                        
                        self.stats.gemini.record_success(elapsed)
                        return {
                            "success": True,
                            "code": content,
                            "model": "gemini",
                            "time": elapsed
                        }
                    else:
                        self.stats.gemini.record_failure(time.time() - start, "No candidates")
                        return None
                        
                elif resp.status == 429:
                    self.stats.gemini.record_rate_limit()
                    retry_after = resp.headers.get('Retry-After', '60')
                    logger.warning(f"Gemini rate limited. Retry after {retry_after}s")
                    
                    await asyncio.sleep(int(retry_after))
                    return await self._call_gemini(prompt, retry_count + 1)
                    
                else:
                    error = await resp.text()
                    self.stats.gemini.record_failure(time.time() - start, error)
                    logger.api_error("Gemini", resp.status, error)
                    
                    if 500 <= resp.status < 600:  # Server errors
                        delay = RETRY_DELAY * (BACKOFF_FACTOR ** retry_count)
                        await asyncio.sleep(delay)
                        return await self._call_gemini(prompt, retry_count + 1)
                    
                    return None
                    
        except asyncio.TimeoutError:
            logger.error("Gemini timeout")
            self.stats.gemini.record_failure(time.time() - start, "timeout")
            
            if retry_count < MAX_RETRIES - 1:
                delay = RETRY_DELAY * (BACKOFF_FACTOR ** retry_count)
                await asyncio.sleep(delay)
                return await self._call_gemini(prompt, retry_count + 1)
            
            return None
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            self.stats.gemini.record_failure(time.time() - start, str(e))
            return None
    
    async def generate_code(self, question: str, domain: str = "general") -> Dict[str, Any]:
        """
        توليد كود SymPy مع خطوات مفصلة و LaTeX
        
        Args:
            question: السؤال
            domain: المجال
            
        Returns:
            Dict: {
                "success": bool,
                "code": str,
                "model": str,
                "time": float,
                "solution": Dict (نتيجة مع خطوات)
            }
        """
        if not self._running:
            return {
                "success": False,
                "error": "Engine not started. Call start() first."
            }
        
        self.stats.requests += 1
        domain_metrics = self.stats.get_domain_metrics(domain)
        start = time.time()
        
        # معالجة الأسئلة القصيرة
        if not question or len(question.strip()) < 3:
            self.stats.short_questions += 1
            question = complete_short_question(question, domain)
        
        # التحقق من Cache
        cache_key = self.cache._make_key(question, domain)
        cached = self.cache.get(cache_key)
        if cached:
            self.stats.cache_hits += 1
            cached["from_cache"] = True
            cached["time"] = time.time() - start
            return cached
        
        self.stats.cache_misses += 1
        
        # تحضير الـ prompt حسب المجال
        prompt = DomainSpecificPrompts.get_prompt(domain, question)
        
        # تجربة APIs
        api_result = None
        
        if self.groq_available:
            api_result = await self._call_groq(prompt)
        if not api_result and self.gemini_available:
            api_result = await self._call_gemini(prompt)
        
        if api_result and api_result.get("success"):
            code = self._clean_code(api_result["code"])
            
            # تنفيذ في Sandbox
            valid, solution = await self.sandbox.execute(code)
            
            result = {
                "success": True,
                "code": code,
                "model": api_result["model"],
                "time": api_result["time"],
                "solution": solution.to_dict() if solution else None
            }
            
            if valid:
                self.stats.successes += 1
                domain_metrics.record_api(1.0)
            else:
                self.stats.failures += 1
                result["error"] = solution.error if solution else "Unknown error"
            
            self.cache.set(cache_key, result)
            return result
        
        # Simulation
        self.stats.successes += 1
        template_name, confidence, func = self.template_manager.choose_template(question, domain)
        
        if template_name:
            code = self.template_manager.generate_code(template_name, func, domain)
            logger.info(f"Using template '{template_name}' (confidence: {confidence:.2f})")
            domain_metrics.record_simulation(confidence)
        else:
            code = self.template_manager.generate_code(None, None, domain)
            logger.info("Using default code")
            domain_metrics.record_simulation(0.0)
        
        # تنفيذ الكود في Sandbox للحصول على الخطوات
        valid, solution = await self.sandbox.execute(code)
        
        elapsed = time.time() - start
        result = {
            "success": True,
            "code": code,
            "model": "simulation",
            "time": elapsed,
            "template": template_name,
            "confidence": round(confidence, 2) if template_name else 0,
            "solution": solution.to_dict() if solution else None,
            "warning": "⚠️ Simulation mode - API not available"
        }
        
        self.cache.set(cache_key, result)
        return result
    
    async def start(self):
        """بدء تشغيل المحرك"""
        if self._running:
            logger.warning("Engine already running")
            return
        
        logger.info("Starting AI Engine...")
        await self._ensure_session()
        self._running = True
        
        # التحقق من المفاتيح
        if self._valid_key(self.groq_key):
            self.groq_available = await self._verify_key_with_retry(self._verify_groq, "Groq")
        
        if self._valid_key(self.gemini_key):
            self.gemini_available = await self._verify_key_with_retry(self._verify_gemini, "Gemini")
        
        if not self.groq_available and not self.gemini_available:
            logger.warning("⚠️ No APIs available - running in simulation mode")
        
        logger.info(f"AI Engine started - Groq: {self.groq_available}, Gemini: {self.gemini_available}")
    
    async def stop(self):
        """إيقاف المحرك وتنظيف الموارد"""
        if not self._running:
            return
        
        logger.info("Stopping AI Engine...")
        self._running = False
        
        async with self._cleanup_lock:
            if self.session and not self.session.closed:
                await self.session.close()
            
            await self.sandbox.cleanup()
            await asyncio.sleep(0.2)
        
        logger.info("AI Engine stopped")
    
    async def health_check(self) -> Dict:
        """فحص صحة المحرك"""
        return {
            "status": "running" if self._running else "stopped",
            "sympy_available": SYMPY_AVAILABLE,
            "stats": self.stats.to_dict(),
            "cache": self.cache.get_stats(),
            "apis": {
                "groq": self.groq_available,
                "gemini": self.gemini_available
            },
            "templates": len(self.template_manager.templates),
            "domains": [d.value for d in DomainType]
        }
    
    def get_stats(self) -> Dict:
        """الحصول على الإحصائيات"""
        return self.stats.to_dict()
    
    def reset_stats(self):
        """إعادة تعيين الإحصائيات"""
        self.stats = EngineStats()
        logger.info("Statistics reset")


# للاختبار
async def main():
    """اختبار المحرك"""
    print("\n" + "="*90)
    print("🧪 AI Engine - Advanced Dynamic Domains Test")
    print("="*90)
    
    engine = AIEngine()
    await engine.start()
    
    test_questions = [
        # General
        ("general", "Find derivative of x^3 + 2x^2"),
        ("general", "Solve equation 2x + 5 = 13"),
        
        # Calculus
        ("calculus", "Find integral of sin(x)"),
        ("calculus", "Find limit of sin(x)/x as x→0"),
        
        # Mechanics
        ("mechanics", "Calculate force: mass=10kg, acceleration=9.8 m/s²"),
        ("mechanics", "Find kinetic energy: mass=5kg, velocity=20 m/s"),
        
        # Electricity
        ("electricity", "Calculate voltage: current=2A, resistance=100Ω"),
        ("electricity", "Apply Ohm's law"),
        
        # Advanced
        ("thermodynamics", "Ideal gas law"),
        ("fluid_mechanics", "Bernoulli's equation"),
        ("control_systems", "Laplace transform of e^(-t) sin(t)"),
        ("signal_processing", "Fourier transform of exp(-x^2)"),
        
        # Short questions
        ("general", "derivative"),
        ("mechanics", "force"),
        ("electricity", "voltage"),
        ("calculus", "limit"),
    ]
    
    for i, (domain, q) in enumerate(test_questions, 1):
        print(f"\n📌 {i}. [{domain}] {q}")
        result = await engine.generate_code(q, domain)
        print(f"Model: {result.get('model')}")
        print(f"Time: {result.get('time', 0):.3f}s")
        if 'confidence' in result:
            print(f"Confidence: {result['confidence']}")
        if 'warning' in result:
            print(f"⚠️ {result['warning']}")
        if 'solution' in result and result['solution']:
            sol = result['solution']
            if sol.get('steps'):
                print(f"Steps: {len(sol['steps'])}")
            if sol.get('result_latex'):
                print(f"LaTeX: {sol['result_latex'][:100]}...")
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
    
    health = await engine.health_check()
    print(f"\n📊 Health Check:")
    print(f"   {json.dumps(health, indent=2, ensure_ascii=False)}")
    
    await engine.stop()
    print("\n✅ Test Complete")


if __name__ == "__main__":
    asyncio.run(main())
