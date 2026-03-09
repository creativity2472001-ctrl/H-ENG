# calculator.py - محرك الحسابات الأساسي (نسخة مصححة)
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
        """حل جميع أنواع المعادلات - نسخة محسنة"""
        try:
            if '=' not in equation:
                return "المعادلة يجب أن تحتوي على علامة ="
            
            # تنظيف المعادلة
            equation = equation.strip()
            
            # ===== تحويل الرموز الخاصة =====
            modified = equation
            modified = modified.replace('²', '**2').replace('³', '**3')
            modified = modified.replace('^', '**')
            modified = modified.replace(' ', '')
            
            # ===== معالجة القيمة المطلقة =====
            if '|' in modified:
                modified = re.sub(r'\|([^|]+)\|', r'Abs(\1)', modified)
            
            # ===== استيراد sympy =====
            try:
                from sympy import symbols, Eq, solve, sympify, N
                from sympy import Abs
            except ImportError:
                return "خطأ: مكتبة sympy غير مثبتة. قم بتشغيل: pip install sympy"
            
            x = symbols('x')
            
            # ===== فصل طرفي المعادلة =====
            # معالجة الحالة التي يكون فيها الطرف الأيمن مجرد رقم
            if '=' in modified:
                left, right = modified.split('=', 1)
            else:
                return "صيغة المعادلة غير صحيحة"
            
            # ===== تحويل الصيغ =====
            # تحويل 2x إلى 2*x
            left = re.sub(r'(\d+)([a-zA-Z\(])', r'\1*\2', left)
            right = re.sub(r'(\d+)([a-zA-Z\(])', r'\1*\2', right)
            
            # تحويل x2 إلى x*2
            left = re.sub(r'([a-zA-Z])(\d+)', r'\1*\2', left)
            right = re.sub(r'([a-zA-Z])(\d+)', r'\1*\2', right)
            
            # معالجة خاصة للمعادلات التي فيها x في الطرفين
            # مثل: 5x + 3 = 2x + 9
            left = left.replace('+', ' +').replace('-', ' -')
            right = right.replace('+', ' +').replace('-', ' -')
            
            # ===== تحويل النصوص إلى تعابير رياضية =====
            try:
                left_expr = sympify(left)
                right_expr = sympify(right)
            except Exception as e:
                # محاولة ثانية بمعالجة مختلفة
                left = left.replace('**', '^').replace('^', '**')
                right = right.replace('**', '^').replace('^', '**')
                left_expr = sympify(left)
                right_expr = sympify(right)
            
            # ===== بناء المعادلة وحلها =====
            eq = Eq(left_expr, right_expr)
            solutions = solve(eq, x)
            
            if not solutions:
                return "لا يوجد حل"
            
            # ===== تنسيق النتائج بشكل جميل =====
            formatted_solutions = []
            for sol in solutions:
                # تحويل الحلول إلى أعداد عشرية
                if sol.is_real:
                    try:
                        val = float(N(sol))
                        # إذا كان الحل صحيحاً (1.0 → 1)
                        if abs(val - round(val)) < 1e-10:
                            formatted_solutions.append(str(int(round(val))))
                        else:
                            # تقريب إلى 3 منازل عشرية
                            rounded = round(val, 3)
                            if abs(rounded - round(rounded)) < 1e-10:
                                formatted_solutions.append(str(int(round(rounded))))
                            else:
                                formatted_solutions.append(str(rounded).rstrip('0').rstrip('.'))
                    except:
                        formatted_solutions.append(str(sol))
                else:
                    # حلول مركبة
                    formatted_solutions.append(str(sol).replace('I', 'i'))
            
            # ===== إرجاع النتيجة =====
            if len(formatted_solutions) == 1:
                return f"x = {formatted_solutions[0]}"
            elif len(formatted_solutions) == 2:
                return f"x = {formatted_solutions[0]} أو x = {formatted_solutions[1]}"
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
        if a >= 0:
            return a ** (1/3)
        else:
            return -((-a) ** (1/3))
    
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
