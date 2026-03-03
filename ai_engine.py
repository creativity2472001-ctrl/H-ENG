# ai_engine.py (النسخة المطورة - بدون AI)
import sympy as sp
import re

class AIEngine:
    """محرك رياضيات متكامل - بدون AI"""
    
    def __init__(self):
        self.ready = True
        self.x, self.y, self.z = sp.symbols('x y z')
        print("✅ AI Engine ready (مطوّر)")
    
    async def start(self):
        pass
    
    async def stop(self):
        pass
    
    async def generate_code(self, question: str, domain: str = "general") -> dict:
        question = question.lower().strip()
        
        # ========== 1. مشتقات ==========
        if any(word in question for word in ["مشتق", "derivative", "diff", "اشتقاق"]):
            return self._handle_derivative(question)
        
        # ========== 2. تكاملات ==========
        elif any(word in question for word in ["تكامل", "integral", "integrate", "∫"]):
            return self._handle_integral(question)
        
        # ========== 3. معادلات ==========
        elif any(word in question for word in ["حل", "solve", "معادلة", "equation"]):
            return self._handle_equation(question)
        
        # ========== 4. نهايات ==========
        elif any(word in question for word in ["نهاية", "limit"]):
            return self._handle_limit(question)
        
        # ========== 5. مصفوفات ==========
        elif any(word in question for word in ["مصفوفة", "matrix"]):
            return self._handle_matrix(question)
        
        # ========== 6. آلة حاسبة ==========
        elif self._is_simple_math(question):
            return self._handle_calculator(question)
        
        return {"success": False, "error": "لم نتعرف على نوع المسألة"}
    
    # ========== المشتقات ==========
    def _handle_derivative(self, question):
        """معالجة جميع أنواع المشتقات"""
        # استخراج الدالة من السؤال
        func = self._extract_function(question)
        
        if not func:
            return {"success": False, "error": "لم نتمكن من استخراج الدالة"}
        
        try:
            # تحويل النص إلى تعبير SymPy
            expr = sp.sympify(func)
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
        except:
            return {"success": False, "error": "خطأ في صيغة الدالة"}
    
    # ========== التكاملات ==========
    def _handle_integral(self, question):
        """معالجة جميع أنواع التكاملات"""
        func = self._extract_function(question)
        
        if not func:
            return {"success": False, "error": "لم نتمكن من استخراج الدالة"}
        
        try:
            expr = sp.sympify(func)
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
        except:
            return {"success": False, "error": "خطأ في صيغة الدالة"}
    
    # ========== المعادلات ==========
    def _handle_equation(self, question):
        """حل جميع أنواع المعادلات"""
        eq = self._extract_equation(question)
        
        if not eq:
            return {"success": False, "error": "لم نتمكن من استخراج المعادلة"}
        
        try:
            # تقسيم المعادلة إلى طرفين
            if "=" in eq:
                left, right = eq.split("=")
                expr = sp.sympify(f"{left} - ({right})")
            else:
                expr = sp.sympify(eq)
            
            solutions = sp.solve(expr, self.x)
            
            code = f"""
import sympy as sp
x = sp.symbols('x')
expr = {expr}
final_result = sp.solve(expr, x)
steps = [
    {{"text": "المعادلة: {eq}", "latex": sp.latex(sp.Eq(expr, 0))}},
    {{"text": f"الحل: x = {{final_result}}", "latex": f"x = {{final_result}}"}}
]
"""
            return {"success": True, "code": code, "model": "equation"}
        except:
            return {"success": False, "error": "خطأ في صيغة المعادلة"}
    
    # ========== النهايات ==========
    def _handle_limit(self, question):
        """حساب النهايات"""
        # استخراج الدالة والنقطة
        match = re.search(r'نهاية\s+(.+?)\s+عندما\s+(\w+)\s*→\s*([^\s]+)', question)
        if match:
            func, var, point = match.groups()
            var_sym = sp.symbols(var)
            
            try:
                expr = sp.sympify(func)
                point_val = sp.sympify(point)
                limit = sp.limit(expr, var_sym, point_val)
                
                code = f"""
import sympy as sp
{var} = sp.symbols('{var}')
f = {func}
final_result = sp.limit(f, {var}, {point})
steps = [
    {{"text": "الدالة: f({var}) = {func}", "latex": sp.latex(f)}},
    {{"text": "النهاية عندما {var} → {point}", "latex": sp.latex(final_result)}}
]
"""
                return {"success": True, "code": code, "model": "limit"}
            except:
                pass
        
        return {"success": False, "error": "صيغة النهاية غير صحيحة. مثال: نهاية x^2 عندما x→2"}
    
    # ========== المصفوفات ==========
    def _handle_matrix(self, question):
        """عمليات على المصفوفات"""
        # مثال بسيط: ضرب مصفوفتين
        code = """
import sympy as sp
A = sp.Matrix([[1, 2], [3, 4]])
B = sp.Matrix([[5, 6], [7, 8]])
final_result = A * B
steps = [
    {"text": "المصفوفة A:", "latex": sp.latex(A)},
    {"text": "المصفوفة B:", "latex": sp.latex(B)},
    {"text": "الضرب: A × B", "latex": sp.latex(final_result)}
]
"""
        return {"success": True, "code": code, "model": "matrix"}
    
    # ========== آلة حاسبة ==========
    def _handle_calculator(self, question):
        """عمليات حسابية بسيطة"""
        expr = question.replace(" ", "")
        return {
            "success": True,
            "code": f"""
import sympy as sp
result = eval("{expr}")
final_result = result
steps = [{{"text": "{expr} = {eval(expr)}"}}]
""",
            "model": "calculator"
        }
    
    # ========== دوال مساعدة ==========
    def _is_simple_math(self, q):
        q = q.replace(" ", "")
        return all(c in "0123456789+-*/()" for c in q)
    
    def _extract_function(self, question):
        """استخراج الدالة الرياضية من السؤال"""
        # محاولة استخراج الدالة بعد كلمة "مشتقة" أو "تكامل"
        patterns = [
            r'(?:مشتق|مشتقة|اشتقاق|derivative|diff|تكامل|integral)\s+([^(]+)',
            r'([a-zA-Z0-9\^\*\/\+\-\s\(\)]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, question)
            if match:
                return match.group(1).strip()
        return None
    
    def _extract_equation(self, question):
        """استخراج المعادلة من السؤال"""
        patterns = [
            r'(?:حل|solve|معادلة)\s+([^=]+=[^=]+)',
            r'([^=]+=[^=]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, question)
            if match:
                return match.group(1).strip().replace(" ", "")
        return None
