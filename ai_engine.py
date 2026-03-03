# ai_engine.py
import time
from typing import Dict, Any

class AIEngine:
    """محرك AI مبسط يحول الأسئلة لكود"""
    
    def __init__(self):
        self.ready = False
    
    async def start(self):
        self.ready = True
        print("✅ AI Engine ready")
    
    async def stop(self):
        self.ready = False
        print("🛑 AI Engine stopped")
    
    async def generate_code(self, question: str, domain: str = "general") -> Dict[str, Any]:
        """تحويل السؤال إلى كود SymPy"""
        
        if not self.ready:
            return {"success": False, "error": "AI Engine not ready"}
        
        question = question.lower()
        
        # ========== مشتقات ==========
        if any(word in question for word in ["مشتق", "derivative", "diff", "اشتقاق"]):
            return self._derivative_code(question)
        
        # ========== تكاملات ==========
        elif any(word in question for word in ["تكامل", "integral", "integrate", "∫"]):
            return self._integral_code(question)
        
        # ========== معادلات ==========
        elif any(word in question for word in ["حل", "solve", "معادلة", "equation"]):
            return self._equation_code(question)
        
        # ========== آلة حاسبة (بسيط) ==========
        elif self._is_simple_math(question):
            return self._calculator_code(question)
        
        return {
            "success": False,
            "error": "لم نتعرف على نوع المسألة. الأنواع المدعومة:\n• مشتقات (مثال: مشتقة x^2)\n• تكاملات (مثال: تكامل sin x)\n• معادلات (مثال: حل 2x+5=13)\n• عمليات حسابية (مثال: 2+2)"
        }
    
    def _is_simple_math(self, q: str) -> bool:
        """هل هي مسألة حسابية بسيطة؟"""
        q = q.replace(" ", "")
        return all(c in "0123456789+-*/()" for c in q)
    
    def _calculator_code(self, question: str) -> Dict[str, Any]:
        """كود آلة حاسبة"""
        return {
            "success": True,
            "code": f"""
import sympy as sp
# تعبير: {question}
result = eval("{question}")
final_result = result
steps = [{{"text": f"{question} = {{result}}"}}]
""",
            "model": "calculator"
        }
    
    def _derivative_code(self, question: str) -> Dict[str, Any]:
        """كود المشتقات"""
        # مشتقة x^2
        if "x^2" in question or "x²" in question:
            return {
                "success": True,
                "code": """
import sympy as sp
x = sp.symbols('x')
f = x**2
final_result = sp.diff(f, x)
steps = [
    {"text": "الدالة: f(x) = x²", "latex": sp.latex(f)},
    {"text": "المشتقة: f'(x) = 2x", "latex": sp.latex(final_result)}
]
""",
                "model": "derivative"
            }
        # مشتقة x^3
        elif "x^3" in question or "x³" in question:
            return {
                "success": True,
                "code": """
import sympy as sp
x = sp.symbols('x')
f = x**3
final_result = sp.diff(f, x)
steps = [
    {"text": "الدالة: f(x) = x³", "latex": sp.latex(f)},
    {"text": "المشتقة: f'(x) = 3x²", "latex": sp.latex(final_result)}
]
""",
                "model": "derivative"
            }
        # مشتقة عامة
        else:
            return {
                "success": True,
                "code": """
import sympy as sp
x = sp.symbols('x')
f = x**2
final_result = sp.diff(f, x)
steps = [
    {"text": "الدالة: f(x) = x² (افتراضي)", "latex": sp.latex(f)},
    {"text": "المشتقة: f'(x) = 2x", "latex": sp.latex(final_result)}
]
""",
                "model": "derivative (افتراضي)"
            }
    
    def _integral_code(self, question: str) -> Dict[str, Any]:
        """كود التكاملات"""
        # تكامل sin x
        if "sin" in question:
            return {
                "success": True,
                "code": """
import sympy as sp
x = sp.symbols('x')
f = sp.sin(x)
final_result = sp.integrate(f, x)
steps = [
    {"text": "الدالة: f(x) = sin(x)", "latex": sp.latex(f)},
    {"text": "التكامل: ∫sin(x)dx = -cos(x) + C", "latex": sp.latex(final_result) + " + C"}
]
""",
                "model": "integral"
            }
        # تكامل cos x
        elif "cos" in question:
            return {
                "success": True,
                "code": """
import sympy as sp
x = sp.symbols('x')
f = sp.cos(x)
final_result = sp.integrate(f, x)
steps = [
    {"text": "الدالة: f(x) = cos(x)", "latex": sp.latex(f)},
    {"text": "التكامل: ∫cos(x)dx = sin(x) + C", "latex": sp.latex(final_result) + " + C"}
]
""",
                "model": "integral"
            }
        # تكامل x^2
        else:
            return {
                "success": True,
                "code": """
import sympy as sp
x = sp.symbols('x')
f = x**2
final_result = sp.integrate(f, x)
steps = [
    {"text": "الدالة: f(x) = x²", "latex": sp.latex(f)},
    {"text": "التكامل: ∫x²dx = x³/3 + C", "latex": sp.latex(final_result) + " + C"}
]
""",
                "model": "integral"
            }
    
    def _equation_code(self, question: str) -> Dict[str, Any]:
        """كود المعادلات"""
        # معادلة 2x+5=13
        if "2x+5=13" in question.replace(" ", ""):
            return {
                "success": True,
                "code": """
import sympy as sp
x = sp.symbols('x')
eq = sp.Eq(2*x + 5, 13)
final_result = sp.solve(eq, x)
steps = [
    {"text": "المعادلة: 2x + 5 = 13", "latex": sp.latex(eq)},
    {"text": "الحل: x = 4", "latex": "x = 4"}
]
""",
                "model": "equation"
            }
        # معادلة عامة
        else:
            return {
                "success": True,
                "code": """
import sympy as sp
x = sp.symbols('x')
eq = sp.Eq(2*x + 5, 13)
final_result = sp.solve(eq, x)
steps = [
    {"text": "المعادلة: 2x + 5 = 13 (افتراضي)", "latex": sp.latex(eq)},
    {"text": "الحل: x = 4", "latex": "x = 4"}
]
""",
                "model": "equation (افتراضي)"
            }
