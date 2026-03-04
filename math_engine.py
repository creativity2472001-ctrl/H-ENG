# math_engine.py - محرك العمليات الحسابية المتوافق مع ai_engine.py
import sympy as sp
import math
import logging
from typing import List, Optional, Any, Dict, Tuple, Union
from dataclasses import dataclass, field

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ========== ثوابت الأمان (مطابقة لـ ai_engine.py) ==========
MAX_MATRIX_SIZE = 10  # الحد الأقصى لحجم المصفوفة (10x10)

@dataclass
class Step:
    """خطوة حل واحدة - متوافق مع ai_engine.py"""
    text: str
    latex: str = ""
    
    def to_dict(self) -> dict:
        return {"text": self.text, "latex": self.latex}

@dataclass
class ExecutionResult:
    """نتيجة تنفيذ عملية حسابية - متوافق مع ai_engine.py"""
    success: bool
    result: Any = None
    result_str: str = ""
    steps: List[Step] = field(default_factory=list)
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "result": str(self.result) if self.result is not None else None,
            "result_str": self.result_str,
            "steps": [step.to_dict() for step in self.steps],
            "error": self.error
        }

# دوال مساعدة إحصائية
def _calculate_mean(data: List[float]) -> float:
    """حساب المتوسط الحسابي"""
    if not data:
        return 0
    return sum(data) / len(data)

def _calculate_variance(data: List[float], mean_val: float = None, sample: bool = False) -> float:
    """حساب التباين"""
    if not data or len(data) < 2:
        return 0
    if mean_val is None:
        mean_val = _calculate_mean(data)
    
    n = len(data)
    sum_sq = sum((x - mean_val) ** 2 for x in data)
    
    if sample:
        return sum_sq / (n - 1) if n > 1 else 0
    else:
        return sum_sq / n

def _calculate_std_dev(data: List[float], mean_val: float = None, sample: bool = False) -> float:
    """حساب الانحراف المعياري"""
    variance = _calculate_variance(data, mean_val, sample)
    return variance ** 0.5

