import os
import json
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any
import warnings
import ast

# ============================================================================
# 🚨🚨🚨  تنبيهات الإنتاج النهائية - اقرأها قبل النشر  🚨🚨🚨
# ============================================================================
#
# 1️⃣  مفاتيح API (الأهم!)
#     ----------------------------------------
#     ⚠️  المفاتيح الحالية محاكية (simulated) ولن تعمل في الإنتاج
#     ✅  استخدم متغيرات البيئة للمفاتيح الحقيقية:
#         export GROQ_API_KEY="gsk_your_real_key_here"
#         export GEMINI_API_KEY="AIza_your_real_key_here"
#     ❌  بدون مفاتيح حقيقية، سيعمل النظام بوضع المحاكاة فقط
#
# 2️⃣  Executor (الأداء على الخوادم الكبيرة)
#     ----------------------------------------
#     🖥️  خوادم > 8 أنوية: حدد MAX_WORKERS = 4 أو 8
#     💻  خوادم صغيرة: MAX_WORKERS = 2 كافٍ
#     ⚙️  الإعداد الافتراضي (0) = تلقائي، لكنه قد يستهلك موارد كثيرة
#
# 3️⃣  Sandbox (تنفيذ الكود)
#     ----------------------------------------
#     ⏱️  SANDBOX_TIMEOUT: مهلة تنفيذ الكود بالثواني (افتراضي: 10)
#     💾  SANDBOX_MEMORY_LIMIT: حد الذاكرة بالميجابايت (افتراضي: 256)
#     🔄  SANDBOX_MAX_RETRIES: عدد محاولات إعادة التنفيذ (افتراضي: 2)
#
# 4️⃣  Validator (التحقق من مخرجات LLM)
#     ----------------------------------------
#     ✅  VALIDATE_LLM_OUTPUT: تفعيل التحقق من مخرجات النماذج (افتراضي: True)
#     📏  VALIDATE_MAX_STEPS: الحد الأقصى لعدد الخطوات (افتراضي: 20)
#     🔍  VALIDATE_REQUIRE_FINAL_RESULT: التأكد من وجود final_result (افتراضي: True)
#
# 5️⃣  Audit Log (سجل التدقيق)
#     ----------------------------------------
#     📝  AUDIT_LOG_ENABLED: تفعيل سجل التدقيق (افتراضي: True)
#     📁  AUDIT_LOG_PATH: مسار ملف السجل (افتراضي: ./logs/audit.log)
#     🔐  AUDIT_LOG_MAX_SIZE: الحجم الأقصى للملف بالميجابايت (افتراضي: 100)
#     🔄  AUDIT_LOG_BACKUP_COUNT: عدد النسخ الاحتياطية (افتراضي: 5)
#
# 6️⃣  NUMPY (خطر أمني)
#     ----------------------------------------
#     🔴  ENABLE_NUMPY = False (لا تغيره!)
#     ⚠️  numpy قد يسبب ثغرات أمنية - لا تفعله إلا بعد مراجعة دقيقة
#
# 7️⃣  DEBUG_MODE (تسريب المعلومات)
#     ----------------------------------------
#     🔐  في الإنتاج: DEBUG_MODE = False (يمنع كشف المفاتيح وتفاصيل النظام)
#     🧪  في التطوير: DEBUG_MODE = True (يساعد في التصحيح)
#
# ============================================================================

# ========== إعدادات التطبيق الأساسية ==========
VERSION = "3.2.0"
APP_NAME = "Zaky Matik API"

# ========== إعدادات السيرفر ==========
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# ========== إعدادات التصحيح والإنتاج ==========
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
PRODUCTION_MODE = os.getenv("PRODUCTION_MODE", "True").lower() == "true"

# تحذير إذا كان DEBUG_MODE = True في الإنتاج
if PRODUCTION_MODE and DEBUG_MODE:
    warnings.warn(
        "\n" + "="*60 +
        "\n🔴🔴🔴 خطر أمني شديد 🔴🔴🔴" +
        "\nDEBUG_MODE = True في بيئة الإنتاج!" +
        "\nهذا قد يكشف:" +
        "\n   • مفاتيح API" +
        "\n   • تفاصيل النظام الداخلية" +
        "\n   • أكواد المستخدمين" +
        "\n⚡ قم فوراً بتعيين DEBUG_MODE = False" +
        "\n" + "="*60,
        RuntimeWarning
    )

