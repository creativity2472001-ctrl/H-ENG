# ai_engine.py - الإصدار النهائي مع الذاكرة الذكية والتحسينات (v3.1)
import sympy as sp
import re
import httpx
import os
import hashlib
import json
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
        r'[\d\+\-\*/\^\(\)]',
        r'(sin|cos|tan|cot|sec|csc|log|ln|exp|sqrt)',
        r'[xyz]',
    ]
    text_lower = text.lower()
    for pattern in math_patterns:
        if re.search(pattern, text_lower):
            return True
    return False

def format_step(text: str, latex: str = "") -> Tuple[str, str]:
    """تنسيق خطوة واحدة (نص + LaTeX)"""
    return (text, latex)

# ========== الذاكرة الذكية المحسنة ==========
class SmartMemory:
    """ذاكرة ذكية تتعرف على الأنماط وليس النصوص فقط"""
    
    def __init__(self):
        self.cache = {}  # للتخزين السريع
        self.patterns = {}  # للأنماط الذكية
        self.stats = {"hits": 0, "misses": 0, "pattern_matches": 0}
    
    def _make_key(self, text: str) -> str:
        """توليد مفتاح عادي"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def _extract_numbers(self, text: str) -> List[str]:
        """استخراج الأرقام من النص"""
        return re.findall(r'\d+', text)
    
    def _extract_pattern(self, question: str, solution: Dict) -> Optional[Dict]:
        """استخراج نمط من السؤال والحل"""
        try:
            normalized = normalize_question(question)
            model = solution.get("model", "")
            
            # أنماط المشتقات
            if "derivative" in model or "مشتق" in question:
                # مشتقات القوى (x^n)
                power_match = re.search(r'x\*\*(\d+)', normalized)
                if power_match:
                    power = power_match.group(1)
                    return {
                        "type": "derivative_power",
                        "pattern": "x**n",
                        "params": {"n": power},
                        "solution_template": solution,
                        "func": "power"
                    }
                
                # مشتقات الدوال المثلثية (sin(ax))
                trig_match = re.search(r'(sin|cos|tan)\((\d*)([a-z])\)', normalized)
                if trig_match:
                    func, coeff, var = trig_match.groups()
                    coeff = coeff if coeff else "1"
                    return {
                        "type": "derivative_trig",
                        "pattern": f"{func}({coeff}*{var})",
                        "params": {"func": func, "coeff": coeff, "var": var},
                        "solution_template": solution
                    }
            
            # أنماط التكاملات
            elif "integral" in model or "تكامل" in question:
                # تكاملات القوى (x^n)
                power_match = re.search(r'x\*\*(\d+)', normalized)
                if power_match:
                    power = power_match.group(1)
                    return {
                        "type": "integral_power",
                        "pattern": "x**n",
                        "params": {"n": power},
                        "solution_template": solution
                    }
                
                # تكاملات الدوال المثلثية
                trig_match = re.search(r'(sin|cos|tan)\((\d*)([a-z])\)', normalized)
                if trig_match:
                    func, coeff, var = trig_match.groups()
                    coeff = coeff if coeff else "1"
                    return {
                        "type": "integral_trig",
                        "pattern": f"{func}({coeff}*{var})",
                        "params": {"func": func, "coeff": coeff, "var": var},
                        "solution_template": solution
                    }
            
            # أنماط المعادلات
            elif "equation" in model or "=" in normalized:
                match = re.search(r'([^=]+)=([^=]+)', normalized)
                if match:
                    left, right = match.groups()
                    # استخراج الأرقام من المعادلة
                    left_nums = self._extract_numbers(left)
                    right_nums = self._extract_numbers(right)
                    
                    return {
                        "type": "equation",
                        "pattern": f"{left}={right}",
                        "params": {
                            "left": left,
                            "right": right,
                            "left_numbers": left_nums,
                            "right_numbers": right_nums
                        },
                        "solution_template": solution
                    }
            
            return None
        except Exception as e:
            print(f"⚠️ خطأ في استخراج النمط: {e}")
            return None
    
    def _apply_power_rule(self, old_power: str, new_power: str, steps: List) -> Tuple[str, List]:
        """تطبيق قاعدة القوة على المشتقات/التكاملات"""
        try:
            old_power_int = int(old_power)
            new_power_int = int(new_power)
            
            # حساب النتيجة الجديدة
            if "derivative" in str(steps):
                new_result = f"{new_power_int}*x**{new_power_int-1}"
            else:  # integral
                new_result = f"x**{new_power_int+1}/{new_power_int+1}"
            
            # تحديث الخطوات
            new_steps = []
            for step in steps:
                if isinstance(step, tuple):
                    desc, latex = step
                    # استبدال الأرقام في النصوص
                    desc = desc.replace(f"^{old_power}", f"^{new_power}")
                    desc = desc.replace(f"**{old_power}", f"**{new_power}")
                    desc = desc.replace(f"/{old_power}", f"/{new_power}")
                    
                    latex = latex.replace(f"^{old_power}", f"^{new_power}")
                    latex = latex.replace(f"{{{old_power}}}", f"{{{new_power}}}")
                    
                    new_steps.append((desc, latex))
                else:
                    new_steps.append(step)
            
            return new_result, new_steps
        except:
            return None, None
    
    def _apply_trig_rule(self, old_coeff: str, new_coeff: str, func: str, steps: List) -> Tuple[str, List]:
        """تطبيق قاعدة الدوال المثلثية"""
        try:
            new_steps = []
            for step in steps:
                if isinstance(step, tuple):
                    desc, latex = step
                    # استبدال المعامل
                    desc = desc.replace(f"{old_coeff}", f"{new_coeff}")
                    latex = latex.replace(f"{old_coeff}", f"{new_coeff}")
                    new_steps.append((desc, latex))
                else:
                    new_steps.append(step)
            
            # النتيجة تعتمد على نوع الدالة
            if func == "sin":
                new_result = f"{new_coeff}*cos({new_coeff}*x)"
            elif func == "cos":
                new_result = f"-{new_coeff}*sin({new_coeff}*x)"
            else:
                new_result = None
            
            return new_result, new_steps
        except:
            return None, None
    
    def _apply_pattern(self, pattern: Dict, question: str) -> Optional[Dict]:
        """تطبيق نمط على سؤال جديد"""
        try:
            normalized = normalize_question(question)
            pattern_type = pattern.get("type")
            
            if pattern_type == "derivative_power":
                # استخراج القوة الجديدة
                match = re.search(r'x\*\*(\d+)', normalized)
                if match:
                    new_power = match.group(1)
                    old_power = pattern["params"]["n"]
                    
                    if new_power != old_power:
                        new_result, new_steps = self._apply_power_rule(
                            old_power, new_power, 
                            pattern["solution_template"]["steps"]
                        )
                        
                        if new_result:
                            return {
                                "success": True,
                                "result": new_result,
                                "steps": new_steps,
                                "model": "pattern_match_derivative",
                                "from_cache": True
                            }
            
            elif pattern_type == "derivative_trig":
                # استخراج المعامل الجديد
                match = re.search(r'(sin|cos|tan)\((\d*)([a-z])\)', normalized)
                if match:
                    func, new_coeff, var = match.groups()
                    new_coeff = new_coeff if new_coeff else "1"
                    old_coeff = pattern["params"]["coeff"]
                    
                    if new_coeff != old_coeff and func == pattern["params"]["func"]:
                        new_result, new_steps = self._apply_trig_rule(
                            old_coeff, new_coeff, func,
                            pattern["solution_template"]["steps"]
                        )
                        
                        if new_result:
                            return {
                                "success": True,
                                "result": new_result,
                                "steps": new_steps,
                                "model": "pattern_match_trig",
                                "from_cache": True
                            }
            
            elif pattern_type == "integral_power":
                # مشابه للمشتقات لكن للتكامل
                match = re.search(r'x\*\*(\d+)', normalized)
                if match:
                    new_power = match.group(1)
                    old_power = pattern["params"]["n"]
                    
                    if new_power != old_power:
                        new_result, new_steps = self._apply_power_rule(
                            old_power, new_power,
                            pattern["solution_template"]["steps"]
                        )
                        
                        if new_result:
                            return {
                                "success": True,
                                "result": new_result + " + C",
                                "steps": new_steps,
                                "model": "pattern_match_integral",
                                "from_cache": True
                            }
            
            return None
        except Exception as e:
            print(f"⚠️ خطأ في تطبيق النمط: {e}")
            return None
    
    def get(self, question: str) -> Optional[Dict]:
        """البحث في الذاكرة (نص عادي أو نمط)"""
        normalized = normalize_question(question)
        key = self._make_key(normalized)
        
        # 1️⃣ البحث المباشر
        if key in self.cache:
            self.stats["hits"] += 1
            print(f"✅ تم العثور على التطابق التام في الذاكرة")
            return self.cache[key]
        
        # 2️⃣ البحث بالأنماط
        for pattern_key, pattern in self.patterns.items():
            matched = self._apply_pattern(pattern, question)
            if matched:
                self.stats["pattern_matches"] += 1
                print(f"✅ تم العثور على نمط مطابق: {pattern_key}")
                return matched
        
        self.stats["misses"] += 1
        print(f"❌ لم يتم العثور على السؤال في الذاكرة")
        return None
    
    def set(self, question: str, value: Dict):
        """حفظ في الذاكرة"""
        normalized = normalize_question(question)
        key = self._make_key(normalized)
        
        # حفظ النص الأصلي
        self.cache[key] = value
        print(f"💾 تم حفظ السؤال في الذاكرة المباشرة")
        
        # استخراج وحفظ النمط
        pattern = self._extract_pattern(question, value)
        if pattern:
            pattern_key = f"{pattern['type']}_{json.dumps(pattern['params'])}"
            self.patterns[pattern_key] = pattern
            print(f"🧠 تم حفظ النمط الذكي: {pattern['type']}")
    
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
        """حساب المشتقة"""
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
        """حساب التكامل"""
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
        """حل المعادلة"""
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

# ========== محرك AI مع Fallback متعدد ==========
class AIEngine:
    def __init__(self):
        self.math = SymbolicMath()
        self.memory = SmartMemory()
        self.ready = True
        self.groq_key = GROQ_API_KEY
        self.gemini_key = GEMINI_API_KEY
        print("✅ AI Engine ready - الإصدار الذكي مع الذاكرة الذكية المحسنة")
    
    def _is_simple_arithmetic(self, expr: str) -> bool:
        """فحص إذا كان التعبير حسابياً بسيطاً"""
        cleaned = expr.replace(" ", "")
        if any(var in cleaned for var in ['x', 'y', 'z']):
            return False
        allowed_chars = "0123456789+-*/()."
        return all(c in allowed_chars for c in cleaned)
    
    async def ask_gemini(self, question: str) -> Dict[str, Any]:
        """سؤال Gemini API"""
        if not self.gemini_key:
            return {"success": False, "error": "مفتاح Gemini غير موجود"}
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
                
                # ✅ prompt محسن للترجمة إلى SymPy
                prompt = f"""أنت مترجم رياضيات متخصص. مهمتك تحويل الأسئلة الرياضية إلى صيغة SymPy فقط.