class MathEngine:
    """محرك العمليات الحسابية - متوافق مع ai_engine.py"""
    
    def __init__(self):
        # تعريف المتغيرات الرمزية الأساسية
        self.x, self.y, self.z, self.t = sp.symbols('x y z t')
        self.n, self.k = sp.symbols('n k')
        
        self.execution_count = 0
        self.history = []
        self.max_history = 1000
        
        print("✅ Math Engine v1.0 - متوافق مع AI Engine")
        logger.info("Math Engine initialized")
    
    def _log_operation(self, operation: str, params: dict, result: Any):
        """تسجيل عملية في السجل"""
        self.history.append({
            "operation": operation,
            "params": params,
            "result": str(result)[:200]
        })
        
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def _increment_count(self):
        """زيادة عداد التنفيذ"""
        self.execution_count += 1
    
    def _validate_angle_for_asin(self, value: float) -> bool:
        """تدقيق أن قيمة arcsin ضمن [-1, 1]"""
        return -1 <= value <= 1
    
    # ========== الأساسيات (10 قوالب) ==========
    
    def calculate(self, expr: sp.Expr) -> ExecutionResult:
        """قالب 1: آلة حاسبة بسيطة"""
        try:
            result = expr.evalf()
            result_float = float(result)
            
            self._increment_count()
            self._log_operation("calculate", {"expr": str(expr)}, result_float)
            
            steps = [Step("🔢 عملية حسابية", f"{expr} = {result_float}")]
            
            if result.is_Rational and result.q != 1:
                steps.append(Step("📝 القيمة الدقيقة", str(expr)))
            
            return ExecutionResult(
                success=True,
                result=result_float,
                result_str=str(result_float),
                steps=steps
            )
        except Exception as e:
            logger.error(f"Error in calculate: {e}")
            return ExecutionResult(
                success=False,
                error=f"خطأ في الحساب: {str(e)}"
            )
    
    def power(self, base: float, exp: float) -> ExecutionResult:
        """قالب 2: رفع لقوة"""
        try:
            result = base ** exp
            self._increment_count()
            self._log_operation("power", {"base": base, "exp": exp}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=[Step("📈 رفع لقوة", f"{base}^{exp} = {result}")]
            )
        except Exception as e:
            logger.error(f"Error in power: {e}")
            return ExecutionResult(
                success=False,
                error=f"خطأ في رفع القوة: {str(e)}"
            )
    
    def sqrt(self, num: float) -> ExecutionResult:
        """قالب 3: جذر تربيعي"""
        try:
            if num < 0:
                result = sp.sqrt(num)
                result_str = str(result)
                steps = [Step("🔮 جذر تربيعي (عدد مركب)", f"√{num} = {result_str}")]
            else:
                result = num ** 0.5
                result_str = str(result)
                steps = [Step("√ جذر تربيعي", f"√{num} = {result_str}")]
            
            self._increment_count()
            self._log_operation("sqrt", {"num": num}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=result_str,
                steps=steps
            )
        except Exception as e:
            logger.error(f"Error in sqrt: {e}")
            return ExecutionResult(
                success=False,
                error=f"خطأ في حساب الجذر: {str(e)}"
            )
    
    def factorial(self, n: int) -> ExecutionResult:
        """قالب 4: مضروب"""
        try:
            if n < 0:
                return ExecutionResult(
                    success=False,
                    error="لا يمكن حساب مضروب لعدد سالب"
                )
            
            if n > 100:
                return ExecutionResult(
                    success=False,
                    error="العدد كبير جداً لحساب المضروب"
                )
            
            result = math.factorial(n)
            
            self._increment_count()
            self._log_operation("factorial", {"n": n}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=[Step("! مضروب", f"{n}! = {result}")]
            )
        except Exception as e:
            logger.error(f"Error in factorial: {e}")
            return ExecutionResult(
                success=False,
                error=f"خطأ في حساب المضروب: {str(e)}"
            )
    
    def percent(self, value: float, total: float) -> ExecutionResult:
        """قالب 5: نسبة مئوية"""
        try:
            result = (value / 100) * total
            self._increment_count()
            self._log_operation("percent", {"value": value, "total": total}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=[Step("📊 نسبة مئوية", f"{value}% من {total} = {result}")]
            )
        except Exception as e:
            logger.error(f"Error in percent: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def absolute(self, value: float) -> ExecutionResult:
        """قالب 6: قيمة مطلقة"""
        try:
            result = abs(value)
            self._increment_count()
            self._log_operation("absolute", {"value": value}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=[Step("📏 قيمة مطلقة", f"|{value}| = {result}")]
            )
        except Exception as e:
            logger.error(f"Error in absolute: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def gcd(self, a: int, b: int) -> ExecutionResult:
        """قالب 7: القاسم المشترك الأكبر"""
        try:
            result = math.gcd(a, b)
            self._increment_count()
            self._log_operation("gcd", {"a": a, "b": b}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=[Step("🔢 القاسم المشترك الأكبر", f"GCD({a}, {b}) = {result}")]
            )
        except Exception as e:
            logger.error(f"Error in gcd: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def lcm(self, a: int, b: int) -> ExecutionResult:
        """قالب 8: المضاعف المشترك الأصغر"""
        try:
            result = abs(a * b) // math.gcd(a, b) if a and b else 0
            self._increment_count()
            self._log_operation("lcm", {"a": a, "b": b}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=[Step("📐 المضاعف المشترك الأصغر", f"LCM({a}, {b}) = {result}")]
            )
        except Exception as e:
            logger.error(f"Error in lcm: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def log10(self, num: float) -> ExecutionResult:
        """قالب 9: لوغاريتم عشري"""
        try:
            if num <= 0:
                return ExecutionResult(
                    success=False,
                    error="لا يمكن حساب لوغاريتم لعدد سالب أو صفر"
                )
            
            result = math.log10(num)
            self._increment_count()
            self._log_operation("log10", {"num": num}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=[Step("📊 لوغاريتم عشري", f"log₁₀({num}) = {result}")]
            )
        except Exception as e:
            logger.error(f"Error in log10: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def ln(self, num: float) -> ExecutionResult:
        """قالب 10: لوغاريتم طبيعي"""
        try:
            if num <= 0:
                return ExecutionResult(
                    success=False,
                    error="لا يمكن حساب لوغاريتم لعدد سالب أو صفر"
                )
            
            result = math.log(num)
            self._increment_count()
            self._log_operation("ln", {"num": num}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=[Step("📈 لوغاريتم طبيعي", f"ln({num}) = {result}")]
            )
        except Exception as e:
            logger.error(f"Error in ln: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    # ========== معادلات (10 قوالب) ==========
    
    def solve_linear(self, a: float, b: float) -> ExecutionResult:
        """قالب 11: حل معادلة خطية: ax + b = 0"""
        try:
            if a == 0:
                if b == 0:
                    return ExecutionResult(
                        success=True,
                        result="جميع الأعداد حلول",
                        result_str="جميع الأعداد حلول",
                        steps=[Step("📐 معادلة خطية", "0 = 0: جميع الأعداد حلول")]
                    )
                else:
                    return ExecutionResult(
                        success=False,
                        error="معادلة غير قابلة للحل (0 = قيمة غير صفرية)"
                    )
            
            x = -b / a
            self._increment_count()
            self._log_operation("solve_linear", {"a": a, "b": b}, x)
            
            return ExecutionResult(
                success=True,
                result=x,
                result_str=f"x = {x}",
                steps=[
                    Step("📐 معادلة خطية", f"{a}x + {b} = 0"),
                    Step("✏️ حل", f"x = -{b} / {a} = {x}")
                ]
            )
        except Exception as e:
            logger.error(f"Error in solve_linear: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def solve_quadratic(self, a: float, b: float, c: float) -> ExecutionResult:
        """قالب 12: حل معادلة تربيعية: ax² + bx + c = 0"""
        try:
            if a == 0:
                return self.solve_linear(b, c)
            
            discriminant = b**2 - 4*a*c
            sqrt_d = abs(discriminant) ** 0.5
            
            steps = [
                Step("📐 معادلة تربيعية", f"{a}x² + {b}x + {c} = 0"),
                Step("🔍 حساب المميز", f"Δ = b² - 4ac = {b}² - 4({a})({c}) = {discriminant}")
            ]
            
            if discriminant > 0:
                x1 = (-b + sqrt_d) / (2*a)
                x2 = (-b - sqrt_d) / (2*a)
                result_str = f"x₁ = {x1}, x₂ = {x2}"
                steps.append(Step("✅ حلان حقيقيان", f"x₁ = {x1}, x₂ = {x2}"))
                
                self._log_operation("solve_quadratic", {"a": a, "b": b, "c": c}, (x1, x2))
                return ExecutionResult(
                    success=True,
                    result=(x1, x2),
                    result_str=result_str,
                    steps=steps
                )
            elif discriminant == 0:
                x = -b / (2*a)
                result_str = f"x = {x} (حل مكرر)"
                steps.append(Step("🔁 حل مكرر", f"x = {x}"))
                
                self._log_operation("solve_quadratic", {"a": a, "b": b, "c": c}, x)
                return ExecutionResult(
                    success=True,
                    result=x,
                    result_str=result_str,
                    steps=steps
                )
            else:
                real = -b / (2*a)
                imag = sqrt_d / (2*a)
                result_str = f"x₁ = {real} + {imag}i, x₂ = {real} - {imag}i"
                steps.append(Step("🔮 حلان مركبان", result_str))
                
                self._log_operation("solve_quadratic", {"a": a, "b": b, "c": c}, (complex(real, imag), complex(real, -imag)))
                return ExecutionResult(
                    success=True,
                    result=(complex(real, imag), complex(real, -imag)),
                    result_str=result_str,
                    steps=steps
                )
        except Exception as e:
            logger.error(f"Error in solve_quadratic: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def solve_cubic(self, a: float, b: float, c: float, d: float) -> ExecutionResult:
        """قالب 13: حل معادلة تكعيبية: ax³ + bx² + cx + d = 0"""
        try:
            if a == 0:
                return self.solve_quadratic(b, c, d)
            
            x = sp.Symbol('x')
            expr = a*x**3 + b*x**2 + c*x + d
            solutions = sp.solve(expr, x)
            
            steps = [
                Step("📐 معادلة تكعيبية", f"{a}x³ + {b}x² + {c}x + {d} = 0"),
                Step("🔍 الحلول", f"x = {[str(s) for s in solutions]}")
            ]
            
            self._increment_count()
            self._log_operation("solve_cubic", {"a": a, "b": b, "c": c, "d": d}, solutions)
            
            return ExecutionResult(
                success=True,
                result=solutions,
                result_str=str([str(s) for s in solutions]),
                steps=steps
            )
        except Exception as e:
            logger.error(f"Error in solve_cubic: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def solve_system_2x2(self, a1: float, b1: float, c1: float, a2: float, b2: float, c2: float) -> ExecutionResult:
        """قالب 14: حل نظام معادلتين خطيتين"""
        try:
            det = a1*b2 - a2*b1
            
            if det == 0:
                if a1*c2 == a2*c1 and b1*c2 == b2*c1:
                    return ExecutionResult(
                        success=True,
                        result="عدد لا نهائي من الحلول",
                        result_str="عدد لا نهائي من الحلول",
                        steps=[Step("📐 نظام معادلات", "المعادلتان متطابقتان")]
                    )
                else:
                    return ExecutionResult(
                        success=False,
                        error="النظام غير متوافق (لا يوجد حل)"
                    )
            
            x = (c1*b2 - c2*b1) / det
            y = (a1*c2 - a2*c1) / det
            
            steps = [
                Step("📐 نظام معادلتين", f"{a1}x + {b1}y = {c1}"),
                Step("", f"{a2}x + {b2}y = {c2}"),
                Step("🔍 حساب المحدد الرئيسي", f"Δ = {a1}*{b2} - {a2}*{b1} = {det}"),
                Step("✅ الحل", f"x = {x}, y = {y}")
            ]
            
            self._increment_count()
            self._log_operation("solve_system_2x2", {"a1": a1, "b1": b1, "c1": c1, "a2": a2, "b2": b2, "c2": c2}, (x, y))
            
            return ExecutionResult(
                success=True,
                result=(x, y),
                result_str=f"x = {x}, y = {y}",
                steps=steps
            )
        except Exception as e:
            logger.error(f"Error in solve_system_2x2: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    # ========== مشتقات (10 قوالب) ==========
    
    def derivative(self, expr: sp.Expr, var: sp.Symbol = None) -> ExecutionResult:
        """قالب مشتقة عام"""
        try:
            if var is None:
                var = self.x
            
            result = sp.diff(expr, var)
            simplified = sp.simplify(result)
            
            steps = [
                Step("📐 مشتقة", f"d/d{var} ({expr})"),
                Step("✅ النتيجة", f"= {sp.latex(simplified)}")
            ]
            
            self._increment_count()
            self._log_operation("derivative", {"expr": str(expr), "var": str(var)}, simplified)
            
            return ExecutionResult(
                success=True,
                result=simplified,
                result_str=sp.latex(simplified),
                steps=steps
            )
        except Exception as e:
            logger.error(f"Error in derivative: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def derivative_power(self, n: float) -> ExecutionResult:
        """قالب 16: مشتقة x^n"""
        try:
            expr = self.x ** n
            result = sp.diff(expr, self.x)
            simplified = sp.simplify(result)
            
            self._increment_count()
            self._log_operation("derivative_power", {"n": n}, simplified)
            
            return ExecutionResult(
                success=True,
                result=simplified,
                result_str=sp.latex(simplified),
                steps=[Step("📐 مشتقة قوة", f"d/dx (x^{{{n}}}) = {sp.latex(simplified)}")]
            )
        except Exception as e:
            logger.error(f"Error in derivative_power: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def derivative_sin(self) -> ExecutionResult:
        """قالب 17: مشتقة sin(x)"""
        expr = sp.sin(self.x)
        result = sp.diff(expr, self.x)
        
        self._increment_count()
        self._log_operation("derivative_sin", {}, result)
        
        return ExecutionResult(
            success=True,
            result=result,
            result_str=sp.latex(result),
            steps=[Step("📐 مشتقة جيب", f"d/dx sin(x) = {sp.latex(result)}")]
        )
    
    def derivative_cos(self) -> ExecutionResult:
        """قالب 18: مشتقة cos(x)"""
        expr = sp.cos(self.x)
        result = sp.diff(expr, self.x)
        
        self._increment_count()
        self._log_operation("derivative_cos", {}, result)
        
        return ExecutionResult(
            success=True,
            result=result,
            result_str=sp.latex(result),
            steps=[Step("📐 مشتقة جيب تمام", f"d/dx cos(x) = {sp.latex(result)}")]
        )
    
    def derivative_tan(self) -> ExecutionResult:
        """قالب 19: مشتقة tan(x)"""
        expr = sp.tan(self.x)
        result = sp.diff(expr, self.x)
        
        self._increment_count()
        self._log_operation("derivative_tan", {}, result)
        
        return ExecutionResult(
            success=True,
            result=result,
            result_str=sp.latex(result),
            steps=[Step("📐 مشتقة ظل", f"d/dx tan(x) = {sp.latex(result)}")]
        )
    
    def derivative_exp(self) -> ExecutionResult:
        """قالب 20: مشتقة e^x"""
        expr = sp.exp(self.x)
        result = sp.diff(expr, self.x)
        
        self._increment_count()
        self._log_operation("derivative_exp", {}, result)
        
        return ExecutionResult(
            success=True,
            result=result,
            result_str=sp.latex(result),
            steps=[Step("📐 مشتقة أسية", f"d/dx e^x = {sp.latex(result)}")]
        )
    
    def derivative_ln(self) -> ExecutionResult:
        """قالب 21: مشتقة ln(x)"""
        expr = sp.log(self.x)
        result = sp.diff(expr, self.x)
        
        self._increment_count()
        self._log_operation("derivative_ln", {}, result)
        
        return ExecutionResult(
            success=True,
            result=result,
            result_str=sp.latex(result),
            steps=[Step("📐 مشتقة لوغاريتم", f"d/dx ln(x) = {sp.latex(result)}")]
        )
    
    def derivative_product(self, u: sp.Expr, v: sp.Expr) -> ExecutionResult:
        """قالب 22: مشتقة حاصل ضرب دالتين"""
        try:
            result = sp.diff(u * v, self.x)
            simplified = sp.simplify(result)
            
            steps = [
                Step("📐 قاعدة الضرب", f"d/dx [{u} × {v}]"),
                Step("✅ النتيجة", f"= {sp.latex(simplified)}")
            ]
            
            self._increment_count()
            self._log_operation("derivative_product", {"u": str(u), "v": str(v)}, simplified)
            
            return ExecutionResult(
                success=True,
                result=simplified,
                result_str=sp.latex(simplified),
                steps=steps
            )
        except Exception as e:
            logger.error(f"Error in derivative_product: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def derivative_quotient(self, u: sp.Expr, v: sp.Expr) -> ExecutionResult:
        """قالب 23: مشتقة حاصل قسمة دالتين"""
        try:
            result = sp.diff(u / v, self.x)
            simplified = sp.simplify(result)
            
            steps = [
                Step("📐 قاعدة القسمة", f"d/dx [{u} / {v}]"),
                Step("✅ النتيجة", f"= {sp.latex(simplified)}")
            ]
            
            self._increment_count()
            self._log_operation("derivative_quotient", {"u": str(u), "v": str(v)}, simplified)
            
            return ExecutionResult(
                success=True,
                result=simplified,
                result_str=sp.latex(simplified),
                steps=steps
            )
        except Exception as e:
            logger.error(f"Error in derivative_quotient: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def derivative_chain(self, outer: sp.Expr, inner: sp.Expr, var: sp.Symbol = None) -> ExecutionResult:
        """قالب 24: مشتقة قاعدة السلسلة"""
        try:
            if var is None:
                var = self.x
            
            composed = outer.subs(var, inner)
            result = sp.diff(composed, var)
            simplified = sp.simplify(result)
            
            steps = [
                Step("📐 قاعدة السلسلة", f"d/d{var} {outer}({inner})"),
                Step("✅ النتيجة", f"= {sp.latex(simplified)}")
            ]
            
            self._increment_count()
            self._log_operation("derivative_chain", {"outer": str(outer), "inner": str(inner), "var": str(var)}, simplified)
            
            return ExecutionResult(
                success=True,
                result=simplified,
                result_str=sp.latex(simplified),
                steps=steps
            )
        except Exception as e:
            logger.error(f"Error in derivative_chain: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    # ========== تكاملات (10 قوالب) ==========
    
    def integral(self, expr: sp.Expr, var: sp.Symbol = None) -> ExecutionResult:
        """قالب تكامل عام"""
        try:
            if var is None:
                var = self.x
            
            result = sp.integrate(expr, var)
            
            steps = [
                Step("📦 تكامل", f"∫ {expr} d{var}"),
                Step("✅ النتيجة", f"= {sp.latex(result)} + C")
            ]
            
            self._increment_count()
            self._log_operation("integral", {"expr": str(expr), "var": str(var)}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=sp.latex(result) + " + C",
                steps=steps
            )
        except Exception as e:
            logger.error(f"Error in integral: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def integral_power(self, n: float) -> ExecutionResult:
        """قالب 26: تكامل x^n"""
        try:
            expr = self.x ** n
            result = sp.integrate(expr, self.x)
            
            self._increment_count()
            self._log_operation("integral_power", {"n": n}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=sp.latex(result) + " + C",
                steps=[Step("∫ تكامل قوة", f"∫ x^{{{n}}} dx = {sp.latex(result)} + C")]
            )
        except Exception as e:
            logger.error(f"Error in integral_power: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def integral_sin(self) -> ExecutionResult:
        """قالب 27: تكامل sin(x)"""
        expr = sp.sin(self.x)
        result = sp.integrate(expr, self.x)
        
        self._increment_count()
        self._log_operation("integral_sin", {}, result)
        
        return ExecutionResult(
            success=True,
            result=result,
            result_str=sp.latex(result) + " + C",
            steps=[Step("∫ تكامل جيب", f"∫ sin(x) dx = {sp.latex(result)} + C")]
        )
    
    def integral_cos(self) -> ExecutionResult:
        """قالب 28: تكامل cos(x)"""
        expr = sp.cos(self.x)
        result = sp.integrate(expr, self.x)
        
        self._increment_count()
        self._log_operation("integral_cos", {}, result)
        
        return ExecutionResult(
            success=True,
            result=result,
            result_str=sp.latex(result) + " + C",
            steps=[Step("∫ تكامل جيب تمام", f"∫ cos(x) dx = {sp.latex(result)} + C")]
        )
    
    def integral_exp(self) -> ExecutionResult:
        """قالب 29: تكامل e^x"""
        expr = sp.exp(self.x)
        result = sp.integrate(expr, self.x)
        
        self._increment_count()
        self._log_operation("integral_exp", {}, result)
        
        return ExecutionResult(
            success=True,
            result=result,
            result_str=sp.latex(result) + " + C",
            steps=[Step("∫ تكامل أسية", f"∫ e^x dx = {sp.latex(result)} + C")]
        )
    
    def integral_ln(self) -> ExecutionResult:
        """قالب 30: تكامل ln(x)"""
        expr = sp.log(self.x)
        result = sp.integrate(expr, self.x)
        
        self._increment_count()
        self._log_operation("integral_ln", {}, result)
        
        return ExecutionResult(
            success=True,
            result=result,
            result_str=sp.latex(result) + " + C",
            steps=[Step("∫ تكامل لوغاريتم", f"∫ ln(x) dx = {sp.latex(result)} + C")]
        )
    
    def integral_definite(self, expr: sp.Expr, lower: float, upper: Union[float, str], var: sp.Symbol = None) -> ExecutionResult:
        """قالب 31: تكامل محدد"""
        try:
            if var is None:
                var = self.x
            
            if isinstance(upper, str) and upper in ['∞', 'infinity']:
                upper_val = sp.oo
            else:
                upper_val = float(upper)
            
            lower_val = float(lower)
            
            result = sp.integrate(expr, (var, lower_val, upper_val))
            
            steps = [
                Step("📦 تكامل محدد", f"∫_{lower}^{upper} {expr} d{var}"),
                Step("✅ النتيجة", f"= {sp.latex(result)}")
            ]
            
            try:
                float_val = float(result.evalf())
                if result != float_val:
                    steps.append(Step("📊 قيمة تقريبية", f"≈ {float_val:.6f}"))
            except:
                pass
            
            self._increment_count()
            self._log_operation("integral_definite", {"expr": str(expr), "lower": lower, "upper": upper}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=sp.latex(result),
                steps=steps
            )
        except Exception as e:
            logger.error(f"Error in integral_definite: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def integral_substitution(self, func: sp.Expr) -> ExecutionResult:
        """قالب 34: تكامل بالتعويض (تلقائي)"""
        try:
            result = sp.integrate(func, self.x)
            
            self._increment_count()
            self._log_operation("integral_substitution", {"func": str(func)}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=sp.latex(result) + " + C",
                steps=[
                    Step("🔄 تكامل بالتعويض", f"∫ {func} dx"),
                    Step("✅ النتيجة", f"= {sp.latex(result)} + C")
                ]
            )
        except Exception as e:
            logger.error(f"Error in integral_substitution: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def integral_by_parts(self, u: sp.Expr, dv: sp.Expr) -> ExecutionResult:
        """قالب 33: تكامل بالأجزاء"""
        try:
            v = sp.integrate(dv, self.x)
            du = sp.diff(u, self.x)
            result = u * v - sp.integrate(v * du, self.x)
            
            steps = [
                Step("📦 تكامل بالأجزاء", f"نختار u = {u}, dv = {dv} dx"),
                Step("📝 نحسب v", f"v = ∫ {dv} dx = {sp.latex(v)}"),
                Step("📝 نحسب du", f"du = d/dx ({u}) dx = {sp.latex(du)} dx"),
                Step("✅ النتيجة", f"∫ u dv = uv - ∫ v du = {sp.latex(result)} + C")
            ]
            
            self._increment_count()
            self._log_operation("integral_by_parts", {"u": str(u), "dv": str(dv)}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=sp.latex(result) + " + C",
                steps=steps
            )
        except Exception as e:
            logger.error(f"Error in integral_by_parts: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    # ========== مصفوفات (7 قوالب) ==========
    
    def matrix_determinant(self, matrix: List[List[float]]) -> ExecutionResult:
        """قالب 41: محدد مصفوفة"""
        try:
            if len(matrix) > MAX_MATRIX_SIZE:
                return ExecutionResult(
                    success=False,
                    error=f"حجم المصفوفة كبير جداً. الحد الأقصى {MAX_MATRIX_SIZE}x{MAX_MATRIX_SIZE}"
                )
            
            M = sp.Matrix(matrix)
            result = M.det()
            
            steps = [
                Step("📊 مصفوفة", f"{M}"),
                Step("🔍 المحدد", f"det = {result}")
            ]
            
            self._increment_count()
            self._log_operation("matrix_determinant", {"matrix": matrix}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps
            )
        except Exception as e:
            logger.error(f"Error in matrix_determinant: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def matrix_inverse(self, matrix: List[List[float]]) -> ExecutionResult:
        """قالب 42: معكوس مصفوفة"""
        try:
            if len(matrix) > MAX_MATRIX_SIZE:
                return ExecutionResult(
                    success=False,
                    error=f"حجم المصفوفة كبير جداً. الحد الأقصى {MAX_MATRIX_SIZE}x{MAX_MATRIX_SIZE}"
                )
            
            M = sp.Matrix(matrix)
            
            if not M.is_invertible():
                return ExecutionResult(
                    success=False,
                    error="المصفوفة غير قابلة للعكس (محددها صفر أو غير قابلة للعكس)"
                )
            
            result = M.inv()
            
            steps = [
                Step("📊 مصفوفة", f"{M}"),
                Step("🔄 المعكوس", f"M⁻¹ = {result}")
            ]
            
            self._increment_count()
            self._log_operation("matrix_inverse", {"matrix": matrix}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps
            )
        except Exception as e:
            logger.error(f"Error in matrix_inverse: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def matrix_transpose(self, matrix: List[List[float]]) -> ExecutionResult:
        """قالب 43: مدور مصفوفة"""
        try:
            if len(matrix) > MAX_MATRIX_SIZE:
                return ExecutionResult(
                    success=False,
                    error=f"حجم المصفوفة كبير جداً. الحد الأقصى {MAX_MATRIX_SIZE}x{MAX_MATRIX_SIZE}"
                )
            
            M = sp.Matrix(matrix)
            result = M.T
            
            steps = [
                Step("📊 مصفوفة", f"{M}"),
                Step("🔄 المدور", f"Mᵀ = {result}")
            ]
            
            self._increment_count()
            self._log_operation("matrix_transpose", {"matrix": matrix}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps
            )
        except Exception as e:
            logger.error(f"Error in matrix_transpose: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def matrix_multiply(self, A: List[List[float]], B: List[List[float]]) -> ExecutionResult:
        """قالب 44: ضرب مصفوفتين"""
        try:
            if len(A) > MAX_MATRIX_SIZE or len(B) > MAX_MATRIX_SIZE:
                return ExecutionResult(
                    success=False,
                    error=f"حجم المصفوفة كبير جداً. الحد الأقصى {MAX_MATRIX_SIZE}x{MAX_MATRIX_SIZE}"
                )
            
            M1 = sp.Matrix(A)
            M2 = sp.Matrix(B)
            
            if M1.shape[1] != M2.shape[0]:
                return ExecutionResult(
                    success=False,
                    error=f"أبعاد المصفوفتين غير متوافقة للضرب: {M1.shape} و {M2.shape}"
                )
            
            result = M1 * M2
            
            steps = [
                Step("📊 المصفوفة الأولى", f"{M1}"),
                Step("📊 المصفوفة الثانية", f"{M2}"),
                Step("✖️ حاصل الضرب", f"M1 × M2 = {result}")
            ]
            
            self._increment_count()
            self._log_operation("matrix_multiply", {"A": A, "B": B}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps
            )
        except Exception as e:
            logger.error(f"Error in matrix_multiply: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def matrix_add(self, A: List[List[float]], B: List[List[float]]) -> ExecutionResult:
        """جمع مصفوفتين"""
        try:
            if len(A) > MAX_MATRIX_SIZE or len(B) > MAX_MATRIX_SIZE:
                return ExecutionResult(
                    success=False,
                    error=f"حجم المصفوفة كبير جداً. الحد الأقصى {MAX_MATRIX_SIZE}x{MAX_MATRIX_SIZE}"
                )
            
            M1 = sp.Matrix(A)
            M2 = sp.Matrix(B)
            
            if M1.shape != M2.shape:
                return ExecutionResult(
                    success=False,
                    error=f"أبعاد المصفوفتين غير متطابقة للجمع: {M1.shape} و {M2.shape}"
                )
            
            result = M1 + M2
            
            steps = [
                Step("📊 المصفوفة الأولى", f"{M1}"),
                Step("📊 المصفوفة الثانية", f"{M2}"),
                Step("➕ ناتج الجمع", f"M1 + M2 = {result}")
            ]
            
            self._increment_count()
            self._log_operation("matrix_add", {"A": A, "B": B}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps
            )
        except Exception as e:
            logger.error(f"Error in matrix_add: {e}")
            return ExecutionResult(success=False, error=str(e))

    def matrix_subtract(self, A: List[List[float]], B: List[List[float]]) -> ExecutionResult:
        """طرح مصفوفتين"""
        try:
            if len(A) > MAX_MATRIX_SIZE or len(B) > MAX_MATRIX_SIZE:
                return ExecutionResult(
                    success=False,
                    error=f"حجم المصفوفة كبير جداً. الحد الأقصى {MAX_MATRIX_SIZE}x{MAX_MATRIX_SIZE}"
                )
            
            M1 = sp.Matrix(A)
            M2 = sp.Matrix(B)
            
            if M1.shape != M2.shape:
                return ExecutionResult(
                    success=False,
                    error=f"أبعاد المصفوفتين غير متطابقة للطرح: {M1.shape} و {M2.shape}"
                )
            
            result = M1 - M2
            
            steps = [
                Step("📊 المصفوفة الأولى", f"{M1}"),
                Step("📊 المصفوفة الثانية", f"{M2}"),
                Step("➖ ناتج الطرح", f"M1 - M2 = {result}")
            ]
            
            self._increment_count()
            self._log_operation("matrix_subtract", {"A": A, "B": B}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=steps
            )
        except Exception as e:
            logger.error(f"Error in matrix_subtract: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def matrix_eigenvalues(self, matrix: List[List[float]]) -> ExecutionResult:
        """قالب 45: القيم الذاتية لمصفوفة"""
        try:
            if len(matrix) > MAX_MATRIX_SIZE:
                return ExecutionResult(
                    success=False,
                    error=f"حجم المصفوفة كبير جداً. الحد الأقصى {MAX_MATRIX_SIZE}x{MAX_MATRIX_SIZE}"
                )
            
            M = sp.Matrix(matrix)
            
            if M.rows != M.cols:
                return ExecutionResult(
                    success=False,
                    error="القيم الذاتية معرفة فقط للمصفوفات المربعة"
                )
            
            eigenvals = M.eigenvals()
            
            steps = [
                Step("📊 مصفوفة", f"{M}"),
                Step("🔍 القيم الذاتية", f"λ = {list(eigenvals.keys())}")
            ]
            
            self._increment_count()
            self._log_operation("matrix_eigenvalues", {"matrix": matrix}, eigenvals)
            
            return ExecutionResult(
                success=True,
                result=eigenvals,
                result_str=str(list(eigenvals.keys())),
                steps=steps
            )
        except Exception as e:
            logger.error(f"Error in matrix_eigenvalues: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    # ========== نهايات (5 قوالب) ==========
    
    def limit(self, expr: sp.Expr, var: sp.Symbol, approach: Union[float, str]) -> ExecutionResult:
        """قالب 46: نهاية دالة"""
        try:
            if isinstance(approach, str):
                if approach in ['∞', 'infinity']:
                    approach_val = sp.oo
                elif approach in ['-∞', '-infinity']:
                    approach_val = -sp.oo
                else:
                    approach_val = float(approach)
            else:
                approach_val = approach
            
            result = sp.limit(expr, var, approach_val)
            
            steps = [
                Step("📈 نهاية", f"lim_{{{var}→{approach}}} ({expr})"),
                Step("✅ النتيجة", f"= {sp.latex(result)}")
            ]
            
            self._increment_count()
            self._log_operation("limit", {"expr": str(expr), "var": str(var), "approach": approach}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=sp.latex(result),
                steps=steps
            )
        except Exception as e:
            logger.error(f"Error in limit: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    # ========== مثلثات (5 قوالب) ==========
    
    def sin(self, angle: float, unit: str = "deg") -> ExecutionResult:
        """قالب 51: جيب الزاوية"""
        try:
            if unit == "deg":
                rad = math.radians(angle)
            else:
                rad = angle
            
            result = math.sin(rad)
            
            self._increment_count()
            self._log_operation("sin", {"angle": angle, "unit": unit}, result)
            
            unit_str = "°" if unit == "deg" else " rad"
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=[Step("📐 sin", f"sin({angle}{unit_str}) = {result:.6f}")]
            )
        except Exception as e:
            logger.error(f"Error in sin: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def cos(self, angle: float, unit: str = "deg") -> ExecutionResult:
        """قالب 52: جيب تمام"""
        try:
            if unit == "deg":
                rad = math.radians(angle)
            else:
                rad = angle
            
            result = math.cos(rad)
            
            self._increment_count()
            self._log_operation("cos", {"angle": angle, "unit": unit}, result)
            
            unit_str = "°" if unit == "deg" else " rad"
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=[Step("📐 cos", f"cos({angle}{unit_str}) = {result:.6f}")]
            )
        except Exception as e:
            logger.error(f"Error in cos: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def tan(self, angle: float, unit: str = "deg") -> ExecutionResult:
        """قالب 53: ظل الزاوية"""
        try:
            if unit == "deg":
                rad = math.radians(angle)
            else:
                rad = angle
            
            result = math.tan(rad)
            
            self._increment_count()
            self._log_operation("tan", {"angle": angle, "unit": unit}, result)
            
            unit_str = "°" if unit == "deg" else " rad"
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=[Step("📐 tan", f"tan({angle}{unit_str}) = {result:.6f}")]
            )
        except Exception as e:
            logger.error(f"Error in tan: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def law_of_sines(self, a: float, A: float, b: float, unit: str = "deg") -> ExecutionResult:
        """قالب 54: قانون الجيب"""
        try:
            if unit == "deg":
                A_rad = math.radians(A)
                unit_str = "°"
            else:
                A_rad = A
                unit_str = " rad"
            
            sinA = math.sin(A_rad)
            sinB = (b * sinA) / a
            
            if not self._validate_angle_for_asin(sinB):
                return ExecutionResult(
                    success=False,
                    error="لا يوجد حل - قيمة خارج نطاق arcsin"
                )
            
            B_rad = math.asin(sinB)
            
            if unit == "deg":
                B = math.degrees(B_rad)
            else:
                B = B_rad
            
            self._increment_count()
            self._log_operation("law_of_sines", {"a": a, "A": A, "b": b, "unit": unit}, B)
            
            return ExecutionResult(
                success=True,
                result=B,
                result_str=f"{B}{unit_str}",
                steps=[
                    Step("📐 قانون الجيب", f"a/sin(A) = b/sin(B)"),
                    Step("🔍 الحساب", f"sin(B) = (b × sin(A)) / a = ({b} × {sinA:.4f}) / {a} = {sinB:.4f}"),
                    Step("✅ النتيجة", f"B = {B:.4f}{unit_str}")
                ]
            )
        except Exception as e:
            logger.error(f"Error in law_of_sines: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def law_of_cosines(self, a: float, b: float, C: float, unit: str = "deg") -> ExecutionResult:
        """قالب 55: قانون جيب التمام"""
        try:
            unit_str = "°" if unit == "deg" else " rad"
            
            if unit == "deg":
                C_rad = math.radians(C)
            else:
                C_rad = C
            
            cosC = math.cos(C_rad)
            c_squared = a**2 + b**2 - 2*a*b*cosC
            
            steps = [
                Step("📐 قانون جيب التمام", f"c² = {a}² + {b}² - 2({a})({b}) cos({C}{unit_str})"),
                Step("🔍 الحساب", f"c² = {a**2:.4f} + {b**2:.4f} - 2({a})({b}) × {cosC:.4f} = {c_squared:.4f}")
            ]
            
            c = math.sqrt(max(c_squared, 0))
            
            if c_squared < 0:
                steps.append(Step("⚠️ تنبيه", f"c² كانت سالبة ({c_squared:.6f})، تم استخدام max(c², 0)"))
            
            steps.append(Step("✅ النتيجة", f"c = {c:.6f}"))
            
            self._increment_count()
            self._log_operation("law_of_cosines", {"a": a, "b": b, "C": C, "unit": unit}, c)
            
            return ExecutionResult(
                success=True,
                result=c,
                result_str=str(c),
                steps=steps
            )
        except Exception as e:
            logger.error(f"Error in law_of_cosines: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    # ========== إحصاء (5 قوالب) ==========
    
    def mean(self, data: List[float]) -> ExecutionResult:
        """قالب 56: المتوسط الحسابي"""
        try:
            if not data:
                return ExecutionResult(success=False, error="لا توجد بيانات")
            
            result = _calculate_mean(data)
            
            self._increment_count()
            self._log_operation("mean", {"data": data[:5]}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=[Step("📊 متوسط", f"المتوسط = {result:.6f}")]
            )
        except Exception as e:
            logger.error(f"Error in mean: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def median(self, data: List[float]) -> ExecutionResult:
        """قالب 57: الوسيط"""
        try:
            if not data:
                return ExecutionResult(success=False, error="لا توجد بيانات")
            
            sorted_data = sorted(data)
            n = len(sorted_data)
            
            if n % 2 == 1:
                result = sorted_data[n // 2]
            else:
                result = (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
            
            self._increment_count()
            self._log_operation("median", {"data": data[:5]}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=[Step("📊 وسيط", f"الوسيط = {result:.6f}")]
            )
        except Exception as e:
            logger.error(f"Error in median: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def variance(self, data: List[float], sample: bool = True) -> ExecutionResult:
        """قالب 58: التباين"""
        try:
            if not data or len(data) < 2:
                return ExecutionResult(success=False, error="البيانات غير كافية لحساب التباين")
            
            mean_val = _calculate_mean(data)
            result = _calculate_variance(data, mean_val, sample)
            
            variance_type = "العيني" if sample else "المجتمعي"
            
            self._increment_count()
            self._log_operation("variance", {"data": data[:5], "sample": sample}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=[
                    Step("📊 متوسط", f"μ = {mean_val:.6f}"),
                    Step(f"📊 تباين {variance_type}", f"σ² = {result:.6f}")
                ]
            )
        except Exception as e:
            logger.error(f"Error in variance: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def std_dev(self, data: List[float], sample: bool = True) -> ExecutionResult:
        """قالب 59: الانحراف المعياري"""
        try:
            if not data or len(data) < 2:
                return ExecutionResult(success=False, error="البيانات غير كافية لحساب الانحراف المعياري")
            
            mean_val = _calculate_mean(data)
            variance = _calculate_variance(data, mean_val, sample)
            result = variance ** 0.5
            
            std_type = "العياري" if sample else "المجتمعي"
            
            self._increment_count()
            self._log_operation("std_dev", {"data": data[:5], "sample": sample}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=[
                    Step("📊 متوسط", f"μ = {mean_val:.6f}"),
                    Step("📊 تباين", f"σ² = {variance:.6f}"),
                    Step(f"📊 انحراف معياري {std_type}", f"σ = {result:.6f}")
                ]
            )
        except Exception as e:
            logger.error(f"Error in std_dev: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    def correlation(self, data1: List[float], data2: List[float]) -> ExecutionResult:
        """قالب 60: معامل ارتباط بيرسون"""
        try:
            if len(data1) != len(data2) or len(data1) < 2:
                return ExecutionResult(success=False, error="البيانات غير صالحة لحساب الارتباط")
            
            n = len(data1)
            mean1 = _calculate_mean(data1)
            mean2 = _calculate_mean(data2)
            
            covariance = sum((data1[i] - mean1) * (data2[i] - mean2) for i in range(n)) / (n - 1)
            
            std1 = _calculate_std_dev(data1, mean1, sample=True)
            std2 = _calculate_std_dev(data2, mean2, sample=True)
            
            if std1 == 0 or std2 == 0:
                return ExecutionResult(success=False, error="لا يمكن حساب الارتباط (أحد المتغيرات ثابت)")
            
            result = covariance / (std1 * std2)
            
            abs_r = abs(result)
            if abs_r > 0.9:
                interpretation = "قوية جداً"
            elif abs_r > 0.7:
                interpretation = "قوية"
            elif abs_r > 0.5:
                interpretation = "متوسطة"
            elif abs_r > 0.3:
                interpretation = "ضعيفة"
            else:
                interpretation = "ضعيفة جداً"
            
            self._increment_count()
            self._log_operation("correlation", {}, result)
            
            return ExecutionResult(
                success=True,
                result=result,
                result_str=f"{result:.6f}",
                steps=[
                    Step("📊 معامل الارتباط (بيرسون)", f"r = {result:.6f}"),
                    Step("📝 تفسير", f"قوة العلاقة: {interpretation}" + 
                         (" (طردية)" if result > 0 else " (عكسية)" if result < 0 else ""))
                ]
            )
        except Exception as e:
            logger.error(f"Error in correlation: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    # ========== سجل العمليات وإحصائيات ==========
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """الحصول على آخر العمليات"""
        return self.history[-limit:]
    
    def clear_history(self):
        """مسح سجل العمليات"""
        self.history.clear()
        logger.info("History cleared")
    
    def get_stats(self):
        """الحصول على إحصائيات المحرك"""
        return {
            "execution_count": self.execution_count,
            "status": "ready",
            "history_size": len(self.history)
        }