# ========== ⚠️⚠️⚠️ مفاتيح API - استبدل المحاكية بمفاتيح حقيقية ⚠️⚠️⚠️ ==========
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "gsk_simulated_key_for_testing")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIza_simulated_key_for_testing")

# تحذير شديد للمفاتيح المحاكية في الإنتاج
if PRODUCTION_MODE:
    keys_issue = False
    if "simulated" in GROQ_API_KEY:
        warnings.warn(
            "\n" + "="*60 +
            "\n🔴 خطأ: Groq API key محاكي في الإنتاج!" +
            "\nلن يعمل الاتصال بـ Groq." +
            "\n✅ الحل: export GROQ_API_KEY='your_real_key'" +
            "\n" + "="*60,
            RuntimeWarning
        )
        keys_issue = True
    if "simulated" in GEMINI_API_KEY:
        warnings.warn(
            "\n" + "="*60 +
            "\n🔴 خطأ: Gemini API key محاكي في الإنتاج!" +
            "\nلن يعمل الاتصال بـ Gemini." +
            "\n✅ الحل: export GEMINI_API_KEY='your_real_key'" +
            "\n" + "="*60,
            RuntimeWarning
        )
        keys_issue = True
    
    if keys_issue:
        warnings.warn(
            "\n⚠️ النظام سيعمل بوضع المحاكاة (Simulation) فقط." +
            "\nالنتائج ستكون تقديرية وغير دقيقة.",
            RuntimeWarning
        )

# ========== إعدادات نماذج الذكاء الاصطناعي ==========
PRIMARY_MODEL = os.getenv("PRIMARY_MODEL", "llama-3.3-70b-versatile")
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "gemini-1.5-flash")

# ========== إعدادات الأداء ==========
SYSTEM_PROMPT_SIZE = os.getenv("SYSTEM_PROMPT_SIZE", "normal")  # "compact", "normal", "detailed"
ENABLE_ADVANCED_LATEX = os.getenv("ENABLE_ADVANCED_LATEX", "True").lower() == "true"

# ========== 🔴🔴🔴 NUMPY مقفل للأمان - لا تغيره! 🔴🔴🔴 ==========
ENABLE_NUMPY = False  # 🔴 ممنوع التغيير!

# ========== إعدادات الـ API و Timeout ==========
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "20"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY = float(os.getenv("RETRY_DELAY", "1"))
BACKOFF_FACTOR = int(os.getenv("BACKOFF_FACTOR", "2"))

# ========== ⚙️ إعدادات Executor للخوادم الكبيرة ==========
USE_PROCESS_POOL = os.getenv("USE_PROCESS_POOL", "False").lower() == "true"
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "0"))  # 0 = auto

# تحذير للخوادم الكبيرة (> 8 أنوية)
cpu_count = os.cpu_count() or 1
if PRODUCTION_MODE and MAX_WORKERS == 0 and cpu_count > 8:
    warnings.warn(
        f"\n🖥️  خادم بـ {cpu_count} نواة و MAX_WORKERS = 0 (تلقائي)." +
        f"\nهذا قد يستهلك موارد كثيرة." +
        f"\n✅ يوصى بتحديد MAX_WORKERS = 4 أو 8 للتحكم في الأداء." +
        f"\n⚡ مثال: export MAX_WORKERS=4",
        RuntimeWarning
    )

# ========== ⏱️ إعدادات Sandbox (تنفيذ الكود) ==========
SANDBOX_TIMEOUT = int(os.getenv("SANDBOX_TIMEOUT", "10"))  # مهلة التنفيذ بالثواني
SANDBOX_MEMORY_LIMIT = int(os.getenv("SANDBOX_MEMORY_LIMIT", "256"))  # حد الذاكرة بالميجابايت
SANDBOX_MAX_RETRIES = int(os.getenv("SANDBOX_MAX_RETRIES", "2"))  # عدد محاولات إعادة التنفيذ

# تحذير إذا كانت إعدادات Sandbox غير مناسبة للإنتاج
if PRODUCTION_MODE:
    if SANDBOX_TIMEOUT > 30:
        warnings.warn(
            f"\n⚠️ SANDBOX_TIMEOUT = {SANDBOX_TIMEOUT}s كبير جداً." +
            f"\nقد يتسبب في تعليق النظام. يوصى بـ 5-10 ثواني.",
            RuntimeWarning
        )
    if SANDBOX_MEMORY_LIMIT < 64:
        warnings.warn(
            f"\n⚠️ SANDBOX_MEMORY_LIMIT = {SANDBOX_MEMORY_LIMIT}MB صغير جداً." +
            f"\nقد لا يكفي للعمليات المعقدة. يوصى بـ 128-256MB.",
            RuntimeWarning
        )

