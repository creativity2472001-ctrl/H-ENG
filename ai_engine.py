# ai_engine.py - الإصدار النهائي الكامل مع جميع التحسينات
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
        return variables[0]
    return sp.symbols('x')

def extract_variables_from_expr(expr_str: str) -> List[str]:
    """استخراج جميع المتغيرات من تعبير"""
    try:
        expr = safe_sympify(expr_str)
        return [str(var) for var in expr.free_symbols]
    except:
        # إذا فشل التحويل، ابحث عن المتغيرات بالنمط
        return re.findall(r'[xyz]', expr_str)

# ========== دوال LaTeX ==========
def to_latex(expr) -> str:
    """تحويل تعبير إلى LaTeX بأمان"""
    try:
        return sp.latex(expr)
    except:
        return str(expr)

def is_math(text: str) -> bool:
    """فحص إذا كان النص يحتوي على معادلة رياضية"""
    math_patterns = [
        r'[\d\+\-\*/\^\(\)]',  # رموز رياضية
        r'(sin|cos|tan|cot|sec|csc|log|ln|exp|sqrt)',  # دوال رياضية
        r'[xyz]',  # متغيرات
    ]
    text_lower = text.lower()
    for pattern in math_patterns:
        if re.search(pattern, text_lower):
            return True
    return False

def format_step(text: str, latex: str = "") -> Tuple[str, str]:
    """تنسيق خطوة واحدة (نص + LaTeX)"""
    return (text, latex)

# ========== ذاكرة التخزين المؤقت ==========
class Memory:
    def __init__(self):
        self.cache = {}
        self.stats = {"hits": 0, "misses": 0}
    
    def _make_key(self, text: str) -> str:
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

# ========== محرك الرياضيات الرمزية ==========
class SymbolicMath:
    """محرك الرياضيات الرمزية"""
    
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
                (f"التعبير: {expr_latex}", expr_latex),
                (f"النتيجة: {result_latex}", result_latex),
                ("✅ الإجابة النهائية:", f"\\boxed{{{result_latex}}}")
            ]
            return str(result), steps
        except Exception as e:
            return "خطأ", [(f"❌ {str(e)}", "")]
    
    def derivative(self, func: str) -> Tuple[str, List[tuple]]:
        """حساب المشتقة مع اكتشاف المتغيرات"""
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
        """حساب التكامل مع اكتشاف المتغيرات"""
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
        """حل المعادلة مع اكتشاف المتغيرات"""
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
                ("الحلول:", ""),
                (sol_str, sol_str),
                ("✅ الإجابة النهائية:", f"\\boxed{{{sol_str}}}")
            ]
            return sol_str, steps
        except Exception as e:
            return "خطأ", [(f"❌ {str(e)}", "")]

