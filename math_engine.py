# math_engine.py - محرك العمليات الحسابية المتوافق مع ai_engine.py (v2.0)
import sympy as sp
import math
import logging
import asyncio
import hashlib
from typing import List, Optional, Any, Dict, Tuple, Union, Callable
from datetime import datetime
from dataclasses import dataclass, field

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ========== ثوابت الأمان ==========
MAX_INPUT_LENGTH = 300
MAX_MATRIX_SIZE = 10
TIMEOUT_SECONDS = 5

# ========== البيئة الآمنة لـ SymPy ==========
ALLOWED_SYMBOLS = {
    'x': sp.Symbol('x'), 'y': sp.Symbol('y'), 'z': sp.Symbol('z'), 't': sp.Symbol('t'),
    'n': sp.Symbol('n'), 'k': sp.Symbol('k'),
    'pi': sp.pi, 'E': sp.E, 'I': sp.I, 'oo': sp.oo,
    'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan, 'cot': sp.cot,
    'sec': sp.sec, 'csc': sp.csc, 'asin': sp.asin, 'acos': sp.acos,
    'atan': sp.atan, 'acot': sp.acot,
    'sinh': sp.sinh, 'cosh': sp.cosh, 'tanh': sp.tanh,
    'asinh': sp.asinh, 'acosh': sp.acosh, 'atanh': sp.atanh,
    'log': sp.log, 'ln': sp.log, 'exp': sp.exp, 'sqrt': sp.sqrt,
    'Abs': sp.Abs, 'sign': sp.sign, 'floor': sp.floor, 'ceiling': sp.ceiling,
    'gamma': sp.gamma, 'beta': sp.beta,
}

# الكلمات المحظورة
FORBIDDEN_PATTERNS = ["__", "lambda", "import", "exec", "eval", "globals", "locals", "__builtins__"]

@dataclass
class Step:
    """خطوة حل واحدة - متوافق مع ai_engine.py v8.0"""
    icon: str  # 📥, 🔍, 📝, 🧮, ✅, ⚠️, etc.
    title: str
    content: str
    latex: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "icon": self.icon,
            "title": self.title,
            "content": self.content,
            "latex": self.latex
        }

@dataclass
class ExecutionResult:
    """نتيجة تنفيذ عملية حسابية - متوافق مع ai_engine.py v8.0"""
    success: bool
    result: Any = None
    result_str: str = ""
    steps: List[Step] = field(default_factory=list)
    error: Optional[str] = None
    model: str = ""
    
    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "result": str(self.result) if self.result is not None else None,
            "result_str": self.result_str,
            "steps": [step.to_dict() for step in self.steps],
            "error": self.error,
            "model": self.model
        }

# دوال مساعدة إحصائية
def _calculate_mean(data: List[float]) -> float:
    if not data: return 0
    return sum(data) / len(data)

def _calculate_variance(data: List[float], mean_val: float = None, sample: bool = False) -> float:
    if not data or len(data) < 2: return 0
    if mean_val is None: mean_val = _calculate_mean(data)
    n = len(data)
    sum_sq = sum((x - mean_val) ** 2 for x in data)
    return sum_sq / (n - 1) if sample else sum_sq / n

def _calculate_std_dev(data: List[float], mean_val: float = None, sample: bool = False) -> float:
    return _calculate_variance(data, mean_val, sample) ** 0.5

def safe_sympify(expr_str: str) -> Optional[sp.Expr]:
    """تحويل آمن للتعبيرات الرياضية - مطابق لـ ai_engine.py"""
    if not expr_str or len(expr_str) > MAX_INPUT_LENGTH:
        return None
    
    expr_lower = expr_str.lower()
    for bad in FORBIDDEN_PATTERNS:
        if bad in expr_lower:
            logger.warning(f"Forbidden pattern detected: {bad}")
            return None
    
    try:
        expr_str = expr_str.replace('^', '**').replace(' ', '')
        from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
        transformations = (standard_transformations + (implicit_multiplication_application,))
        
        return parse_expr(
            expr_str,
            transformations=transformations,
            local_dict=ALLOWED_SYMBOLS,
            global_dict={},
            evaluate=True
        )
    except Exception as e:
        logger.debug(f"Safe sympify error: {e}")
        return None

async def run_with_timeout(func: Callable, *args, timeout=TIMEOUT_SECONDS):
    """تشغيل دالة مع مهلة زمنية"""
    try:
        return await asyncio.wait_for(asyncio.to_thread(func, *args), timeout=timeout)
    except asyncio.TimeoutError:
        logger.warning(f"Operation timed out after {timeout} seconds")
        return ExecutionResult(success=False, error=f"انتهت المهلة الزمنية ({timeout} ثوانٍ)", model="timeout")
    except Exception as e:
        logger.error(f"Error in timed operation: {e}")
        return ExecutionResult(success=False, error=str(e), model="error")