# ========== ✅ إعدادات Validator (التحقق من مخرجات LLM) ==========
VALIDATE_LLM_OUTPUT = os.getenv("VALIDATE_LLM_OUTPUT", "True").lower() == "true"
VALIDATE_MAX_STEPS = int(os.getenv("VALIDATE_MAX_STEPS", "20"))  # الحد الأقصى للخطوات
VALIDATE_REQUIRE_FINAL_RESULT = os.getenv("VALIDATE_REQUIRE_FINAL_RESULT", "True").lower() == "true"
VALIDATE_REQUIRE_STEPS = os.getenv("VALIDATE_REQUIRE_STEPS", "False").lower() == "true"
VALIDATE_MAX_CODE_LENGTH = int(os.getenv("VALIDATE_MAX_CODE_LENGTH", "5000"))  # الحد الأقصى لطول الكود

# ========== 📝 إعدادات Audit Log (سجل التدقيق) ==========
AUDIT_LOG_ENABLED = os.getenv("AUDIT_LOG_ENABLED", "True").lower() == "true"
AUDIT_LOG_PATH = os.getenv("AUDIT_LOG_PATH", "./logs/audit.log")
AUDIT_LOG_MAX_SIZE = int(os.getenv("AUDIT_LOG_MAX_SIZE", "100"))  # بالميجابايت
AUDIT_LOG_BACKUP_COUNT = int(os.getenv("AUDIT_LOG_BACKUP_COUNT", "5"))
AUDIT_LOG_FORMAT = os.getenv("AUDIT_LOG_FORMAT", "json")  # "json" أو "text"

# إنشاء مجلد logs إذا لم يكن موجوداً
if AUDIT_LOG_ENABLED and AUDIT_LOG_PATH:
    log_dir = os.path.dirname(AUDIT_LOG_PATH)
    if log_dir:
        try:
            os.makedirs(log_dir, exist_ok=True)
            if DEBUG_MODE:
                print(f"📁 Log directory ready: {log_dir}")
        except Exception as e:
            warnings.warn(f"⚠️ Could not create log directory: {e}")

# ========== 📦 إعدادات Cache ==========
USE_CACHE = os.getenv("USE_CACHE", "True").lower() == "true"
CACHE_TYPE = os.getenv("CACHE_TYPE", "memory")  # "memory", "redis", "file"
CACHE_SIZE = int(os.getenv("CACHE_SIZE", "100"))
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))
CACHE_FILE_PATH = os.getenv("CACHE_FILE_PATH", "./cache/zaky_cache.json")

# تحذير: استخدام ملف مع Workers متعددين
if PRODUCTION_MODE and CACHE_TYPE == "file" and MAX_WORKERS > 1:
    warnings.warn(
        f"\n⚠️ تحذير: CACHE_TYPE = 'file' مع MAX_WORKERS = {MAX_WORKERS}" +
        f"\nهذا قد يسبب تضارب (Race Condition) في الوصول للملف." +
        f"\n✅ استخدم CACHE_TYPE = 'redis' بدلاً من ذلك.",
        RuntimeWarning
    )

# التأكد من وجود مجلد Cache وأذونات الكتابة (للنوع file)
if CACHE_TYPE == "file" and CACHE_FILE_PATH:
    cache_dir = os.path.dirname(CACHE_FILE_PATH)
    if cache_dir:
        try:
            os.makedirs(cache_dir, exist_ok=True)
            # اختبار أذونات الكتابة
            test_file = os.path.join(cache_dir, ".write_test")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            if DEBUG_MODE:
                print(f"📁 Cache directory ready: {cache_dir}")
        except PermissionError:
            warnings.warn(
                f"\n🔴 خطأ في أذونات الكتابة: {cache_dir}" +
                f"\nلن يتمكن النظام من حفظ Cache." +
                f"\n✅ الحل: mkdir -p {cache_dir} && chmod 755 {cache_dir}",
                RuntimeWarning
            )
        except Exception as e:
            if DEBUG_MODE:
                print(f"⚠️ تحذير: {e}")

