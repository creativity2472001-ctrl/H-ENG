# ============================================
# ملف: config.py (الإصدار 2.8)
# الوظيفة: إعدادات التطبيق - كامل مع التحذيرات
# ============================================

import os
import json
from datetime import datetime

# ============================================================================
# ⚠️ ⚠️ ⚠️  تنبيهات مهمة جداً - اقرأها قبل الاستخدام  ⚠️ ⚠️ ⚠️
# ============================================================================
# 
# 1️⃣  Simulation (وضع المحاكاة):
#     ----------------------------------------
#     ❌ لا تعتمد على نتائج Simulation هندسياً
#     ✅ مفيد فقط للتجربة أو عند فشل API
#     ⚠️  القيم تقديرية وعشوائية ولا تمثل حلول دقيقة
# 
# 2️⃣  Cache (التخزين المؤقت):
#     ----------------------------------------
#     📦 التخزين في الذاكرة (RAM) فقط
#     ❌ يضيع عند إعادة تشغيل البرنامج
#     🔄 نضيف Redis أو ملف مستقبلاً للحفظ الدائم
# 
# 3️⃣  Timeout (مهلة الاتصال):
#     ----------------------------------------
#     ⏱️ القيمة الافتراضية: 20 ثانية
#     ✅ مناسبة للاستخدام العادي
#     🔧 يمكن زيادتها للعمليات الثقيلة عبر API_TIMEOUT
# 
# 4️⃣  الأمان (Security):
#     ----------------------------------------
#     🛡️ قائمة DANGEROUS_PATTERNS تمنع الأكواد الخطيرة
#     ⚠️ يجب تحديث هذه القائمة باستمرار
#     🔍 راجعها دورياً وأضف أي أنماط جديدة
# 
# 5️⃣  numpy:
#     ----------------------------------------
#     🔴 مقفل تماماً حالياً (ENABLE_NUMPY = False)
#     ✅ للأمان ومنع الثغرات
#     🔓 سيفتح في إصدار خاص بالعمليات الآمنة مستقبلاً
# 
# ============================================================================
# ✅ للإنتاج: تأكد من DEBUG_MODE = False
# ✅ للمفاتيح: استخدم متغيرات البيئة للأمان
# ============================================================================

# ========== مفاتيح API ==========
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "gsk_simulated_key_for_testing")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIza_simulated_key_for_testing")

# ========== إعدادات النماذج ==========
PRIMARY_MODEL = "llama-3.3-70b-versatile"
FALLBACK_MODEL = "gemini-1.5-flash"

# ========== إعدادات التصحيح والإنتاج ==========
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
PRODUCTION_MODE = not DEBUG_MODE

# ========== إعدادات الأداء ==========
SYSTEM_PROMPT_SIZE = "normal"  # "compact", "normal", "detailed"
ENABLE_ADVANCED_LATEX = True
ENABLE_NUMPY = False  # 🔴 مقفل للأمان حالياً

# ========== إعدادات الـ API و Timeout ==========
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "20"))  # 20 ثانية افتراضياً
MAX_RETRIES = 3
RETRY_DELAY = 1
BACKOFF_FACTOR = 2

# ========== إعدادات الـ Cache ==========
USE_CACHE = True
CACHE_TYPE = "memory"  # "memory", "redis", "file"
CACHE_SIZE = 100
CACHE_TTL = 3600  # ساعة واحدة
CACHE_FILE_PATH = "./cache/zaky_cache.json"  # للاستخدام المستقبلي

# ========== إعدادات الأمان ==========
MAX_CODE_LENGTH = 5000