# ========== دوال توليد الكود المحسنة ==========
class CodeGenerator:
    """توليد كود SymPy بشكل آمن"""
    
    @staticmethod
    def _escape_string(text: str) -> str:
        """تنظيف النص من علامات الاقتباس"""
        if text is None:
            return ""
        return str(text).replace('"', '\\"').replace('\n', '\\n')
    
    @staticmethod
    def _steps_to_code(steps: List[tuple]) -> str:
        """تحويل الخطوات إلى كود"""
        steps_code = []
        for step in steps:
            desc, latex = step
            desc = CodeGenerator._escape_string(desc)
            latex = CodeGenerator._escape_string(latex)
            steps_code.append(f'    format_step("{desc}", "{latex}")')
        return ',\n'.join(steps_code)
    
    @staticmethod
    def calculator(expr: str, result: float, steps: List[tuple]) -> str:
        """توليد كود آلة حاسبة"""
        steps_code = CodeGenerator._steps_to_code(steps)
        expr_clean = CodeGenerator._escape_string(expr)
        
        return f'''# كود آلة حاسبة
import sympy as sp

def format_step(text: str, latex: str = "") -> tuple:
    return (text, latex)

expr = sp.sympify("{expr_clean}")
final_result = expr.evalf()
steps = [
{steps_code}
]'''
    
    @staticmethod
    def derivative(func: str, steps: List[tuple]) -> str:
        """توليد كود مشتقة مع اكتشاف المتغيرات"""
        # استخراج المتغيرات
        variables = extract_variables_from_expr(func)
        var_name = variables[0] if variables else 'x'
        
        steps_code = CodeGenerator._steps_to_code(steps)
        func_clean = CodeGenerator._escape_string(func)
        
        return f'''# كود مشتقة
import sympy as sp

def format_step(text: str, latex: str = "") -> tuple:
    return (text, latex)

{var_name} = sp.symbols('{var_name}')
f = sp.sympify("{func_clean}")
final_result = sp.diff(f, {var_name})
steps = [
{steps_code}
]'''
    
    @staticmethod
    def integral(func: str, steps: List[tuple]) -> str:
        """توليد كود تكامل مع اكتشاف المتغيرات"""
        # استخراج المتغيرات
        variables = extract_variables_from_expr(func)
        var_name = variables[0] if variables else 'x'
        
        steps_code = CodeGenerator._steps_to_code(steps)
        func_clean = CodeGenerator._escape_string(func)
        
        return f'''# كود تكامل
import sympy as sp

def format_step(text: str, latex: str = "") -> tuple:
    return (text, latex)

{var_name} = sp.symbols('{var_name}')
f = sp.sympify("{func_clean}")
final_result = sp.integrate(f, {var_name})
steps = [
{steps_code}
]'''
    
    @staticmethod
    def equation(eq: str, steps: List[tuple]) -> str:
        """توليد كود معادلة مع اكتشاف المتغيرات"""
        # استخراج المتغيرات
        variables = extract_variables_from_expr(eq)
        var_name = variables[0] if variables else 'x'
        
        steps_code = CodeGenerator._steps_to_code(steps)
        eq_clean = CodeGenerator._escape_string(eq)
        
        left_part = eq.split('=')[0] if '=' in eq else eq
        right_part = eq.split('=')[1] if '=' in eq else '0'
        left_clean = CodeGenerator._escape_string(left_part)
        right_clean = CodeGenerator._escape_string(right_part)
        
        return f'''# كود معادلة
import sympy as sp

def format_step(text: str, latex: str = "") -> tuple:
    return (text, latex)

{var_name} = sp.symbols('{var_name}')
left = sp.sympify("{left_clean}")
right = sp.sympify("{right_clean}")
expr = left - right
final_result = sp.solve(expr, {var_name})
steps = [
{steps_code}
]'''
    
    @staticmethod
    def ai_fallback(provider: str, result: str, steps: List[tuple]) -> str:
        """توليد كود لنتيجة الذكاء الاصطناعي"""
        result_clean = CodeGenerator._escape_string(result)
        
        steps_code = []
        for step in steps:
            desc, latex = step
            desc = CodeGenerator._escape_string(desc)
            latex = CodeGenerator._escape_string(latex)
            steps_code.append(f'    ("{desc}", "{latex}")')
        steps_str = ',\n'.join(steps_code)
        
        return f'''# إجابة {provider}
result = "{result_clean}"
steps = [
{steps_str}
]
final_result = result'''

