# ai_engine.py - الإصدار النهائي المحسن (مع كل الترقيات)
import sympy as sp
import re
import httpx
import os
import hashlib
from typing import Dict, Any, Optional, Tuple, List

# ========== المفاتيح ==========
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# ========== SymPy الآمن ==========
# قائمة الدوال المسموح بها فقط
ALLOWED_FUNCTIONS = {
    'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
    'cot': sp.cot, 'csc': sp.csc, 'sec': sp.sec,
    'asin': sp.asin, 'acos': sp.acos, 'atan': sp.atan,
    'log': sp.log, 'ln': sp.log, 'exp': sp.exp,
    'sqrt': sp.sqrt, 'abs': sp.Abs
}

def safe_sympify(expr: str):
    """تحويل آمن للتعبير باستخدام sympify"""
    try:
        # ✅ تقييد الدوال المسموح بها
        return sp.sympify(expr, locals=ALLOWED_FUNCTIONS, evaluate=True)
    except:
        raise ValueError(f"تعبير غير صالح: {expr}")

# ========== دوال التنظيف ==========
def clean_input(text: str) -> str:
    """تنظيف الإدخال من المشاكل"""
    text = text.replace("السؤال :", "").replace("السؤال:", "")
    text = text.replace("سؤال :", "").replace("سؤال:", "")
    text = text.strip()
    return text

def clean_math_input(text: str) -> str:
    """تحويل الرموز العربية إلى صيغة Python موحدة"""
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

# ========== استخراج المتغيرات ==========
def extract_variable(expr) -> sp.Symbol:
    """استخراج المتغير المستخدم في التعبير"""
    variables = list(expr.free_symbols)
    if variables:
        return variables[0]  # أول متغير
    return sp.symbols('x')  # افتراضي

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

# ========== ذاكرة التخزين المؤقت المحسنة ==========
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

# ========== محرك الرياضيات الآمن والمحسن ==========
class MathEngine:
    def __init__(self):
        self.x, self.y, self.z = sp.symbols('x y z')
    
    def calculator(self, expr: str) -> Tuple[str, List[tuple]]:
        """آلة حاسبة آمنة"""
        try:
            result_expr = safe_sympify(expr)
            result = result_expr.evalf()
            result_latex = to_latex(result)
            expr_latex = to_latex(result_expr)
            
            steps = [
                ("🔢 عملية حسابية", ""),
                ("التعبير:", expr_latex),
                ("النتيجة:", result_latex),
                ("✅ الإجابة النهائية:", f"\\boxed{{{result_latex}}}")
            ]
            return str(result), steps
        except Exception as e:
            return "خطأ", [(f"❌ {str(e)}", "")]
    
    def derivative(self, func: str) -> Tuple[str, List[tuple]]:
        """حساب المشتقة مع اكتشاف المتغير تلقائياً"""
        try:
            expr = safe_sympify(func)
            var = extract_variable(expr)
            result = sp.diff(expr, var)
            var_name = var.name
            
            steps = [
                (f"📐 مشتقة بالنسبة لـ {var_name}", ""),
                (f"f({var_name}) = {to_latex(expr)}", to_latex(expr)),
                ("نطبق قواعد الاشتقاق:", ""),
                (f"f'({var_name}) = {to_latex(result)}", to_latex(result)),
                ("✅ الإجابة النهائية:", f"\\boxed{{{to_latex(result)}}}")
            ]
            return str(result), steps
        except Exception as e:
            return "خطأ", [(f"❌ {str(e)}", "")]
    
    def integral(self, func: str) -> Tuple[str, List[tuple]]:
        """حساب التكامل مع اكتشاف المتغير تلقائياً"""
        try:
            expr = safe_sympify(func)
            var = extract_variable(expr)
            result = sp.integrate(expr, var)
            var_name = var.name
            
            steps = [
                (f"📊 تكامل بالنسبة لـ {var_name}", ""),
                (f"∫ {to_latex(expr)} d{var_name}", f"∫ {to_latex(expr)} d{var_name}"),
                ("نطبق قواعد التكامل:", ""),
                (f"= {to_latex(result)} + C", f"{to_latex(result)} + C"),
                ("✅ الإجابة النهائية:", f"\\boxed{{{to_latex(result)} + C}}")
            ]
            return str(result) + " + C", steps
        except Exception as e:
            return "خطأ", [(f"❌ {str(e)}", "")]
    
    def equation(self, eq: str) -> Tuple[str, List[tuple]]:
        """حل المعادلة مع خطوات"""
        try:
            if "=" in eq:
                left, right = eq.split("=")
                left_expr = safe_sympify(left)
                right_expr = safe_sympify(right)
                expr = left_expr - right_expr
            else:
                left_expr = safe_sympify(eq)
                right_expr = 0
                expr = left_expr
            
            var = extract_variable(expr)
            solutions = sp.solve(expr, var)
            var_name = var.name
            
            sol_list = []
            for sol in solutions:
                if sol.is_real:
                    sol_list.append(f"{var_name} = {to_latex(sol)}")
                else:
                    sol_list.append(f"{var_name} = {to_latex(sol)} (مركب)")
            
            sol_str = '  أو  '.join(sol_list) if sol_list else "لا يوجد حل حقيقي"
            
            steps = [
                ("⚖️ معادلة", ""),
                (f"{to_latex(left_expr)} = {to_latex(right_expr)}", f"{to_latex(left_expr)} = {to_latex(right_expr)}"),
                ("ننقل الحدود:", ""),
                (f"{to_latex(expr)} = 0", f"{to_latex(expr)} = 0"),
                (f"الحلول:", ""),
                (sol_str, sol_str),
                ("✅ الإجابة النهائية:", f"\\boxed{{{sol_str}}}")
            ]
            return sol_str, steps
        except Exception as e:
            return "خطأ", [(f"❌ {str(e)}", "")]

