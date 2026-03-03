# ai_engine.py - الإصدار المتوافق مع math_engine.py
import sympy as sp
import re
import httpx
import os
import hashlib
import sys
from typing import Dict, Any, Optional, Tuple, List

# ========== المفاتيح ==========
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# ========== التحقق من إصدار Python ==========
PYTHON_VERSION = sys.version_info
if PYTHON_VERSION < (3, 9):
    print("⚠️ تحذير: يفضل استخدام Python 3.9+ للحصول على أفضل النتائج")

# ========== دوال التنظيف ==========
def clean_input(text: str) -> str:
    """تنظيف الإدخال من المشاكل"""
    text = text.replace("السؤال :", "").replace("السؤال:", "")
    text = text.replace("سؤال :", "").replace("سؤال:", "")
    text = text.strip()
    return text

def clean_math_input(text: str) -> str:
    """تحويل الرموز العربية إلى صيغة Python"""
    text = text.lower()
    text = text.replace("²", "**2")
    text = text.replace("³", "**3")
    text = text.replace("⁴", "**4")
    text = text.replace("⁵", "**5")
    text = text.replace("^", "**")
    text = text.replace("×", "*")
    text = text.replace("÷", "/")
    text = text.replace(" ", "")
    return text

def normalize_question(text: str) -> str:
    """تطبيع السؤال للحصول على مفتاح موحد للذاكرة"""
    return clean_math_input(clean_input(text))

# ========== دوال LaTeX ==========
def to_latex(expr) -> str:
    """تحويل تعبير إلى LaTeX بأمان"""
    try:
        return sp.latex(expr)
    except:
        return str(expr)

def is_math(text: str) -> bool:
    """فحص إذا كان النص يحتوي على معادلة رياضية"""
    return any(c in text for c in '+-*/^=()')

def format_step(text: str, latex: str = "") -> Tuple[str, str]:
    """تنسيق خطوة واحدة (نص + LaTeX)"""
    return (text, latex)