# ========== إعدادات الأمان ==========
MAX_CODE_LENGTH = int(os.getenv("MAX_CODE_LENGTH", "5000"))

# قائمة الأنماط الخطيرة - محدثة بأحدث المخاطر
DANGEROUS_PATTERNS: List[str] = [
    # استيرادات خطيرة
    "__import__", "import os", "from os", "import sys", "from sys",
    "import subprocess", "from subprocess", "import socket", "from socket",
    "import pickle", "from pickle", "import ctypes", "from ctypes",
    
    # دوال تنفيذ
    "eval(", "exec(", "compile(", "globals()", "locals()", "__dict__",
    
    # دوال خطيرة إضافية
    "getattr(", "setattr(", "delattr(", "hasattr(",
    "__builtins__", "__builtins__.", "builtins.",
    
    # ملفات
    "open(", "file(", "read(", "write(", "remove(", "unlink(",
    
    # numpy (ممنوع)
    "numpy", "np.", "import numpy", "from numpy",
    
    # أوامر نظام
    "os.system", "os.popen", "subprocess.run", "subprocess.Popen",
    "os.environ", "os.getenv", "os.putenv",
    
    # شبكات
    "requests.get", "requests.post", "urllib", "httpx",
    
    # تسلسل خطير
    "pickle.loads", "pickle.dumps", "marshal",
    
    # دوال بايثون خطيرة
    "__reduce__", "__reduce_ex__", "__setstate__",
    "__getattribute__", "__setattr__",
    
    # حذف ملفات
    "os.remove", "os.rmdir", "shutil.rmtree",
]

def advanced_code_check(code: str) -> Tuple[bool, Optional[str]]:
    """
    فحص متقدم للكود باستخدام AST للكشف عن محاولات الالتفاف على الفحص النصي.
    
    Args:
        code: الكود المراد فحصه
        
    Returns:
        (safe, reason): safe = True إذا كان الكود آمناً
    """
    try:
        tree = ast.parse(code)
        
        for node in ast.walk(tree):
            # الكشف عن concatenation في أسماء الدوال
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
                if isinstance(node.left, ast.Str) or isinstance(node.right, ast.Str):
                    return False, "String concatenation detected - possible bypass attempt"
            
            # الكشف عن استدعاء getattr
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'getattr':
                    return False, "getattr() detected - possible dynamic execution"
                if isinstance(node.func, ast.Attribute) and node.func.attr == 'getattr':
                    return False, "getattr() detected - possible dynamic execution"
            
            # الكشف عن الوصول إلى __builtins__
            if isinstance(node, ast.Attribute):
                if node.attr == '__builtins__' or node.attr == '__builtins__':
                    return False, "__builtins__ access detected"
        
        return True, None
    except SyntaxError:
        # سيتم التعامل مع SyntaxError لاحقاً
        return True, None
    except Exception as e:
        return False, f"AST analysis error: {e}"

# ========== القوالب التوجيهية ==========
BASE_PROMPT = """
أنت محرك رياضي وهندسي متخصص في SymPy.

**القواعد:**
1. كود خام (Plain Text) - بدون Markdown
2. import sympy as sp فقط (numpy غير مسموح)
3. استخدم sp.symbols() للمتغيرات
4. النتيجة: final_result
5. الخطوات: steps [{"text":"شرح","latex":"صيغة"}]

**العمليات:** diff, integrate, solve, limit, dsolve, Sum, Product
"""

ADVANCED_LATEX_RULES = """
📐 **معالجة LaTeX المتقدمة:**
- استخدم sp.latex() أولاً
- إذا فشل: استخدم sp.simplify() ثم sp.latex()
- إذا فشل أيضاً: استخدم str() مع تنظيف الناتج
"""

COMPACT_PROMPT = """
أنت محرك SymPy. حول السؤال لكود.
قواعد: كود خام، sp.symbols، final_result، steps مع latex.
"""

DETAILED_PROMPT = BASE_PROMPT + """
📚 **تعليمات متقدمة:**
- للمشتقات الجزئية: sp.diff(f, x, y)
- للتكامل المحدد: sp.integrate(f, (x, a, b))
- للمعادلات التفاضلية: sp.dsolve(eq)
- للمصفوفات: sp.Matrix([[a,b],[c,d]])
- للمتسلسلات: sp.series(f, x, 0, 5)
"""

# بناء SYSTEM_PROMPT النهائي
if SYSTEM_PROMPT_SIZE == "compact":
    SYSTEM_PROMPT = COMPACT_PROMPT
