# ai_engine.py - إصدار بسيط يعمل فوراً مع OpenRouter
import sympy as sp
import re
import httpx
import os
import hashlib
from typing import Dict, Any, Optional, Tuple, List

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

ALLOWED_FUNCTIONS = {
    'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
    'sqrt': sp.sqrt, 'log': sp.log, 'exp': sp.exp
}

def safe_sympify(expr: str):
    try:
        return sp.sympify(expr, locals=ALLOWED_FUNCTIONS, evaluate=True)
    except:
        raise ValueError(f"تعبير غير صالح: {expr}")

def clean_math_input(text: str) -> str:
    text = text.lower()
    text = text.replace("²", "**2").replace("³", "**3").replace("⁴", "**4")
    text = text.replace("^", "**").replace("×", "*").replace("÷", "/")
    text = text.replace(" ", "")
    return text

def to_latex(expr) -> str:
    try:
        return sp.latex(expr)
    except:
        return str(expr)

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

class SymbolicMath:
    def derivative(self, func: str) -> Tuple[str, List[tuple]]:
        expr = safe_sympify(func)
        var = list(expr.free_symbols)[0] if expr.free_symbols else sp.symbols('x')
        result = sp.diff(expr, var)
        return str(result), [
            ("📐 المشتقة", ""),
            (f"f({var}) = {to_latex(expr)}", to_latex(expr)),
            (f"f'({var}) = {to_latex(result)}", to_latex(result)),
        ]
    
    def integral(self, func: str) -> Tuple[str, List[tuple]]:
        expr = safe_sympify(func)
        var = list(expr.free_symbols)[0] if expr.free_symbols else sp.symbols('x')
        result = sp.integrate(expr, var)
        return str(result) + " + C", [
            ("📊 التكامل", ""),
            (f"∫ {to_latex(expr)} d{var}", f"∫ {to_latex(expr)} d{var}"),
            (f"= {to_latex(result)} + C", f"{to_latex(result)} + C"),
        ]
    
    def equation(self, eq: str) -> Tuple[str, List[tuple]]:
        if "=" in eq:
            left, right = eq.split("=")
            expr = safe_sympify(left) - safe_sympify(right)
        else:
            expr = safe_sympify(eq)
        var = list(expr.free_symbols)[0] if expr.free_symbols else sp.symbols('x')
        solutions = sp.solve(expr, var)
        sol_str = ' أو '.join([f"{var} = {to_latex(s)}" for s in solutions])
        return sol_str, [("⚖️ المعادلة", ""), (f"{eq}", ""), (f"الحل: {sol_str}", "")]
    
    def calculator(self, expr: str) -> Tuple[str, List[tuple]]:
        result = safe_sympify(expr).evalf()
        return str(result), [("🔢 عملية حسابية", ""), (f"{expr} = {result}", "")]

class AIEngine:
    def __init__(self):
        self.math = SymbolicMath()
        self.memory = Memory()
        self.openrouter_key = OPENROUTER_API_KEY
        print("✅ AI Engine ready - إصدار سريع مع OpenRouter")
    
    async def ask_openrouter(self, question: str) -> Dict[str, Any]:
        if not self.openrouter_key:
            return {"success": False, "error": "مفتاح OpenRouter غير موجود"}
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "google/gemini-2.0-flash-exp:free",
                        "messages": [{
                            "role": "user", 
                            "content": f"حول هذا السؤال لصيغة SymPy فقط: {question}\nمثال: 'مشتقة sin(2x)' → 'diff(sin(2*x), x)'"
                        }]
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data["choices"][0]["message"]["content"].strip()
                    return {"success": True, "sympy_expr": answer, "model": "openrouter"}
                return {"success": False, "error": f"خطأ {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def generate_code(self, question: str) -> Dict[str, Any]:
        normalized = clean_math_input(question)
        
        # 1️⃣ بحث في الذاكرة
        cached = self.memory.get(normalized)
        if cached:
            return cached
        
        # 2️⃣ أسئلة بسيطة
        if all(c in "0123456789+-*/()." for c in normalized):
            result, steps = self.math.calculator(normalized)
        elif "=" in normalized:
            result, steps = self.math.equation(normalized)
        elif "مشتق" in question or "derivative" in question:
            result, steps = self.math.derivative(normalized.replace("مشتقة", "").replace("مشتق", ""))
        elif "تكامل" in question or "integral" in question:
            result, steps = self.math.integral(normalized.replace("تكامل", ""))
        else:
            # 3️⃣ استدعاء OpenRouter
            ai_result = await self.ask_openrouter(question)
            if not ai_result.get("success"):
                return {"success": False, "error": "لم يتم التعرف على السؤال"}
            
            # تنفيذ التعبير
            if "diff" in ai_result["sympy_expr"]:
                func = re.search(r'diff\(([^,]+)', ai_result["sympy_expr"]).group(1)
                result, steps = self.math.derivative(func)
            elif "integrate" in ai_result["sympy_expr"]:
                func = re.search(r'integrate\(([^,]+)', ai_result["sympy_expr"]).group(1)
                result, steps = self.math.integral(func)
            else:
                return {"success": False, "error": "لم أتمكن من فهم السؤال"}
        
        response = {"success": True, "result": result, "steps": steps, "model": "math"}
        self.memory.set(normalized, response)
        return response
