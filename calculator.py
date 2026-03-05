# calculator.py - آلة حاسبة علمية متكاملة مع معادلات (نسخة محسّنة نهائية)
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
import math
import re
from typing import Union, Optional, List, Dict, Any, Tuple

# المتغيرات الرمزية
x, y, z, t = sp.symbols('x y z t')

class Calculator:
    """
    آلة حاسبة علمية متكاملة للمهندسين:
    - العمليات الأساسية (جمع، طرح، ضرب، قسمة، قوى، جذور، مضروب، نسبة مئوية)
    - دوال مثلثية (sin, cos, tan, cot, sec, csc) مع دعم الدرجات والراديان
    - دوال زائدية (sinh, cosh, tanh) + دوال عكسية
    - لوغاريتمات (ln, log, log10) وأسية (exp)
    - دوال رياضية إضافية: abs, round, floor, ceiling
    - دوال توافقيات: nCr, nPr
    - ثوابت: pi, e, oo, I (وحدة تخيلية)
    - حل معادلات (يدعم متغيرات متعددة)
    - تبسيط، فك أقواس، تحليل إلى عوامل
    - ذاكرة (M+, M-, MR, MC)
    - أرقام عشوائية
    - تخزين مؤقت للتعبيرات المتكررة
    """
    
    def __init__(self):
        self.memory = 0.0
        self.last_result = 0.0
        self.cache = {}  # تخزين التعبيرات المحللة مسبقاً
        
        # البيئة الآمنة لـ sympy - موسعة بالكامل
        self.local_dict = {
            # متغيرات
            'x': x, 'y': y, 'z': z, 't': t,
            
            # ثوابت
            'pi': sp.pi, 'e': sp.E, 'I': sp.I, 'oo': sp.oo,
            
            # دوال مثلثية
            'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
            'cot': sp.cot, 'sec': sp.sec, 'csc': sp.csc,
            'asin': sp.asin, 'acos': sp.acos, 'atan': sp.atan,
            
            # دوال زائدية
            'sinh': sp.sinh, 'cosh': sp.cosh, 'tanh': sp.tanh,
            'asinh': sp.asinh, 'acosh': sp.acosh, 'atanh': sp.atanh,
            
            # دوال جذرية وأسية
            'sqrt': sp.sqrt, 'cbrt': lambda x: x ** (1/3),
            'exp': sp.exp, 'pow': sp.Pow,
            
            # لوغاريتمات
            'log': sp.log, 'ln': sp.log, 'log10': lambda x: sp.log(x, 10),
            'log2': lambda x: sp.log(x, 2),
            
            # دوال رياضية إضافية
            'abs': sp.Abs, 'Abs': sp.Abs,
            'round': lambda x, n=0: round(float(x), n) if n else round(float(x)),
            'floor': sp.floor, 'ceiling': sp.ceiling,
            
            # دوال توافقيات
            'factorial': sp.factorial,
            'binomial': sp.binomial,  # nCr
            'permutations': lambda n, k: sp.factorial(n) / sp.factorial(n-k),  # nPr تقريبي
            
            # دوال إحصائية (يمكن توسيعها)
            'mean': lambda *args: sum(args) / len(args),
            'std': lambda *args: (sum((x - sum(args)/len(args))**2 for x in args) / len(args))**0.5,
        }
        
        # التحويلات لفهم 2x و 2(x+1) و (x+1)(x+2)
        self.transformations = standard_transformations + (implicit_multiplication_application, convert_xor)
    
    def _parse_expr(self, expr_str: str, use_cache: bool = True):
        """
        تحويل النص إلى تعبير SymPy مع دعم الكاش.
        يدعم الدرجات تلقائياً (مثل sin(30deg))
        """
        if not expr_str:
            raise ValueError("التعبير فارغ")
        
        # التحقق من الكاش
        cache_key = expr_str
        if use_cache and cache_key in self.cache:
            return self.cache[cache_key]
        
        # معالجة الدرجات: تحويل sin(30) إلى sin(30*pi/180)
        def convert_degrees(match):
            func = match.group(1)
            num = match.group(2)
            return f"{func}({num}*pi/180)"
        
        # البحث عن أنماط مثل sin(30), cos(45), tan(60)
        pattern = r'(sin|cos|tan|cot|sec|csc)\((\d+(?:\.\d+)?)\)'
        expr_str = re.sub(pattern, convert_degrees, expr_str)
        
        # البحث عن أنماط مثل sin(30deg), cos(45deg)
        pattern_deg = r'(sin|cos|tan|cot|sec|csc)\((\d+(?:\.\d+)?)deg\)'
        expr_str = re.sub(pattern_deg, convert_degrees, expr_str)
        
        # استبدال ! بـ factorial
        expr_str = re.sub(r'(\d+)!', r'factorial(\1)', expr_str)
        
        try:
            # استخدام parse_expr مع التحويلات
            expr = parse_expr(
                expr_str,
                local_dict=self.local_dict,
                transformations=self.transformations,
                evaluate=True
            )
            
            # تخزين في الكاش
            if use_cache:
                self.cache[cache_key] = expr
            
            return expr
        except Exception as e:
            raise ValueError(f"تعبير غير صالح: {e}")
    
    def clear_cache(self):
        """مسح الذاكرة المؤقتة للتعبيرات"""
        self.cache.clear()
    
    # ========== العمليات الأساسية ==========
    def calculate(self, expression: str) -> Union[float, complex]:
        """حساب قيمة تعبير رقمي"""
        expr = self._parse_expr(expression)
        result = expr.evalf()
        return complex(result) if result.has(sp.I) else float(result)
    
    # ========== الدوال المثلثية مع دعم الدرجات ==========
    def sin(self, angle: float, unit: str = 'deg') -> float:
        if unit == 'deg':
            angle = math.radians(angle)
        return math.sin(angle)
    
    def cos(self, angle: float, unit: str = 'deg') -> float:
        if unit == 'deg':
            angle = math.radians(angle)
        return math.cos(angle)
    
    def tan(self, angle: float, unit: str = 'deg') -> float:
        if unit == 'deg':
            angle = math.radians(angle)
        return math.tan(angle)
    
    # ========== دوال رياضية إضافية ==========
    def nCr(self, n: int, r: int) -> int:
        """عدد التوافيق"""
        if r > n:
            return 0
        return math.comb(n, r)
    
    def nPr(self, n: int, r: int) -> int:
        """عدد التباديل"""
        if r > n:
            return 0
        return math.perm(n, r)
    
    def gcd(self, a: int, b: int) -> int:
        """القاسم المشترك الأكبر"""
        return math.gcd(a, b)
    
    def lcm(self, a: int, b: int) -> int:
        """المضاعف المشترك الأصغر"""
        return abs(a * b) // math.gcd(a, b) if a and b else 0
    
    # ========== حل المعادلات (محسّن) ==========
    def solve_equation(self, equation: str) -> str:
        """
        حل معادلة نصية - تدعم متغيرات متعددة وأنظمة معادلات
        أمثلة:
        - x+5=10
        - x**2 + y**2 = 25, x - y = 1
        """
        try:
            # فصل المعادلات إذا كان هناك عدة معادلات
            equations = []
            if ',' in equation or ';' in equation:
                # نظام معادلات
                parts = re.split(r'[,;]', equation)
                for part in parts:
                    part = part.strip()
                    if not part:
                        continue
                    if '=' in part:
                        left, right = part.split('=')
                        left_expr = self._parse_expr(left.strip())
                        right_expr = self._parse_expr(right.strip())
                        equations.append(sp.Eq(left_expr, right_expr))
                    else:
                        expr = self._parse_expr(part)
                        equations.append(sp.Eq(expr, 0))
            else:
                # معادلة واحدة
                if '=' in equation:
                    left, right = equation.split('=')
                    left_expr = self._parse_expr(left.strip())
                    right_expr = self._parse_expr(right.strip())
                    equations = [sp.Eq(left_expr, right_expr)]
                else:
                    expr = self._parse_expr(equation)
                    equations = [sp.Eq(expr, 0)]
            
            # استخراج جميع المتغيرات
            all_vars = set()
            for eq in equations:
                all_vars.update(eq.free_symbols)
            all_vars = list(all_vars)
            
            if not all_vars:
                # معادلة بدون متغيرات
                if all(eq.lhs == eq.rhs for eq in equations):
                    return "المعادلة صحيحة دائماً"
                else:
                    return "المعادلة خاطئة"
            
            # حل النظام
            if len(equations) == 1:
                solutions = sp.solve(equations[0], all_vars[0], dict=True)
            else:
                solutions = sp.solve(equations, all_vars, dict=True)
            
            if not solutions:
                return "لا يوجد حل"
            
            # تنسيق الحلول
            if isinstance(solutions, list) and all(isinstance(s, dict) for s in solutions):
                # عدة حلول
                result = []
                for i, sol in enumerate(solutions):
                    sol_str = ", ".join(f"{k} = {v}" for k, v in sol.items())
                    result.append(f"الحل {i+1}: {sol_str}")
                return "\n".join(result)
            elif isinstance(solutions, dict):
                # حل وحيد لمتغيرات متعددة
                return ", ".join(f"{k} = {v}" for k, v in solutions.items())
            else:
                # حل وحيد لمتغير واحد
                return f"{all_vars[0]} = {solutions}"
                
        except Exception as e:
            return f"خطأ في حل المعادلة: {e}"
    
    # ========== دوال جبرية متقدمة ==========
    def simplify(self, expression: str) -> str:
        """تبسيط تعبير"""
        expr = self._parse_expr(expression)
        return str(sp.simplify(expr))
    
    def expand(self, expression: str) -> str:
        """فك الأقواس"""
        expr = self._parse_expr(expression)
        return str(sp.expand(expr))
    
    def factor(self, expression: str) -> str:
        """تحليل إلى عوامل"""
        expr = self._parse_expr(expression)
        return str(sp.factor(expr))
    
    # ========== تفاضل وتكامل (للتوافق مع التوسعات المستقبلية) ==========
    def diff(self, expression: str, var: str = 'x', order: int = 1) -> str:
        """مشتقة"""
        expr = self._parse_expr(expression)
        var_sym = self.local_dict.get(var, sp.Symbol(var))
        result = sp.diff(expr, var_sym, order)
        return str(sp.simplify(result))
    
    def integrate(self, expression: str, var: str = 'x', 
                  lower: Optional[str] = None, upper: Optional[str] = None) -> str:
        """تكامل"""
        expr = self._parse_expr(expression)
        var_sym = self.local_dict.get(var, sp.Symbol(var))
        
        if lower is not None and upper is not None:
            lower_expr = self._parse_expr(lower)
            upper_expr = self._parse_expr(upper)
            result = sp.integrate(expr, (var_sym, lower_expr, upper_expr))
        else:
            result = sp.integrate(expr, var_sym)
        
        return str(result)
    
    def limit(self, expression: str, var: str = 'x', approach: str = '0') -> str:
        """نهاية"""
        expr = self._parse_expr(expression)
        var_sym = self.local_dict.get(var, sp.Symbol(var))
        
        # معالجة الرموز الخاصة
        if approach in ['oo', 'infinity', '∞']:
            approach_val = sp.oo
        elif approach in ['-oo', '-infinity', '-∞']:
            approach_val = -sp.oo
        else:
            approach_val = self._parse_expr(approach)
        
        result = sp.limit(expr, var_sym, approach_val)
        return str(result)
    
    # ========== الذاكرة ==========
    def mc(self):
        self.memory = 0.0
        return "✅ تم مسح الذاكرة"
    
    def mr(self) -> float:
        return self.memory
    
    def m_plus(self, value: float):
        self.memory += value
        return f"✅ تمت الإضافة، الذاكرة = {self.memory}"
    
    def m_minus(self, value: float):
        self.memory -= value
        return f"✅ تم الطرح، الذاكرة = {self.memory}"
    
    # ========== أرقام عشوائية ==========
    def random(self, a: float = 0, b: float = 1) -> float:
        import random
        return random.uniform(a, b)
    
    # ========== دوال إحصائية بسيطة ==========
    def mean(self, *args) -> float:
        """متوسط حسابي"""
        if not args:
            return 0
        return sum(args) / len(args)
    
    def median(self, *args) -> float:
        """وسيط"""
        if not args:
            return 0
        sorted_args = sorted(args)
        n = len(sorted_args)
        if n % 2 == 1:
            return sorted_args[n // 2]
        return (sorted_args[n//2 - 1] + sorted_args[n//2]) / 2
    
    def std(self, *args) -> float:
        """انحراف معياري"""
        if len(args) < 2:
            return 0
        m = self.mean(*args)
        variance = sum((x - m) ** 2 for x in args) / (len(args) - 1)
        return variance ** 0.5


# ========== للاختبار المباشر (اختياري) ==========
if __name__ == "__main__":
    calc = Calculator()
    print("="*60)
    print("آلة حاسبة علمية متكاملة (نسخة اختبار)")
    print("="*60)
    
    # اختبارات سريعة
    test_expressions = [
        "2+2",
        "sin(30)",  # 0.5
        "sin(pi/2)",  # 1
        "cos(60)",  # 0.5
        "5!",
        "2x+3 when x=5",
        "solve: x^2 - 5x + 6 = 0",
        "solve: x^2 + y^2 = 25, x - y = 1",
        "simplify: (x^2-1)/(x-1)",
        "expand: (x+2)^2",
        "factor: x^2-5x+6",
    ]
    
    for expr in test_expressions:
        print(f"\n>>> {expr}")
        try:
            if expr.startswith("solve:"):
                result = calc.solve_equation(expr[6:])
            elif expr.startswith("simplify:"):
                result = calc.simplify(expr[9:])
            elif expr.startswith("expand:"):
                result = calc.expand(expr[7:])
            elif expr.startswith("factor:"):
                result = calc.factor(expr[7:])
            else:
                result = calc.calculate(expr)
            print(f"= {result}")
        except Exception as e:
            print(f"خطأ: {e}")