elif SYSTEM_PROMPT_SIZE == "detailed":
    SYSTEM_PROMPT = DETAILED_PROMPT + (ADVANCED_LATEX_RULES if ENABLE_ADVANCED_LATEX else "")
else:
    SYSTEM_PROMPT = BASE_PROMPT + (ADVANCED_LATEX_RULES if ENABLE_ADVANCED_LATEX else "")

# ========== القوالب المتخصصة ==========
PROMPT_MECHANICS = SYSTEM_PROMPT + """

🔧 **ميكانيكا:**
- F=ma, KE=0.5*m*v**2, PE=m*g*h, g=9.81
- معادلات الحركة: v=u+at, s=ut+0.5at², v²=u²+2as
- استخدم sp.sqrt للجذور التربيعية
"""

PROMPT_ELECTRICITY = SYSTEM_PROMPT + """

⚡ **كهرباء:**
- V=IR, KVL, KCL
- المكثفات: Q=CV, I=C dV/dt
- الملفات: V=L dI/dt
- القدرة: P=VI=I²R=V²/R
"""

PROMPT_CALCULUS = SYSTEM_PROMPT + """

📐 **تفاضل وتكامل:**
- المشتقات: sp.diff()
- التكامل: sp.integrate()
- النهايات: sp.limit()
- المتسلسلات: sp.series()
- المجموع: sp.Sum()
- الجداء: sp.Product()
"""

# ========== رسائل النظام ==========
ERROR_MESSAGES = {
    "no_api_key": "⚠️ لا توجد مفاتيح API صالحة. استخدام وضع المحاكاة (نتائج تقديرية)",
    "code_too_long": f"⚠️ الكود طويل جداً (الحد {MAX_CODE_LENGTH} حرف)",
    "dangerous_code": "⚠️ كود غير آمن: {pattern}",
    "execution_failed": "❌ فشل التنفيذ: {error}",
    "invalid_question": "❌ السؤال غير صحيح",
    "latex_failed": "⚠️ تحويل LaTeX فشل، استخدام نص عادي",
    "numpy_forbidden": "⚠️ numpy غير مسموح به حالياً للأمان",
    "rate_limit": "⚠️ تجاوز حد الطلبات، انتظر قليلاً",
    "timeout": "⏱️ تجاوز الوقت المسموح ({timeout} ثانية)",
    "sandbox_timeout": f"⏱️ تجاوز وقت تنفيذ الكود ({SANDBOX_TIMEOUT} ثانية)",
    "sandbox_memory": f"💾 تجاوز حد الذاكرة المسموح ({SANDBOX_MEMORY_LIMIT} MB)",
    "validation_failed": "❌ فشل التحقق من مخرجات النموذج: {reason}"
}

SUCCESS_MESSAGES = {
    "using_groq": "✅ استخدام Groq API",
    "using_gemini": "✅ استخدام Gemini API",
    "using_simulation": "🔄 وضع المحاكاة (نتائج تقديرية)",
    "cached_response": "📦 من الذاكرة المؤقتة",
    "latex_success": "✅ تحويل LaTeX ناجح",
    "validation_passed": "✅ التحقق من المخرجات ناجح"
}

# ========== معلومات الإصدار ==========
LAST_UPDATED = datetime.now().strftime("%Y-%m-%d")

# ========== دوال المساعدة ==========

def _check_key_valid(key: str) -> bool:
    """التحقق من صحة المفتاح (مفتاح حقيقي وليس محاكي)"""
    return bool(key and "simulated" not in key and len(key) > 20)