# ========== محرك AI مع Fallback ==========
class AIEngine:
    def __init__(self):
        self.math = MathEngine()
        self.memory = Memory()
        self.ready = True
        self.groq_key = GROQ_API_KEY
        self.gemini_key = GEMINI_API_KEY
        print("✅ AI Engine ready - الإصدار المحسن النهائي")
    
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
                            ("🤖 إجابة Gemini", ""),
                            (answer, answer if is_math(answer) else ""),
                            ("", "")
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
        # تطبيع السؤال للذاكرة
        normalized = normalize_question(question)
        
        # 1. التحقق من الذاكرة (بالمفتاح الموحد)
        cached = self.memory.get(normalized)
        if cached:
            cached["from_cache"] = True
            return cached
        
        result = ""
        steps = []
        model = ""
        
        try:
            # آلة حاسبة
            if all(c in "0123456789+-*/()." for c in normalized.replace(" ", "")):
                result, steps = self.math.calculator(normalized)
                model = "calculator"
            
            # مشتقات
            elif "مشتق" in question or "derivative" in question or "diff" in question:
                func_match = re.search(r'([a-zA-Z0-9\*\-\+\/\(\)\^]+)', normalized)
                if func_match:
                    result, steps = self.math.derivative(func_match.group(1))
                    model = "derivative"
                else:
                    return {"success": False, "error": "لم نتمكن من استخراج الدالة"}
            
            # تكاملات
            elif "تكامل" in question or "integral" in question:
                func_match = re.search(r'([a-zA-Z0-9\*\-\+\/\(\)\^]+)', normalized)
                if func_match:
                    result, steps = self.math.integral(func_match.group(1))
                    model = "integral"
                else:
                    return {"success": False, "error": "لم نتمكن من استخراج الدالة"}
            
            # معادلات
            elif "حل" in question or "solve" in question or "=" in normalized:
                result, steps = self.math.equation(normalized)
                model = "equation"
            
            # AI Fallback
            else:
                ai_result = await self.ask_gemini(question)
                if ai_result.get("success"):
                    self.memory.set(normalized, ai_result)
                    return ai_result
                else:
                    return {"success": False, "error": "لم يتم التعرف على نوع المسألة"}
            
            # تجهيز النتيجة
            response = {
                "success": True,
                "result": result,
                "steps": steps,
                "model": model,
                "from_cache": False
            }
            
            # حفظ في الذاكرة (بالمفتاح الموحد)
            self.memory.set(normalized, response)
            return response
            
        except Exception as e:
            return {"success": False, "error": f"خطأ في الحساب: {str(e)}"}
    
    def get_stats(self):
        return {
            "memory": self.memory.get_stats()
        }
    
    async def start(self):
        pass
    
    async def stop(self):
        pass