السؤال: {question}

قواعد الترجمة:
- المشتقات → استخدم diff(الدالة, المتغير)
- التكاملات → استخدم integrate(الدالة, المتغير)
- حل المعادلات → استخدم solve(المعادلة, المتغير)
- العمليات الحسابية → اكتب التعبير كما هو

أمثلة:
1. "مشتقة sin(2x)" → diff(sin(2*x), x)
2. "تكامل x^2" → integrate(x**2, x)
3. "حل x^2 - 4 = 0" → solve(x**2 - 4, x)
4. "2+2" → 2+2

اكتب فقط التعبير بصيغة SymPy الصحيحة، بدون أي كلمات إضافية أو شرح."""
                
                response = await client.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{
                            "parts": [{"text": prompt}]
                        }]
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "candidates" in data:
                        sympy_expr = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                        # تنظيف النتيجة من أي علامات اقتباس أو كلمات زائدة
                        sympy_expr = re.sub(r'^["\']|["\']$', '', sympy_expr)
                        return {
                            "success": True,
                            "sympy_expr": sympy_expr,
                            "model": "gemini"
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
                
                prompt = f"""أنت مترجم رياضيات متخصص. مهمتك تحويل الأسئلة الرياضية إلى صيغة SymPy فقط.

السؤال: {question}