def get_config_info() -> Dict[str, Any]:
    """
    الحصول على معلومات الإعدادات الحالية.
    
    Returns:
        قاموس يحتوي على معلومات الإعدادات (بدون مفاتيح API)
    """
    return {
        "version": VERSION,
        "app_name": APP_NAME,
        "debug_mode": DEBUG_MODE,
        "production_mode": PRODUCTION_MODE,
        "cache_type": CACHE_TYPE,
        "cache_size": CACHE_SIZE,
        "cache_ttl": CACHE_TTL,
        "primary_model": PRIMARY_MODEL,
        "fallback_model": FALLBACK_MODEL,
        "api_timeout": API_TIMEOUT,
        "max_retries": MAX_RETRIES,
        "max_workers": MAX_WORKERS if MAX_WORKERS > 0 else cpu_count,
        "use_process_pool": USE_PROCESS_POOL,
        "enable_advanced_latex": ENABLE_ADVANCED_LATEX,
        "enable_numpy": ENABLE_NUMPY,
        "max_code_length": MAX_CODE_LENGTH,
        "groq_available": _check_key_valid(GROQ_API_KEY),
        "gemini_available": _check_key_valid(GEMINI_API_KEY),
        "cpu_count": cpu_count,
        "last_updated": LAST_UPDATED,
        
        # إعدادات Sandbox
        "sandbox_timeout": SANDBOX_TIMEOUT,
        "sandbox_memory_limit": SANDBOX_MEMORY_LIMIT,
        "sandbox_max_retries": SANDBOX_MAX_RETRIES,
        
        # إعدادات Validator
        "validate_llm_output": VALIDATE_LLM_OUTPUT,
        "validate_max_steps": VALIDATE_MAX_STEPS,
        "validate_require_final_result": VALIDATE_REQUIRE_FINAL_RESULT,
        "validate_require_steps": VALIDATE_REQUIRE_STEPS,
        "validate_max_code_length": VALIDATE_MAX_CODE_LENGTH,
        
        # إعدادات Audit Log
        "audit_log_enabled": AUDIT_LOG_ENABLED,
        "audit_log_path": AUDIT_LOG_PATH if DEBUG_MODE else "[hidden]",
        "audit_log_max_size": AUDIT_LOG_MAX_SIZE,
        "audit_log_backup_count": AUDIT_LOG_BACKUP_COUNT,
        "audit_log_format": AUDIT_LOG_FORMAT
    }

def is_code_safe(code: str, use_ast: bool = True) -> Tuple[bool, Optional[str]]:
    """
    التحقق من أمان الكود (نصياً وباستخدام AST).
    
    Args:
        code: الكود المراد فحصه
        use_ast: تفعيل فحص AST المتقدم
        
    Returns:
        (safe, reason): safe = True إذا كان الكود آمناً
    """
    # الفحص النصي
    code_lower = code.lower()
    for pattern in DANGEROUS_PATTERNS:
        if pattern.lower() in code_lower:
            return False, pattern
    
    # الفحص المتقدم باستخدام AST
    if use_ast:
        ast_safe, ast_reason = advanced_code_check(code)
        if not ast_safe:
            return False, ast_reason
    
    return True, None

def get_prompt_by_size(size: str = "normal") -> str:
    """اختيار حجم القالب المناسب"""
    prompts = {
        "compact": COMPACT_PROMPT,
        "normal": SYSTEM_PROMPT,
        "detailed": DETAILED_PROMPT + (ADVANCED_LATEX_RULES if ENABLE_ADVANCED_LATEX else "")
    }
    return prompts.get(size, SYSTEM_PROMPT)

