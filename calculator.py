# calculator.py - محرك الحسابات الأساسي (نسخة مصححة نهائياً)
import math
import re

class Calculator:
    """آلة حاسبة علمية - تعمل مع CLI والويب"""
    
    def __init__(self):
        self.last_result = None
        self.memory = 0
    
    # ========== العمليات الأساسية (محسنة) ==========
    
    def calculate(self, expression: str):
        """حساب تعبير رياضي كامل - مع دعم جميع الرموز"""
        try:
            # استبدال الرموز الأساسية
            expr = expression.replace('×', '*').replace('÷', '/')
            expr = expr.replace('√', 'sqrt')
            expr = expr.replace('²', '**2').replace('³', '**3').replace('⁴', '**4')
            
            # ===== إصلاح المشكلة 1: تحويل ^ إلى ** (الأس) =====
            expr = re.sub(r'(\d+)\s*\^\s*(\d+)', r'\1**\2', expr)
            expr = re.sub(r'([a-zA-Z])\s*\^\s*(\d+)', r'\1**\2', expr)
            
            # معالجة الدوال المثلثية (تحويل الدرجات إلى راديان)
            def replace_trig(match):
                func = match.group(1)  # sin, cos, tan
                angle = float(match.group(2))
                rad = math.radians(angle)
                if func == 'sin':
                    return str(math.sin(rad))
                elif func == 'cos':
                    return str(math.cos(rad))
                elif func == 'tan':
                    return str(math.tan(rad))
                return match.group(0)
            
            # استبدال sin(30), cos(60), tan(45)
            expr = re.sub(r'(sin|cos|tan)\((\d+)\)', replace_trig, expr)
            
            # ===== إصلاح المشكلة 2: sin²(30) + cos²(30) =====
            # طريقة مباشرة: حساب القيمة ثم إرجاع النص
            def replace_sin_sq_direct(match):
                angle = int(match.group(1))
                val = math.sin(math.radians(angle))
                return str(val * val)  # مباشرة نرجعالقيمة المربعة
            
            def replace_cos_sq_direct(match):
                angle = int(match.group(1))
                val = math.cos(math.radians(angle))
                return str(val * val)
            
            def replace_tan_sq_direct(match):
                angle = int(match.group(1))
                val = math.tan(math.radians(angle))
                return str(val * val)
            
            # معالجة sin²(30), cos²(30), tan²(45) مباشرة
            expr = re.sub(r'sin²\((\d+)\)', replace_sin_sq_direct, expr)
            expr = re.sub(r'cos²\((\d+)\)', replace_cos_sq_direct, expr)
            expr = re.sub(r'tan²\((\d+)\)', replace_tan_sq_direct, expr)
            
            # معالجة المضروب (4! -> math.factorial(4))
            expr = re.sub(r'(\d+)!', r'math.factorial(\1)', expr)
            
            # معالجة اللوغاريتم الطبيعي (ln(10) -> math.log(10))
            expr = re.sub(r'ln\(([^)]+)\)', r'math.log(\1)', expr)
            
            # معالجة اللوغاريتم العشري (log10(100) -> math.log10(100))
            expr = re.sub(r'log10\(([^)]+)\)', r'math.log10(\1)', expr)
            
            # ===== التعديل المهم: إضافة math إلى المتغيرات المسموحة =====
            allowed_names = {
                k: v for k, v in math.__dict__.items() if not k.startswith("__")
            }
            allowed_names["math"] = math  # إضافة math نفسه
            
            # تقييم آمن
            result = eval(expr, {"__builtins__": {}}, allowed_names)
            self.last_result = result
            
            # تنسيق النتيجة
            if isinstance(result, float):
                if result.is_integer():
                    return int(result)
                return round(result, 6)
            return result
            
        except Exception as e:
            return f"خطأ: {str(e)}"
    
    # ========== حل المعادلات (محسنة للمعادلات التكعيبية) ==========
    
    def solve_equation(self, equation: str):
        """حل جميع أنواع المعادلات - مع دعم التكعيبية والرباعية"""
        try:
            if '=' not in equation:
                return "المعادلة يجب أن تحتوي على علامة ="
            
            # تنظيف المعادلة
            equation = equation.strip()
            
            # ===== تحويل الرموز الخاصة =====
            modified = equation
            modified = modified.replace('²', '**2').replace('³', '**3').replace('⁴', '**4')
            modified = modified.replace('^', '**')
            modified = modified.replace(' ', '')
            modified = modified.replace('√', 'sqrt')
            
            # ===== معالجة القيمة المطلقة =====
            if '|' in modified:
                modified = re.sub(r'\|([^|]+)\|', r'Abs(\1)', modified)
            
            # ===== استيراد sympy =====
            try:
                from sympy import symbols, Eq, solve, sympify, N
                from sympy import Abs, sqrt
            except ImportError:
                return "خطأ: مكتبة sympy غير مثبتة. قم بتشغيل: pip install sympy"
            
            x = symbols('x')
            
            # ===== فصل طرفي المعادلة =====
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
            
            # ===== تحويل النصوص إلى تعابير رياضية =====
            try:
                left_expr = sympify(left)
                right_expr = sympify(right)
            except Exception as e:
                # محاولة ثانية
                left = left.replace('**', '^').replace('^', '**')
                right = right.replace('**', '^').replace('^', '**')
                left_expr = sympify(left)
                right_expr = sympify(right)
            
            # ===== بناء المعادلة وحلها =====
            eq = Eq(left_expr, right_expr)
            solutions = solve(eq, x)
            
            if not solutions:
                return "لا يوجد حل"
            
            # ===== تنسيق النتائج =====
            formatted_solutions = []
            for sol in solutions:
                if sol.is_real:
                    try:
                        val = float(N(sol))
                        if abs(val - round(val)) < 1e-10:
                            formatted_solutions.append(str(int(round(val))))
                        else:
                            rounded = round(val, 4)
                            if abs(rounded - round(rounded)) < 1e-10:
                                formatted_solutions.append(str(int(round(rounded))))
                            else:
                                formatted_solutions.append(str(rounded).rstrip('0').rstrip('.'))
                    except:
                        formatted_solutions.append(str(sol))
                else:
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
    
    # ========== دوال مساعدة ==========
    
    def sin(self, angle):
        """جيب الزاوية (الزاوية بالدرجات)"""
        return math.sin(math.radians(angle))
    
    def cos(self, angle):
        """جيب تمام الزاوية (الزاوية بالدرجات)"""
        return math.cos(math.radians(angle))
    
    def tan(self, angle):
        """ظل الزاوية (الزاوية بالدرجات)"""
        return math.tan(math.radians(angle))
    
    def factorial(self, n):
        """مضروب العدد"""
        return math.factorial(int(n))
    
    def ln(self, a):
        """اللوغاريتم الطبيعي"""
        if a <= 0:
            return "خطأ: اللوغاريتم الطبيعي غير معرف للأعداد السالبة أو الصفر"
        return math.log(a)
    
    def log10(self, a):
        """اللوغاريتم العشري"""
        if a <= 0:
            return "خطأ: اللوغاريتم غير معرف للأعداد السالبة أو الصفر"
        return math.log10(a)
    
    def sqrt(self, a):
        """الجذر التربيعي"""
        if a < 0:
            return "خطأ: جذر تربيعي لعدد سالب"
        return math.sqrt(a)
    
    def cbrt(self, a):
        """الجذر التكعيبي"""
        return math.copysign(abs(a) ** (1/3), a)
    
    # ========== العمليات الأساسية ==========
    
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