class MathEngine:
    """محرك العمليات الحسابية - 60 قالب - متوافق مع ai_engine.py v8.0"""
    
    def __init__(self):
        self.x, self.y, self.z, self.t = sp.symbols('x y z t')
        self.n, self.k = sp.symbols('n k')
        self.execution_count = 0
        self.history = []
        self.max_history = 1000
        
        print("✅ Math Engine v2.0 - 60 قالب حسابي - متوافق مع AI Engine v8.0")
        logger.info("Math Engine v2.0 initialized")
    
    def _log_operation(self, operation: str, params: dict, result: Any):
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "params": params,
            "result": str(result)[:200]
        })
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def _increment_count(self):
        self.execution_count += 1
    
    def _validate_angle_for_asin(self, value: float) -> bool:
        return -1 <= value <= 1
    
    # ========== الأساسيات (10 قوالب) ==========
    
    async def calculate(self, expression: str) -> ExecutionResult:
        """قالب 1: آلة حاسبة بسيطة - تستقبل نص"""
        try:
            expr = safe_sympify(expression)
            if expr is None:
                return ExecutionResult(success=False, error="تعبير غير صالح", model="calculate")
            
            result = expr.evalf()
            result_float = float(result)
            
            steps = [
                Step("📥", "السؤال", f"حساب: {expression}"),
                Step("🔍", "التحليل", "تعبير رياضي بسيط"),
                Step("🧮", "الحساب", f"{expression} = {result_float}")
            ]
            
            if result.is_Rational and result.q != 1:
                steps.append(Step("📝", "القيمة الدقيقة", str(expr), sp.latex(expr)))
            
            steps.append(Step("✅", "النتيجة", str(result_float)))
            
            self._increment_count()
            self._log_operation("calculate", {"expression": expression}, result_float)
            
            return ExecutionResult(
                success=True,
                result=result_float,
                result_str=str(result_float),
                steps=steps,
                model="calculate"
            )
        except Exception as e:
            logger.error(f"Error in calculate: {e}")
            return ExecutionResult(success=False, error=str(e), model="calculate")
    
    async def power(self, base: float, exponent: float) -> ExecutionResult:
        """قالب 2: رفع لقوة"""
        try:
            result = base ** exponent
            steps = [
                Step("📥", "السؤال", f"حساب {base} ^ {exponent}"),
                Step("🔍", "التحليل", f"رفع {base} إلى القوة {exponent}"),
                Step("🧮", "الحساب", f"{base}^{exponent} = {result}"),
                Step("✅", "النتيجة", str(result))
            ]
            
            self._increment_count()
            self._log_operation("power", {"base": base, "exponent": exponent}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps,
                model="power"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="power")
    
    async def sqrt(self, number: float) -> ExecutionResult:
        """قالب 3: جذر تربيعي"""
        try:
            if number < 0:
                result = sp.sqrt(number)
                steps = [
                    Step("📥", "السؤال", f"√{number}"),
                    Step("🔍", "التحليل", "الجذر التربيعي لعدد سالب يعطي عدداً مركباً"),
                    Step("🧮", "الحساب", f"√{number} = {result}"),
                    Step("✅", "النتيجة", str(result))
                ]
            else:
                result = number ** 0.5
                steps = [
                    Step("📥", "السؤال", f"√{number}"),
                    Step("🔍", "التحليل", f"إيجاد الجذر التربيعي لـ {number}"),
                    Step("🧮", "الحساب", f"√{number} = {result}"),
                    Step("✅", "النتيجة", str(result))
                ]
            
            self._increment_count()
            self._log_operation("sqrt", {"number": number}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps,
                model="sqrt"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="sqrt")
    
    async def factorial(self, n: int) -> ExecutionResult:
        """قالب 4: مضروب"""
        try:
            if n < 0:
                return ExecutionResult(success=False, error="لا يمكن حساب مضروب لعدد سالب", model="factorial")
            if n > 100:
                return ExecutionResult(success=False, error="العدد كبير جداً", model="factorial")
            
            result = math.factorial(n)
            steps = [
                Step("📥", "السؤال", f"{n}!"),
                Step("🔍", "التحليل", f"حساب مضروب العدد {n}"),
                Step("🧮", "الحساب", f"{n}! = {result}"),
                Step("✅", "النتيجة", str(result))
            ]
            
            self._increment_count()
            self._log_operation("factorial", {"n": n}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps,
                model="factorial"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="factorial")
    
    async def percent(self, value: float, total: float) -> ExecutionResult:
        """قالب 5: نسبة مئوية"""
        try:
            result = (value / 100) * total
            steps = [
                Step("📥", "السؤال", f"{value}% من {total}"),
                Step("🔍", "التحليل", "حساب النسبة المئوية"),
                Step("🧮", "الحساب", f"({value}/100) × {total} = {result}"),
                Step("✅", "النتيجة", str(result))
            ]
            
            self._increment_count()
            self._log_operation("percent", {"value": value, "total": total}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps,
                model="percent"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="percent")
    
    async def absolute(self, value: float) -> ExecutionResult:
        """قالب 6: قيمة مطلقة"""
        try:
            result = abs(value)
            steps = [
                Step("📥", "السؤال", f"|{value}|"),
                Step("🔍", "التحليل", "حساب القيمة المطلقة"),
                Step("🧮", "الحساب", f"|{value}| = {result}"),
                Step("✅", "النتيجة", str(result))
            ]
            
            self._increment_count()
            self._log_operation("absolute", {"value": value}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps,
                model="absolute"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="absolute")
    
    async def gcd(self, a: int, b: int) -> ExecutionResult:
        """قالب 7: القاسم المشترك الأكبر"""
        try:
            result = math.gcd(a, b)
            steps = [
                Step("📥", "السؤال", f"GCD({a}, {b})"),
                Step("🔍", "التحليل", f"إيجاد القاسم المشترك الأكبر لـ {a} و {b}"),
                Step("🧮", "الحساب", f"GCD({a}, {b}) = {result}"),
                Step("✅", "النتيجة", str(result))
            ]
            
            self._increment_count()
            self._log_operation("gcd", {"a": a, "b": b}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps,
                model="gcd"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="gcd")
    
    async def lcm(self, a: int, b: int) -> ExecutionResult:
        """قالب 8: المضاعف المشترك الأصغر"""
        try:
            result = abs(a * b) // math.gcd(a, b) if a and b else 0
            steps = [
                Step("📥", "السؤال", f"LCM({a}, {b})"),
                Step("🔍", "التحليل", f"إيجاد المضاعف المشترك الأصغر لـ {a} و {b}"),
                Step("🧮", "الحساب", f"LCM({a}, {b}) = {result}"),
                Step("✅", "النتيجة", str(result))
            ]
            
            self._increment_count()
            self._log_operation("lcm", {"a": a, "b": b}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps,
                model="lcm"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="lcm")
    
    async def log10(self, num: float) -> ExecutionResult:
        """قالب 9: لوغاريتم عشري"""
        try:
            if num <= 0:
                return ExecutionResult(success=False, error="لا يمكن حساب لوغاريتم لعدد سالب أو صفر", model="log10")
            
            result = math.log10(num)
            steps = [
                Step("📥", "السؤال", f"log₁₀({num})"),
                Step("🔍", "التحليل", f"حساب اللوغاريتم العشري لـ {num}"),
                Step("🧮", "الحساب", f"log₁₀({num}) = {result:.6f}"),
                Step("✅", "النتيجة", str(result))
            ]
            
            self._increment_count()
            self._log_operation("log10", {"num": num}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps,
                model="log10"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="log10")
    
    async def ln(self, num: float) -> ExecutionResult:
        """قالب 10: لوغاريتم طبيعي"""
        try:
            if num <= 0:
                return ExecutionResult(success=False, error="لا يمكن حساب لوغاريتم لعدد سالب أو صفر", model="ln")
            
            result = math.log(num)
            steps = [
                Step("📥", "السؤال", f"ln({num})"),
                Step("🔍", "التحليل", f"حساب اللوغاريتم الطبيعي لـ {num}"),
                Step("🧮", "الحساب", f"ln({num}) = {result:.6f}"),
                Step("✅", "النتيجة", str(result))
            ]
            
            self._increment_count()
            self._log_operation("ln", {"num": num}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps,
                model="ln"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="ln")
    
    # ========== معادلات (10 قوالب) ==========
    
    async def solve_linear(self, a: float, b: float) -> ExecutionResult:
        """قالب 11: حل معادلة خطية: ax + b = 0"""
        try:
            steps = [
                Step("📥", "السؤال", f"حل المعادلة: {a}x + {b} = 0"),
                Step("🔍", "التحليل", f"معادلة خطية من الدرجة الأولى")
            ]
            
            if a == 0:
                if b == 0:
                    steps.append(Step("✅", "النتيجة", "جميع الأعداد حلول"))
                    return ExecutionResult(
                        success=True,
                        result="جميع الأعداد حلول",
                        result_str="جميع الأعداد حلول",
                        steps=steps,
                        model="solve_linear"
                    )
                else:
                    return ExecutionResult(
                        success=False,
                        error="معادلة غير قابلة للحل",
                        steps=steps,
                        model="solve_linear"
                    )
            
            x = -b / a
            steps.extend([
                Step("📝", "القانون", f"x = -b / a = -({b}) / {a}"),
                Step("🧮", "الحساب", f"x = {x}"),
                Step("✅", "النتيجة", f"x = {x}")
            ])
            
            self._increment_count()
            self._log_operation("solve_linear", {"a": a, "b": b}, x)
            
            return ExecutionResult(
                success=True,
                result=x,
                result_str=f"x = {x}",
                steps=steps,
                model="solve_linear"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="solve_linear")
    
    async def solve_quadratic(self, a: float, b: float, c: float) -> ExecutionResult:
        """قالب 12: حل معادلة تربيعية: ax² + bx + c = 0"""
        try:
            steps = [
                Step("📥", "السؤال", f"حل المعادلة: {a}x² + {b}x + {c} = 0"),
                Step("🔍", "التحليل", f"معادلة تربيعية")
            ]
            
            if a == 0:
                return await self.solve_linear(b, c)
            
            discriminant = b**2 - 4*a*c
            steps.append(Step("📝", "المميز", f"Δ = b² - 4ac = {b}² - 4({a})({c}) = {discriminant}"))
            
            sqrt_d = abs(discriminant) ** 0.5
            
            if discriminant > 0:
                x1 = (-b + sqrt_d) / (2*a)
                x2 = (-b - sqrt_d) / (2*a)
                steps.append(Step("🧮", "الحلان", f"x₁ = {x1}, x₂ = {x2}"))
                steps.append(Step("✅", "النتيجة", f"x₁ = {x1}, x₂ = {x2}"))
                result = (x1, x2)
            elif discriminant == 0:
                x = -b / (2*a)
                steps.append(Step("🧮", "الحل", f"x = {x} (حل مكرر)"))
                steps.append(Step("✅", "النتيجة", f"x = {x}"))
                result = x
            else:
                real = -b / (2*a)
                imag = sqrt_d / (2*a)
                steps.append(Step("🧮", "الحلان", f"x₁ = {real} + {imag}i, x₂ = {real} - {imag}i"))
                steps.append(Step("✅", "النتيجة", f"x₁ = {real} + {imag}i, x₂ = {real} - {imag}i"))
                result = (complex(real, imag), complex(real, -imag))
            
            self._increment_count()
            self._log_operation("solve_quadratic", {"a": a, "b": b, "c": c}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps,
                model="solve_quadratic"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="solve_quadratic")
    
    async def solve_cubic(self, a: float, b: float, c: float, d: float) -> ExecutionResult:
        """قالب 13: حل معادلة تكعيبية: ax³ + bx² + cx + d = 0"""
        try:
            steps = [
                Step("📥", "السؤال", f"حل المعادلة: {a}x³ + {b}x² + {c}x + {d} = 0"),
                Step("🔍", "التحليل", f"معادلة تكعيبية")
            ]
            
            if a == 0:
                return await self.solve_quadratic(b, c, d)
            
            x = sp.Symbol('x')
            expr = a*x**3 + b*x**2 + c*x + d
            solutions = sp.solve(expr, x)
            
            steps.append(Step("🧮", "الحلول", f"x = {[str(s) for s in solutions]}"))
            steps.append(Step("✅", "النتيجة", str([str(s) for s in solutions])))
            
            self._increment_count()
            self._log_operation("solve_cubic", {"a": a, "b": b, "c": c, "d": d}, solutions)
            
            return ExecutionResult(
                success=True,
                result=solutions,
                result_str=str([str(s) for s in solutions]),
                steps=steps,
                model="solve_cubic"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="solve_cubic")
    
    async def solve_system_2x2(self, a1: float, b1: float, c1: float, a2: float, b2: float, c2: float) -> ExecutionResult:
        """قالب 14: حل نظام معادلتين خطيتين"""
        try:
            steps = [
                Step("📥", "السؤال", f"حل النظام:\n{a1}x + {b1}y = {c1}\n{a2}x + {b2}y = {c2}"),
                Step("🔍", "التحليل", f"نظام معادلتين خطيتين")
            ]
            
            det = a1*b2 - a2*b1
            steps.append(Step("📝", "المحدد الرئيسي", f"Δ = {a1}×{b2} - {a2}×{b1} = {det}"))
            
            if det == 0:
                if a1*c2 == a2*c1 and b1*c2 == b2*c1:
                    steps.append(Step("✅", "النتيجة", "عدد لا نهائي من الحلول"))
                    return ExecutionResult(
                        success=True,
                        result="عدد لا نهائي من الحلول",
                        result_str="عدد لا نهائي من الحلول",
                        steps=steps,
                        model="solve_system_2x2"
                    )
                else:
                    return ExecutionResult(
                        success=False,
                        error="النظام غير متوافق",
                        steps=steps,
                        model="solve_system_2x2"
                    )
            
            x = (c1*b2 - c2*b1) / det
            y = (a1*c2 - a2*c1) / det
            
            steps.append(Step("🧮", "الحل", f"x = {x}, y = {y}"))
            steps.append(Step("✅", "النتيجة", f"x = {x}, y = {y}"))
            
            self._increment_count()
            self._log_operation("solve_system_2x2", {"a1": a1, "b1": b1, "c1": c1, "a2": a2, "b2": b2, "c2": c2}, (x, y))
            
            return ExecutionResult(
                success=True,
                result=(x, y),
                result_str=f"x = {x}, y = {y}",
                steps=steps,
                model="solve_system_2x2"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="solve_system_2x2")
    
    # ========== مشتقات (10 قوالب) ==========
    
    async def derivative(self, expression: str, variable: str = 'x') -> ExecutionResult:
        """قالب 15: مشتقة عامة - تستقبل نص"""
        try:
            expr = safe_sympify(expression)
            if expr is None:
                return ExecutionResult(success=False, error="تعبير غير صالح", model="derivative")
            
            var = ALLOWED_SYMBOLS.get(variable, sp.Symbol(variable))
            
            steps = [
                Step("📥", "السؤال", f"إيجاد مشتقة: {expression}"),
                Step("🔍", "التحليل", f"الاشتقاق بالنسبة للمتغير {variable}")
            ]
            
            result = sp.diff(expr, var)
            simplified = sp.simplify(result)
            
            steps.append(Step("🧮", "الحساب", f"d/d{variable} ({expression}) = {simplified}", sp.latex(simplified)))
            steps.append(Step("✅", "النتيجة", str(simplified)))
            
            self._increment_count()
            self._log_operation("derivative", {"expression": expression, "variable": variable}, simplified)
            
            return ExecutionResult(
                success=True,
                result=simplified,
                result_str=str(simplified),
                steps=steps,
                model="derivative"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="derivative")
    
    async def derivative_power(self, n: float) -> ExecutionResult:
        """قالب 16: مشتقة x^n"""
        try:
            steps = [
                Step("📥", "السؤال", f"مشتقة x^{n}"),
                Step("🔍", "التحليل", "تطبيق قاعدة مشتقة القوى")
            ]
            
            expr = self.x ** n
            result = sp.diff(expr, self.x)
            simplified = sp.simplify(result)
            
            steps.append(Step("📝", "القاعدة", "d/dx (x^n) = n·x^(n-1)"))
            steps.append(Step("🧮", "التطبيق", f"d/dx (x^{n}) = {n}·x^{{{n-1}}} = {simplified}", sp.latex(simplified)))
            steps.append(Step("✅", "النتيجة", str(simplified)))
            
            self._increment_count()
            self._log_operation("derivative_power", {"n": n}, simplified)
            
            return ExecutionResult(
                success=True,
                result=simplified,
                result_str=str(simplified),
                steps=steps,
                model="derivative_power"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="derivative_power")
    
    async def derivative_sin(self, variable: str = 'x') -> ExecutionResult:
        """قالب 17: مشتقة sin(x)"""
        steps = [
            Step("📥", "السؤال", f"مشتقة sin({variable})"),
            Step("🔍", "التحليل", "تطبيق قاعدة مشتقة الجيب"),
            Step("📝", "القاعدة", "d/dx sin(x) = cos(x)"),
            Step("🧮", "الحساب", f"d/d{variable} sin({variable}) = cos({variable})"),
            Step("✅", "النتيجة", f"cos({variable})")
        ]
        
        self._increment_count()
        self._log_operation("derivative_sin", {}, "cos")
        
        return ExecutionResult(
            success=True,
            result=f"cos({variable})",
            result_str=f"cos({variable})",
            steps=steps,
            model="derivative_sin"
        )
    
    async def derivative_cos(self, variable: str = 'x') -> ExecutionResult:
        """قالب 18: مشتقة cos(x)"""
        steps = [
            Step("📥", "السؤال", f"مشتقة cos({variable})"),
            Step("🔍", "التحليل", "تطبيق قاعدة مشتقة جيب التمام"),
            Step("📝", "القاعدة", "d/dx cos(x) = -sin(x)"),
            Step("🧮", "الحساب", f"d/d{variable} cos({variable}) = -sin({variable})"),
            Step("✅", "النتيجة", f"-sin({variable})")
        ]
        
        self._increment_count()
        self._log_operation("derivative_cos", {}, "-sin")
        
        return ExecutionResult(
            success=True,
            result=f"-sin({variable})",
            result_str=f"-sin({variable})",
            steps=steps,
            model="derivative_cos"
        )
    
    async def derivative_tan(self, variable: str = 'x') -> ExecutionResult:
        """قالب 19: مشتقة tan(x)"""
        steps = [
            Step("📥", "السؤال", f"مشتقة tan({variable})"),
            Step("🔍", "التحليل", "تطبيق قاعدة مشتقة الظل"),
            Step("📝", "القاعدة", "d/dx tan(x) = sec²(x)"),
            Step("🧮", "الحساب", f"d/d{variable} tan({variable}) = sec²({variable})"),
            Step("✅", "النتيجة", f"sec²({variable})")
        ]
        
        self._increment_count()
        self._log_operation("derivative_tan", {}, "sec^2")
        
        return ExecutionResult(
            success=True,
            result=f"sec²({variable})",
            result_str=f"sec²({variable})",
            steps=steps,
            model="derivative_tan"
        )
    
    async def derivative_exp(self, variable: str = 'x') -> ExecutionResult:
        """قالب 20: مشتقة e^x"""
        steps = [
            Step("📥", "السؤال", f"مشتقة e^{{{variable}}}"),
            Step("🔍", "التحليل", "تطبيق قاعدة مشتقة الدالة الأسية"),
            Step("📝", "القاعدة", "d/dx e^x = e^x"),
            Step("🧮", "الحساب", f"d/d{variable} e^{{{variable}}} = e^{{{variable}}}"),
            Step("✅", "النتيجة", f"e^{{{variable}}}")
        ]
        
        self._increment_count()
        self._log_operation("derivative_exp", {}, "exp")
        
        return ExecutionResult(
            success=True,
            result=f"e^{{{variable}}}",
            result_str=f"e^{variable}",
            steps=steps,
            model="derivative_exp"
        )
    
    async def derivative_ln(self, variable: str = 'x') -> ExecutionResult:
        """قالب 21: مشتقة ln(x)"""
        steps = [
            Step("📥", "السؤال", f"مشتقة ln({variable})"),
            Step("🔍", "التحليل", "تطبيق قاعدة مشتقة اللوغاريتم الطبيعي"),
            Step("📝", "القاعدة", "d/dx ln(x) = 1/x"),
            Step("🧮", "الحساب", f"d/d{variable} ln({variable}) = 1/{variable}"),
            Step("✅", "النتيجة", f"1/{variable}")
        ]
        
        self._increment_count()
        self._log_operation("derivative_ln", {}, "1/x")
        
        return ExecutionResult(
            success=True,
            result=f"1/{variable}",
            result_str=f"1/{variable}",
            steps=steps,
            model="derivative_ln"
        )
    
    async def derivative_product(self, u: str, v: str, variable: str = 'x') -> ExecutionResult:
        """قالب 22: مشتقة حاصل ضرب دالتين"""
        try:
            u_expr = safe_sympify(u)
            v_expr = safe_sympify(v)
            if u_expr is None or v_expr is None:
                return ExecutionResult(success=False, error="تعبير غير صالح", model="derivative_product")
            
            var = ALLOWED_SYMBOLS.get(variable, sp.Symbol(variable))
            
            steps = [
                Step("📥", "السؤال", f"مشتقة {u} × {v}"),
                Step("🔍", "التحليل", "تطبيق قاعدة ضرب الدوال"),
                Step("📝", "القاعدة", "d/dx [u·v] = u'·v + u·v'")
            ]
            
            result = sp.diff(u_expr * v_expr, var)
            simplified = sp.simplify(result)
            
            steps.append(Step("🧮", "الحساب", f"= {simplified}", sp.latex(simplified)))
            steps.append(Step("✅", "النتيجة", str(simplified)))
            
            self._increment_count()
            self._log_operation("derivative_product", {"u": u, "v": v}, simplified)
            
            return ExecutionResult(
                success=True,
                result=simplified,
                result_str=str(simplified),
                steps=steps,
                model="derivative_product"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="derivative_product")
    
    async def derivative_quotient(self, u: str, v: str, variable: str = 'x') -> ExecutionResult:
        """قالب 23: مشتقة حاصل قسمة دالتين"""
        try:
            u_expr = safe_sympify(u)
            v_expr = safe_sympify(v)
            if u_expr is None or v_expr is None:
                return ExecutionResult(success=False, error="تعبير غير صالح", model="derivative_quotient")
            
            var = ALLOWED_SYMBOLS.get(variable, sp.Symbol(variable))
            
            steps = [
                Step("📥", "السؤال", f"مشتقة {u} / {v}"),
                Step("🔍", "التحليل", "تطبيق قاعدة قسمة الدوال"),
                Step("📝", "القاعدة", "d/dx [u/v] = (u'·v - u·v') / v²")
            ]
            
            result = sp.diff(u_expr / v_expr, var)
            simplified = sp.simplify(result)
            
            steps.append(Step("🧮", "الحساب", f"= {simplified}", sp.latex(simplified)))
            steps.append(Step("✅", "النتيجة", str(simplified)))
            
            self._increment_count()
            self._log_operation("derivative_quotient", {"u": u, "v": v}, simplified)
            
            return ExecutionResult(
                success=True,
                result=simplified,
                result_str=str(simplified),
                steps=steps,
                model="derivative_quotient"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="derivative_quotient")
    
    async def derivative_chain(self, outer: str, inner: str, variable: str = 'x') -> ExecutionResult:
        """قالب 24: مشتقة قاعدة السلسلة"""
        try:
            outer_expr = safe_sympify(outer)
            inner_expr = safe_sympify(inner)
            if outer_expr is None or inner_expr is None:
                return ExecutionResult(success=False, error="تعبير غير صالح", model="derivative_chain")
            
            var = ALLOWED_SYMBOLS.get(variable, sp.Symbol(variable))
            
            steps = [
                Step("📥", "السؤال", f"مشتقة {outer}({inner})"),
                Step("🔍", "التحليل", "تطبيق قاعدة السلسلة"),
                Step("📝", "القاعدة", "d/dx f(g(x)) = f'(g(x)) · g'(x)")
            ]
            
            composed = outer_expr.subs(var, inner_expr)
            result = sp.diff(composed, var)
            simplified = sp.simplify(result)
            
            steps.append(Step("🧮", "الحساب", f"= {simplified}", sp.latex(simplified)))
            steps.append(Step("✅", "النتيجة", str(simplified)))
            
            self._increment_count()
            self._log_operation("derivative_chain", {"outer": outer, "inner": inner}, simplified)
            
            return ExecutionResult(
                success=True,
                result=simplified,
                result_str=str(simplified),
                steps=steps,
                model="derivative_chain"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="derivative_chain")
    
    # ========== تكاملات (10 قوالب) ==========
    
    async def integral(self, expression: str, variable: str = 'x') -> ExecutionResult:
        """قالب 25: تكامل عام - تستقبل نص"""
        try:
            expr = safe_sympify(expression)
            if expr is None:
                return ExecutionResult(success=False, error="تعبير غير صالح", model="integral")
            
            var = ALLOWED_SYMBOLS.get(variable, sp.Symbol(variable))
            
            steps = [
                Step("📥", "السؤال", f"∫ {expression} d{variable}"),
                Step("🔍", "التحليل", f"إيجاد التكامل غير المحدد للدالة")
            ]
            
            result = sp.integrate(expr, var)
            
            steps.append(Step("🧮", "الحساب", f"∫ {expression} d{variable} = {result} + C", sp.latex(result)))
            steps.append(Step("✅", "النتيجة", f"{result} + C"))
            steps.append(Step("ℹ️", "ملاحظة", "C هو ثابت التكامل"))
            
            self._increment_count()
            self._log_operation("integral", {"expression": expression}, result)
            
            return ExecutionResult(
                success=True,
                result=f"{result} + C",
                result_str=f"{result} + C",
                steps=steps,
                model="integral"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="integral")
    
    async def integral_power(self, n: float, variable: str = 'x') -> ExecutionResult:
        """قالب 26: تكامل x^n"""
        try:
            steps = [
                Step("📥", "السؤال", f"∫ {variable}^{n} d{variable}"),
                Step("🔍", "التحليل", "تطبيق قاعدة تكامل القوى")
            ]
            
            if n == -1:
                steps.append(Step("📝", "القاعدة", "∫ x⁻¹ dx = ln|x| + C"))
                steps.append(Step("🧮", "الحساب", f"∫ {variable}^{n} d{variable} = ln|{variable}| + C"))
                steps.append(Step("✅", "النتيجة", f"ln|{variable}| + C"))
                result = f"ln|{variable}| + C"
            else:
                steps.append(Step("📝", "القاعدة", "∫ x^n dx = x^(n+1)/(n+1) + C"))
                result_expr = sp.integrate(self.x ** n, self.x)
                steps.append(Step("🧮", "الحساب", f"∫ {variable}^{n} d{variable} = {result_expr} + C", sp.latex(result_expr)))
                steps.append(Step("✅", "النتيجة", f"{result_expr} + C"))
                result = f"{result_expr} + C"
            
            self._increment_count()
            self._log_operation("integral_power", {"n": n}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=result,
                steps=steps,
                model="integral_power"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="integral_power")
    
    async def integral_sin(self, variable: str = 'x') -> ExecutionResult:
        """قالب 27: تكامل sin(x)"""
        steps = [
            Step("📥", "السؤال", f"∫ sin({variable}) d{variable}"),
            Step("🔍", "التحليل", "تطبيق قاعدة تكامل الجيب"),
            Step("📝", "القاعدة", "∫ sin(x) dx = -cos(x) + C"),
            Step("🧮", "الحساب", f"∫ sin({variable}) d{variable} = -cos({variable}) + C"),
            Step("✅", "النتيجة", f"-cos({variable}) + C")
        ]
        
        self._increment_count()
        self._log_operation("integral_sin", {}, "-cos + C")
        
        return ExecutionResult(
            success=True,
            result=f"-cos({variable}) + C",
            result_str=f"-cos({variable}) + C",
            steps=steps,
            model="integral_sin"
        )
    
    async def integral_cos(self, variable: str = 'x') -> ExecutionResult:
        """قالب 28: تكامل cos(x)"""
        steps = [
            Step("📥", "السؤال", f"∫ cos({variable}) d{variable}"),
            Step("🔍", "التحليل", "تطبيق قاعدة تكامل جيب التمام"),
            Step("📝", "القاعدة", "∫ cos(x) dx = sin(x) + C"),
            Step("🧮", "الحساب", f"∫ cos({variable}) d{variable} = sin({variable}) + C"),
            Step("✅", "النتيجة", f"sin({variable}) + C")
        ]
        
        self._increment_count()
        self._log_operation("integral_cos", {}, "sin + C")
        
        return ExecutionResult(
            success=True,
            result=f"sin({variable}) + C",
            result_str=f"sin({variable}) + C",
            steps=steps,
            model="integral_cos"
        )
    
    async def integral_exp(self, variable: str = 'x') -> ExecutionResult:
        """قالب 29: تكامل e^x"""
        steps = [
            Step("📥", "السؤال", f"∫ e^{{{variable}}} d{variable}"),
            Step("🔍", "التحليل", "تطبيق قاعدة تكامل الدالة الأسية"),
            Step("📝", "القاعدة", "∫ e^x dx = e^x + C"),
            Step("🧮", "الحساب", f"∫ e^{{{variable}}} d{variable} = e^{{{variable}}} + C"),
            Step("✅", "النتيجة", f"e^{{{variable}}} + C")
        ]
        
        self._increment_count()
        self._log_operation("integral_exp", {}, "exp + C")
        
        return ExecutionResult(
            success=True,
            result=f"e^{{{variable}}} + C",
            result_str=f"e^{variable} + C",
            steps=steps,
            model="integral_exp"
        )
    
    async def integral_ln(self, variable: str = 'x') -> ExecutionResult:
        """قالب 30: تكامل ln(x)"""
        steps = [
            Step("📥", "السؤال", f"∫ ln({variable}) d{variable}"),
            Step("🔍", "التحليل", "تطبيق قاعدة تكامل اللوغاريتم الطبيعي"),
            Step("📝", "القاعدة", "∫ ln(x) dx = x·ln|x| - x + C"),
            Step("🧮", "الحساب", f"∫ ln({variable}) d{variable} = {variable}·ln|{variable}| - {variable} + C"),
            Step("✅", "النتيجة", f"{variable}·ln|{variable}| - {variable} + C")
        ]
        
        self._increment_count()
        self._log_operation("integral_ln", {}, "x ln x - x + C")
        
        return ExecutionResult(
            success=True,
            result=f"{variable}·ln|{variable}| - {variable} + C",
            result_str=f"{variable}·ln|{variable}| - {variable} + C",
            steps=steps,
            model="integral_ln"
        )
    
    async def integral_definite(self, expression: str, lower: float, upper: float, variable: str = 'x') -> ExecutionResult:
        """قالب 31: تكامل محدد - تستقبل نص"""
        try:
            expr = safe_sympify(expression)
            if expr is None:
                return ExecutionResult(success=False, error="تعبير غير صالح", model="integral_definite")
            
            var = ALLOWED_SYMBOLS.get(variable, sp.Symbol(variable))
            
            steps = [
                Step("📥", "السؤال", f"∫ من {lower} إلى {upper} لـ {expression} d{variable}"),
                Step("🔍", "التحليل", f"إيجاد التكامل المحدد على الفترة [{lower}, {upper}]")
            ]
            
            upper_val = sp.oo if upper in [float('inf'), '∞', 'infinity'] else float(upper)
            lower_val = float(lower)
            
            result = sp.integrate(expr, (var, lower_val, upper_val))
            
            steps.append(Step("🧮", "الحساب", f"∫_{lower}^{upper} {expression} d{variable} = {result}", sp.latex(result)))
            
            try:
                float_val = float(result.evalf())
                if result != float_val:
                    steps.append(Step("📊", "القيمة التقريبية", f"≈ {float_val:.6f}"))
            except:
                pass
            
            steps.append(Step("✅", "النتيجة", str(result)))
            
            self._increment_count()
            self._log_operation("integral_definite", {"expression": expression, "lower": lower, "upper": upper}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps,
                model="integral_definite"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="integral_definite")
    
    async def integral_by_parts(self, u: str, dv: str, variable: str = 'x') -> ExecutionResult:
        """قالب 33: تكامل بالأجزاء"""
        try:
            u_expr = safe_sympify(u)
            dv_expr = safe_sympify(dv)
            if u_expr is None or dv_expr is None:
                return ExecutionResult(success=False, error="تعبير غير صالح", model="integral_by_parts")
            
            var = ALLOWED_SYMBOLS.get(variable, sp.Symbol(variable))
            
            steps = [
                Step("📥", "السؤال", f"∫ {u} d({dv})"),
                Step("🔍", "التحليل", "تطبيق قاعدة التكامل بالأجزاء"),
                Step("📝", "القاعدة", "∫ u dv = u·v - ∫ v du")
            ]
            
            v_expr = sp.integrate(dv_expr, var)
            du_expr = sp.diff(u_expr, var)
            result = u_expr * v_expr - sp.integrate(v_expr * du_expr, var)
            
            steps.extend([
                Step("📝", "نختار", f"u = {u}, dv = {dv} d{variable}"),
                Step("📝", "نحسب", f"v = ∫ {dv} d{variable} = {v_expr}"),
                Step("📝", "نحسب", f"du = d/d{variable} ({u}) d{variable} = {du_expr} d{variable}"),
                Step("🧮", "التطبيق", f"= {u}·{v_expr} - ∫ {v_expr}·{du_expr} d{variable}"),
                Step("🧮", "النتيجة", f"= {result} + C", sp.latex(result)),
                Step("✅", "النتيجة النهائية", f"{result} + C")
            ])
            
            self._increment_count()
            self._log_operation("integral_by_parts", {"u": u, "dv": dv}, result)
            
            return ExecutionResult(
                success=True,
                result=f"{result} + C",
                result_str=f"{result} + C",
                steps=steps,
                model="integral_by_parts"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="integral_by_parts")
    
    async def integral_substitution(self, expression: str, variable: str = 'x') -> ExecutionResult:
        """قالب 34: تكامل بالتعويض (تلقائي)"""
        try:
            expr = safe_sympify(expression)
            if expr is None:
                return ExecutionResult(success=False, error="تعبير غير صالح", model="integral_substitution")
            
            var = ALLOWED_SYMBOLS.get(variable, sp.Symbol(variable))
            
            steps = [
                Step("📥", "السؤال", f"∫ {expression} d{variable}"),
                Step("🔍", "التحليل", "إيجاد التكامل باستخدام التعويض المناسب")
            ]
            
            result = sp.integrate(expr, var)
            
            steps.append(Step("🧮", "الحساب", f"= {result} + C", sp.latex(result)))
            steps.append(Step("✅", "النتيجة", f"{result} + C"))
            
            self._increment_count()
            self._log_operation("integral_substitution", {"expression": expression}, result)
            
            return ExecutionResult(
                success=True,
                result=f"{result} + C",
                result_str=f"{result} + C",
                steps=steps,
                model="integral_substitution"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="integral_substitution")
    
    # ========== مصفوفات (7 قوالب) ==========
    
    async def matrix_determinant(self, matrix: List[List[float]]) -> ExecutionResult:
        """قالب 41: محدد مصفوفة"""
        try:
            if len(matrix) > MAX_MATRIX_SIZE:
                return ExecutionResult(success=False, error=f"حجم المصفوفة كبير جداً", model="matrix_determinant")
            
            M = sp.Matrix(matrix)
            result = M.det()
            
            steps = [
                Step("📥", "السؤال", f"إيجاد محدد المصفوفة"),
                Step("📊", "المصفوفة", f"{M}", sp.latex(M)),
                Step("🧮", "الحساب", f"det = {result}"),
                Step("✅", "النتيجة", str(result))
            ]
            
            self._increment_count()
            self._log_operation("matrix_determinant", {"matrix": matrix}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps,
                model="matrix_determinant"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="matrix_determinant")
    
    async def matrix_inverse(self, matrix: List[List[float]]) -> ExecutionResult:
        """قالب 42: معكوس مصفوفة"""
        try:
            if len(matrix) > MAX_MATRIX_SIZE:
                return ExecutionResult(success=False, error=f"حجم المصفوفة كبير جداً", model="matrix_inverse")
            
            M = sp.Matrix(matrix)
            
            steps = [
                Step("📥", "السؤال", f"إيجاد معكوس المصفوفة"),
                Step("📊", "المصفوفة", f"{M}", sp.latex(M))
            ]
            
            if not M.is_invertible():
                return ExecutionResult(success=False, error="المصفوفة غير قابلة للعكس", steps=steps, model="matrix_inverse")
            
            result = M.inv()
            
            steps.extend([
                Step("🧮", "الحساب", f"M⁻¹ = {result}", sp.latex(result)),
                Step("✅", "النتيجة", str(result))
            ])
            
            self._increment_count()
            self._log_operation("matrix_inverse", {"matrix": matrix}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps,
                model="matrix_inverse"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="matrix_inverse")
    
    async def matrix_transpose(self, matrix: List[List[float]]) -> ExecutionResult:
        """قالب 43: مدور مصفوفة"""
        try:
            if len(matrix) > MAX_MATRIX_SIZE:
                return ExecutionResult(success=False, error=f"حجم المصفوفة كبير جداً", model="matrix_transpose")
            
            M = sp.Matrix(matrix)
            result = M.T
            
            steps = [
                Step("📥", "السؤال", f"إيجاد مدور المصفوفة"),
                Step("📊", "المصفوفة", f"{M}", sp.latex(M)),
                Step("🧮", "الحساب", f"Mᵀ = {result}", sp.latex(result)),
                Step("✅", "النتيجة", str(result))
            ]
            
            self._increment_count()
            self._log_operation("matrix_transpose", {"matrix": matrix}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps,
                model="matrix_transpose"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="matrix_transpose")
    
    async def matrix_multiply(self, A: List[List[float]], B: List[List[float]]) -> ExecutionResult:
        """قالب 44: ضرب مصفوفتين"""
        try:
            if len(A) > MAX_MATRIX_SIZE or len(B) > MAX_MATRIX_SIZE:
                return ExecutionResult(success=False, error=f"حجم المصفوفة كبير جداً", model="matrix_multiply")
            
            M1 = sp.Matrix(A)
            M2 = sp.Matrix(B)
            
            steps = [
                Step("📥", "السؤال", f"ضرب مصفوفتين"),
                Step("📊", "المصفوفة الأولى", f"{M1}", sp.latex(M1)),
                Step("📊", "المصفوفة الثانية", f"{M2}", sp.latex(M2))
            ]
            
            if M1.shape[1] != M2.shape[0]:
                return ExecutionResult(
                    success=False, 
                    error=f"أبعاد غير متوافقة: {M1.shape} و {M2.shape}", 
                    steps=steps, 
                    model="matrix_multiply"
                )
            
            result = M1 * M2
            
            steps.extend([
                Step("🧮", "الحساب", f"M1 × M2 = {result}", sp.latex(result)),
                Step("✅", "النتيجة", str(result))
            ])
            
            self._increment_count()
            self._log_operation("matrix_multiply", {"A": A, "B": B}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps,
                model="matrix_multiply"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="matrix_multiply")
    
    async def matrix_add(self, A: List[List[float]], B: List[List[float]]) -> ExecutionResult:
        """قالب 45: جمع مصفوفتين"""
        try:
            if len(A) > MAX_MATRIX_SIZE or len(B) > MAX_MATRIX_SIZE:
                return ExecutionResult(success=False, error=f"حجم المصفوفة كبير جداً", model="matrix_add")
            
            M1 = sp.Matrix(A)
            M2 = sp.Matrix(B)
            
            steps = [
                Step("📥", "السؤال", f"جمع مصفوفتين"),
                Step("📊", "المصفوفة الأولى", f"{M1}", sp.latex(M1)),
                Step("📊", "المصفوفة الثانية", f"{M2}", sp.latex(M2))
            ]
            
            if M1.shape != M2.shape:
                return ExecutionResult(
                    success=False, 
                    error=f"الأبعاد غير متطابقة: {M1.shape} و {M2.shape}", 
                    steps=steps, 
                    model="matrix_add"
                )
            
            result = M1 + M2
            
            steps.extend([
                Step("🧮", "الحساب", f"M1 + M2 = {result}", sp.latex(result)),
                Step("✅", "النتيجة", str(result))
            ])
            
            self._increment_count()
            self._log_operation("matrix_add", {"A": A, "B": B}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps,
                model="matrix_add"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="matrix_add")
    
    async def matrix_subtract(self, A: List[List[float]], B: List[List[float]]) -> ExecutionResult:
        """قالب 46: طرح مصفوفتين"""
        try:
            if len(A) > MAX_MATRIX_SIZE or len(B) > MAX_MATRIX_SIZE:
                return ExecutionResult(success=False, error=f"حجم المصفوفة كبير جداً", model="matrix_subtract")
            
            M1 = sp.Matrix(A)
            M2 = sp.Matrix(B)
            
            steps = [
                Step("📥", "السؤال", f"طرح مصفوفتين"),
                Step("📊", "المصفوفة الأولى", f"{M1}", sp.latex(M1)),
                Step("📊", "المصفوفة الثانية", f"{M2}", sp.latex(M2))
            ]
            
            if M1.shape != M2.shape:
                return ExecutionResult(
                    success=False, 
                    error=f"الأبعاد غير متطابقة: {M1.shape} و {M2.shape}", 
                    steps=steps, 
                    model="matrix_subtract"
                )
            
            result = M1 - M2
            
            steps.extend([
                Step("🧮", "الحساب", f"M1 - M2 = {result}", sp.latex(result)),
                Step("✅", "النتيجة", str(result))
            ])
            
            self._increment_count()
            self._log_operation("matrix_subtract", {"A": A, "B": B}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps,
                model="matrix_subtract"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="matrix_subtract")
    
    async def matrix_eigenvalues(self, matrix: List[List[float]]) -> ExecutionResult:
        """قالب 47: القيم الذاتية لمصفوفة"""
        try:
            if len(matrix) > MAX_MATRIX_SIZE:
                return ExecutionResult(success=False, error=f"حجم المصفوفة كبير جداً", model="matrix_eigenvalues")
            
            M = sp.Matrix(matrix)
            
            steps = [
                Step("📥", "السؤال", f"إيجاد القيم الذاتية للمصفوفة"),
                Step("📊", "المصفوفة", f"{M}", sp.latex(M))
            ]
            
            if M.rows != M.cols:
                return ExecutionResult(
                    success=False, 
                    error="القيم الذاتية للمصفوفات المربعة فقط", 
                    steps=steps, 
                    model="matrix_eigenvalues"
                )
            
            eigenvals = M.eigenvals()
            result = list(eigenvals.keys())
            
            steps.extend([
                Step("🧮", "الحساب", f"λ = {result}"),
                Step("✅", "النتيجة", str(result))
            ])
            
            self._increment_count()
            self._log_operation("matrix_eigenvalues", {"matrix": matrix}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps,
                model="matrix_eigenvalues"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="matrix_eigenvalues")
    
    # ========== نهايات (5 قوالب) ==========
    
    async def limit(self, expression: str, variable: str, approach: str) -> ExecutionResult:
        """قالب 48: نهاية دالة - تستقبل نص"""
        try:
            expr = safe_sympify(expression)
            if expr is None:
                return ExecutionResult(success=False, error="تعبير غير صالح", model="limit")
            
            var = ALLOWED_SYMBOLS.get(variable, sp.Symbol(variable))
            
            steps = [
                Step("📥", "السؤال", f"إيجاد نهاية {expression} عندما {variable} → {approach}"),
                Step("🔍", "التحليل", f"حساب lim_{{{variable}→{approach}}} {expression}")
            ]
            
            if approach in ['∞', 'infinity']:
                approach_val = sp.oo
            elif approach in ['-∞', '-infinity']:
                approach_val = -sp.oo
            else:
                approach_val = float(approach)
            
            result = sp.limit(expr, var, approach_val)
            
            steps.append(Step("🧮", "الحساب", f"= {result}", sp.latex(result)))
            steps.append(Step("✅", "النتيجة", str(result)))
            
            self._increment_count()
            self._log_operation("limit", {"expression": expression, "approach": approach}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps,
                model="limit"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="limit")
    
    # ========== مثلثات (5 قوالب) ==========
    
    async def sin(self, angle: float, unit: str = "deg") -> ExecutionResult:
        """قالب 49: جيب الزاوية"""
        try:
            rad = math.radians(angle) if unit == "deg" else angle
            result = math.sin(rad)
            unit_str = "°" if unit == "deg" else " rad"
            
            steps = [
                Step("📥", "السؤال", f"sin({angle}{unit_str})"),
                Step("🔍", "التحليل", f"حساب جيب الزاوية {angle}{unit_str}"),
                Step("🧮", "الحساب", f"sin({angle}{unit_str}) = {result:.6f}"),
                Step("✅", "النتيجة", str(result))
            ]
            
            self._increment_count()
            self._log_operation("sin", {"angle": angle, "unit": unit}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps,
                model="sin"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="sin")
    
    async def cos(self, angle: float, unit: str = "deg") -> ExecutionResult:
        """قالب 50: جيب تمام"""
        try:
            rad = math.radians(angle) if unit == "deg" else angle
            result = math.cos(rad)
            unit_str = "°" if unit == "deg" else " rad"
            
            steps = [
                Step("📥", "السؤال", f"cos({angle}{unit_str})"),
                Step("🔍", "التحليل", f"حساب جيب تمام الزاوية {angle}{unit_str}"),
                Step("🧮", "الحساب", f"cos({angle}{unit_str}) = {result:.6f}"),
                Step("✅", "النتيجة", str(result))
            ]
            
            self._increment_count()
            self._log_operation("cos", {"angle": angle, "unit": unit}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps,
                model="cos"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="cos")
    
    async def tan(self, angle: float, unit: str = "deg") -> ExecutionResult:
        """قالب 51: ظل الزاوية"""
        try:
            rad = math.radians(angle) if unit == "deg" else angle
            result = math.tan(rad)
            unit_str = "°" if unit == "deg" else " rad"
            
            steps = [
                Step("📥", "السؤال", f"tan({angle}{unit_str})"),
                Step("🔍", "التحليل", f"حساب ظل الزاوية {angle}{unit_str}"),
                Step("🧮", "الحساب", f"tan({angle}{unit_str}) = {result:.6f}"),
                Step("✅", "النتيجة", str(result))
            ]
            
            self._increment_count()
            self._log_operation("tan", {"angle": angle, "unit": unit}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps,
                model="tan"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="tan")
    
    async def law_of_sines(self, a: float, A: float, b: float, unit: str = "deg") -> ExecutionResult:
        """قالب 52: قانون الجيب"""
        try:
            unit_str = "°" if unit == "deg" else " rad"
            A_rad = math.radians(A) if unit == "deg" else A
            
            steps = [
                Step("📥", "السؤال", f"إيجاد الزاوية B باستخدام قانون الجيب: a={a}, A={A}{unit_str}, b={b}"),
                Step("🔍", "التحليل", "تطبيق قانون الجيب: a/sin(A) = b/sin(B)")
            ]
            
            sinA = math.sin(A_rad)
            sinB = (b * sinA) / a
            
            if not self._validate_angle_for_asin(sinB):
                return ExecutionResult(success=False, error="لا يوجد حل - قيمة خارج نطاق arcsin", steps=steps, model="law_of_sines")
            
            B_rad = math.asin(sinB)
            B = math.degrees(B_rad) if unit == "deg" else B_rad
            
            steps.extend([
                Step("📝", "الحساب", f"sin(B) = (b × sin(A)) / a = ({b} × {sinA:.4f}) / {a} = {sinB:.4f}"),
                Step("🧮", "النتيجة", f"B = {B:.4f}{unit_str}"),
                Step("✅", "الحل", f"الزاوية B = {B:.4f}{unit_str}")
            ])
            
            self._increment_count()
            self._log_operation("law_of_sines", {"a": a, "A": A, "b": b}, B)
            
            return ExecutionResult(
                success=True,
                result=B,
                result_str=f"{B:.4f}{unit_str}",
                steps=steps,
                model="law_of_sines"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="law_of_sines")
    
    async def law_of_cosines(self, a: float, b: float, C: float, unit: str = "deg") -> ExecutionResult:
        """قالب 53: قانون جيب التمام"""
        try:
            unit_str = "°" if unit == "deg" else " rad"
            C_rad = math.radians(C) if unit == "deg" else C
            
            steps = [
                Step("📥", "السؤال", f"إيجاد الضلع c: a={a}, b={b}, C={C}{unit_str}"),
                Step("🔍", "التحليل", "تطبيق قانون جيب التمام: c² = a² + b² - 2ab·cos(C)")
            ]
            
            cosC = math.cos(C_rad)
            c_squared = a**2 + b**2 - 2*a*b*cosC
            c = math.sqrt(max(c_squared, 0))
            
            steps.extend([
                Step("📝", "الحساب", f"c² = {a}² + {b}² - 2×{a}×{b}×cos({C}{unit_str})"),
                Step("🧮", "التفاصيل", f"= {a**2:.4f} + {b**2:.4f} - 2×{a}×{b}×{cosC:.4f} = {c_squared:.4f}"),
                Step("🧮", "النتيجة", f"c = √{c_squared:.4f} = {c:.6f}"),
                Step("✅", "الحل", f"الضلع c = {c:.6f}")
            ])
            
            if c_squared < 0:
                steps.insert(-2, Step("⚠️", "تنبيه", f"c² سالبة، تم استخدام القيمة المطلقة"))
            
            self._increment_count()
            self._log_operation("law_of_cosines", {"a": a, "b": b, "C": C}, c)
            
            return ExecutionResult(
                success=True,
                result=c,
                result_str=str(c),
                steps=steps,
                model="law_of_cosines"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="law_of_cosines")
    
    # ========== إحصاء (5 قوالب) ==========
    
    async def mean(self, data: List[float]) -> ExecutionResult:
        """قالب 54: المتوسط الحسابي"""
        try:
            if not data:
                return ExecutionResult(success=False, error="لا توجد بيانات", model="mean")
            
            result = _calculate_mean(data)
            
            steps = [
                Step("📥", "السؤال", f"حساب المتوسط الحسابي للبيانات: {data}"),
                Step("🔍", "التحليل", f"المتوسط = مجموع القيم / عددها"),
                Step("🧮", "الحساب", f"= {sum(data):.4f} / {len(data)} = {result:.4f}"),
                Step("✅", "النتيجة", f"{result:.4f}")
            ]
            
            self._increment_count()
            self._log_operation("mean", {"data": data[:5]}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=f"{result:.4f}",
                steps=steps,
                model="mean"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="mean")
    
    async def median(self, data: List[float]) -> ExecutionResult:
        """قالب 55: الوسيط"""
        try:
            if not data:
                return ExecutionResult(success=False, error="لا توجد بيانات", model="median")
            
            sorted_data = sorted(data)
            n = len(sorted_data)
            
            steps = [
                Step("📥", "السؤال", f"حساب الوسيط للبيانات: {data}"),
                Step("🔍", "التحليل", f"ترتيب البيانات تصاعدياً: {sorted_data}")
            ]
            
            if n % 2 == 1:
                result = sorted_data[n // 2]
                steps.append(Step("🧮", "الحساب", f"عدد البيانات فردي ({n})، الوسيط هو القيمة الوسطى: {result:.4f}"))
            else:
                result = (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
                steps.append(Step("🧮", "الحساب", f"عدد البيانات زوجي ({n})، الوسيط = (القيمتان الوسطيتان)/2 = ({sorted_data[n//2-1]:.4f} + {sorted_data[n//2]:.4f})/2 = {result:.4f}"))
            
            steps.append(Step("✅", "النتيجة", f"{result:.4f}"))
            
            self._increment_count()
            self._log_operation("median", {"data": data[:5]}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=f"{result:.4f}",
                steps=steps,
                model="median"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="median")
    
    async def variance(self, data: List[float], sample: bool = True) -> ExecutionResult:
        """قالب 56: التباين"""
        try:
            if not data or len(data) < 2:
                return ExecutionResult(success=False, error="البيانات غير كافية", model="variance")
            
            mean_val = _calculate_mean(data)
            var_type = "العيني" if sample else "المجتمعي"
            n = len(data)
            denominator = n - 1 if sample else n
            
            steps = [
                Step("📥", "السؤال", f"حساب التباين {var_type} للبيانات: {data}"),
                Step("🔍", "التحليل", f"المتوسط الحسابي = {mean_val:.4f}"),
                Step("📝", "القانون", f"التباين = Σ(x - μ)² / {denominator}")
            ]
            
            deviations = [(x - mean_val) ** 2 for x in data]
            sum_sq = sum(deviations)
            result = sum_sq / denominator
            
            steps.append(Step("🧮", "الحساب", f"Σ(x - μ)² = {sum_sq:.4f}"))
            steps.append(Step("🧮", "التطبيق", f"التباين = {sum_sq:.4f} / {denominator} = {result:.4f}"))
            steps.append(Step("✅", "النتيجة", f"{result:.4f}"))
            
            self._increment_count()
            self._log_operation("variance", {"data": data[:5], "sample": sample}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=f"{result:.4f}",
                steps=steps,
                model="variance"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="variance")
    
    async def std_dev(self, data: List[float], sample: bool = True) -> ExecutionResult:
        """قالب 57: الانحراف المعياري"""
        try:
            if not data or len(data) < 2:
                return ExecutionResult(success=False, error="البيانات غير كافية", model="std_dev")
            
            mean_val = _calculate_mean(data)
            var_type = "العياري" if sample else "المجتمعي"
            n = len(data)
            denominator = n - 1 if sample else n
            
            steps = [
                Step("📥", "السؤال", f"حساب الانحراف المعياري {var_type} للبيانات: {data}"),
                Step("🔍", "التحليل", f"المتوسط الحسابي = {mean_val:.4f}")
            ]
            
            deviations = [(x - mean_val) ** 2 for x in data]
            sum_sq = sum(deviations)
            variance = sum_sq / denominator
            result = variance ** 0.5
            
            steps.extend([
                Step("📝", "القانون", f"التباين = Σ(x - μ)² / {denominator}"),
                Step("🧮", "التباين", f"= {sum_sq:.4f} / {denominator} = {variance:.4f}"),
                Step("🧮", "الانحراف المعياري", f"σ = √{variance:.4f} = {result:.4f}"),
                Step("✅", "النتيجة", f"{result:.4f}")
            ])
            
            self._increment_count()
            self._log_operation("std_dev", {"data": data[:5], "sample": sample}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=f"{result:.4f}",
                steps=steps,
                model="std_dev"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="std_dev")
    
    async def correlation(self, data1: List[float], data2: List[float]) -> ExecutionResult:
        """قالب 58: معامل ارتباط بيرسون"""
        try:
            if len(data1) != len(data2) or len(data1) < 2:
                return ExecutionResult(success=False, error="البيانات غير صالحة", model="correlation")
            
            n = len(data1)
            mean1 = _calculate_mean(data1)
            mean2 = _calculate_mean(data2)
            
            steps = [
                Step("📥", "السؤال", f"حساب معامل الارتباط بين المجموعتين"),
                Step("📊", "البيانات الأولى", f"{data1}"),
                Step("📊", "البيانات الثانية", f"{data2}"),
                Step("🔍", "التحليل", f"المتوسط الأول = {mean1:.4f}, المتوسط الثاني = {mean2:.4f}")
            ]
            
            covariance = sum((data1[i] - mean1) * (data2[i] - mean2) for i in range(n)) / (n - 1)
            std1 = _calculate_std_dev(data1, mean1, sample=True)
            std2 = _calculate_std_dev(data2, mean2, sample=True)
            
            if std1 == 0 or std2 == 0:
                return ExecutionResult(success=False, error="أحد المتغيرات ثابت", steps=steps, model="correlation")
            
            result = covariance / (std1 * std2)
            
            abs_r = abs(result)
            if abs_r > 0.9:
                strength = "قوية جداً"
            elif abs_r > 0.7:
                strength = "قوية"
            elif abs_r > 0.5:
                strength = "متوسطة"
            elif abs_r > 0.3:
                strength = "ضعيفة"
            else:
                strength = "ضعيفة جداً"
            
            direction = "طردية" if result > 0 else "عكسية"
            
            steps.extend([
                Step("📝", "التغاير", f"cov = {covariance:.4f}"),
                Step("📝", "الانحراف المعياري الأول", f"σ₁ = {std1:.4f}"),
                Step("📝", "الانحراف المعياري الثاني", f"σ₂ = {std2:.4f}"),
                Step("🧮", "معامل الارتباط", f"r = cov / (σ₁·σ₂) = {covariance:.4f} / ({std1:.4f}×{std2:.4f}) = {result:.4f}"),
                Step("📊", "التفسير", f"علاقة {direction} {strength}"),
                Step("✅", "النتيجة", f"r = {result:.4f}")
            ])
            
            self._increment_count()
            self._log_operation("correlation", {}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=f"{result:.4f}",
                steps=steps,
                model="correlation"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="correlation")
    
    # ========== إضافيات (قوالب 59-60) ==========
    
    async def simplify(self, expression: str) -> ExecutionResult:
        """قالب 59: تبسيط تعبير جبري"""
        try:
            expr = safe_sympify(expression)
            if expr is None:
                return ExecutionResult(success=False, error="تعبير غير صالح", model="simplify")
            
            steps = [
                Step("📥", "السؤال", f"تبسيط: {expression}"),
                Step("🔍", "التحليل", "تطبيق قواعد التبسيط الجبرية")
            ]
            
            simplified = sp.simplify(expr)
            
            steps.append(Step("🧮", "التبسيط", f"= {simplified}", sp.latex(simplified)))
            steps.append(Step("✅", "النتيجة", str(simplified)))
            
            self._increment_count()
            self._log_operation("simplify", {"expression": expression}, simplified)
            
            return ExecutionResult(
                success=True,
                result=simplified,
                result_str=str(simplified),
                steps=steps,
                model="simplify"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="simplify")
    
    async def expand(self, expression: str) -> ExecutionResult:
        """قالب 60: فك الأقواس"""
        try:
            expr = safe_sympify(expression)
            if expr is None:
                return ExecutionResult(success=False, error="تعبير غير صالح", model="expand")
            
            steps = [
                Step("📥", "السؤال", f"فك الأقواس: {expression}"),
                Step("🔍", "التحليل", "تطبيق خاصية التوزيع")
            ]
            
            expanded = sp.expand(expr)
            
            steps.append(Step("🧮", "الفك", f"= {expanded}", sp.latex(expanded)))
            steps.append(Step("✅", "النتيجة", str(expanded)))
            
            self._increment_count()
            self._log_operation("expand", {"expression": expression}, expanded)
            
            return ExecutionResult(
                success=True,
                result=expanded,
                result_str=str(expanded),
                steps=steps,
                model="expand"
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), model="expand")
    
    # ========== سجل العمليات وإحصائيات ==========
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        return self.history[-limit:]
    
    def clear_history(self):
        self.history.clear()
        logger.info("History cleared")
    
    def get_stats(self):
        return {
            "execution_count": self.execution_count,
            "status": "ready",
            "history_size": len(self.history)
        }