# ========== محرك AI مع Fallback متعدد ==========
class AIEngine:
    def __init__(self):
        self.math = SymbolicMath()
        self.memory = Memory()
        self.ready = True
        self.groq_key = GROQ_API_KEY
        self.gemini_key = GEMINI_API_KEY
        self.code_gen = CodeGenerator()
        print("✅ AI Engine ready - الإصدار النهائي مع جميع التحسينات")
    
    def _is_simple_arithmetic(self, expr: str) -> bool:
        """فحص إذا كان التعبير حسابياً بسيطاً (أرقام فقط)"""
        cleaned = expr.replace(" ", "")
        
        # إذا كان هناك متغيرات، فليس حساباً بسيطاً
        if any(var in cleaned for var in ['x', 'y', 'z']):
            return False
        
        allowed_chars = "0123456789+-*/()."
        return all(c in allowed_chars for c in cleaned)
    
    def _extract_math_expression(self, text: str) -> Optional[str]:
        """استخراج التعبير الرياضي من النص بشكل دقيق"""
        # تنظيف النص أولاً
        cleaned = clean_math_input(text)
        
        # إزالة الكلمات الدالة
        for word in ["مشتقة", "مشتق", "derivative", "diff", "تكامل", "integral", "حل", "solve"]:
            cleaned = cleaned.replace(word, "").strip()
        
        # قائمة الأنماط المتقدمة
        patterns = [
            # نمط f(x) = ...
            r'f\([xyz]\)\s*=\s*([^,\n]+)',
            
            # نمط دالة بين قوسين
            r'[\(\s]*([a-zA-Z0-9\*\-\+\/\(\)\^]+(?:sin|cos|tan|log|exp|sqrt)[a-zA-Z0-9\*\-\+\/\(\)\^]*)[\)\s]*',
            
            # نمط أي تعبير رياضي مع دوال
            r'([a-zA-Z0-9\*\-\+\/\(\)\^]+(?:sin|cos|tan|log|exp|sqrt)[a-zA-Z0-9\*\-\+\/\(\)\^]*)',
            
            # نمط معادلة مع علامة =
            r'([^=\s]+=[^=\s]+)',
            
            # نمط عام مع متغيرات متعددة
            r'([xyz][\s\*\-\+\/\(\)\^]*[xyz]*(?:\s*[\+\-\*\/]\s*[xyz\da-zA-Z]+)*)',
            
            # آخر خيار: أي تعبير رياضي
            r'([a-zA-Z0-9\*\-\+\/\(\)\^]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, cleaned, re.IGNORECASE)
            if match:
                expr = match.group(1).strip()
                if expr and len(expr) > 0:
                    return expr
        
        return None
    
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
    
    async def ask_groq(self, question: str) -> Dict[str, Any]:
        """سؤال Groq API"""
        if not self.groq_key:
            return {"success": False, "error": "مفتاح Groq غير موجود"}
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                url = "https://api.groq.com/openai/v1/chat/completions"
                response = await client.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {self.groq_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "mixtral-8x7b-32768",
                        "messages": [{"role": "user", "content": question}],
                        "temperature": 0.7
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data["choices"][0]["message"]["content"]
                    steps = [
                        ("🤖 إجابة Groq", ""),
                        (answer, answer if is_math(answer) else ""),
                    ]
                    return {
                        "success": True,
                        "result": answer,
                        "steps": steps,
                        "model": "groq",
                        "from_cache": False
                    }
                return {"success": False, "error": f"Groq error: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": f"Groq error: {str(e)}"}
    
    async def _try_ai_fallback(self, question: str) -> Dict[str, Any]:
        """محاولة الذكاء الاصطناعي مع عدة مزودين"""
        providers = []
        
        if self.gemini_key:
            providers.append(("gemini", self.ask_gemini))
        if self.groq_key:
            providers.append(("groq", self.ask_groq))
        
        for provider_name, provider_func in providers:
            try:
                result = await provider_func(question)
                if result.get("success"):
                    return result
            except Exception:
                continue
        
        return {"success": False, "error": "جميع مزودي الذكاء الاصطناعي غير متاحين"}
    
    async def generate_code(self, question: str, domain: str = "general") -> Dict[str, Any]:
        """توليد كود SymPy متوافق مع MathEngine"""
        
        # تطبيع السؤال للذاكرة
        normalized = normalize_question(question)
        
        # التحقق من الذاكرة
        cached = self.memory.get(normalized)
        if cached:
            cached["from_cache"] = True
            return cached
        
        result = ""
        steps = []
        model = ""
        code = ""
        
        try:
            # آلة حاسبة (أرقام فقط)
            if self._is_simple_arithmetic(normalized):
                result, steps = self.math.calculator(normalized)
                code = self.code_gen.calculator(
                    normalized, 
                    float(result) if result != "خطأ" else 0, 
                    steps
                )
                model = "calculator"
            
            # مشتقات
            elif any(word in question for word in ["مشتق", "derivative", "diff"]):
                expr = self._extract_math_expression(question)
                if expr:
                    result, steps = self.math.derivative(expr)
                    code = self.code_gen.derivative(expr, steps)
                    model = "derivative"
                else:
                    return {"success": False, "error": "لم نتمكن من استخراج الدالة"}
            
            # تكاملات
            elif any(word in question for word in ["تكامل", "integral"]):
                expr = self._extract_math_expression(question)
                if expr:
                    result, steps = self.math.integral(expr)
                    code = self.code_gen.integral(expr, steps)
                    model = "integral"
                else:
                    return {"success": False, "error": "لم نتمكن من استخراج الدالة"}
            
            # معادلات
            elif any(word in question for word in ["حل", "solve"]) or "=" in normalized:
                result, steps = self.math.equation(normalized)
                code = self.code_gen.equation(normalized, steps)
                model = "equation"
            
            # AI Fallback مع عدة مزودين
            else:
                ai_result = await self._try_ai_fallback(question)
                if ai_result.get("success"):
                    code = self.code_gen.ai_fallback(
                        ai_result["model"],
                        ai_result["result"],
                        ai_result["steps"]
                    )
                    ai_result["code"] = code
                    self.memory.set(normalized, ai_result)
                    return ai_result
                else:
                    return {"success": False, "error": "لم يتم التعرف على نوع المسألة"}
            
            # تجهيز النتيجة مع الكود
            response = {
                "success": True,
                "result": result,
                "steps": steps,
                "code": code,
                "model": model,
                "from_cache": False
            }
            
            # حفظ في الذاكرة
            self.memory.set(normalized, response)
            return response
            
        except Exception as e:
            return {"success": False, "error": f"خطأ في الحساب: {str(e)}"}
    
    def get_stats(self):
        return {
            "memory": self.memory.get_stats()
        }
    
    async def start(self):
        """بدء تشغيل المحرك"""
        pass
    
    async def stop(self):
        """إيقاف المحرك"""
        pass
