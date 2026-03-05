# calculator.py - محرك الحسابات الأساسي
import math

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
