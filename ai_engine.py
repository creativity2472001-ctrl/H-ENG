# ai_engine.py - نسخة مصححة
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
steps = [{{"text": "{question} = {result}"}}]
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
        """حل المشتقات"""
        # استخراج الدالة
        func_match = re.search(r'([a-zA-Z0-9\*\-\+\/\(\)]+)', question)
        if not func_match:
            return {"success": False, "error": "لم نتمكن من استخراج الدالة"}
        
        func = func_match.group(1)
        if 'x' not in func:
            func = func + '*x' if func.isdigit() else func
        
        try:
            expr = eval(f"sp.{func}")
            derivative = sp.diff(expr, self.x)
            
            code = f"""
import sympy as sp
x = sp.symbols('x')
f = {func}
final_result = sp.diff(f, x)
steps = [
    {{"text": "الدالة: f(x) = {func}", "latex": sp.latex(f)}},
    {{"text": "المشتقة: f'(x) = {derivative}", "latex": sp.latex(final_result)}}
]
"""
            return {"success": True, "code": code, "model": "derivative"}
        except Exception as e:
            return {"success": False, "error": f"خطأ في الحساب: {str(e)}"}
    
    async def _handle_integral(self, question):
        """حل التكاملات"""
        func_match = re.search(r'([a-zA-Z0-9\*\-\+\/\(\)]+)', question)
        if not func_match:
            return {"success": False, "error": "لم نتمكن من استخراج الدالة"}
        
        func = func_match.group(1)
        
        try:
            expr = eval(f"sp.{func}")
            integral = sp.integrate(expr, self.x)
            
            code = f"""
import sympy as sp
x = sp.symbols('x')
f = {func}
final_result = sp.integrate(f, x)
steps = [
    {{"text": "الدالة: f(x) = {func}", "latex": sp.latex(f)}},
    {{"text": "التكامل: ∫f(x)dx = {integral} + C", "latex": sp.latex(final_result) + " + C"}}
]
"""
            return {"success": True, "code": code, "model": "integral"}
        except Exception as e:
            return {"success": False, "error": f"خطأ في الحساب: {str(e)}"}
    
    async def _handle_equation(self, question):
        """حل المعادلات"""
        eq_match = re.search(r'([^=]+)=([^=]+)', question)
        if not eq_match:
            return {"success": False, "error": "صيغة المعادلة غير صحيحة"}
        
        left, right = eq_match.groups()
        
        try:
            left_expr = eval(f"sp.{left}")
            right_expr = eval(f"sp.{right}")
            expr = left_expr - right_expr
            solutions = sp.solve(expr, self.x)
            
            code = f"""
import sympy as sp
x = sp.symbols('x')
left = {left}
right = {right}
expr = left - right
final_result = sp.solve(expr, x)
steps = [
    {{"text": "المعادلة: {left} = {right}", "latex": sp.latex(sp.Eq(left, right))}},
    {{"text": f"الحل: x = {{final_result}}", "latex": f"x = {{final_result}}"}}
]
"""
            return {"success": True, "code": code, "model": "equation"}
        except Exception as e:
            return {"success": False, "error": f"خطأ في الحساب: {str(e)}"}
    
    async def start(self):
        pass
    
    async def stop(self):
        pass
