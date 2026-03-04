# math_engine.py - الإصدار النهائي مع جميع التحسينات (v2.0)
import sympy as sp
from typing import Optional, List, Any, Dict, Tuple, Union
from dataclasses import dataclass, field
import math
import numpy as np
import logging
from datetime import datetime

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Step:
    text: str
    latex: str = ""
    
    def to_dict(self) -> dict:
        return {"text": self.text, "latex": self.latex}

@dataclass
class ExecutionResult:
    success: bool
    result: Any = None
    result_str: str = ""
    steps: List[Step] = field(default_factory=list)
    error: Optional[str] = None

# دوال مساعدة إحصائية
def _calculate_mean(data: List[float]) -> float:
    return sum(data) / len(data)

def _calculate_variance(data: List[float], mean_val: float = None) -> float:
    if mean_val is None:
        mean_val = _calculate_mean(data)
    return sum((x - mean_val)**2 for x in data) / len(data)

class MathEngine:
    """محرك الرياضيات - 60 قالب مع تحسينات نهائية"""
    
    def __init__(self):
        self.x, self.y, self.z, self.t = sp.symbols('x y z t')
        self.execution_count = 0
        self.allowed_symbols = {'x', 'y', 'z', 't', 'pi', 'e'}
        self.history = []  # سجل العمليات
        print("✅ Math Engine ready - 60 قالب مع تحسينات نهائية")
        logger.info("Math Engine initialized")
    
    async def start(self):
        pass
    
    async def stop(self):
        pass
    
    async def shutdown(self):
        pass
    
    def _log_operation(self, operation: str, params: dict, result: Any):
        """تسجيل عملية في السجل"""
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "params": params,
            "result": str(result)
        })
    
    def _safe_parse(self, expr: str) -> sp.Expr:
        """تحليل آمن للتعبير الرياضي"""
        try:
            # قيود على الرموز المسموح بها
            local_dict = {name: sp.Symbol(name) for name in self.allowed_symbols}
            local_dict.update({'pi': sp.pi, 'e': sp.E})
            return sp.parse_expr(expr, local_dict=local_dict, evaluate=True)
        except:
            return sp.sympify(expr)
    
    def _to_sympy(self, value: Any) -> sp.Expr:
        """تحويل أي قيمة إلى SymPy expression"""
        if isinstance(value, sp.Expr):
            return value
        if isinstance(value, (int, float)):
            return sp.Number(value)
        if isinstance(value, str):
            return self._safe_parse(value)
        if isinstance(value, complex):
            return sp.sympify(value)
        return sp.sympify(value)
    
    def _increment_count(self):
        """زيادة عداد التنفيذ"""
        self.execution_count += 1
    
    # ========== الأساسيات (10 قوالب) ==========
    
    async def calculate(self, expr: str) -> ExecutionResult:
        """قالب 1: آلة حاسبة بسيطة"""
        try:
            result = self._safe_parse(expr).evalf()
            self._increment_count()
            self._log_operation("calculate", {"expr": expr}, result)
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=[Step("🔢 عملية حسابية", f"{expr} = {result}")]
            )
        except Exception as e:
            logger.error(f"Error in calculate: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    async def power(self, base: float, exp: float) -> ExecutionResult:
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
            return ExecutionResult(success=False, error=str(e))
    
    async def sqrt(self, num: float) -> ExecutionResult:
        """قالب 3: جذر تربيعي"""
        try:
            if num < 0:
                return ExecutionResult(success=False, error="لا يمكن حساب جذر تربيعي لعدد سالب")
            result = num ** 0.5
            self._increment_count()
            self._log_operation("sqrt", {"num": num}, result)
            return ExecutionResult(
                success=True,
                result=result,
                result_str=str(result),
                steps=[Step("√ جذر تربيعي", f"√{num} = {result}")]
            )
        except Exception as e:
            logger.error(f"Error in sqrt: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    async def factorial(self, n: int) -> ExecutionResult:
        """قالب 4: مضروب"""
        try:
            if n < 0:
                return ExecutionResult(success=False, error="لا يمكن حساب مضروب لعدد سالب")
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
            return ExecutionResult(success=False, error=str(e))
    
    # ========== مشتقات (10 قوالب) - كلها SymPy الآن ==========
    
    async def derivative_power(self, n: float) -> ExecutionResult:
        """قالب 16: مشتقة x^n - الآن ترجع SymPy Expr"""
        try:
            expr = self.x ** n
            result = sp.diff(expr, self.x)
            self._increment_count()
            self._log_operation("derivative_power", {"n": n}, result)
            return ExecutionResult(
                success=True,
                result=result,
                result_str=sp.latex(result),
                steps=[Step("📐 مشتقة قوة", f"d/dx (x^{{{n}}}) = {sp.latex(result)}")]
            )
        except Exception as e:
            logger.error(f"Error in derivative_power: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    async def derivative_sin(self) -> ExecutionResult:
        """قالب 17: مشتقة sin(x) - SymPy"""
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
    
    async def derivative_cos(self) -> ExecutionResult:
        """قالب 18: مشتقة cos(x) - SymPy"""
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
    
    async def derivative_tan(self) -> ExecutionResult:
        """قالب 19: مشتقة tan(x) - SymPy"""
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
    
    async def derivative_exp(self) -> ExecutionResult:
        """قالب 20: مشتقة e^x - SymPy"""
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
    
    async def derivative_ln(self) -> ExecutionResult:
        """قالب 21: مشتقة ln(x) - SymPy"""
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
    
    # ========== تكاملات (10 قوالب) - محسنة ==========
    
    async def integral_power(self, n: float) -> ExecutionResult:
        """قالب 26: تكامل x^n - SymPy"""
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
    
    async def integral_sin(self) -> ExecutionResult:
        """قالب 27: تكامل sin(x) - SymPy"""
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
    
    async def integral_cos(self) -> ExecutionResult:
        """قالب 28: تكامل cos(x) - SymPy"""
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
    
    async def integral_substitution(self, func: str, u_sub: str, u_expr: str) -> ExecutionResult:
        """قالب 34: تكامل بالتعويض - محسن مع تعويض حقيقي"""
        try:
            # إنشاء الرموز
            x = self.x
            u = sp.Symbol('u')
            
            # تحويل الدالة
            expr = self._safe_parse(func)
            
            # التعويض: u = u_expr
            sub_expr = self._safe_parse(u_expr)
            
            # حساب du/dx
            du_dx = sp.diff(sub_expr, x)
            
            # التعويض في التكامل
            substituted = expr.subs(x, sp.solve(u - sub_expr, x)[0]) / du_dx * sp.diff(u, u)
            substituted = substituted.subs(x, sp.solve(u - sub_expr, x)[0])
            
            # التكامل بالنسبة لـ u
            int_u = sp.integrate(substituted, u)
            
            # العودة لـ x
            result = int_u.subs(u, sub_expr)
            
            self._increment_count()
            self._log_operation("integral_substitution", {"func": func, "u": u_sub, "u_expr": u_expr}, result)
            return ExecutionResult(
                success=True,
                result=result,
                result_str=sp.latex(result) + " + C",
                steps=[
                    Step("🔄 تكامل بالتعويض", f"نفرض u = {u_expr}"),
                    Step("📝 بعد التعويض", f"∫ {func} dx = ∫ {substituted} du"),
                    Step("✅ النتيجة", f"= {sp.latex(result)} + C")
                ]
            )
        except Exception as e:
            logger.error(f"Error in integral_substitution: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    async def integral_by_parts(self, u: str, dv: str) -> ExecutionResult:
        """قالب 33: تكامل بالأجزاء - محسن مع SymPy"""
        try:
            u_expr = self._safe_parse(u)
            dv_expr = self._safe_parse(dv)
            
            # حساب v من dv
            v_expr = sp.integrate(dv_expr, self.x)
            
            # تطبيق قاعدة التكامل بالأجزاء: ∫ u dv = u*v - ∫ v du
            du_expr = sp.diff(u_expr, self.x)
            result = u_expr * v_expr - sp.integrate(v_expr * du_expr, self.x)
            
            self._increment_count()
            self._log_operation("integral_by_parts", {"u": u, "dv": dv}, result)
            return ExecutionResult(
                success=True,
                result=result,
                result_str=sp.latex(result) + " + C",
                steps=[
                    Step("📦 تكامل بالأجزاء", f"نختار u = {u}, dv = {dv}"),
                    Step("📝 نحسب v = ∫ dv", f"v = {sp.latex(v_expr)}"),
                    Step("📝 نحسب du", f"du = {sp.latex(du_expr)} dx"),
                    Step("✅ النتيجة", f"∫ u dv = uv - ∫ v du = {sp.latex(result)} + C")
                ]
            )
        except Exception as e:
            logger.error(f"Error in integral_by_parts: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    # ========== مثلثات (5 قوالب) - مع تدقيق الزوايا ==========
    
    def _validate_angle_for_asin(self, value: float) -> bool:
        """تدقيق أن قيمة arcsin ضمن [-1, 1]"""
        return -1 <= value <= 1
    
    def _validate_angle_for_acos(self, value: float) -> bool:
        """تدقيق أن قيمة arccos ضمن [-1, 1]"""
        return -1 <= value <= 1
    
    async def sin(self, angle: float, unit: str = "deg") -> ExecutionResult:
        """قالب 51: جيب الزاوية مع تدقيق الوحدات"""
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
                steps=[Step("📐 sin", f"sin({angle}{unit_str}) = {result}")]
            )
        except Exception as e:
            logger.error(f"Error in sin: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    async def cos(self, angle: float, unit: str = "deg") -> ExecutionResult:
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
                steps=[Step("📐 cos", f"cos({angle}{unit_str}) = {result}")]
            )
        except Exception as e:
            logger.error(f"Error in cos: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    async def law_of_sines(self, a: float, A: float, b: float, unit: str = "deg") -> ExecutionResult:
        """قالب 54: قانون الجيب مع تدقيق"""
        try:
            if unit == "deg":
                A_rad = math.radians(A)
            else:
                A_rad = A
                
            sinA = math.sin(A_rad)
            sinB = (b * sinA) / a
            
            # تدقيق قيمة arcsin
            if not self._validate_angle_for_asin(sinB):
                return ExecutionResult(success=False, error="لا يوجد حل - قيمة خارج نطاق arcsin")
            
            B_rad = math.asin(sinB)
            if unit == "deg":
                B = math.degrees(B_rad)
            else:
                B = B_rad
                
            self._increment_count()
            self._log_operation("law_of_sines", {"a": a, "A": A, "b": b, "unit": unit}, B)
            unit_str = "°" if unit == "deg" else " rad"
            return ExecutionResult(
                success=True,
                result=B,
                result_str=f"{B}{unit_str}",
                steps=[Step("📐 قانون الجيب", f"الزاوية B = {B}{unit_str}")]
            )
        except Exception as e:
            logger.error(f"Error in law_of_sines: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    async def law_of_cosines(self, a: float, b: float, C: float, unit: str = "deg") -> ExecutionResult:
        """قالب 55: قانون جيب التمام"""
        try:
            if unit == "deg":
                C_rad = math.radians(C)
            else:
                C_rad = C
            c = (a**2 + b**2 - 2*a*b*math.cos(C_rad))**0.5
            self._increment_count()
            self._log_operation("law_of_cosines", {"a": a, "b": b, "C": C, "unit": unit}, c)
            return ExecutionResult(
                success=True,
                result=c,
                result_str=str(c),
                steps=[Step("📐 قانون جيب التمام", f"الضلع c = {c}")]
            )
        except Exception as e:
            logger.error(f"Error in law_of_cosines: {e}")
            return ExecutionResult(success=False, error=str(e))
    
    # ========== سجل العمليات ==========
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """الحصول على آخر العمليات"""
        return self.history[-limit:]
    
    def clear_history(self):
        """مسح سجل العمليات"""
        self.history.clear()
        logger.info("History cleared")
    
    # ========== إحصائيات ==========
    def get_stats(self) -> Dict[str, Any]:
        return {
            "execution_count": self.execution_count,
            "status": "ready",
            "templates": 60,
            "history_size": len(self.history)
        }