# قائمة الأنماط الخطيرة - يجب تحديثها باستمرار
DANGEROUS_PATTERNS = [
    # استيرادات خطيرة
    "__import__", "import os", "from os", "import sys", "from sys",
    "import subprocess", "from subprocess", "import socket", "from socket",
    "import pickle", "from pickle", "import ctypes", "from ctypes",
    
    # دوال تنفيذ
    "eval(", "exec(", "compile(", "globals()", "locals()", "__dict__",
    
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

# ========== إعدادات السيرفر ==========
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# ========== القوالب التوجيهية ==========

# القالب الأساسي
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

# قواعد LaTeX المتقدمة
ADVANCED_LATEX_RULES = """
📐 **معالجة LaTeX المتقدمة:**
- استخدم sp.latex() أولاً
- إذا فشل: استخدم sp.simplify() ثم sp.latex()
- إذا فشل أيضاً: استخدم str() مع تنظيف الناتج
"""

# النسخة المضغوطة (للسرعة)
COMPACT_PROMPT = """
أنت محرك SymPy. حول السؤال لكود.
قواعد: كود خام، sp.symbols، final_result، steps مع latex.
"""

# النسخة المفصلة (للدقة)
DETAILED_PROMPT = BASE_PROMPT + """
📚 **تعليمات متقدمة:**
- للمشتقات الجزئية: sp.diff(f, x, y)
- للتكامل المحدد: sp.integrate(f, (x, a, b))
- للمعادلات التفاضلية: sp.dsolve(eq)
- للمصفوفات: sp.Matrix([[a,b],[c,d]])
- للمتسلسلات: sp.series(f, x, 0, 5)
"""

# بناء SYSTEM_PROMPT النهائي حسب الحجم المختار
if SYSTEM_PROMPT_SIZE == "compact":
    SYSTEM_PROMPT = COMPACT_PROMPT
elif SYSTEM_PROMPT_SIZE == "detailed":
    SYSTEM_PROMPT = DETAILED_PROMPT + (ADVANCED_LATEX_RULES if ENABLE_ADVANCED_LATEX else "")
else:  # normal
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
- V=IR, KVL (مجموع الجهود=0), KCL (مجموع التيارات=0)
- المكثفات: Q=CV, I=C dV/dt
- الملفات: V=L dI/dt
- القدرة: P=VI=I²R=V²/R
- المقاومات: التوالي R_total=R1+R2، التوازي 1/R_total=1/R1+1/R2
"""

PROMPT_CALCULUS = SYSTEM_PROMPT + """

📐 **تفاضل وتكامل:**
- المشتقات: sp.diff() (عادية وجزئية)
- التكامل: sp.integrate() (محدد وغير محدد)
- النهايات: sp.limit() (من اليمين واليسار)
- المتسلسلات: sp.series() (تايلور وماكلورين)
- المجموع: sp.Sum() (Σ)
- الجداء: sp.Product() (Π)
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
    "timeout": "⏱️ تجاوز الوقت المسموح ({timeout} ثانية)"
}

SUCCESS_MESSAGES = {
    "using_groq": "✅ استخدام Groq API",
    "using_gemini": "✅ استخدام Gemini API",
    "using_simulation": "🔄 وضع المحاكاة (نتائج تقديرية - لا تعتمد عليها)",
    "cached_response": "📦 من الذاكرة المؤقتة",
    "latex_success": "✅ تحويل LaTeX ناجح"
}

# ========== معلومات الإصدار والتحليلات ==========
VERSION = "2.8.0"
APP_NAME = "ذكي ماتك - المحرك الهندسي"
LAST_UPDATED = datetime.now().strftime("%Y-%m-%d")

# تنبيهات واضحة للمطور
CONFIG_NOTES = {
    "simulation": {
        "status": "تقديري فقط",
        "warning": "❌ لا تعتمد على Simulation هندسياً - قيم عشوائية"
    },
    "cache": {
        "status": "ذاكرة مؤقتة (RAM)",
        "warning": "❌ يضيع عند إعادة التشغيل"
    },
    "timeout": {
        "status": f"{API_TIMEOUT} ثانية",
        "note": "✅ مناسب للاستخدام العادي، زدها للعمليات الثقيلة"
    },
    "security": {
        "status": "قائمة محدثة",
        "warning": "⚠️ راجع DANGEROUS_PATTERNS دورياً"
    },
    "numpy": {
        "status": "مقفل 🔴",
        "reason": "للأمان - سيفتح مستقبلاً"
    }
}

CONFIG_ANALYSIS = {
    "version": VERSION,
    "last_updated": LAST_UPDATED,
    "production_ready": PRODUCTION_MODE,
    "numpy_enabled": ENABLE_NUMPY,
    "advanced_latex": ENABLE_ADVANCED_LATEX,
    "prompt_size": SYSTEM_PROMPT_SIZE,
    "cache_type": CACHE_TYPE,
    "api_timeout": API_TIMEOUT,
    "max_retries": MAX_RETRIES,
    "suitable_for": "الاستخدام الفردي والمتوسط (طلاب - مهندسين)",
    "limitations": [
        "⚠️ Simulation تقديري - لا تعتمد عليه هندسياً",
        "⚠️ Cache بالذاكرة فقط - يضيع عند إعادة التشغيل",
        f"⚠️ Timeout {API_TIMEOUT} ثانية - زدها للعمليات الثقيلة",
        "⚠️ الأمان يحتاج تحديث دوري لـ DANGEROUS_PATTERNS"
    ],
    "notes": CONFIG_NOTES
}

# ========== دوال المساعدة ==========

