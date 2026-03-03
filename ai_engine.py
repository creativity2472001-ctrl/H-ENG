# ai_engine.py - نسخة محسنة مع عرض جميل
import sympy as sp
import re
import httpx
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def clean_input(text):
    """تنظيف الإدخال من المشاكل"""
    text = text.replace("السؤال :", "").replace("السؤال:", "")
    text = text.replace("سؤال :", "").replace("سؤال:", "")
    text = text.strip()
    return text

def clean_math_input(text):
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

class AIEngine:
    def __init__(self):
        self.ready = True
        self.x, self.y, self.z = sp.symbols('x y z')
        print("✅ AI Engine ready")
    
    async def generate_code(self, question: str, domain: str = "general") -> dict:
        # تنظيف الإدخال
        question = clean_input(question)
        question = clean_math_input(question)
        
        # ========== 1. آلة حاسبة ==========
        if all(c in "0123456789+-*/()" for c in question):
            try:
                result = eval(question)
                return {
                    "success": True,
                    "code": f"""
import sympy as sp
result = {result}
final_result = result
steps = [{{"text": "{question} = {result}", "latex": f"{question} = {result}"}}]
""",
                    "model": "calculator"
                }
            except:
                return {"success": False, "error": "خطأ في العملية الحسابية"}
        
        # ========== 2. مشتقات ==========
        if "مشتق" in question or "derivative" in question or "diff" in question:
            return await self._handle_derivative(question)
        
        # ========== 3. تكاملات ==========
        if "تكامل" in question or "integral" in question:
            return await self._handle_integral(question)
        
        # ========== 4. معادلات ==========
        if "حل" in question or "solve" in question or "=" in question:
            return await self._handle_equation(question)
        
        return {"success": False, "error": "لم يتم التعرف على نوع المسألة"}
    
    async def _handle_derivative(self, question):
        """حل المشتقات مع عرض جميل"""
        # استخراج الدالة
        func_match = re.search(r'([a-zA-Z0-9\*\-\+\/\(\)]+)', question)
        if not func_match:
            return {"success": False, "error": "لم نتمكن من استخراج الدالة"}
        
        func = func_match.group(1)
        if 'x' not in func:
            func = func + '*x' if func.isdigit() else func
        
        try:
            x = sp.symbols('x')
            expr = sp.sympify(func)
            derivative = sp.diff(expr, x)
            
            # تحويل الصيغة للعرض
            func_latex = sp.latex(expr).replace('**', '^')
            deriv_latex = sp.latex(derivative).replace('**', '^')
            
            code = f"""
import sympy as sp
x = sp.symbols('x')
f = {func}
final_result = sp.diff(f, x)

# ========== عرض جميل ==========
func_latex = r"${func_latex}$"
deriv_latex = r"${deriv_latex}$"

steps = [
    {{"text": "**مشتقة:**", "latex": ""}},
    {{"text": f"{func_latex}", "latex": func_latex}},
    {{"text": "نستخدم قاعدة القوى:", "latex": r"$\\frac{{d}}{{dx}} (x^n) = n x^{{n-1}}$"}},
    {{"text": "إذن:", "latex": ""}},
    {{"text": f"$\\frac{{d}}{{dx}} ({func_latex}) = {deriv_latex}$", "latex": f"$\\\\frac{{d}}{{dx}} ({func_latex}) = {deriv_latex}$"}},
    {{"text": "✔️ **النتيجة النهائية:**", "latex": ""}},
    {{"text": f"$\\boxed{{{deriv_latex}}}$", "latex": f"$\\\\boxed{{{deriv_latex}}}$"}}
]
"""
            return {"success": True, "code": code, "model": "derivative"}
        except Exception as e:
            return {"success": False, "error": f"خطأ في الحساب: {str(e)}"}
    
    async def _handle_integral(self, question):
        """حل التكاملات مع عرض جميل"""
        func_match = re.search(r'([a-zA-Z0-9\*\-\+\/\(\)]+)', question)
        if not func_match:
            return {"success": False, "error": "لم نتمكن من استخراج الدالة"}
        
        func = func_match.group(1)
        
        try:
            x = sp.symbols('x')
            expr = sp.sympify(func)
            integral = sp.integrate(expr, x)
            
            func_latex = sp.latex(expr).replace('**', '^')
            integral_latex = sp.latex(integral).replace('**', '^')
            
            code = f"""
import sympy as sp
x = sp.symbols('x')
f = {func}
final_result = sp.integrate(f, x)

# ========== عرض جميل ==========
func_latex = r"${func_latex}$"
integral_latex = r"${integral_latex}$"

steps = [
    {{"text": "**تكامل:**", "latex": ""}},
    {{"text": f"$\\int {func_latex} \\, dx$", "latex": f"$\\\\int {func_latex} \\\\, dx$"}},
    {{"text": "نستخدم قواعد التكامل:", "latex": ""}},
    {{"text": f"$\\int {func_latex} \\, dx = {integral_latex} + C$", "latex": f"$\\\\int {func_latex} \\\\, dx = {integral_latex} + C$"}},
    {{"text": "✔️ **النتيجة النهائية:**", "latex": ""}},
    {{"text": f"$\\boxed{{{integral_latex} + C}}$", "latex": f"$\\\\boxed{{{integral_latex} + C}}$"}}
]
"""
            return {"success": True, "code": code, "model": "integral"}
        except Exception as e:
            return {"success": False, "error": f"خطأ في الحساب: {str(e)}"}
    
    async def _handle_equation(self, question):
        """حل المعادلات مع عرض جميل"""
        eq_match = re.search(r'([^=]+)=([^=]+)', question)
        if not eq_match:
            return {"success": False, "error": "صيغة المعادلة غير صحيحة"}
        
        left, right = eq_match.groups()
        
        try:
            x = sp.symbols('x')
            left_expr = sp.sympify(left)
            right_expr = sp.sympify(right)
            expr = left_expr - right_expr
            solutions = sp.solve(expr, x)
            
            left_latex = sp.latex(left_expr).replace('**', '^')
            right_latex = sp.latex(right_expr).replace('**', '^')
            solutions_latex = ', '.join([f"x = {sp.latex(sol).replace('**', '^')}" for sol in solutions])
            
            code = f"""
import sympy as sp
x = sp.symbols('x')
left = {left}
right = {right}
expr = left - right
final_result = sp.solve(expr, x)

# ========== عرض جميل ==========
left_latex = r"${left_latex}$"
right_latex = r"${right_latex}$"
solutions_latex = r"{solutions_latex}"

steps = [
    {{"text": "**معادلة:**", "latex": ""}},
    {{"text": f"{left_latex} = {right_latex}", "latex": f"{left_latex} = {right_latex}"}},
    {{"text": "ننقل الحدود:", "latex": ""}},
    {{"text": f"${left_latex} - {right_latex} = 0$", "latex": f"${left_latex} - {right_latex} = 0$"}},
    {{"text": "الحل:", "latex": ""}},
    {{"text": f"${solutions_latex}$", "latex": f"${solutions_latex}$"}},
    {{"text": "✔️ **النتيجة النهائية:**", "latex": ""}},
    {{"text": f"$\\boxed{{{solutions_latex}}}$", "latex": f"$\\\\boxed{{{solutions_latex}}}$"}}
]
"""
            return {"success": True, "code": code, "model": "equation"}
        except Exception as e:
            return {"success": False, "error": f"خطأ في الحساب: {str(e)}"}
    
    async def start(self):
        pass
    
    async def stop(self):
        pass
