# calculator.py - محرك الحسابات الأساسي (نسخة مصححة ومحسنة)
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
            expr = expr.replace('²', '**2').replace('³', '**3')
            
            # تقييم آمن
            result = eval(expr, {"__builtins__": {}}, math.__dict__)
            self.last_result = result
            return result
        except Exception as e:
            return f"خطأ: {e}"
    
    # ========== حل المعادلات (نسخة محسنة) ==========
    
    def solve_equation(self, equation: str):
        """
        حل جميع أنواع المعادلات:
        - معادلات خطية: 3x + 5 = 14
        - معادلات تربيعية: x² - 5x + 6 = 0, x^2 - 5x + 6 = 0
        - معادلات تكعيبية: x³ - 6x² + 11x - 6 = 0
        - معادلات لوغاريتمية: log(x) + log(3) = 2
        - معادلات أسية: 2^x = 16
        - معادلات القيمة المطلقة: |2x - 5| = 7
        """
        try:
            if '=' not in equation:
                return "المعادلة يجب أن تحتوي على علامة ="
            
            # ===== 1. تنظيف المعادلة وتحضيرها =====
            modified_equation = equation.strip()
            
            # تحويل الرموز الخاصة
            modified_equation = modified_equation.replace('²', '**2')
            modified_equation = modified_equation.replace('³', '**3')
            modified_equation = modified_equation.replace('^', '**')
            modified_equation = modified_equation.replace('√', 'sqrt')
            modified_equation = modified_equation.replace(' ', '')
            
            # ===== 2. معالجة القيمة المطلقة =====
            # تحويل |x| إلى Abs(x)
            modified_equation = re.sub(r'\|([^|]+)\|', r'Abs(\1)', modified_equation)
            
            # ===== 3. استيراد sympy =====
            try:
                from sympy import symbols, Eq, solve, sympify, simplify, N
                from sympy import log, exp, sin, cos, tan, Abs, sqrt
                from sympy import I, pi, E
            except ImportError:
                return "خطأ: مكتبة sympy غير مثبتة. قم بتشغيل: pip install sympy"
            
            # ===== 4. تحضير المتغيرات =====
            x = symbols('x', real=True)  # نستخدم real=True للحصول على حلول حقيقية
            
            # ===== 5. فصل طرفي المعادلة =====
            left, right = modified_equation.split('=')
            
            # ===== 6. تحويل الصيغ الرياضية =====
            # تحويل 2x إلى 2*x
            left = re.sub(r'(\d+)([a-zA-Z\(])', r'\1*\2', left)
            right = re.sub(r'(\d+)([a-zA-Z\(])', r'\1*\2', right)
            
            # تحويل x2 إلى x*2
            left = re.sub(r'([a-zA-Z])(\d+)', r'\1*\2', left)
            right = re.sub(r'([a-zA-Z])(\d+)', r'\1*\2', right)
            
            # ===== 7. تحويل النصوص إلى تعابير رياضية =====
            try:
                left_expr = sympify(left)
                right_expr = sympify(right)
            except Exception as e:
                # إذا فشل التحويل، نحاول مرة أخرى بعد تنظيف إضافي
                left = left.replace('**', '^').replace('^', '**')
                right = right.replace('**', '^').replace('^', '**')
                left_expr = sympify(left)
                right_expr = sympify(right)
            
            # ===== 8. بناء المعادلة وحلها =====
            eq = Eq(left_expr, right_expr)
            
            # محاولة حل المعادلة
            solutions = solve(eq, x)
            
            # ===== 9. معالجة النتائج =====
            if not solutions:
                return "لا يوجد حل"
            
            # تنسيق الحلول بشكل جميل
            formatted_solutions = []
            for sol in solutions:
                # تقريب الحلول العشرية
                if sol.is_real:
                    try:
                        # تحويل إلى عدد عشري
                        decimal_val = float(N(sol))
                        
                        # إذا كان الحل صحيحاً (1.0 → 1)
                        if abs(decimal_val - round(decimal_val)) < 1e-10:
                            formatted_solutions.append(str(int(round(decimal_val))))
                        else:
                            # تقريب إلى 3 منازل عشرية
                            rounded = round(decimal_val, 3)
                            if abs(rounded - round(rounded)) < 1e-10:
                                formatted_solutions.append(str(int(round(rounded))))
                            else:
                                formatted_solutions.append(str(rounded).rstrip('0').rstrip('.'))
                    except:
                        formatted_solutions.append(str(sol))
                else:
                    # حلول مركبة
                    formatted_solutions.append(str(sol).replace('I', 'i'))
            
            # ===== 10. إرجاع النتيجة =====
            if len(formatted_solutions) == 1:
                return f"x = {formatted_solutions[0]}"
            elif len(formatted_solutions) == 2:
                return f"x = {formatted_solutions[0]}  أو  x = {formatted_solutions[1]}"
            else:
                return f"x = {', '.join(formatted_solutions)}"
            
        except Exception as e:
            return f"خطأ في حل المعادلة: {str(e)}"
    
    # ========== دوال مساعدة للمعادلات الخاصة ==========
    
    def solve_quadratic(self, a, b, c):
        """حل معادلة تربيعية: ax² + bx + c = 0"""
        try:
            discriminant = b**2 - 4*a*c
            
            if discriminant > 0:
                x1 = (-b + math.sqrt(discriminant)) / (2*a)
                x2 = (-b - math.sqrt(discriminant)) / (2*a)
                return [x1, x2]
            elif discriminant == 0:
                x = -b / (2*a)
                return [x]
            else:
                real = -b / (2*a)
                imag = math.sqrt(-discriminant) / (2*a)
                return [complex(real, imag), complex(real, -imag)]
        except:
            return None
    
    def solve_linear(self, a, b):
        """حل معادلة خطية: ax + b = 0"""
        try:
            if a == 0:
                if b == 0:
                    return "عدد لا نهائي من الحلول"
                else:
                    return "لا يوجد حل"
            return [-b / a]
        except:
            return None
    
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
        return a ** (1/3) if a >= 0 else -((-a) ** (1/3))
    
    def sin(self, angle):
        return math.sin(math.radians(angle))
    
    def cos(self, angle):
        return math.cos(math.radians(angle))
    
    def tan(self, angle):
        return math.tan(math.radians(angle))
    
    def factorial(self, n):
        return math.factorial(int(n))
    
    def log10(self, a):
        if a <= 0:
            return "خطأ: اللوغاريتم غير معرف للأعداد السالبة أو الصفر"
        return math.log10(a)
    
    def ln(self, a):
        if a <= 0:
            return "خطأ: اللوغاريتم الطبيعي غير معرف للأعداد السالبة أو الصفر"
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
    
    # ========== دوال مساعدة إضافية ==========
    
    def simplify_expression(self, expression: str):
        """تبسيط تعبير رياضي"""
        try:
            from sympy import simplify, sympify
            expr = sympify(expression.replace(' ', ''))
            simplified = simplify(expr)
            return str(simplified)
        except Exception as e:
            return f"خطأ في التبسيط: {e}"
    
    def expand_expression(self, expression: str):
        """توسيع تعبير رياضي"""
        try:
            from sympy import expand, sympify
            expr = sympify(expression.replace(' ', ''))
            expanded = expand(expr)
            return str(expanded)
        except Exception as e:
            return f"خطأ في التوسيع: {e}"
    
    def factor_expression(self, expression: str):
        """تحليل تعبير رياضي"""
        try:
            from sympy import factor, sympify
            expr = sympify(expression.replace(' ', ''))
            factored = factor(expr)
            return str(factored)
        except Exception as e:
            return f"خطأ في التحليل: {e}"


# ===== اختبار سريع =====
if __name__ == "__main__":
    calc = Calculator()
    
    print("="*60)
    print("اختبار الآلة الحاسبة")
    print("="*60)
    
    # اختبار المعادلات
    test_equations = [
        "x² - 5x + 6 = 0",      # تربيعية
        "x^2 - 5x + 6 = 0",      # تربيعية بصيغة أخرى
        "3x + 5 = 14",           # خطية
        "x³ - 6x² + 11x - 6 = 0", # تكعيبية
        "|2x - 5| = 7",          # قيمة مطلقة
        "2^x = 16",              # أسية
        "log(x) + log(3) = 2",   # لوغاريتمية
        "x² + 2x + 1 = 0",       # مربع كامل
        "2x² + 3x - 2 = 0",      # تربيعية أخرى
    ]
    
    for eq in test_equations:
        result = calc.solve_equation(eq)
        print(f"📌 {eq:30} → {result}")
    
    print("="*60)
    print("✅ جميع الاختبارات اكتملت")
    print("="*60)