قواعد الترجمة:
- المشتقات → استخدم diff(الدالة, المتغير)
- التكاملات → استخدم integrate(الدالة, المتغير)
- حل المعادلات → استخدم solve(المعادلة, المتغير)
- العمليات الحسابية → اكتب التعبير كما هو

أمثلة:
1. "مشتقة sin(2x)" → diff(sin(2*x), x)
2. "تكامل x^2" → integrate(x**2, x)
3. "حل x^2 - 4 = 0" → solve(x**2 - 4, x)
4. "2+2" → 2+2

اكتب فقط التعبير بصيغة SymPy الصحيحة، بدون أي كلمات إضافية أو شرح."""
                
                response = await client.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {self.groq_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "mixtral-8x7b-32768",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3  # درجة حرارة منخفضة لدقة أكبر
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data["choices"][0]["message"]["content"].strip()
                    # تنظيف النتيجة
                    answer = re.sub(r'^["\']|["\']$', '', answer)
                    return {
                        "success": True,
                        "sympy_expr": answer,
                        "model": "groq"
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
        
        errors = []
        for provider_name, provider_func in providers:
            try:
                print(f"🤖 محاولة مع {provider_name}...")
                result = await provider_func(question)
                if result.get("success"):
                    print(f"✅ نجح {provider_name}")
                    return result
                else:
                    errors.append(f"{provider_name}: {result.get('error')}")
            except Exception as e:
                errors.append(f"{provider_name}: {str(e)}")
                continue
        
        return {"success": False, "error": f"جميع مزودي الذكاء الاصطناعي غير متاحين: {', '.join(errors)}"}
    
    # ========== الدالة الرئيسية المعدلة ==========
    async def generate_code(self, question: str, domain: str = "general") -> Dict[str, Any]:
        """
        الآلية الذكية:
        1. 🔍 البحث في الذاكرة (نص + أنماط)
        2. 📊 إذا كان السؤال بسيطاً → حل مباشر
        3. 🤖 إذا لا → استدعاء AI للترجمة إلى SymPy
        4. 🧮 حل المسألة باستخدام SymPy
        5. 💾 حفظ في الذاكرة
        """
        
        print(f"\n{'='*60}")
        print(f"🔍 معالجة السؤال: {question}")
        print(f"{'='*60}")
        
        # 1️⃣ البحث في الذاكرة الذكية
        cached = self.memory.get(question)
        if cached:
            print(f"✅ تم العثور على الحل في الذاكرة!")
            return cached
        
        # 2️⃣ الأسئلة البسيطة (بدون AI)
        normalized = normalize_question(question)
        
        # آلة حاسبة
        if self._is_simple_arithmetic(normalized):
            print("📊 استخدام الآلة الحاسبة")
            result, steps = self.math.calculator(normalized)
            response = {
                "success": True,
                "result": result,
                "steps": steps,
                "model": "calculator",
                "from_cache": False
            }
            self.memory.set(question, response)
            return response
        
        # معادلات بسيطة
        if "=" in normalized and len(normalized.split("=")) == 2:
            print("⚖️ استخدام حل المعادلات")
            result, steps = self.math.equation(normalized)
            response = {
                "success": True,
                "result": result,
                "steps": steps,
                "model": "equation",
                "from_cache": False
            }
            self.memory.set(question, response)
            return response
        
        # 3️⃣ استدعاء AI للترجمة إلى SymPy
        print("🤖 استدعاء الذكاء الاصطناعي للترجمة...")
        ai_result = await self._try_ai_fallback(question)
        
        if not ai_result.get("success"):
            error_msg = ai_result.get("error", "فشل في ترجمة السؤال")
            print(f"❌ فشل AI: {error_msg}")
            return {"success": False, "error": error_msg}
        
        sympy_expr = ai_result["sympy_expr"]
        print(f"📝 التعبير المُترجم: {sympy_expr}")
        
        # 4️⃣ تنفيذ التعبير باستخدام SymPy
        try:
            result = ""
            steps = []
            model = ai_result["model"]
            
            # تحديد نوع العملية من التعبير
            if sympy_expr.startswith("diff"):
                # مشتقة
                func_match = re.search(r'diff\(([^,]+),', sympy_expr)
                if func_match:
                    func = func_match.group(1).strip()
                    print(f"🔢 حساب مشتقة: {func}")
                    result, steps = self.math.derivative(func)
                    model = f"{model}_derivative"
            
            elif sympy_expr.startswith("integrate"):
                # تكامل
                func_match = re.search(r'integrate\(([^,]+),', sympy_expr)
                if func_match:
                    func = func_match.group(1).strip()
                    print(f"∫ حساب تكامل: {func}")
                    result, steps = self.math.integral(func)
                    model = f"{model}_integral"
            
            elif sympy_expr.startswith("solve"):
                # معادلة
                eq_match = re.search(r'solve\(([^,]+),', sympy_expr)
                if eq_match:
                    eq = eq_match.group(1).strip()
                    print(f"⚖️ حل معادلة: {eq}")
                    result, steps = self.math.equation(eq)
                    model = f"{model}_equation"
            
            else:
                # تعبير عادي
                print(f"🧮 حساب تعبير: {sympy_expr}")
                result, steps = self.math.calculator(sympy_expr)
                model = f"{model}_expression"
            
            # تجهيز الرد
            response = {
                "success": True,
                "result": result,
                "steps": steps,
                "model": model,
                "from_cache": False
            }
            
            # 5️⃣ حفظ في الذاكرة للاستخدام المستقبلي
            self.memory.set(question, response)
            print(f"✅ تم حفظ الحل في الذاكرة")
            
            return response
            
        except Exception as e:
            error_msg = f"خطأ في تنفيذ التعبير: {str(e)}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
    
    def get_stats(self):
        return {
            "memory": self.memory.get_stats()
        }
    
    async def start(self):
        pass
    
    async def stop(self):
        pass
