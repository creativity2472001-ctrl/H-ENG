# calculator.py - محرك الحسابات الأساسي
import math
import re

class Calculator:
    """آلة حاسبة علمية - تعمل مع CLI والويب"""
    
    def __init__(self):
        self.last_result = None
        self.memory = 0
    
    # ========== العمليات الأساسية ==========
    
    def calculate(self, expression: str):
        """حساب تعبير رياضي كامل"""
        try:
            # استبدال الرموز
            expr = expression.replace('×', '*').replace('÷', '/')
            expr = expr.replace('^', '**')
            expr = expr.replace('√', 'sqrt')
            
            # تقييم آمن
            result = eval(expr, {"__builtins__": {}}, math.__dict__)
            self.last_result = result
            return result
        except Exception as e:
            return f"خطأ: {e}"
    
    # ========== حل المعادلات (إضافة جديدة) ==========
    
    def solve_equation(self, equation: str):
        """حل معادلة بسيطة مثل x+5=10 أو 2x+3=7"""
        try:
            if '=' not in equation:
                return "المعادلة يجب أن تحتوي على علامة ="
            
            # ===== إضافة دعم صيغة القيمة المطلقة |x| بطريقة آمنة =====
            modified_equation = equation
            if '|' in modified_equation:
                # استخدام regex للتعامل مع كل |تعبير| بشكل منفصل
                pattern = r'\|([^|]+)\|'
                modified_equation = re.sub(pattern, r'Abs(\1)', modified_equation)
            
            # استيراد sympy هنا لتجنب الاعتماد عليه إذا لم يكن مثبتاً
            from sympy import symbols, Eq, solve, sympify
            
            x = symbols('x')
            left, right = modified_equation.split('=')
            
            # تحويل 2x إلى 2*x
            left = left.strip()
            left = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', left)
            left = re.sub(r'([a-zA-Z])(\d+)', r'\1*\2', left)
            
            # تحويل الطرفين إلى تعابير sympy
            left_expr = sympify(left)
            right_expr = sympify(right.strip())
            
            eq = Eq(left_expr, right_expr)
            solutions = solve(eq, x)
            
            if not solutions:
                return "لا يوجد حل"
            
            if len(solutions) == 1:
                return f"x = {solutions[0]}"
            else:
                return f"x = {solutions}"
        except ImportError:
            return "خطأ: مكتبة sympy غير مثبتة. قم بتشغيل: pip install sympy"
        except Exception as e:
            return f"خطأ في حل المعادلة: {e}"
    
    # ========== عمليات منفصلة (للويب) ==========
    
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
    
    def multiply(self, a, b):
        return a * b
    
    def divide(self, a, b):
        if b == 0:
            return "خطأ: القسمة على صفر"
        return a / b
    
    def power(self, a, b):
        return a ** b
    
    def sqrt(self, a):
        if a < 0:
            return "خطأ: جذر تربيعي لعدد سالب"
        return a ** 0.5
    
    def cbrt(self, a):
        return a ** (1/3)
    
    def sin(self, angle):
        return math.sin(math.radians(angle))
    
    def cos(self, angle):
        return math.cos(math.radians(angle))
    
    def tan(self, angle):
        return math.tan(math.radians(angle))
    
    def factorial(self, n):
        return math.factorial(int(n))
    
    def log10(self, a):
        return math.log10(a)
    
    def ln(self, a):
        return math.log(a)
    
    # ========== الذاكرة ==========
    
    def mc(self):
        self.memory = 0
        return "تم مسح الذاكرة"
    
    def mr(self):
        return self.memory
    
    def m_plus(self, value):
        self.memory += value
        return self.memory
    
    def m_minus(self, value):
        self.memory -= value
        return self.memory