# ========== ذاكرة التخزين المؤقت ==========
class Memory:
    def __init__(self):
        self.cache = {}
        self.stats = {"hits": 0, "misses": 0}
    
    def _make_key(self, text: str) -> str:
        """توليد مفتاح آمن من النص الطبيعي"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def get(self, text: str) -> Optional[Dict]:
        key = self._make_key(text)
        if key in self.cache:
            self.stats["hits"] += 1
            return self.cache[key]
        self.stats["misses"] += 1
        return None
    
    def set(self, text: str, value: Dict):
        key = self._make_key(text)
        self.cache[key] = value
    
    def get_stats(self):
        return self.stats

# ========== محرك الذكاء الاصطناعي ==========
class AIEngine:
    def __init__(self):
        self.memory = Memory()
        self.ready = True
        self.groq_key = GROQ_API_KEY
        self.gemini_key = GEMINI_API_KEY
        self.x, self.y, self.z = sp.symbols('x y z')
        print(f"✅ AI Engine ready - Python {PYTHON_VERSION.major}.{PYTHON_VERSION.minor}")
    
    def _generate_calculator_code(self, expr: str, result: float) -> str:
        """توليد كود آلة حاسبة"""
        return f'''
import sympy as sp
expr = sp.sympify("{expr}")
final_result = expr.evalf()
steps = [
    {format_step("🔢 عملية حسابية", "")},
    {format_step(f"${expr}$", f"${expr}$")},
    {format_step("✅ النتيجة النهائية:", f"$\\\\boxed{{{result}}}$")}
]
'''
    
    def _generate_derivative_code(self, func: str) -> str:
        """توليد كود مشتقة"""
        return f'''
import sympy as sp
x = sp.symbols('x')
f = sp.sympify("{func}")
final_result = sp.diff(f, x)
steps = [
    {format_step("📐 مشتقة", "")},
    {format_step(f"$f(x) = {func}$", f"$f(x) = {func}$")},
    {format_step("نطبق قواعد الاشتقاق", "")},
    {format_step(f"$f'(x) = {to_latex(sp.diff(sp.sympify(func), sp.symbols('x')))}$", 
                 f"$f'(x) = {to_latex(sp.diff(sp.sympify(func), sp.symbols('x')))}$")},
    {format_step("✅ النتيجة النهائية:", f"$\\\\boxed{{{to_latex(sp.diff(sp.sympify(func), sp.symbols('x')))}}}$")}
]
'''
    
    def _generate_integral_code(self, func: str) -> str:
        """توليد كود تكامل"""
        integral = sp.integrate(sp.sympify(func), sp.symbols('x'))
        return f'''
import sympy as sp
x = sp.symbols('x')
f = sp.sympify("{func}")
final_result = sp.integrate(f, x)
steps = [
    {format_step("📊 تكامل", "")},
    {format_step(f"$\\int {func} \\, dx$", f"$\\\\int {func} \\\\, dx$")},
    {format_step("نطبق قواعد التكامل", "")},
    {format_step(f"$\\int {func} \\, dx = {to_latex(integral)} + C$", 
                 f"$\\\\int {func} \\\\, dx = {to_latex(integral)} + C$")},
    {format_step("✅ النتيجة النهائية:", f"$\\\\boxed{{{to_latex(integral)} + C}}$")}
]
'''
    
    def _generate_equation_code(self, eq: str) -> str:
        """توليد كود معادلة"""
        return f'''
import sympy as sp
x = sp.symbols('x')
left, right = sp.sympify("{eq.split('=')[0]}"), sp.sympify("{eq.split('=')[1]}")
expr = left - right
final_result = sp.solve(expr, x)
steps = [
    {format_step("⚖️ معادلة", "")},
    {format_step(f"${eq}$", f"${eq}$")},
    {format_step("ننقل الحدود", "")},
    {format_step(f"${to_latex(left)} - {to_latex(right)} = 0$", f"${to_latex(left)} - {to_latex(right)} = 0$")},
    {format_step(f"الحل: $x = {to_latex(sp.solve(expr, x)[0])}$", f"$x = {to_latex(sp.solve(expr, x)[0])}$")},
    {format_step("✅ النتيجة النهائية:", f"$\\\\boxed{{x = {to_latex(sp.solve(expr, x)[0])}}}$")}
]
'''
    
    async def ask_gemini(self, question: str) -> Dict[str, Any]:
        """سؤال Gemini API"""
        if not self.gemini_key:
            return {"success": False, "error": "مفتاح Gemini غير موجود"}
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
                response = await client.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{
                            "parts": [{"text": question}]
                        }]
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "candidates" in data:
                        answer = data["candidates"][0]["content"]["parts"][0]["text"]
                        steps = [
                            format_step("🤖 إجابة Gemini", ""),
                            format_step(answer, answer if is_math(answer) else ""),
                            format_step("", "")
                        ]
                        return {
                            "success": True,
                            "result": answer,
                            "steps": steps,
                            "model": "gemini",
                            "from_cache": False
                        }
                return {"success": False, "error": f"Gemini error: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": f"Gemini error: {str(e)}"}
    
    async def generate_code(self, question: str, domain: str = "general") -> Dict[str, Any]:
        """توليد كود SymPy متوافق مع MathEngine"""
        
        # تطبيع السؤال للذاكرة
        normalized = normalize_question(question)
        
        # 1. التحقق من الذاكرة
        cached = self.memory.get(normalized)
        if cached:
            cached["from_cache"] = True
            return cached
        
        # تنظيف الإدخال
        cleaned = clean_math_input(question)
        
        try:
            # آلة حاسبة
            if all(c in "0123456789+-*/()." for c in cleaned.replace(" ", "")):
                result = sp.sympify(cleaned).evalf()
                code = self._generate_calculator_code(cleaned, float(result))
                response = {
                    "success": True,
                    "code": code,
                    "model": "calculator",
                    "from_cache": False
                }
                self.memory.set(normalized, response)
                return response
            
            # مشتقات
            elif "مشتق" in question or "derivative" in question or "diff" in question:
                func_match = re.search(r'([a-zA-Z0-9\*\-\+\/\(\)\^]+)', cleaned)
                if func_match:
                    func = func_match.group(1)
                    code = self._generate_derivative_code(func)
                    response = {
                        "success": True,
                        "code": code,
                        "model": "derivative",
                        "from_cache": False
                    }
                    self.memory.set(normalized, response)
                    return response
            
            # تكاملات
            elif "تكامل" in question or "integral" in question:
                func_match = re.search(r'([a-zA-Z0-9\*\-\+\/\(\)\^]+)', cleaned)
                if func_match:
                    func = func_match.group(1)
                    code = self._generate_integral_code(func)
                    response = {
                        "success": True,
                        "code": code,
                        "model": "integral",
                        "from_cache": False
                    }
                    self.memory.set(normalized, response)
                    return response
            
            # معادلات
            elif "حل" in question or "solve" in question or "=" in cleaned:
                code = self._generate_equation_code(cleaned)
                response = {
                    "success": True,
                    "code": code,
                    "model": "equation",
                    "from_cache": False
                }
                self.memory.set(normalized, response)
                return response
            
            # AI Fallback
            else:
                ai_result = await self.ask_gemini(question)
                if ai_result.get("success"):
                    self.memory.set(normalized, ai_result)
                    return ai_result
                else:
                    return {"success": False, "error": "لم يتم التعرف على نوع المسألة"}
                    
        except Exception as e:
            return {"success": False, "error": f"خطأ في التوليد: {str(e)}"}
    
    def get_stats(self):
        return {
            "memory": self.memory.get_stats()
        }
    
    async def start(self):
        pass
    
    async def stop(self):
        pass