def print_config_summary() -> None:
    """طباعة ملخص الإعدادات"""
    config_info = get_config_info()
    
    print(f"\n{'='*80}")
    print(f"🚀 {APP_NAME} v{VERSION}")
    print(f"{'='*80}")
    print(f"🔧 DEBUG_MODE:           {'🟢 ON (تطوير)' if DEBUG_MODE else '🔴 OFF (إنتاج)'}")
    print(f"🔑 Groq API:             {'🟢 حقيقي' if config_info['groq_available'] else '🟡 محاكي'}")
    print(f"🔑 Gemini API:           {'🟢 حقيقي' if config_info['gemini_available'] else '🟡 محاكي'}")
    print(f"⚙️  Executor:             {'Process' if USE_PROCESS_POOL else 'Thread'}Pool")
    print(f"📊 Max Workers:          {config_info['max_workers']}")
    print(f"🖥️  CPU Cores:            {cpu_count}")
    print(f"{'─'*80}")
    print(f"⏱️  Sandbox Timeout:      {SANDBOX_TIMEOUT}s")
    print(f"💾 Sandbox Memory Limit: {SANDBOX_MEMORY_LIMIT}MB")
    print(f"🔄 Sandbox Max Retries:  {SANDBOX_MAX_RETRIES}")
    print(f"{'─'*80}")
    print(f"✅ Validate LLM Output:  {'🟢' if VALIDATE_LLM_OUTPUT else '🔴'}")
    print(f"📏 Max Steps:            {VALIDATE_MAX_STEPS}")
    print(f"🔍 Require Final Result: {'🟢' if VALIDATE_REQUIRE_FINAL_RESULT else '🔴'}")
    print(f"{'─'*80}")
    print(f"📝 Audit Log Enabled:    {'🟢' if AUDIT_LOG_ENABLED else '🔴'}")
    if AUDIT_LOG_ENABLED:
        print(f"📁 Log Path:             {AUDIT_LOG_PATH}")
        print(f"📦 Max Size:             {AUDIT_LOG_MAX_SIZE}MB")
        print(f"🔄 Backups:              {AUDIT_LOG_BACKUP_COUNT}")
    print(f"{'─'*80}")
    print(f"📦 Cache:                {CACHE_TYPE}")
    print(f"⏱️  Timeout:              {API_TIMEOUT}s")
    print(f"📏 Max Code:             {MAX_CODE_LENGTH} chars")
    print(f"{'='*80}")
    
    # تنبيهات صريحة
    if PRODUCTION_MODE:
        if not config_info['groq_available'] or not config_info['gemini_available']:
            print(f"\n⚠️⚠️⚠️  تنبيه: مفاتيح API محاكية في الإنتاج!")
            print(f"   • النظام سيعمل بوضع المحاكاة (نتائج غير دقيقة)")
            print(f"   • استبدلها بمفاتيح حقيقية في متغيرات البيئة")
        
        if MAX_WORKERS == 0 and cpu_count > 8:
            print(f"\n💡 نصيحة أداء: خادمك بـ {cpu_count} نواة")
            print(f"   • حدد MAX_WORKERS = 4 أو 8 لتحسين الأداء")
            print(f"   • مثال: export MAX_WORKERS=4")
    
    if CACHE_TYPE == "file":
        print(f"\n📁 Cache file: {CACHE_FILE_PATH}")
        print(f"   • تأكد من أذونات الكتابة على هذا المسار")
    
    print(f"{'='=80}\n")

# ========== عرض الملخص في وضع التصحيح ==========
if DEBUG_MODE:
    print_config_summary()

# ========== تصدير الإعدادات ==========
__all__ = [
    # معلومات أساسية
    'VERSION', 'APP_NAME', 'LAST_UPDATED',
    
    # إعدادات السيرفر
    'HOST', 'PORT', 'DEBUG_MODE', 'PRODUCTION_MODE',
    
    # مفاتيح API
    'GROQ_API_KEY', 'GEMINI_API_KEY',
    'PRIMARY_MODEL', 'FALLBACK_MODEL',
    
    # إعدادات الأداء
    'SYSTEM_PROMPT_SIZE', 'ENABLE_ADVANCED_LATEX', 'ENABLE_NUMPY',
    'API_TIMEOUT', 'MAX_RETRIES', 'RETRY_DELAY', 'BACKOFF_FACTOR',
    
    # إعدادات Executor
    'MAX_WORKERS', 'USE_PROCESS_POOL',
    
    # إعدادات Sandbox
    'SANDBOX_TIMEOUT', 'SANDBOX_MEMORY_LIMIT', 'SANDBOX_MAX_RETRIES',
    
    # إعدادات Validator
    'VALIDATE_LLM_OUTPUT', 'VALIDATE_MAX_STEPS', 
    'VALIDATE_REQUIRE_FINAL_RESULT', 'VALIDATE_REQUIRE_STEPS',
    'VALIDATE_MAX_CODE_LENGTH',
    
    # إعدادات Audit Log
    'AUDIT_LOG_ENABLED', 'AUDIT_LOG_PATH', 'AUDIT_LOG_MAX_SIZE',
    'AUDIT_LOG_BACKUP_COUNT', 'AUDIT_LOG_FORMAT',
    
    # إعدادات Cache
    'USE_CACHE', 'CACHE_TYPE', 'CACHE_SIZE', 'CACHE_TTL', 'CACHE_FILE_PATH',
    
    # إعدادات الأمان
    'MAX_CODE_LENGTH', 'DANGEROUS_PATTERNS',
    
    # القوالب
    'SYSTEM_PROMPT', 'COMPACT_PROMPT', 'DETAILED_PROMPT',
    'PROMPT_MECHANICS', 'PROMPT_ELECTRICITY', 'PROMPT_CALCULUS',
    
    # الرسائل
    'ERROR_MESSAGES', 'SUCCESS_MESSAGES',
    
    # دوال المساعدة
    'get_config_info', 'is_code_safe', 'get_prompt_by_size', 'print_config_summary',
    'advanced_code_check'
]