def get_config_info():
    """معلومات الإعدادات (بدون مفاتيح)"""
    return {
        "app_name": APP_NAME,
        "version": VERSION,
        "mode": "إنتاج" if PRODUCTION_MODE else "تجريبي",
        "numpy": "ممنوع 🔴" if not ENABLE_NUMPY else "مسموح 🟢",
        "latex": "متقدم" if ENABLE_ADVANCED_LATEX else "بسيط",
        "prompt_size": SYSTEM_PROMPT_SIZE,
        "cache": f"{CACHE_TYPE} 🟢" if USE_CACHE else "غير نشط 🔴",
        "timeout": f"{API_TIMEOUT} ثانية",
        "groq": "جاهز 🟢" if _check_key_valid(GROQ_API_KEY) else "غير جاهز 🔴",
        "gemini": "جاهز 🟢" if _check_key_valid(GEMINI_API_KEY) else "غير جاهز 🔴",
        "limitations": CONFIG_ANALYSIS["limitations"]
    }

def _check_key_valid(key):
    """التحقق من صحة المفتاح"""
    return bool(key and "simulated" not in key and len(key) > 20)

def is_code_safe(code):
    """التحقق من أمان الكود - محدث بأحدث المخاطر"""
    code_lower = code.lower()
    for pattern in DANGEROUS_PATTERNS:
        if pattern.lower() in code_lower:
            return False, pattern
    return True, None

def get_prompt_by_size(size="normal"):
    """اختيار حجم القالب المناسب"""
    prompts = {
        "compact": COMPACT_PROMPT,
        "normal": SYSTEM_PROMPT,
        "detailed": DETAILED_PROMPT + (ADVANCED_LATEX_RULES if ENABLE_ADVANCED_LATEX else "")
    }
    return prompts.get(size, SYSTEM_PROMPT)

def print_config_summary():
    """طباعة ملخص الإعدادات مع التنبيهات"""
    print(f"\n{'='*60}")
    print(f"🚀 {APP_NAME} v{VERSION}")
    print(f"{'='*60}")
    print(f"⚙️  الوضع: {'🔧 تجريبي' if DEBUG_MODE else '✅ إنتاج'}")
    print(f"📦 numpy: {'🔴 ممنوع' if not ENABLE_NUMPY else '🟢 مسموح'}")
    print(f"📐 LaTeX: {'🟢 متقدم' if ENABLE_ADVANCED_LATEX else '🟡 بسيط'}")
    print(f"🎯 حجم القالب: {SYSTEM_PROMPT_SIZE}")
    print(f"⏱️ Timeout: {API_TIMEOUT} ثانية")
    print(f"📦 Cache: {CACHE_TYPE} {'(يضيع عند إعادة التشغيل)' if CACHE_TYPE == 'memory' else ''}")
    print(f"🔑 Groq: {'🟢 جاهز' if _check_key_valid(GROQ_API_KEY) else '🟡 تجريبي'}")
    print(f"🔑 Gemini: {'🟢 جاهز' if _check_key_valid(GEMINI_API_KEY) else '🟡 تجريبي'}")
    print(f"{'='*60}")
    print(f"⚠️  تنبيهات هامة:")
    print(f"   1. ❌ Simulation تقديري - لا تعتمد عليه هندسياً")
    print(f"   2. ❌ Cache بالذاكرة فقط - يضيع عند إعادة التشغيل")
    print(f"   3. ⚠️  الأمان يحتاج تحديث - راجع DANGEROUS_PATTERNS")
    print(f"   4. ⏱️ Timeout {API_TIMEOUT} ثانية - مناسب للاستخدام العادي")
    print(f"{'='*60}\n")

# ========== التحقق من الإعدادات عند التحميل ==========
if DEBUG_MODE:
    print_config_summary()

# ========== تصدير الإعدادات للاستخدام ==========
__all__ = [
    'GROQ_API_KEY', 'GEMINI_API_KEY',
    'PRIMARY_MODEL', 'FALLBACK_MODEL',
    'DEBUG_MODE', 'PRODUCTION_MODE',
    'SYSTEM_PROMPT_SIZE', 'ENABLE_ADVANCED_LATEX', 'ENABLE_NUMPY',
    'API_TIMEOUT', 'MAX_RETRIES', 'RETRY_DELAY', 'BACKOFF_FACTOR',
    'USE_CACHE', 'CACHE_TYPE', 'CACHE_SIZE', 'CACHE_TTL', 'CACHE_FILE_PATH',
    'MAX_CODE_LENGTH', 'DANGEROUS_PATTERNS',
    'HOST', 'PORT',
    'SYSTEM_PROMPT', 'COMPACT_PROMPT', 'DETAILED_PROMPT',
    'PROMPT_MECHANICS', 'PROMPT_ELECTRICITY', 'PROMPT_CALCULUS',
    'ERROR_MESSAGES', 'SUCCESS_MESSAGES',
    'VERSION', 'APP_NAME', 'CONFIG_ANALYSIS', 'CONFIG_NOTES',
    'get_config_info', 'is_code_safe', 'get_prompt_by_size', 'print_config_summary'
]
