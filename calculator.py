# calculator.py - آلة حاسبة علمية متكاملة للمهندسين (نسخة متوافقة مع api.py)
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
import math
import re
from typing import Union, Optional, List, Dict, Any, Tuple
from collections import OrderedDict
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from datetime import datetime

# المتغيرات الرمزية
x, y, z, t = sp.symbols('x y z t')

class LRUCache:
    """ذاكرة تخزين مؤقت مع حد أقصى (FIFO)"""
    def __init__(self, capacity: int = 100):
        self.cache = OrderedDict()
        self.capacity = capacity
    
    def get(self, key: str):
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key: str, value):
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
    
    def clear(self):
        self.cache.clear()
    
    def __len__(self):
        return len(self.cache)

class CommandHistory:
    """سجل الأوامر مع حد أقصى"""
    def __init__(self, max_size: int = 200):
        self.history = []
        self.max_size = max_size
        self.index = 0
    
    def add(self, command: str):
        self.history.append(command)
        self.index = len(self.history)
        if len(self.history) > self.max_size:
            self.history.pop(0)
            self.index = len(self.history)
    
    def get_previous(self) -> Optional[str]:
        if self.index > 0:
            self.index -= 1
            return self.history[self.index]
        return None
    
    def get_next(self) -> Optional[str]:
        if self.index < len(self.history) - 1:
            self.index += 1
            return self.history[self.index]
        return None
    
    def clear(self):
        self.history.clear()
        self.index = 0
    
    def get_all(self) -> List[str]:
        return self.history.copy()
    
    def __len__(self):
        return len(self.history)

class Calculator:
    """
    آلة حاسبة علمية متكاملة للمهندسين (نسخة متوافقة مع api.py)
    - جميع العمليات الحسابية والرياضية
    - دعم الرموز الرياضية والتكامل الرمزي
    - رسوم بيانية متكاملة مع دعم kwargs
    - سجل أوامر ذكي مع حد أقصى
    - تخزين مؤقت متطور
    - دعم نظام المعادلات
    """
    
    def __init__(self, cache_capacity: int = 100, history_max: int = 200):
        self.memory = 0.0
        self.last_result = None
        self.cache = LRUCache(capacity=cache_capacity)
        self.history = CommandHistory(max_size=history_max)
        
        # البيئة الآمنة لـ sympy
        self.local_dict = {
            # متغيرات
            'x': x, 'y': y, 'z': z, 't': t,
            
            # ثوابت
            'pi': sp.pi, 'e': sp.E, 'I': sp.I, 'oo': sp.oo,
            
            # دوال مثلثية
            'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
            'cot': sp.cot, 'sec': sp.sec, 'csc': sp.csc,
            'asin': sp.asin, 'acos': sp.acos, 'atan': sp.atan,
            'atan2': sp.atan2,
            'acot': sp.acot, 'asec': sp.asec, 'acsc': sp.acsc,
            
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
            'binomial': sp.binomial,
            'permutations': lambda n, k: sp.factorial(n) / sp.factorial(n-k),
            
            # دوال إحصائية
            'mean': lambda *args: sum(args) / len(args) if args else 0,
            'median': self._median_helper,
            'std': lambda *args, sample=True: self._std_helper(*args, sample=sample),
            'variance': lambda *args, sample=True: self._variance_helper(*args, sample=sample),
            'sum_sq': lambda *args: sum(x**2 for x in args) if args else 0,
            
            # دوال التكامل الرمزي
            'Integral': sp.Integral,  # عرض رمزي بدون حساب
            'integrate': sp.integrate,  # حساب التكامل
        }
        
        self.transformations = standard_transformations + (implicit_multiplication_application, convert_xor)
    
    # ========== دوال مساعدة إحصائية ==========
    def _median_helper(self, *args):
        if not args:
            return 0
        sorted_args = sorted(args)
        n = len(sorted_args)
        if n % 2 == 1:
            return sorted_args[n // 2]
        return (sorted_args[n//2 - 1] + sorted_args[n//2]) / 2
    
    def _variance_helper(self, *args, sample: bool = True):
        if len(args) < 2:
            return 0
        m = sum(args) / len(args)
        sum_sq = sum((x - m) ** 2 for x in args)
        return sum_sq / (len(args) - 1) if sample else sum_sq / len(args)
    
    def _std_helper(self, *args, sample: bool = True):
        if len(args) < 2:
            return 0
        return self._variance_helper(*args, sample=sample) ** 0.5
    
    # ========== تحسين تحويل الدرجات ==========
    def _convert_degrees(self, expr_str: str) -> str:
        """تحويل sin(30) إلى sin(30*pi/180) مع تحسينات"""
        def replace_deg(match):
            func = match.group(1)
            num = match.group(2)
            if num.replace('.', '').replace('-', '').isdigit():
                return f"{func}({num}*pi/180)"
            return match.group(0)
        
        pattern1 = r'(sin|cos|tan|cot|sec|csc)\((\-?\d+\.?\d*)\)'
        expr_str = re.sub(pattern1, replace_deg, expr_str)
        
        pattern2 = r'(sin|cos|tan|cot|sec|csc)\((\-?\d+\.?\d*)deg\)'
        expr_str = re.sub(pattern2, replace_deg, expr_str)
        
        return expr_str
    
    # ========== تحليل التكامل ==========
    def _parse_integral(self, expr_str: str) -> Optional[Dict]:
        """تحليل صيغ التكامل المختلفة"""
        patterns = [
            # صيغة Integral(x^2, x)
            (r'Integral\(\s*([^,]+)\s*,\s*([^)]+)\s*\)', 'symbolic_var'),
            # صيغة Integral(x^2)
            (r'Integral\(\s*([^)]+)\s*\)', 'symbolic'),
            # صيغة integrate(x^2, x, 0, 1)
            (r'integrate\(\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^)]+)\s*\)', 'definite'),
            # صيغة integrate(x^2, x)
            (r'integrate\(\s*([^,]+)\s*,\s*([^)]+)\s*\)', 'indefinite_var'),
            # صيغة integrate(x^2)
            (r'integrate\(\s*([^)]+)\s*\)', 'indefinite'),
        ]
        
        for pattern, expr_type in patterns:
            match = re.search(pattern, expr_str, re.IGNORECASE)
            if match:
                groups = match.groups()
                if expr_type == 'definite':
                    return {
                        'type': 'definite',
                        'expr': groups[0].strip(),
                        'var': groups[1].strip(),
                        'lower': groups[2].strip(),
                        'upper': groups[3].strip()
                    }
                elif expr_type in ['indefinite_var', 'symbolic_var']:
                    return {
                        'type': expr_type,
                        'expr': groups[0].strip(),
                        'var': groups[1].strip()
                    }
                else:
                    return {
                        'type': expr_type,
                        'expr': groups[0].strip()
                    }
        return None
    
    def _parse_expr(self, expr_str: str, use_cache: bool = True):
        """تحويل النص إلى تعبير SymPy"""
        if not expr_str:
            raise ValueError("التعبير فارغ")
        
        if use_cache:
            cached = self.cache.get(expr_str)
            if cached is not None:
                return cached
        
        expr_str = self._convert_degrees(expr_str)
        expr_str = re.sub(r'(\d+)!', r'factorial(\1)', expr_str)
        
        try:
            expr = parse_expr(
                expr_str,
                local_dict=self.local_dict,
                transformations=self.transformations,
                global_dict={},
                evaluate=True
            )
            
            if use_cache:
                self.cache.put(expr_str, expr)
            
            return expr
        except Exception as e:
            raise ValueError(f"تعبير غير صالح: {e}")
    
    # ========== دوال الرسم البياني المحسّنة (تدعم kwargs) ==========
    def plot(self, expression: str = None, var: str = 'x', 
             limits: Tuple[float, float] = (-10, 10), 
             points: int = 1000,
             show: bool = False,
             title: str = None,
             xlabel: str = None,
             ylabel: str = None,
             theme: str = None,
             grid: bool = True,
             show_legend: bool = True,
             width: int = 800,
             height: int = 600,
             **kwargs) -> Optional[str]:
        """
        رسم بياني لدالة مع دعم kwargs
        إذا show=False: يرجع base64 image string
        إذا show=True: يعرض النافذة مباشرة
        """
        try:
            # استخدام expression من kwargs إذا لم يكن موجوداً
            if expression is None and 'expression' in kwargs:
                expression = kwargs['expression']
            
            if expression is None:
                raise ValueError("لم يتم تحديد تعبير للرسم")
            
            expr = self._parse_expr(expression)
            var_sym = self.local_dict.get(var, sp.Symbol(var))
            
            # تحويل الدالة إلى numpy function
            f = sp.lambdify(var_sym, expr, modules=['numpy', 'sympy'])
            
            # إنشاء نقاط الرسم
            x_vals = np.linspace(limits[0], limits[1], points)
            y_vals = f(x_vals)
            
            # إنشاء الشكل مع الأبعاد المحددة
            plt.figure(figsize=(width/100, height/100))
            
            # تطبيق الثيم
            if theme == 'dark':
                plt.style.use('dark_background')
            elif theme == 'blue':
                plt.style.use('seaborn-v0_8-darkgrid')
            
            plt.plot(x_vals, y_vals, 'b-', linewidth=2, label=f'${sp.latex(expr)}$')
            
            if grid:
                plt.grid(True, alpha=0.3)
            
            plt.xlabel(xlabel or f'${var}$')
            plt.ylabel(ylabel or f'${sp.latex(expr)}$')
            plt.title(title or f'${sp.latex(expr)}$')
            plt.axhline(y=0, color='k', linewidth=0.5)
            plt.axvline(x=0, color='k', linewidth=0.5)
            
            if show_legend:
                plt.legend()
            
            if show:
                plt.show()
                return None
            else:
                # تحويل إلى base64
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                buf.seek(0)
                img_str = base64.b64encode(buf.read()).decode('utf-8')
                plt.close()
                return img_str
                
        except Exception as e:
            return f"خطأ في الرسم: {e}"
    
    def plot_multiple(self, expressions: List[str] = None, var: str = 'x',
                      limits: Tuple[float, float] = (-10, 10),
                      labels: List[str] = None,
                      show: bool = False,
                      title: str = None,
                      theme: str = None,
                      grid: bool = True,
                      width: int = 800,
                      height: int = 600,
                      **kwargs) -> Optional[str]:
        """رسم عدة دوال في نفس الشكل مع دعم kwargs"""
        try:
            # استخدام expressions من kwargs إذا لم يكن موجوداً
            if expressions is None and 'expressions' in kwargs:
                expressions = kwargs['expressions']
            
            if expressions is None or len(expressions) == 0:
                raise ValueError("لم يتم تحديد دوال للرسم")
            
            var_sym = self.local_dict.get(var, sp.Symbol(var))
            x_vals = np.linspace(limits[0], limits[1], 1000)
            
            plt.figure(figsize=(width/100, height/100))
            
            # تطبيق الثيم
            if theme == 'dark':
                plt.style.use('dark_background')
            elif theme == 'blue':
                plt.style.use('seaborn-v0_8-darkgrid')
            
            colors = ['b', 'r', 'g', 'c', 'm', 'y', 'k', 'orange', 'purple', 'brown']
            
            for i, expr_str in enumerate(expressions):
                expr = self._parse_expr(expr_str)
                f = sp.lambdify(var_sym, expr, modules=['numpy', 'sympy'])
                y_vals = f(x_vals)
                
                color = colors[i % len(colors)]
                label = labels[i] if labels and i < len(labels) else f'${sp.latex(expr)}$'
                plt.plot(x_vals, y_vals, color=color, linewidth=2, label=label)
            
            if grid:
                plt.grid(True, alpha=0.3)
            
            plt.xlabel(f'${var}$')
            plt.ylabel('$f(' + var + ')$')
            plt.title(title or 'رسم دوال متعددة')
            plt.legend()
            plt.axhline(y=0, color='k', linewidth=0.5)
            plt.axvline(x=0, color='k', linewidth=0.5)
            
            if show:
                plt.show()
                return None
            else:
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                buf.seek(0)
                img_str = base64.b64encode(buf.read()).decode('utf-8')
                plt.close()
                return img_str
                
        except Exception as e:
            return f"خطأ في الرسم: {e}"
    
    # ========== دوال التكامل الرمزي ==========
    def integral_symbolic(self, expression: str, var: str = 'x') -> str:
        """عرض التكامل بشكل رمزي بدون حساب"""
        try:
            expr = self._parse_expr(expression)
            var_sym = self.local_dict.get(var, sp.Symbol(var))
            integral = sp.Integral(expr, var_sym)
            return str(integral)
        except Exception as e:
            return f"خطأ: {e}"
    
    # ========== العمليات الأساسية ==========
    def calculate(self, expression: str) -> Union[float, complex, str]:
        """حساب قيمة تعبير رقمي"""
        try:
            self.history.add(expression)
            expr = self._parse_expr(expression)
            result = expr.evalf()
            
            if result.has(sp.I):
                return complex(result)
            elif result.is_number:
                return float(result)
            else:
                return str(result)
        except Exception as e:
            return f"خطأ: {e}"
    
    # ========== الدوال المثلثية ==========
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
    
    def atan2(self, y: float, x: float, unit: str = 'deg') -> float:
        result = math.atan2(y, x)
        return math.degrees(result) if unit == 'deg' else result
    
    # ========== دوال إحصائية ==========
    def mean(self, *args) -> float:
        return sum(args) / len(args) if args else 0
    
    def median(self, *args) -> float:
        return self._median_helper(*args)
    
    def variance(self, *args, sample: bool = True) -> float:
        return self._variance_helper(*args, sample=sample)
    
    def std(self, *args, sample: bool = True) -> float:
        return self._std_helper(*args, sample=sample)
    
    def sum_of_squares(self, *args) -> float:
        return sum(x**2 for x in args) if args else 0
    
    # ========== دوال توافقيات ==========
    def nCr(self, n: int, r: int) -> int:
        if r > n:
            return 0
        return math.comb(n, r)
    
    def nPr(self, n: int, r: int) -> int:
        if r > n:
            return 0
        return math.perm(n, r)
    
    # ========== حل المعادلات ==========
    def solve_equation(self, equation: str) -> str:
        """حل معادلة نصية"""
        try:
            self.history.add(equation)
            equations = []
            if ',' in equation or ';' in equation:
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
                if '=' in equation:
                    left, right = equation.split('=')
                    left_expr = self._parse_expr(left.strip())
                    right_expr = self._parse_expr(right.strip())
                    equations = [sp.Eq(left_expr, right_expr)]
                else:
                    expr = self._parse_expr(equation)
                    equations = [sp.Eq(expr, 0)]
            
            all_vars = set()
            for eq in equations:
                all_vars.update(eq.free_symbols)
            all_vars = list(all_vars)
            
            if not all_vars:
                if all(eq.lhs == eq.rhs for eq in equations):
                    return "المعادلة صحيحة دائماً"
                else:
                    return "المعادلة خاطئة"
            
            if len(equations) == 1:
                solutions = sp.solve(equations[0], all_vars[0], dict=True)
            else:
                solutions = sp.solve(equations, all_vars, dict=True)
            
            if not solutions:
                return "لا يوجد حل"
            
            if isinstance(solutions, list) and all(isinstance(s, dict) for s in solutions):
                result = []
                for i, sol in enumerate(solutions):
                    sol_str = ", ".join(f"{k} = {v}" for k, v in sol.items())
                    result.append(f"الحل {i+1}: {sol_str}")
                return "\n".join(result)
            elif isinstance(solutions, dict):
                return ", ".join(f"{k} = {v}" for k, v in solutions.items())
            else:
                return f"{all_vars[0]} = {solutions}"
                
        except Exception as e:
            return f"خطأ في حل المعادلة: {e}"
    
    # ========== حل نظام معادلات (إضافة جديدة) ==========
    def solve_system(self, equations: List[str]) -> str:
        """حل نظام معادلات"""
        try:
            # دمج المعادلات في نص واحد مفصول بفواصل منقوطة
            equations_str = "; ".join(equations)
            return self.solve_equation(equations_str)
        except Exception as e:
            return f"خطأ في حل نظام المعادلات: {e}"
    
    # ========== دوال جبرية ==========
    def simplify(self, expression: str) -> str:
        try:
            expr = self._parse_expr(expression)
            return str(sp.simplify(expr))
        except Exception as e:
            return f"خطأ: {e}"
    
    def expand(self, expression: str) -> str:
        try:
            expr = self._parse_expr(expression)
            return str(sp.expand(expr))
        except Exception as e:
            return f"خطأ: {e}"
    
    def factor(self, expression: str) -> str:
        try:
            expr = self._parse_expr(expression)
            return str(sp.factor(expr))
        except Exception as e:
            return f"خطأ: {e}"
    
    # ========== تفاضل ==========
    def diff(self, expression: str, var: str = 'x', order: int = 1) -> str:
        try:
            expr = self._parse_expr(expression)
            var_sym = self.local_dict.get(var, sp.Symbol(var))
            result = sp.diff(expr, var_sym, order)
            return str(sp.simplify(result))
        except Exception as e:
            return f"خطأ: {e}"
    
    # ========== تكامل محسّن ==========
    def integrate(self, expression: str, 
                  lower: Optional[str] = None, 
                  upper: Optional[str] = None,
                  var: str = 'x') -> str:
        """تكامل مع دعم صيغ متعددة"""
        try:
            # تحقق من صيغة Integral/integrate
            integral_info = self._parse_integral(expression)
            if integral_info:
                if integral_info['type'] in ['definite', 'indefinite_var', 'indefinite']:
                    expr = self._parse_expr(integral_info['expr'])
                    
                    if integral_info['type'] == 'definite':
                        var_sym = self.local_dict.get(integral_info['var'], sp.Symbol(integral_info['var']))
                        lower_val = sp.sympify(integral_info['lower'])
                        upper_val = sp.sympify(integral_info['upper'])
                        result = sp.integrate(expr, (var_sym, lower_val, upper_val))
                    elif integral_info['type'] == 'indefinite_var':
                        var_sym = self.local_dict.get(integral_info['var'], sp.Symbol(integral_info['var']))
                        result = sp.integrate(expr, var_sym)
                    else:  # indefinite
                        result = sp.integrate(expr)
                    return str(result)
                
                elif integral_info['type'] == 'symbolic':
                    # عرض رمزي بدون حساب
                    expr = self._parse_expr(integral_info['expr'])
                    integral = sp.Integral(expr)
                    return str(integral)
                
                elif integral_info['type'] == 'symbolic_var':
                    expr = self._parse_expr(integral_info['expr'])
                    var_sym = self.local_dict.get(integral_info['var'], sp.Symbol(integral_info['var']))
                    integral = sp.Integral(expr, var_sym)
                    return str(integral)
            
            # صيغ أخرى
            if lower is not None and upper is not None:
                expr = self._parse_expr(expression)
                var_sym = self.local_dict.get(var, sp.Symbol(var))
                lower_val = sp.sympify(lower)
                upper_val = sp.sympify(upper)
                result = sp.integrate(expr, (var_sym, lower_val, upper_val))
            else:
                expr = self._parse_expr(expression)
                var_sym = self.local_dict.get(var, sp.Symbol(var))
                result = sp.integrate(expr, var_sym)
            
            return str(result)
        except Exception as e:
            return f"خطأ في التكامل: {e}"
    
    # ========== نهايات ==========
    def limit(self, expression: str, var: str = 'x', approach: str = '0', direction: str = '+') -> str:
        """
        إيجاد نهاية دالة مع دعم الاتجاه
        direction: '+' (يمين), '-' (يسار)
        """
        try:
            expr = self._parse_expr(expression)
            var_sym = self.local_dict.get(var, sp.Symbol(var))
            
            if approach in ['oo', 'infinity', '∞']:
                approach_val = sp.oo
            elif approach in ['-oo', '-infinity', '-∞']:
                approach_val = -sp.oo
            else:
                approach_val = sp.sympify(approach)
            
            if direction == '+':
                result = sp.limit(expr, var_sym, approach_val, dir='+')
            elif direction == '-':
                result = sp.limit(expr, var_sym, approach_val, dir='-')
            else:
                result = sp.limit(expr, var_sym, approach_val)
            
            return str(result)
        except Exception as e:
            return f"خطأ في النهاية: {e}"
    
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
    
    # ========== إدارة الكاش والسجل ==========
    def clear_cache(self):
        self.cache.clear()
    
    def get_cache_size(self) -> int:
        return len(self.cache)
    
    def get_history(self, limit: int = None) -> List[str]:
        history = self.history.get_all()
        if limit:
            return history[-limit:]
        return history
    
    def clear_history(self):
        self.history.clear()
    
    def get_stats(self) -> Dict:
        """إحصائيات المحرك"""
        return {
            'cache_size': len(self.cache),
            'history_size': len(self.history),
            'memory': self.memory,
            'last_result': str(self.last_result) if self.last_result else None
        }


# ========== دوال مساعدة للتوافق ==========
def mean(*args):
    return Calculator().mean(*args)

def median(*args):
    return Calculator().median(*args)

def std(*args, sample=True):
    return Calculator().std(*args, sample=sample)

def variance(*args, sample=True):
    return Calculator().variance(*args, sample=sample)

def sum_of_squares(*args):
    return Calculator().sum_of_squares(*args)

def plot(expr: str, limits=(-10, 10), show=False):
    """دالة مساعدة للرسم"""
    return Calculator().plot(expr, limits=limits, show=show)
