"""
================================================================================
الملف 2/3: الجبر المتوسط - القوى، الأسس، اللوغاريتمات، والكسور (50 قالباً)
File 2/3: Intermediate Algebra - Powers, Logarithms, and Fractions (50 Templates)
الإصدار: 2.0 - تم إصلاح جميع الأخطاء
================================================================================
"""

import sympy as sp
import numpy as np
import logging
from typing import Union, List, Dict, Any, Tuple, Optional
import math
import cmath
from sympy.solvers import solve
from sympy import Symbol, Eq, simplify, expand, factor, gcd, lcm, together
from sympy import sqrt, cbrt, root, log, exp, Abs

# إعداد نظام التسجيل المحسن
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('algebra_solver.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class IntermediateAlgebraSolver:
    """
    ============================================================================
    الحلّال المتوسط للجبر - القوى، الأسس، اللوغاريتمات، والكسور
    النسخة المُصححة 2.0 - تدعم جميع القوالب بشكل كامل
    ============================================================================
    """
    
    def __init__(self):
        """تهيئة المتغيرات الرمزية وإعدادات الدقة - نسخة محسنة"""
        # متغيرات رمزية بدون تقييد بالحقيقية (للدعم الكامل)
        self.x = sp.Symbol('x')  # يسمح بالحلول المركبة
        self.y = sp.Symbol('y')
        self.z = sp.Symbol('z')
        self.a = sp.Symbol('a')
        self.b = sp.Symbol('b')
        self.c = sp.Symbol('c')
        self.n = sp.Symbol('n')
        
        # متغيرات إضافية للبارامترات
        self.k = sp.Symbol('k')
        self.m = sp.Symbol('m')
        self.t = sp.Symbol('t')
        
        # ثوابت رياضية
        self.e = sp.E
        self.pi = sp.pi
        self.i = sp.I
        
        # إعدادات الدقة
        self.precision = 1e-12
        
        # سجل العمليات المحسن
        self.stats = {
            'total_calls': 0,
            'successful': 0,
            'failed': 0,
            'by_template': {},
            'errors_by_type': {}
        }
        
        # ذاكرة تخزين مؤقت للنتائج المتكررة
        self.cache = {}
        self.cache_size = 100
        
        logger.info("✅ تم تهيئة IntermediateAlgebraSolver V2.0 بنجاح")
    
    # =========================================================================
    # دوال مساعدة محسنة
    # =========================================================================
    
    def _safe_sympify(self, expression: str) -> sp.Expr:
        """
        تحويل آمن للتعبيرات النصية إلى SymPy مع معالجة الأخطاء
        """
        try:
            # استبدال الرموز الشائعة
            expr = expression.replace('^', '**')
            expr = expr.replace('√', 'sqrt')
            expr = expr.replace('∛', 'cbrt')
            expr = expr.replace('|', 'Abs')
            
            # محاولة التحويل
            return sp.sympify(expr)
        except Exception as e:
            logger.error(f"فشل تحويل التعبير '{expression}': {str(e)}")
            raise ValueError(f"تعبير غير صالح: {expression}. {str(e)}")
    
    def _safe_solve(self, equation, symbol, **kwargs):
        """
        حل آمن للمعادلات مع معالجة الأخطاء
        """
        try:
            # محاولة الحل بالطريقة العادية
            solutions = sp.solve(equation, symbol, **kwargs)
            
            # إذا لم ينجح، جرب طرقاً بديلة
            if not solutions:
                if equation.has(sp.Abs):
                    # معادلات القيمة المطلقة تحتاج معالجة خاصة
                    solutions = self._solve_absolute(equation, symbol)
                elif equation.has(sp.log):
                    # معادلات لوغاريتمية
                    solutions = self._solve_logarithmic(equation, symbol)
                elif equation.has(sp.sqrt) or equation.has(sp.cbrt):
                    # معادلات جذرية
                    solutions = self._solve_radical(equation, symbol)
            
            return solutions
        except Exception as e:
            logger.warning(f"فشل حل المعادلة {equation}: {str(e)}")
            return []
    
    def _solve_absolute(self, equation, symbol):
        """
        حل متخصص لمعادلات القيمة المطلقة
        """
        try:
            # استخراج تعبير القيمة المطلقة
            abs_expr = None
            for arg in sp.preorder_traversal(equation):
                if isinstance(arg, sp.Abs):
                    abs_expr = arg
                    break
            
            if not abs_expr:
                return []
            
            # فصل المعادلة إلى حالات
            lhs, rhs = equation.lhs, equation.rhs
            
            # الحالة 1: التعبير الداخلي = rhs
            eq1 = sp.Eq(abs_expr.args[0], rhs)
            # الحالة 2: التعبير الداخلي = -rhs
            eq2 = sp.Eq(abs_expr.args[0], -rhs)
            
            sol1 = sp.solve(eq1, symbol)
            sol2 = sp.solve(eq2, symbol)
            
            # دمج الحلول مع إزالة المكرر
            all_sols = list(set(sol1 + sol2))
            
            # التحقق من صحة الحلول
            valid_sols = []
            for sol in all_sols:
                try:
                    if equation.subs(symbol, sol) == True:
                        valid_sols.append(sol)
                except:
                    pass
            
            return valid_sols
        except:
            return []
    
    def _solve_logarithmic(self, equation, symbol):
        """
        حل متخصص للمعادلات اللوغاريتمية
        """
        try:
            # تحويل إلى صيغة أسية
            solutions = []
            
            # البحث عن اللوغاريتمات
            for arg in sp.preorder_traversal(equation):
                if isinstance(arg, sp.log):
                    # log_base(expr) = value  =>  expr = base^value
                    base = arg.args[1] if len(arg.args) > 1 else sp.E
                    expr = arg.args[0]
                    
                    # استخراج الطرف الآخر
                    if equation.lhs == arg:
                        rhs = equation.rhs
                        new_eq = sp.Eq(expr, base ** rhs)
                        sols = sp.solve(new_eq, symbol)
                        solutions.extend(sols)
                    elif equation.rhs == arg:
                        lhs = equation.lhs
                        new_eq = sp.Eq(expr, base ** lhs)
                        sols = sp.solve(new_eq, symbol)
                        solutions.extend(sols)
            
            return list(set(solutions))
        except:
            return []
    
    def _solve_radical(self, equation, symbol):
        """
        حل متخصص للمعادلات الجذرية
        """
        try:
            # تربيع الطرفين للتخلص من الجذور
            current_eq = equation
            
            # تكرار حتى التخلص من جميع الجذور
            max_iter = 10
            for _ in range(max_iter):
                has_radical = False
                
                for arg in sp.preorder_traversal(current_eq):
                    if isinstance(arg, sp.Pow) and arg.exp.is_Rational and arg.exp.q != 1:
                        has_radical = True
                        # رفع الطرفين للقوة المناسبة
                        power = arg.exp.q
                        current_eq = sp.Eq(current_eq.lhs ** power, current_eq.rhs ** power)
                        break
                
                if not has_radical:
                    break
            
            # حل المعادلة بعد التخلص من الجذور
            solutions = sp.solve(current_eq, symbol)
            
            # التحقق من صحة الحلول في المعادلة الأصلية
            valid_sols = []
            for sol in solutions:
                try:
                    if equation.subs(symbol, sol) == True:
                        valid_sols.append(sol)
                except:
                    pass
            
            return valid_sols
        except:
            return []
    
    def _safe_float_conversion(self, expr) -> Union[float, str, complex]:
        """
        تحويل آمن للقيم إلى float مع دعم الأعداد المركبة
        """
        try:
            # محاولة التحويل إلى float
            val = float(sp.N(expr))
            return val
        except (TypeError, ValueError):
            try:
                # محاولة التحويل إلى complex
                val = complex(sp.N(expr))
                return val
            except:
                # إذا فشل، أعد التعبير كنص
                return str(expr)
    
    def _prime_factors(self, n: int) -> List[int]:
        """
        تحليل عدد إلى عوامله الأولية - نسخة محسنة
        """
        if n <= 1:
            return []
        
        factors = []
        d = 2
        n_abs = abs(n)
        
        while d * d <= n_abs:
            while n_abs % d == 0:
                factors.append(d)
                n_abs //= d
            d += 1 if d == 2 else 2  # تحسين: تخطي الأعداد الزوجية بعد 2
        
        if n_abs > 1:
            factors.append(n_abs)
        
        return factors
    
    def _simplify_root(self, value: float, root: int) -> Dict[str, Any]:
        """
        تبسيط الجذور - نسخة كاملة محسنة
        """
        try:
            if value == 0:
                return {
                    'simplified': '0',
                    'outside': 0,
                    'inside': 1,
                    'decimal': 0.0
                }
            
            # معالجة الأعداد السالبة للجذور الفردية
            sign = 1
            val = value
            if value < 0 and root % 2 == 1:
                sign = -1
                val = -value
            
            # تحليل العدد
            if val.is_integer():
                factors = self._prime_factors(int(val))
            else:
                # للكسور العشرية، نكتفي بالقيمة التقريبية
                return {
                    'simplified': f"{sign}*{val:.4f}^{1/{root}}" if sign != 1 else f"{val:.4f}^{1/{root}}",
                    'outside': sign * (val ** (1/root)),
                    'inside': 1,
                    'decimal': sign * (val ** (1/root))
                }
            
            # تجميع العوامل
            factor_counts = {}
            for f in factors:
                factor_counts[f] = factor_counts.get(f, 0) + 1
            
            outside = 1
            inside = 1
            
            for factor, count in factor_counts.items():
                groups = count // root
                remainder = count % root
                outside *= factor ** groups
                inside *= factor ** remainder
            
            # بناء النتيجة
            if inside == 1:
                simplified = f"{sign * outside}"
                decimal = sign * outside
            elif outside == 1:
                simplified = f"{'-' if sign < 0 else ''}{root}√{inside}"
                decimal = sign * (inside ** (1/root))
            else:
                simplified = f"{sign * outside} {root}√{inside}"
                decimal = sign * outside * (inside ** (1/root))
            
            return {
                'simplified': simplified,
                'outside': sign * outside,
                'inside': inside,
                'decimal': decimal,
                'prime_factors': factors,
                'factor_counts': factor_counts
            }
            
        except Exception as e:
            logger.error(f"خطأ في تبسيط الجذر {value}^{1}/{root}: {str(e)}")
            return {
                'simplified': f"{value:.4f}^{1}/{root}",
                'outside': None,
                'inside': None,
                'decimal': value ** (1/root) if value >= 0 or root % 2 == 1 else None,
                'error': str(e)
            }
    
    def _try_denest(self, expr) -> Optional[str]:
        """
        محاولة تبسيط الجذور المتداخلة - نسخة محسنة
        """
        try:
            # البحث عن نمط √(a + √b)
            if isinstance(expr, sp.Pow) and expr.exp == sp.Rational(1, 2):
                inner = expr.args[0]
                if isinstance(inner, sp.Add):
                    # محاولة كتابته على صورة (√p + √q)²
                    terms = inner.as_ordered_terms()
                    if len(terms) == 2:
                        t1, t2 = terms
                        if isinstance(t1, sp.Pow) and t1.exp == sp.Rational(1, 2):
                            # t1 هو جذر
                            a = t1.args[0]
                            if t2.is_Number:
                                # نمط √a + b
                                # نحاول إيجاد p, q بحيث √a + b = (√p + √q)²
                                b = t2
                                # (√p + √q)² = p + q + 2√(pq)
                                # نحتاج: p + q = b, 2√(pq) = √a
                                # => 4pq = a, p+q = b
                                # حل المعادلة التربيعية: t² - bt + a/4 = 0
                                disc = b**2 - a
                                if disc >= 0:
                                    p = (b + math.sqrt(disc)) / 2
                                    q = (b - math.sqrt(disc)) / 2
                                    if p > 0 and q > 0:
                                        return f"√{p:.2f} + √{q:.2f}"
            
            return None
        except:
            return None
    
    def _get_root_rules(self, operation: str, root: int) -> List[Dict[str, str]]:
        """
        قواعد الجذور مع أمثلة
        """
        rules = {
            'multiply': [
                {
                    'rule': f"{root}√a × {root}√b = {root}√(ab)",
                    'example': f"{root}√2 × {root}√8 = {root}√16 = {2 if root==2 else 2 if root==3 else '...'}",
                    'condition': 'a, b ≥ 0' if root % 2 == 0 else 'جميع الأعداد'
                }
            ],
            'divide': [
                {
                    'rule': f"{root}√a ÷ {root}√b = {root}√(a/b)",
                    'example': f"{root}√8 ÷ {root}√2 = {root}√4 = {2 if root==2 else '...'}",
                    'condition': 'a ≥ 0, b > 0' if root % 2 == 0 else 'b ≠ 0'
                }
            ],
            'add': [
                {
                    'rule': "لا يمكن جمع الجذور إلا إذا كانت متشابهة",
                    'example': f"{root}√2 + 2{root}√2 = 3{root}√2",
                    'condition': 'نفس الجذر ونفس الراديكاند'
                }
            ],
            'power': [
                {
                    'rule': f"({root}√a)^m = {root}√(a^m)",
                    'example': f"({root}√2)³ = {root}√8",
                    'condition': 'a ≥ 0' if root % 2 == 0 else 'جميع الأعداد'
                }
            ]
        }
        return rules.get(operation, [])
    
    def _get_log_examples(self, operation: str, base: float) -> List[Dict[str, str]]:
        """
        أمثلة على خصائص اللوغاريتمات
        """
        examples = {
            'product': [
                {
                    'rule': f'log_{base}(M × N) = log_{base} M + log_{base} N',
                    'example': f'log_{base}(2 × 3) = log_{base}2 + log_{base}3'
                }
            ],
            'quotient': [
                {
                    'rule': f'log_{base}(M/N) = log_{base} M - log_{base} N',
                    'example': f'log_{base}(8/2) = log_{base}8 - log_{base}2'
                }
            ],
            'power': [
                {
                    'rule': f'log_{base}(M^n) = n log_{base} M',
                    'example': f'log_{base}(2³) = 3 log_{base}2'
                }
            ],
            'change_base': [
                {
                    'rule': 'log_a M = log_b M / log_b a',
                    'example': f'log_2 8 = log_10 8 / log_10 2 = 3'
                }
            ]
        }
        return examples.get(operation, [])
    
    def _get_exponential_examples(self, problem_type: str) -> List[Dict[str, str]]:
        """
        أمثلة على المسائل الأسية مع الحلول
        """
        examples = {
            'exponential_growth': [
                {
                    'problem': "تعداد مدينة يزداد بنسبة 3% سنوياً، فإذا كان التعداد الحالي 100000، كم يصبح بعد 5 سنوات؟",
                    'formula': 'P(t) = P₀ × (1 + r)^t',
                    'solution': 'P(5) = 100000 × (1.03)^5 = 115927'
                }
            ],
            'exponential_decay': [
                {
                    'problem': "كتلة مادة مشعة تتناقص بمعدل 10% سنوياً، فإذا كانت الكتلة الابتدائية 100 جرام، كم تتبقى بعد 3 سنوات؟",
                    'formula': 'A(t) = A₀ × (1 - r)^t',
                    'solution': 'A(3) = 100 × (0.9)^3 = 72.9 جرام'
                }
            ],
            'compound_interest': [
                {
                    'problem': "استثمرت 10000 ريال بمعدل فائدة 5% سنوياً لمدة 3 سنوات مع التحويل الربع سنوي، كم يصبح المبلغ؟",
                    'formula': 'A = P(1 + r/n)^(nt)',
                    'solution': 'A = 10000 × (1 + 0.05/4)^(12) = 11607.55 ريال'
                }
            ],
            'radioactive_decay': [
                {
                    'problem': "عمر النصف لعنصر مشع هو 10 سنوات، فإذا كانت الكتلة الابتدائية 80 جرام، كم تتبقى بعد 30 سنة؟",
                    'formula': 'A = A₀ × (1/2)^(t/h)',
                    'solution': 'A = 80 × (1/2)^(3) = 10 جرام'
                }
            ]
        }
        return examples.get(problem_type, [])
    
    def _verify_solution(self, equation, variable, solution) -> Dict[str, Any]:
        """
        التحقق من صحة الحل
        """
        try:
            # تعويض الحل في المعادلة
            left_val = equation.lhs.subs(variable, solution)
            right_val = equation.rhs.subs(variable, solution)
            
            # حساب الفرق
            try:
                diff = float(sp.N(abs(left_val - right_val)))
                is_valid = diff < self.precision
            except:
                diff = None
                is_valid = equation.subs(variable, solution) == True
            
            return {
                'solution': self._safe_float_conversion(solution),
                'left_value': self._safe_float_conversion(left_val),
                'right_value': self._safe_float_conversion(right_val),
                'difference': diff,
                'is_valid': is_valid
            }
        except Exception as e:
            return {
                'solution': str(solution),
                'error': str(e),
                'is_valid': False
            }
    
    def _get_rational_domain(self, fractions, include_denom: bool = False) -> Dict[str, Any]:
        """
        الحصول على مجال الكسور الجبرية بشكل مفصل
        """
        denominators = []
        
        def extract_denominators(expr):
            if isinstance(expr, sp.Pow) and expr.exp == -1:
                denominators.append(expr.base)
            elif expr.is_Mul:
                for arg in expr.args:
                    extract_denominators(arg)
            elif expr.is_Add:
                for arg in expr.args:
                    extract_denominators(arg)
        
        for frac in fractions:
            extract_denominators(frac)
        
        if not denominators:
            return {
                'domain': 'جميع الأعداد الحقيقية',
                'interval': '(-∞, ∞)',
                'conditions': []
            }
        
        # حل معادلات المقام
        conditions = []
        excluded = []
        
        for den in denominators:
            solutions = sp.solve(den, self.x)
            for sol in solutions:
                if sol.is_real:
                    excluded.append(float(sp.N(sol)))
                    conditions.append(f"{den} ≠ {float(sp.N(sol))}")
                else:
                    conditions.append(f"{den} ≠ {sol}")
        
        if include_denom:
            conditions.append("المقام الثاني ≠ 0")
        
        # ترتيب القيم المستثناة
        real_excluded = sorted([e for e in excluded if isinstance(e, (int, float))])
        
        # بناء صيغة الفترات
        if not real_excluded:
            interval = "(-∞, ∞)"
        else:
            intervals = []
            if real_excluded[0] > -np.inf:
                intervals.append(f"(-∞, {real_excluded[0]})")
            
            for i in range(len(real_excluded)-1):
                intervals.append(f"({real_excluded[i]}, {real_excluded[i+1]})")
            
            if real_excluded[-1] < np.inf:
                intervals.append(f"({real_excluded[-1]}, ∞)")
            
            interval = " ∪ ".join(intervals)
        
        return {
            'domain': ' و '.join(conditions) if conditions else 'جميع الأعداد',
            'interval': interval,
            'conditions': conditions,
            'excluded_values': excluded
        }
    
    # =========================================================================
    # دوال التحقق المتخصصة
    # =========================================================================
    
    def _verify_exponential_solution(self, base: float, exp1: str, exp2: str, solutions) -> List[Dict]:
        """التحقق من حلول المعادلات الأسية"""
        verification = []
        for sol in solutions:
            if sol.is_real:
                try:
                    val1 = base ** float(sp.N(sp.sympify(exp1).subs(self.x, sol)))
                    val2 = base ** float(sp.N(sp.sympify(exp2).subs(self.x, sol)))
                    verification.append({
                        'solution': float(sp.N(sol)),
                        'left': val1,
                        'right': val2,
                        'error': abs(val1 - val2),
                        'is_valid': abs(val1 - val2) < self.precision
                    })
                except:
                    verification.append({
                        'solution': str(sol),
                        'error': 'فشل التحقق',
                        'is_valid': False
                    })
        return verification
    
    def _verify_logarithmic_solutions(self, arg_expr, base: float, value: float, solutions) -> List[Dict]:
        """التحقق من حلول المعادلات اللوغاريتمية"""
        verification = []
        for sol in solutions:
            try:
                arg_val = float(sp.N(arg_expr.subs(self.x, sol)))
                if arg_val > 0:
                    log_val = math.log(arg_val, base)
                    is_valid = abs(log_val - value) < self.precision
                else:
                    log_val = None
                    is_valid = False
                
                verification.append({
                    'solution': float(sp.N(sol)),
                    'argument_value': arg_val,
                    'log_value': log_val,
                    'expected': value,
                    'is_valid': is_valid
                })
            except:
                verification.append({
                    'solution': str(sol),
                    'error': 'فشل التحقق',
                    'is_valid': False
                })
        return verification
    
    def _verify_absolute_solutions(self, expr, value: float, solutions) -> List[Dict]:
        """التحقق من حلول معادلات القيمة المطلقة - نسخة محسنة"""
        verification = []
        for sol in solutions:
            try:
                if hasattr(sol, 'is_real') and sol.is_real:
                    expr_val = float(sp.N(expr.subs(self.x, sol)))
                    abs_val = abs(expr_val)
                    verification.append({
                        'solution': float(sp.N(sol)),
                        'expression_value': expr_val,
                        'absolute_value': abs_val,
                        'expected': value,
                        'is_valid': abs(abs_val - value) < self.precision
                    })
                else:
                    # حلول مركبة أو غير رقمية
                    verification.append({
                        'solution': str(sol),
                        'note': 'حل غير رقمي',
                        'is_valid': None
                    })
            except Exception as e:
                verification.append({
                    'solution': str(sol),
                    'error': str(e),
                    'is_valid': False
                })
        return verification
    
    def _verify_radical_solutions(self, rad_expr, value: float, root: int, solutions) -> List[Dict]:
        """التحقق من حلول المعادلات الجذرية"""
        verification = []
        for sol in solutions:
            try:
                rad_val = float(sp.N(rad_expr.subs(self.x, sol)))
                
                # حساب الجذر مع مراعاة الإشارة
                if root % 2 == 0:
                    if rad_val >= 0:
                        root_val = rad_val ** (1/root)
                    else:
                        root_val = None
                else:
                    root_val = rad_val ** (1/root) if rad_val >= 0 else -((-rad_val) ** (1/root))
                
                is_valid = abs(root_val - value) < self.precision if root_val is not None else False
                
                verification.append({
                    'solution': float(sp.N(sol)),
                    'radicand_value': rad_val,
                    'root_value': root_val,
                    'expected': value,
                    'is_valid': is_valid
                })
            except:
                verification.append({
                    'solution': str(sol),
                    'error': 'فشل التحقق',
                    'is_valid': False
                })
        return verification
    
    # =========================================================================
    # القسم 11: القوى والأسس (6 قوالب) - Templates 53-58
    # =========================================================================
    
    def template_53_power_rules(self, base: str, exponent: float) -> Dict[str, Any]:
        """
        قالب 53: تطبيق قوانين القوى على تعبير
        """
        self.stats['total_calls'] += 1
        template_id = 53
        
        try:
            base_expr = self._safe_sympify(base)
            
            # تمثيل القوة
            power_expr = base_expr ** exponent
            
            # تطبيق القوانين
            rules_demo = []
            
            # قانون ضرب القوى
            if exponent > 0:
                product = base_expr ** (exponent/2) * base_expr ** (exponent/2)
                rules_demo.append({
                    'rule': 'a^m × a^n = a^(m+n)',
                    'example': f"{base}^{exponent/2} × {base}^{exponent/2} = {base}^{exponent}",
                    'result': str(sp.simplify(product)),
                    'verification': sp.simplify(product) == power_expr
                })
            
            # قانون قسمة القوى
            if exponent > 1:
                division = (base_expr ** exponent) / (base_expr ** (exponent-1))
                rules_demo.append({
                    'rule': 'a^m ÷ a^n = a^(m-n)',
                    'example': f"{base}^{exponent} ÷ {base}^{exponent-1} = {base}¹",
                    'result': str(sp.simplify(division)),
                    'verification': sp.simplify(division) == base_expr
                })
            
            # قانون قوة القوة
            power_of_power = (base_expr ** (exponent/2)) ** 2
            rules_demo.append({
                'rule': '(a^m)^n = a^(m×n)',
                'example': f"({base}^{exponent/2})² = {base}^{exponent}",
                'result': str(sp.simplify(power_of_power)),
                'verification': sp.simplify(power_of_power) == power_expr
            })
            
            # حالات خاصة
            special_cases = {}
            if exponent == 0:
                special_cases['zero_exponent'] = f"{base}⁰ = 1"
            elif exponent < 0:
                special_cases['negative_exponent'] = f"{base}^{exponent} = 1/{base}^{{{-exponent}}}"
            
            if isinstance(exponent, float) and not exponent.is_integer():
                special_cases['fractional_exponent'] = f"{base}^{exponent} = الجذر {int(1/exponent)} للعدد {base}"
            
            result = {
                'template_id': template_id,
                'template_name': 'power_rules',
                'template_name_ar': 'قوانين القوى',
                'input': {'base': base, 'exponent': exponent},
                'expression': str(power_expr),
                'simplified': str(sp.simplify(power_expr)),
                'rules_demonstration': rules_demo,
                'special_cases': special_cases,
                'decimal_value': float(sp.N(power_expr)) if power_expr.is_number else None
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__,
                'suggestion': 'تأكد من صحة قاعدة الأس والتعبير'
            }
    
    def template_54_power_equations_same_base(self, base: float, exp1: str, exp2: str) -> Dict[str, Any]:
        """
        قالب 54: معادلات أسية بنفس الأساس
        """
        template_id = 54
        self.stats['total_calls'] += 1
        
        try:
            # التحقق من صحة الأساس
            if base <= 0:
                raise ValueError(f"الأساس {base} يجب أن يكون موجباً")
            if base == 1:
                raise ValueError("الأساس لا يمكن أن يساوي 1")
            
            # بناء المعادلة
            exp1_expr = self._safe_sympify(exp1)
            exp2_expr = self._safe_sympify(exp2)
            
            # بما أن الأساس متساوي، نساوي الأسس
            equation = sp.Eq(exp1_expr, exp2_expr)
            solution = self._safe_solve(equation, self.x)
            
            # تحويل الحلول
            solutions_list = []
            for sol in solution:
                solutions_list.append(self._safe_float_conversion(sol))
            
            result = {
                'template_id': template_id,
                'template_name': 'power_equations_same_base',
                'template_name_ar': 'معادلات أسية - نفس الأساس',
                'input': {'base': base, 'exponent1': exp1, 'exponent2': exp2},
                'equation': f"{base}^({exp1}) = {base}^({exp2})",
                'equated_exponents': f"{exp1} = {exp2}",
                'solutions': solutions_list,
                'exact_solutions': [str(sol) for sol in solution],
                'verification': self._verify_exponential_solution(base, exp1, exp2, solution),
                'method': 'بما أن الأساس متساوي، نساوي الأسس',
                'domain': 'x ∈ ℝ'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def template_55_power_equations_different_base(self, a: float, b: float) -> Dict[str, Any]:
        """
        قالب 55: معادلات أسية بأسس مختلفة: a^x = b
        """
        template_id = 55
        self.stats['total_calls'] += 1
        
        try:
            # التحقق من الشروط
            if a <= 0:
                raise ValueError(f"الأساس a = {a} يجب أن يكون موجباً")
            if a == 1:
                raise ValueError("الأساس a لا يمكن أن يساوي 1")
            if b <= 0:
                raise ValueError(f"الطرف الأيمن b = {b} يجب أن يكون موجباً")
            
            # الحل باستخدام اللوغاريتم
            x_exact = sp.log(b) / sp.log(a)
            x_decimal = float(sp.N(x_exact))
            
            # التحقق
            verification = abs(a**x_decimal - b) < self.precision
            
            result = {
                'template_id': template_id,
                'template_name': 'power_equations_different_base',
                'template_name_ar': 'معادلات أسية - أساس مختلف',
                'input': {'a': a, 'b': b},
                'equation': f"{a}^x = {b}",
                'solution': {
                    'exact': str(x_exact),
                    'decimal': x_decimal,
                    'logarithmic_form': f"x = log_{a}({b}) = ln({b})/ln({a})"
                },
                'verification': {
                    'substituted': a**x_decimal,
                    'expected': b,
                    'error': abs(a**x_decimal - b),
                    'is_valid': verification
                },
                'domain': 'x ∈ ℝ',
                'conditions': f'a > 0, a ≠ 1, b > 0'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def template_56_power_inequalities(self, a: float, b: float, inequality: str) -> Dict[str, Any]:
        """
        قالب 56: متباينات أسية: a^x > b
        """
        template_id = 56
        self.stats['total_calls'] += 1
        
        try:
            # التحقق من الشروط
            if a <= 0:
                raise ValueError(f"الأساس a = {a} يجب أن يكون موجباً")
            if a == 1:
                raise ValueError("الأساس a لا يمكن أن يساوي 1")
            
            # نقطة التعادل
            if b <= 0:
                critical_point = None
            else:
                critical_point = math.log(b) / math.log(a)
            
            # تحديد نوع الدالة
            function_type = 'متزايدة' if a > 1 else 'متناقصة'
            
            # حل المتباينة
            solution = ""
            solution_interval = ""
            
            if b <= 0:
                if a > 1:
                    if inequality in ['>', '≥']:
                        solution = "جميع الأعداد الحقيقية"
                        solution_interval = "(-∞, ∞)"
                    else:
                        solution = "لا يوجد حل"
                        solution_interval = "∅"
                else:  # 0 < a < 1
                    if inequality in ['>', '≥']:
                        solution = "جميع الأعداد الحقيقية"
                        solution_interval = "(-∞, ∞)"
                    else:
                        solution = "لا يوجد حل"
                        solution_interval = "∅"
            else:
                if a > 1:  # دالة متزايدة
                    if inequality == '>':
                        solution = f"x > {critical_point:.4f}"
                        solution_interval = f"({critical_point:.4f}, ∞)"
                    elif inequality == '≥':
                        solution = f"x ≥ {critical_point:.4f}"
                        solution_interval = f"[{critical_point:.4f}, ∞)"
                    elif inequality == '<':
                        solution = f"x < {critical_point:.4f}"
                        solution_interval = f"(-∞, {critical_point:.4f})"
                    elif inequality == '≤':
                        solution = f"x ≤ {critical_point:.4f}"
                        solution_interval = f"(-∞, {critical_point:.4f}]"
                else:  # دالة متناقصة (0 < a < 1)
                    if inequality == '>':
                        solution = f"x < {critical_point:.4f}"
                        solution_interval = f"(-∞, {critical_point:.4f})"
                    elif inequality == '≥':
                        solution = f"x ≤ {critical_point:.4f}"
                        solution_interval = f"(-∞, {critical_point:.4f}]"
                    elif inequality == '<':
                        solution = f"x > {critical_point:.4f}"
                        solution_interval = f"({critical_point:.4f}, ∞)"
                    elif inequality == '≤':
                        solution = f"x ≥ {critical_point:.4f}"
                        solution_interval = f"[{critical_point:.4f}, ∞)"
            
            result = {
                'template_id': template_id,
                'template_name': 'power_inequalities',
                'template_name_ar': 'متباينات أسية',
                'input': {'a': a, 'b': b, 'inequality': inequality},
                'inequality': f"{a}^x {inequality} {b}",
                'critical_point': critical_point,
                'function_type': function_type,
                'solution': solution,
                'interval_notation': solution_interval,
                'graph_behavior': f'الدالة {function_type}، {"تمر بنقطة (0,1)" if b==1 else ""}'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def template_57_power_system(self, eq1: str, eq2: str) -> Dict[str, Any]:
        """
        قالب 57: نظام معادلات أسية
        """
        template_id = 57
        self.stats['total_calls'] += 1
        
        try:
            # تنظيف المعادلات
            eq1 = eq1.replace(' ', '')
            eq2 = eq2.replace(' ', '')
            
            # تحويل إلى تعبيرات SymPy
            lhs1, rhs1 = eq1.split('=')
            lhs2, rhs2 = eq2.split('=')
            
            expr1 = sp.Eq(self._safe_sympify(lhs1), self._safe_sympify(rhs1))
            expr2 = sp.Eq(self._safe_sympify(lhs2), self._safe_sympify(rhs2))
            
            # حل النظام
            solution = sp.solve([expr1, expr2], [self.x, self.y])
            
            # تنظيم الحلول
            solutions_list = []
            if solution:
                if isinstance(solution, list):
                    for sol in solution:
                        sol_dict = {}
                        if self.x in sol:
                            sol_dict['x'] = self._safe_float_conversion(sol[self.x])
                        if self.y in sol:
                            sol_dict['y'] = self._safe_float_conversion(sol[self.y])
                        solutions_list.append(sol_dict)
                else:
                    sol_dict = {}
                    if self.x in solution:
                        sol_dict['x'] = self._safe_float_conversion(solution[self.x])
                    if self.y in solution:
                        sol_dict['y'] = self._safe_float_conversion(solution[self.y])
                    solutions_list.append(sol_dict)
            
            result = {
                'template_id': template_id,
                'template_name': 'power_system',
                'template_name_ar': 'نظام معادلات أسية',
                'input': {'eq1': eq1, 'eq2': eq2},
                'equations': [str(expr1), str(expr2)],
                'solutions': solutions_list,
                'num_solutions': len(solutions_list),
                'method': 'استخدام خواص الأسس واللوغاريتمات',
                'verification': 'يمكن التحقق بتعويض الحلول في المعادلات الأصلية'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def template_58_power_word_problems(self, problem_type: str, values: Dict) -> Dict[str, Any]:
        """
        قالب 58: مسائل كلامية على الأسس
        """
        template_id = 58
        self.stats['total_calls'] += 1
        
        try:
            applications = {
                'exponential_growth': {
                    'name': 'النمو الأسي',
                    'formula': 'A = P(1 + r)^t',
                    'description': 'A: الكمية النهائية، P: الكمية الابتدائية، r: معدل النمو، t: الزمن',
                    'variables': ['P', 'r', 't', 'A']
                },
                'exponential_decay': {
                    'name': 'الاضمحلال الأسي',
                    'formula': 'A = P(1 - r)^t',
                    'description': 'A: الكمية المتبقية، P: الكمية الابتدائية، r: معدل الاضمحلال، t: الزمن',
                    'variables': ['P', 'r', 't', 'A']
                },
                'compound_interest': {
                    'name': 'الفائدة المركبة',
                    'formula': 'A = P(1 + r/n)^(nt)',
                    'description': 'A: المبلغ النهائي، P: المبلغ الأصلي، r: معدل الفائدة، n: عدد مرات التحويل، t: الزمن',
                    'variables': ['P', 'r', 'n', 't', 'A']
                },
                'radioactive_decay': {
                    'name': 'عمر النصف',
                    'formula': 'A = A₀ × 2^(-t/h)',
                    'description': 'A: الكمية المتبقية، A₀: الكمية الابتدائية، t: الزمن، h: عمر النصف',
                    'variables': ['A₀', 't', 'h', 'A']
                }
            }
            
            if problem_type not in applications:
                raise ValueError(f'نوع المسألة غير معروف: {problem_type}. الأنواع المتاحة: {list(applications.keys())}')
            
            app = applications[problem_type]
            
            # حساب حسب المعطيات المتوفرة
            calculation = None
            steps = []
            
            if problem_type == 'exponential_growth':
                if 'P' in values and 'r' in values and 't' in values:
                    P = values['P']
                    r = values['r']
                    t = values['t']
                    A = P * (1 + r) ** t
                    steps = [
                        f"نطبق قانون النمو الأسي: A = P(1 + r)^t",
                        f"A = {P} × (1 + {r})^{t}",
                        f"A = {P} × ({1+r})^{t}",
                        f"A = {A:.4f}"
                    ]
                    calculation = {
                        'initial': P,
                        'rate': r,
                        'time': t,
                        'final': A,
                        'steps': steps
                    }
            
            elif problem_type == 'exponential_decay':
                if 'P' in values and 'r' in values and 't' in values:
                    P = values['P']
                    r = values['r']
                    t = values['t']
                    A = P * (1 - r) ** t
                    steps = [
                        f"نطبق قانون الاضمحلال الأسي: A = P(1 - r)^t",
                        f"A = {P} × (1 - {r})^{t}",
                        f"A = {P} × ({1-r})^{t}",
                        f"A = {A:.4f}"
                    ]
                    calculation = {
                        'initial': P,
                        'rate': r,
                        'time': t,
                        'final': A,
                        'steps': steps
                    }
            
            elif problem_type == 'compound_interest':
                if all(k in values for k in ['P', 'r', 'n', 't']):
                    P = values['P']
                    r = values['r']
                    n = values['n']
                    t = values['t']
                    A = P * (1 + r/n) ** (n * t)
                    steps = [
                        f"نطبق قانون الفائدة المركبة: A = P(1 + r/n)^(nt)",
                        f"A = {P} × (1 + {r}/{n})^{{{n}×{t}}}",
                        f"A = {P} × ({1 + r/n})^{{{n*t}}}",
                        f"A = {A:.4f}"
                    ]
                    calculation = {
                        'principal': P,
                        'rate': r,
                        'compounding_per_year': n,
                        'time': t,
                        'final': A,
                        'steps': steps
                    }
            
            elif problem_type == 'radioactive_decay':
                if all(k in values for k in ['A₀', 't', 'h']):
                    A0 = values['A₀']
                    t = values['t']
                    h = values['h']
                    A = A0 * 2 ** (-t/h)
                    steps = [
                        f"نطبق قانون عمر النصف: A = A₀ × 2^(-t/h)",
                        f"A = {A0} × 2^(-{t}/{h})",
                        f"A = {A0} × 2^(-{t/h:.4f})",
                        f"A = {A:.4f}"
                    ]
                    calculation = {
                        'initial': A0,
                        'time': t,
                        'half_life': h,
                        'remaining': A,
                        'steps': steps
                    }
            
            result = {
                'template_id': template_id,
                'template_name': 'power_word_problems',
                'template_name_ar': 'مسائل كلامية - الأسس',
                'input': {'problem_type': problem_type, 'values': values},
                'application': {
                    'name': app['name'],
                    'formula': app['formula'],
                    'description': app['description'],
                    'variables': app['variables']
                },
                'calculation': calculation,
                'examples': self._get_exponential_examples(problem_type),
                'note': 'تأكد من استخدام نفس الوحدات للزمن'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    # =========================================================================
    # القسم 12: الجذور التربيعية والتكعيبية (5 قوالب) - Templates 59-63
    # =========================================================================
    
    def template_59_square_root_simplify(self, number: float) -> Dict[str, Any]:
        """
        قالب 59: تبسيط الجذور التربيعية
        """
        template_id = 59
        self.stats['total_calls'] += 1
        
        try:
            if number < 0:
                # جذر تربيعي لعدد سالب (أعداد مركبة)
                simplified = f"{cmath.sqrt(number)}"
                decimal = str(cmath.sqrt(number))
                is_real = False
                simplified_info = self._simplify_root(abs(number), 2)
                simplified_info['simplified'] = f"{'i' if number<0 else ''}{simplified_info['simplified']}"
            else:
                simplified_info = self._simplify_root(number, 2)
                simplified = simplified_info['simplified']
                decimal = math.sqrt(number)
                is_real = True
            
            result = {
                'template_id': template_id,
                'template_name': 'square_root_simplify',
                'template_name_ar': 'تبسيط الجذور التربيعية',
                'input': {'number': number},
                'original': f"√{number}",
                'simplified': simplified_info['simplified'],
                'is_real': is_real,
                'decimal_approximation': decimal,
                'prime_factors': simplified_info.get('prime_factors', []),
                'factor_counts': simplified_info.get('factor_counts', {}),
                'outside_root': simplified_info.get('outside', 1),
                'inside_root': simplified_info.get('inside', 1),
                'method': 'تحليل العدد إلى عوامله الأولية وتجميع الأزواج'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def template_60_cube_root_simplify(self, number: float) -> Dict[str, Any]:
        """
        قالب 60: تبسيط الجذور التكعيبية
        """
        template_id = 60
        self.stats['total_calls'] += 1
        
        try:
            simplified_info = self._simplify_root(number, 3)
            
            result = {
                'template_id': template_id,
                'template_name': 'cube_root_simplify',
                'template_name_ar': 'تبسيط الجذور التكعيبية',
                'input': {'number': number},
                'original': f"∛{number}",
                'simplified': simplified_info['simplified'],
                'decimal_approximation': np.cbrt(number),
                'prime_factors': simplified_info.get('prime_factors', []),
                'factor_counts': simplified_info.get('factor_counts', {}),
                'outside_root': simplified_info.get('outside', 1),
                'inside_root': simplified_info.get('inside', 1),
                'method': 'تحليل العدد إلى عوامله الأولية وتجميع الثلاثيات'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def template_61_root_operations(self, operation: str, radicand1: float, radicand2: float, root: int = 2) -> Dict[str, Any]:
        """
        قالب 61: عمليات على الجذور
        """
        template_id = 61
        self.stats['total_calls'] += 1
        
        try:
            # التحقق من صحة المدخلات
            if root < 2:
                raise ValueError(f"رتبة الجذر {root} غير صالحة (يجب أن تكون ≥ 2)")
            
            if operation not in ['multiply', 'divide', 'add', 'subtract', 'power']:
                raise ValueError(f"عملية غير معروفة: {operation}")
            
            # التحقق من صحة الراديكاندات للجذور الزوجية
            if root % 2 == 0:
                if radicand1 < 0:
                    raise ValueError(f"الراديكاند {radicand1} يجب أن يكون ≥ 0 للجذر التربيعي")
                if radicand2 < 0 and operation in ['multiply', 'divide']:
                    raise ValueError(f"الراديكاند {radicand2} يجب أن يكون ≥ 0 للجذر التربيعي")
            
            result = None
            steps = []
            rules_applied = self._get_root_rules(operation, root)
            
            if operation == 'multiply':
                # ضرب الجذور
                if root == 2:
                    # للجذر التربيعي
                    product_inside = radicand1 * radicand2
                    product = math.sqrt(product_inside)
                    simplified = self._simplify_root(product_inside, root)
                    
                    steps = [
                        f"قاعدة ضرب الجذور: √a × √b = √(a×b)",
                        f"√{radicand1} × √{radicand2} = √({radicand1} × {radicand2})",
                        f"= √{product_inside}",
                        f"= {simplified['simplified']}"
                    ]
                else:
                    # للجذور الأخرى
                    product_inside = radicand1 * radicand2
                    product = product_inside ** (1/root)
                    simplified = self._simplify_root(product_inside, root)
                    
                    steps = [
                        f"قاعدة ضرب الجذور: {root}√a × {root}√b = {root}√(a×b)",
                        f"{root}√{radicand1} × {root}√{radicand2} = {root}√({radicand1} × {radicand2})",
                        f"= {root}√{product_inside}",
                        f"= {simplified['simplified']}"
                    ]
                
                result = {
                    'operation': 'multiplication',
                    'result': simplified['simplified'],
                    'decimal': product,
                    'inside_value': product_inside
                }
                
            elif operation == 'divide':
                # قسمة الجذور
                if radicand2 == 0:
                    raise ValueError("لا يمكن القسمة على صفر")
                
                if root == 2:
                    quotient_inside = radicand1 / radicand2
                    quotient = math.sqrt(quotient_inside)
                    simplified = self._simplify_root(quotient_inside, root)
                    
                    steps = [
                        f"قاعدة قسمة الجذور: √a ÷ √b = √(a/b)",
                        f"√{radicand1} ÷ √{radicand2} = √({radicand1} ÷ {radicand2})",
                        f"= √{quotient_inside:.4f}",
                        f"= {simplified['simplified']}"
                    ]
                else:
                    quotient_inside = radicand1 / radicand2
                    quotient = quotient_inside ** (1/root)
                    simplified = self._simplify_root(quotient_inside, root)
                    
                    steps = [
                        f"قاعدة قسمة الجذور: {root}√a ÷ {root}√b = {root}√(a/b)",
                        f"{root}√{radicand1} ÷ {root}√{radicand2} = {root}√({radicand1} ÷ {radicand2})",
                        f"= {root}√{quotient_inside:.4f}",
                        f"= {simplified['simplified']}"
                    ]
                
                result = {
                    'operation': 'division',
                    'result': simplified['simplified'],
                    'decimal': quotient,
                    'inside_value': quotient_inside
                }
                
            elif operation in ['add', 'subtract']:
                # جمع أو طرح الجذور
                root1_val = radicand1 ** (1/root)
                root2_val = radicand2 ** (1/root)
                
                # التحقق من تشابه الجذور
                if abs(root1_val - root2_val) < self.precision:
                    # جذور متشابهة
                    if operation == 'add':
                        sum_val = 2 * root1_val
                        steps = [
                            f"الجذور متشابهة: {root1_val:.4f} + {root2_val:.4f}",
                            f"= 2 × {root1_val:.4f}",
                            f"= {sum_val:.4f}"
                        ]
                    else:  # subtract
                        sum_val = 0
                        steps = [
                            f"الجذور متشابهة: {root1_val:.4f} - {root2_val:.4f} = 0"
                        ]
                else:
                    # جذور مختلفة
                    if operation == 'add':
                        sum_val = root1_val + root2_val
                        steps = [
                            f"الجذور مختلفة، نجمع القيم العشرية:",
                            f"{root1_val:.4f} + {root2_val:.4f} = {sum_val:.4f}"
                        ]
                    else:  # subtract
                        sum_val = root1_val - root2_val
                        steps = [
                            f"الجذور مختلفة، نطرح القيم العشرية:",
                            f"{root1_val:.4f} - {root2_val:.4f} = {sum_val:.4f}"
                        ]
                
                result = {
                    'operation': 'addition' if operation == 'add' else 'subtraction',
                    'result': f"{sum_val:.4f}",
                    'decimal': sum_val,
                    'are_like_terms': abs(root1_val - root2_val) < self.precision
                }
            
            elif operation == 'power':
                # رفع الجذر لقوة
                power = radicand2  # نستخدم radicand2 كالأس
                result_val = (radicand1 ** (1/root)) ** power
                new_inside = radicand1 ** power
                simplified = self._simplify_root(new_inside, root)
                
                steps = [
                    f"قاعدة رفع الجذر لقوة: ({root}√a)^m = {root}√(a^m)",
                    f"({root}√{radicand1})^{power} = {root}√({radicand1}^{power})",
                    f"= {root}√{new_inside}",
                    f"= {simplified['simplified']}"
                ]
                
                result = {
                    'operation': 'power',
                    'result': simplified['simplified'],
                    'decimal': result_val,
                    'inside_value': new_inside
                }
            
            result_data = {
                'template_id': template_id,
                'template_name': 'root_operations',
                'template_name_ar': 'عمليات على الجذور',
                'input': {
                    'operation': operation,
                    'radicand1': radicand1,
                    'radicand2': radicand2,
                    'root': root
                },
                'steps': steps,
                'result': result,
                'rules_applied': rules_applied,
                'domain_conditions': f"{'a ≥ 0' if root%2==0 else 'جميع الأعداد'}، {'b ≥ 0' if root%2==0 and operation in ['multiply','divide'] else 'b ≠ 0' if operation=='divide' else ''}"
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result_data
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def template_62_rationalizing_denominator(self, numerator: float, denominator: float, root: int = 2) -> Dict[str, Any]:
        """
        قالب 62: توحيد المقام (التخلص من الجذور في المقام)
        """
        template_id = 62
        self.stats['total_calls'] += 1
        
        try:
            # التحقق من صحة المدخلات
            if denominator < 0 and root % 2 == 0:
                raise ValueError(f"المقام يحتوي على جذر عدد سالب (غير معرف في الأعداد الحقيقية)")
            
            if denominator == 0:
                raise ValueError("المقام لا يمكن أن يكون صفراً")
            
            steps = []
            
            if root == 2:
                # للجذر التربيعي: ضرب البسط والمقام في √denominator
                sqrt_den = math.sqrt(abs(denominator))
                new_numerator = numerator * sqrt_den
                new_denominator = denominator
                
                # تبسيط الناتج
                if new_numerator.is_integer() and new_denominator.is_integer():
                    gcd_val = math.gcd(int(new_numerator), int(new_denominator))
                    if gcd_val > 1:
                        simplified_num = int(new_numerator) // gcd_val
                        simplified_den = int(new_denominator) // gcd_val
                        rationalized = f"({simplified_num}√{abs(denominator)})/{simplified_den}" if denominator > 0 else f"({simplified_num}√{abs(denominator)})/{simplified_den}"
                    else:
                        rationalized = f"({int(new_numerator) if new_numerator.is_integer() else new_numerator:.4f}√{abs(denominator)})/{int(new_denominator)}" if denominator > 0 else f"({int(new_numerator) if new_numerator.is_integer() else new_numerator:.4f}√{abs(denominator)})/{int(new_denominator)}"
                else:
                    rationalized = f"({numerator}√{abs(denominator)})/{denominator}" if denominator > 0 else f"({numerator}√{abs(denominator)})/{denominator}"
                
                steps = [
                    f"1. الكسر الأصلي: {numerator}/√{abs(denominator)}",
                    f"2. نضرب البسط والمقام في √{abs(denominator)}:",
                    f"   = ({numerator} × √{abs(denominator)}) / (√{abs(denominator)} × √{abs(denominator)})",
                    f"3. المقام يصبح: (√{abs(denominator)})² = {abs(denominator)}",
                    f"4. النتيجة: {rationalized}"
                ]
                
            elif root == 3:
                # للجذر التكعيبي: نضرب في ∛(denominator²)
                den_abs = abs(denominator)
                cube_root_den = den_abs ** (1/3)
                cube_root_den_sq = den_abs ** (2/3)
                
                new_numerator = numerator * cube_root_den_sq
                new_denominator = denominator
                
                rationalized = f"({numerator}∛{den_abs}²)/{denominator}"
                simplified = rationalized
                
                steps = [
                    f"1. الكسر الأصلي: {numerator}/∛{den_abs}",
                    f"2. نضرب البسط والمقام في ∛{den_abs}²:",
                    f"   = ({numerator} × ∛{den_abs}²) / (∛{den_abs} × ∛{den_abs}²)",
                    f"3. المقام يصبح: ∛{den_abs}³ = {den_abs}",
                    f"4. النتيجة: {rationalized}"
                ]
            else:
                # للجذور ذات الرتب الأعلى
                den_abs = abs(denominator)
                factor = den_abs ** ((root-1)/root)
                
                new_numerator = numerator * factor
                new_denominator = denominator
                
                rationalized = f"({numerator}{root}√{den_abs}^{root-1})/{denominator}"
                simplified = rationalized
                
                steps = [
                    f"1. الكسر الأصلي: {numerator}/{root}√{den_abs}",
                    f"2. نضرب البسط والمقام في {root}√{den_abs}^{root-1}:",
                    f"3. النتيجة: {rationalized}"
                ]
            
            result = {
                'template_id': template_id,
                'template_name': 'rationalizing_denominator',
                'template_name_ar': 'توحيد المقام',
                'input': {
                    'numerator': numerator,
                    'denominator': denominator,
                    'root': root
                },
                'original_fraction': f"{numerator}/{'√' if root==2 else '∛' if root==3 else f'{root}√'}{abs(denominator)}",
                'rationalized': rationalized,
                'simplified': simplified,
                'steps': steps,
                'decimal_approximation': numerator / (denominator ** (1/root)) if denominator > 0 or root % 2 == 1 else None,
                'method': f'ضرب البسط والمقام في الجذر المرافق'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def template_63_nested_radicals(self, expression: str) -> Dict[str, Any]:
        """
        قالب 63: تبسيط الجذور المتداخلة
        """
        template_id = 63
        self.stats['total_calls'] += 1
        
        try:
            expr = self._safe_sympify(expression)
            
            # محاولة التبسيط
            simplified = sp.simplify(expr)
            
            # محاولة فك التداخل
            denested = self._try_denest(expr)
            
            # القيمة العددية
            try:
                numerical = float(sp.N(expr))
            except:
                numerical = str(sp.N(expr))
            
            # تحليل التعبير
            analysis = {
                'has_nested_roots': any(isinstance(arg, sp.Pow) and arg.exp.is_Rational and arg.exp.q != 1 
                                        for arg in sp.preorder_traversal(expr)),
                'root_count': sum(1 for arg in sp.preorder_traversal(expr) 
                                 if isinstance(arg, sp.Pow) and arg.exp.is_Rational and arg.exp.q != 1)
            }
            
            result = {
                'template_id': template_id,
                'template_name': 'nested_radicals',
                'template_name_ar': 'الجذور المتداخلة',
                'input': {'expression': expression},
                'original': str(expr),
                'simplified': str(simplified),
                'denested_form': denested if denested else 'لا يمكن التبسيط أكثر',
                'numerical_value': numerical,
                'analysis': analysis,
                'method': 'محاولة كتابة التعبير على صورة (√a + √b)²',
                'note': 'قد لا يمكن تبسيط جميع الجذور المتداخلة'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    # =========================================================================
    # القسم 13: القواعد اللوغاريتمية (5 قوالب) - Templates 64-68
    # =========================================================================
    
    def template_64_logarithm_basics(self, base: float, argument: float) -> Dict[str, Any]:
        """
        قالب 64: أساسيات اللوغاريتمات
        """
        template_id = 64
        self.stats['total_calls'] += 1
        
        try:
            # التحقق من الشروط
            if base <= 0 or base == 1:
                raise ValueError(f"الأساس {base} يجب أن يكون > 0 ولا يساوي 1")
            if argument <= 0:
                raise ValueError(f"الوسيط {argument} يجب أن يكون > 0")
            
            # حساب اللوغاريتم
            log_value = math.log(argument, base)
            
            # التحقق
            verification = abs(base ** log_value - argument) < self.precision
            
            # خصائص خاصة
            special_cases = {
                f'log_{base}(1)': 0,
                f'log_{base}({base})': 1,
                f'log_{base}({base}^n)': 'n'
            }
            
            # التحقق من العلاقات
            relations = []
            if argument == base:
                relations.append(f"log_{base}({base}) = 1")
            if argument == 1:
                relations.append(f"log_{base}(1) = 0")
            if argument == base ** 2:
                relations.append(f"log_{base}({base}²) = 2")
            
            result = {
                'template_id': template_id,
                'template_name': 'logarithm_basics',
                'template_name_ar': 'أساسيات اللوغاريتمات',
                'input': {'base': base, 'argument': argument},
                'logarithm': {
                    'notation': f'log_{base}({argument})',
                    'value': log_value,
                    'exact': str(sp.log(argument, base))
                },
                'definition': f"log_{base}({argument}) = {log_value:.4f}  يعني أن  {base}^{log_value:.4f} = {argument}",
                'exponential_form': f"{base}^{log_value:.4f} = {argument}",
                'verification': {
                    'computed': base ** log_value,
                    'expected': argument,
                    'error': abs(base ** log_value - argument),
                    'is_valid': verification
                },
                'special_cases': special_cases,
                'relations': relations,
                'properties': [
                    f"log_a(1) = 0",
                    f"log_a(a) = 1",
                    f"log_a(a^n) = n",
                    f"a^(log_a(x)) = x"
                ]
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def template_65_logarithm_properties(self, operation: str, a: float, b: float, base: float = 10) -> Dict[str, Any]:
        """
        قالب 65: خصائص اللوغاريتمات
        """
        template_id = 65
        self.stats['total_calls'] += 1
        
        try:
            # التحقق من صحة المدخلات
            if base <= 0 or base == 1:
                raise ValueError(f"الأساس {base} يجب أن يكون > 0 ولا يساوي 1")
            
            if operation in ['product', 'quotient']:
                if a <= 0 or b <= 0:
                    raise ValueError(f"المدخلات يجب أن تكون موجبة: a={a}, b={b}")
            elif operation == 'power':
                if a <= 0:
                    raise ValueError(f"الأساس a={a} يجب أن يكون موجباً")
            elif operation == 'change_base':
                if a <= 0 or b <= 0:
                    raise ValueError(f"المدخلات يجب أن تكون موجبة: a={a}, b={b}")
            else:
                raise ValueError(f'عملية غير معروفة: {operation}')
            
            properties = {
                'product': {
                    'name': 'خاصية الضرب',
                    'rule': 'log_b(MN) = log_b M + log_b N',
                    'left': math.log(a * b, base),
                    'right': math.log(a, base) + math.log(b, base),
                    'demonstration': f'log_{base}({a}×{b}) = log_{base}{a} + log_{base}{b}'
                },
                'quotient': {
                    'name': 'خاصية القسمة',
                    'rule': 'log_b(M/N) = log_b M - log_b N',
                    'left': math.log(a / b, base),
                    'right': math.log(a, base) - math.log(b, base),
                    'demonstration': f'log_{base}({a}/{b}) = log_{base}{a} - log_{base}{b}'
                },
                'power': {
                    'name': 'خاصية القوة',
                    'rule': 'log_b(M^n) = n log_b M',
                    'left': math.log(a ** b, base),
                    'right': b * math.log(a, base),
                    'demonstration': f'log_{base}({a}^{b}) = {b} × log_{base}{a}'
                },
                'change_base': {
                    'name': 'تغيير الأساس',
                    'rule': 'log_a M = log_b M / log_b a',
                    'left': math.log(a, b) if a > 0 and b > 0 else None,
                    'right': math.log(a, base) / math.log(b, base),
                    'demonstration': f'log_{a}{b} = log_{base}{b} / log_{base}{a}'
                }
            }
            
            prop = properties[operation]
            
            # حساب التحقق
            verification = None
            if prop['left'] is not None and prop['right'] is not None:
                verification = abs(prop['left'] - prop['right']) < self.precision
            
            result = {
                'template_id': template_id,
                'template_name': 'logarithm_properties',
                'template_name_ar': 'خصائص اللوغاريتمات',
                'input': {'operation': operation, 'a': a, 'b': b, 'base': base},
                'property_name': prop['name'],
                'property_rule': prop['rule'],
                'demonstration': prop['demonstration'],
                'calculation': {
                    'left': prop['left'],
                    'right': prop['right'],
                    'difference': abs(prop['left'] - prop['right']) if prop['left'] is not None and prop['right'] is not None else None,
                    'verification': verification
                },
                'examples': self._get_log_examples(operation, base),
                'conditions': {
                    'product': 'M, N > 0',
                    'quotient': 'M, N > 0',
                    'power': 'M > 0',
                    'change_base': 'M, a, b > 0, a ≠ 1, b ≠ 1'
                }.get(operation, '')
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def template_66_logarithm_simplify(self, expression: str) -> Dict[str, Any]:
        """
        قالب 66: تبسيط تعبيرات لوغاريتمية
        """
        template_id = 66
        self.stats['total_calls'] += 1
        
        try:
            expr = self._safe_sympify(expression)
            
            # محاولة التبسيط بطرق مختلفة
            simplified = sp.simplify(expr)
            combined = sp.logcombine(expr, force=True)
            expanded = sp.expand_log(expr, force=True)
            
            # التعرف على القوانين المستخدمة
            laws_used = []
            expr_str = str(expr)
            
            if '+' in expr_str and 'log' in expr_str:
                laws_used.append({
                    'law': 'log_b M + log_b N = log_b (MN)',
                    'condition': 'M, N > 0'
                })
            if '-' in expr_str and 'log' in expr_str:
                laws_used.append({
                    'law': 'log_b M - log_b N = log_b (M/N)',
                    'condition': 'M, N > 0'
                })
            if '*' in expr_str and 'log' in expr_str:
                # تحقق إذا كان هناك معامل أمام اللوغاريتم
                laws_used.append({
                    'law': 'n log_b M = log_b (M^n)',
                    'condition': 'M > 0'
                })
            
            # استخراج المتغيرات
            variables = [str(s) for s in expr.free_symbols]
            
            result = {
                'template_id': template_id,
                'template_name': 'logarithm_simplify',
                'template_name_ar': 'تبسيط تعبيرات لوغاريتمية',
                'input': {'expression': expression},
                'original': str(expr),
                'simplified': str(simplified),
                'combined': str(combined),
                'expanded': str(expanded),
                'laws_applied': laws_used,
                'variables': variables,
                'domain': 'جميع المتغيرات > 0',
                'note': 'قد تختلف نتيجة التبسيط حسب افتراض إشارة المتغيرات'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def template_67_logarithm_change_base(self, value: float, old_base: float, new_base: float) -> Dict[str, Any]:
        """
        قالب 67: تغيير أساس اللوغاريتم
        """
        template_id = 67
        self.stats['total_calls'] += 1
        
        try:
            # التحقق من الشروط
            if value <= 0:
                raise ValueError(f"القيمة {value} يجب أن تكون > 0")
            if old_base <= 0 or old_base == 1:
                raise ValueError(f"الأساس القديم {old_base} يجب أن يكون > 0 ولا يساوي 1")
            if new_base <= 0 or new_base == 1:
                raise ValueError(f"الأساس الجديد {new_base} يجب أن يكون > 0 ولا يساوي 1")
            
            # الحساب بالأساس القديم
            log_old = math.log(value, old_base)
            
            # تغيير الأساس
            log_new = math.log(value, new_base)
            
            # باستخدام القانون: log_a M = log_b M / log_b a
            conversion = math.log(value) / math.log(old_base)  # للأساس e
            conversion_new = math.log(value, new_base) / math.log(old_base, new_base)
            
            # التحقق
            verification = abs(log_old - conversion_new) < self.precision
            
            # صيغ مختلفة
            forms = {
                'natural_log': f'ln({value})/ln({old_base}) = {math.log(value):.4f}/{math.log(old_base):.4f} = {math.log(value)/math.log(old_base):.4f}',
                'common_log': f'log({value})/log({old_base}) = {math.log10(value):.4f}/{math.log10(old_base):.4f} = {math.log10(value)/math.log10(old_base):.4f}',
                f'log_{new_base}': f'log_{new_base}({value})/log_{new_base}({old_base}) = {math.log(value, new_base):.4f}/{math.log(old_base, new_base):.4f} = {conversion_new:.4f}'
            }
            
            result = {
                'template_id': template_id,
                'template_name': 'logarithm_change_base',
                'template_name_ar': 'تغيير أساس اللوغاريتم',
                'input': {'value': value, 'old_base': old_base, 'new_base': new_base},
                'original': f'log_{old_base}({value}) = {log_old:.4f}',
                'converted': {
                    'formula': f'log_{old_base}({value}) = log_{new_base}({value}) / log_{new_base}({old_base})',
                    'calculation': f'= {math.log(value, new_base):.4f} / {math.log(old_base, new_base):.4f}',
                    'result': conversion_new,
                    'result_formatted': f'{conversion_new:.4f}'
                },
                'alternative_forms': forms,
                'verification': {
                    'original_value': log_old,
                    'converted_value': conversion_new,
                    'difference': abs(log_old - conversion_new),
                    'is_valid': verification
                },
                'general_formula': 'log_a M = log_b M / log_b a'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def template_68_logarithm_inequalities(self, base: float, argument: str, value: float, inequality: str) -> Dict[str, Any]:
        """
        قالب 68: متباينات لوغاريتمية (مكتمل)
        """
        template_id = 68
        self.stats['total_calls'] += 1
        
        try:
            # التحقق من الأساس
            if base <= 0 or base == 1:
                raise ValueError(f"الأساس {base} يجب أن يكون > 0 ولا يساوي 1")
            
            # تحويل التعبير
            arg_expr = self._safe_sympify(argument)
            
            # حل المتباينة: log_base(argument) inequality value
            # => argument inequality base^value مع مراعاة اتجاه المتباينة حسب الأساس
            
            critical_point = base ** value
            
            # تحديد نوع الدالة
            function_type = 'متزايدة' if base > 1 else 'متناقصة'
            
            # حل المتباينة
            solution = ""
            solution_interval = ""
            domain_condition = f"{argument} > 0"
            
            if base > 1:  # دالة متزايدة
                if inequality == '>':
                    solution = f"{argument} > {critical_point:.4f}"
                    solution_interval = f"({critical_point:.4f}, ∞)"
                elif inequality == '≥':
                    solution = f"{argument} ≥ {critical_point:.4f}"
                    solution_interval = f"[{critical_point:.4f}, ∞)"
                elif inequality == '<':
                    solution = f"0 < {argument} < {critical_point:.4f}"
                    solution_interval = f"(0, {critical_point:.4f})"
                elif inequality == '≤':
                    solution = f"0 < {argument} ≤ {critical_point:.4f}"
                    solution_interval = f"(0, {critical_point:.4f}]"
            else:  # 0 < base < 1 (دالة متناقصة)
                if inequality == '>':
                    solution = f"0 < {argument} < {critical_point:.4f}"
                    solution_interval = f"(0, {critical_point:.4f})"
                elif inequality == '≥':
                    solution = f"0 < {argument} ≤ {critical_point:.4f}"
                    solution_interval = f"(0, {critical_point:.4f}]"
                elif inequality == '<':
                    solution = f"{argument} > {critical_point:.4f}"
                    solution_interval = f"({critical_point:.4f}, ∞)"
                elif inequality == '≤':
                    solution = f"{argument} ≥ {critical_point:.4f}"
                    solution_interval = f"[{critical_point:.4f}, ∞)"
            
            result = {
                'template_id': template_id,
                'template_name': 'logarithm_inequalities',
                'template_name_ar': 'متباينات لوغاريتمية',
                'input': {'base': base, 'argument': argument, 'value': value, 'inequality': inequality},
                'inequality': f'log_{base}({argument}) {inequality} {value}',
                'critical_point': critical_point,
                'function_type': function_type,
                'domain': domain_condition,
                'solution': solution,
                'solution_interval': solution_interval,
                'method': f'تحويل المتباينة إلى صيغة أسية مع مراعاة أن الدالة {function_type}',
                'notes': [
                    'يجب أن يكون argument > 0',
                    f'عندما يكون الأساس > 1، اتجاه المتباينة يبقى كما هو',
                    f'عندما يكون الأساس بين 0 و1، ينعكس اتجاه المتباينة'
                ]
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    # =========================================================================
    # القسم 14: المعادلات اللوغاريتمية (6 قوالب) - Templates 69-74
    # =========================================================================
    
    def template_69_logarithmic_simple(self, base: float, argument: str, value: float) -> Dict[str, Any]:
        """
        قالب 69: معادلة لوغاريتمية بسيطة
        """
        template_id = 69
        self.stats['total_calls'] += 1
        
        try:
            # التحقق من الأساس
            if base <= 0 or base == 1:
                raise ValueError(f"الأساس {base} يجب أن يكون > 0 ولا يساوي 1")
            
            # تحويل التعبير
            arg_expr = self._safe_sympify(argument)
            
            # log_base(argument) = value  =>  argument = base^value
            rhs = base ** value
            equation = sp.Eq(arg_expr, rhs)
            
            # حل المعادلة
            solutions = self._safe_solve(equation, self.x)
            
            # التحقق من مجال اللوغاريتم
            valid_solutions = []
            verification_results = []
            
            for sol in solutions:
                try:
                    # التحقق من أن argument > 0
                    arg_val = float(sp.N(arg_expr.subs(self.x, sol)))
                    if arg_val > 0:
                        valid_solutions.append(self._safe_float_conversion(sol))
                        verification_results.append({
                            'solution': self._safe_float_conversion(sol),
                            'argument_value': arg_val,
                            'log_value': math.log(arg_val, base) if arg_val > 0 else None,
                            'expected': value,
                            'is_valid': True
                        })
                except:
                    continue
            
            result = {
                'template_id': template_id,
                'template_name': 'logarithmic_simple',
                'template_name_ar': 'معادلة لوغاريتمية بسيطة',
                'input': {'base': base, 'argument': argument, 'value': value},
                'equation': f"log_{base}({argument}) = {value}",
                'exponential_form': f"{argument} = {base}^{value} = {rhs}",
                'solutions': valid_solutions,
                'all_candidates': [self._safe_float_conversion(s) for s in solutions],
                'domain_condition': f"{argument} > 0",
                'verification': verification_results,
                'method': 'تحويل المعادلة اللوغاريتمية إلى صيغة أسية'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def template_70_logarithmic_sum(self, terms: List[str], value: float, base: float = 10) -> Dict[str, Any]:
        """
        قالب 70: معادلة لوغاريتمية بمجموع لوغاريتمات
        """
        template_id = 70
        self.stats['total_calls'] += 1
        
        try:
            # التحقق من الأساس
            if base <= 0 or base == 1:
                raise ValueError(f"الأساس {base} يجب أن يكون > 0 ولا يساوي 1")
            
            # تحويل المجموع: log(A) + log(B) = log(A*B)
            product = 1
            term_exprs = []
            
            for term in terms:
                term_expr = self._safe_sympify(term)
                term_exprs.append(term_expr)
                product *= term_expr
            
            # المعادلة: log(product) = value
            rhs = base ** value
            equation = sp.Eq(product, rhs)
            
            # حل المعادلة
            solutions = self._safe_solve(equation, self.x)
            
            # التحقق من المجال (جميع الحدود > 0)
            valid_solutions = []
            verification = []
            
            for sol in solutions:
                valid = True
                term_values = []
                
                for i, term_expr in enumerate(term_exprs):
                    try:
                        term_val = float(sp.N(term_expr.subs(self.x, sol)))
                        term_values.append(term_val)
                        if term_val <= 0:
                            valid = False
                    except:
                        valid = False
                        break
                
                if valid:
                    valid_solutions.append(self._safe_float_conversion(sol))
                    verification.append({
                        'solution': self._safe_float_conversion(sol),
                        'term_values': term_values,
                        'product': float(sp.N(product.subs(self.x, sol))),
                        'log_product': math.log(float(sp.N(product.subs(self.x, sol))), base),
                        'expected': value,
                        'is_valid': True
                    })
            
            result = {
                'template_id': template_id,
                'template_name': 'logarithmic_sum',
                'template_name_ar': 'معادلة لوغاريتمية - مجموع لوغاريتمات',
                'input': {'terms': terms, 'value': value, 'base': base},
                'original_equation': ' + '.join([f'log_{base}({t})' for t in terms]) + f' = {value}',
                'combined_form': f'log_{base}({" × ".join(terms)}) = {value}',
                'exponential_form': f"{' × '.join(terms)} = {base}^{value} = {base**value:.4f}",
                'solutions': valid_solutions,
                'domain_conditions': [f"{t} > 0" for t in terms],
                'verification': verification,
                'method': 'استخدام خاصية log A + log B = log AB ثم التحويل للصيغة الأسية'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def template_71_logarithmic_difference(self, term1: str, term2: str, value: float, base: float = 10) -> Dict[str, Any]:
        """
        قالب 71: معادلة لوغاريتمية بطرح لوغاريتمين
        """
        template_id = 71
        self.stats['total_calls'] += 1
        
        try:
            # التحقق من الأساس
            if base <= 0 or base == 1:
                raise ValueError(f"الأساس {base} يجب أن يكون > 0 ولا يساوي 1")
            
            # تحويل الطرح: log(A) - log(B) = log(A/B)
            A = self._safe_sympify(term1)
            B = self._safe_sympify(term2)
            
            quotient = A / B
            
            # المعادلة: log(quotient) = value
            rhs = base ** value
            equation = sp.Eq(quotient, rhs)
            
            # حل المعادلة
            solutions = self._safe_solve(equation, self.x)
            
            # التحقق من المجال
            valid_solutions = []
            verification = []
            
            for sol in solutions:
                try:
                    A_val = float(sp.N(A.subs(self.x, sol)))
                    B_val = float(sp.N(B.subs(self.x, sol)))
                    
                    if A_val > 0 and B_val > 0:
                        valid_solutions.append(self._safe_float_conversion(sol))
                        verification.append({
                            'solution': self._safe_float_conversion(sol),
                            'A_value': A_val,
                            'B_value': B_val,
                            'quotient': A_val / B_val,
                            'log_quotient': math.log(A_val / B_val, base),
                            'expected': value,
                            'is_valid': True
                        })
                except:
                    continue
            
            result = {
                'template_id': template_id,
                'template_name': 'logarithmic_difference',
                'template_name_ar': 'معادلة لوغاريتمية - طرح لوغاريتمين',
                'input': {'term1': term1, 'term2': term2, 'value': value, 'base': base},
                'original_equation': f'log_{base}({term1}) - log_{base}({term2}) = {value}',
                'combined_form': f'log_{base}({term1}/{term2}) = {value}',
                'exponential_form': f'{term1}/{term2} = {base}^{value} = {base**value:.4f}',
                'solutions': valid_solutions,
                'domain_conditions': [f"{term1} > 0", f"{term2} > 0"],
                'verification': verification,
                'method': 'استخدام خاصية log A - log B = log(A/B) ثم التحويل للصيغة الأسية'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def template_72_logarithmic_power(self, base: float, coefficient: float, argument: str, value: float) -> Dict[str, Any]:
        """
        قالب 72: معادلة لوغاريتمية مع معامل
        """
        template_id = 72
        self.stats['total_calls'] += 1
        
        try:
            # التحقق من الأساس
            if base <= 0 or base == 1:
                raise ValueError(f"الأساس {base} يجب أن يكون > 0 ولا يساوي 1")
            
            # تحويل: n log(argument) = value  =>  log(argument^n) = value
            arg_expr = self._safe_sympify(argument)
            
            # argument^n = base^value
            rhs = base ** value
            
            # المعادلة: arg_expr^coefficient = rhs
            equation = sp.Eq(arg_expr ** coefficient, rhs)
            
            # حل المعادلة
            solutions = self._safe_solve(equation, self.x)
            
            # التحقق من المجال
            valid_solutions = []
            verification = []
            
            for sol in solutions:
                try:
                    arg_val = float(sp.N(arg_expr.subs(self.x, sol)))
                    if arg_val > 0:
                        valid_solutions.append(self._safe_float_conversion(sol))
                        verification.append({
                            'solution': self._safe_float_conversion(sol),
                            'argument_value': arg_val,
                            'powered_value': arg_val ** coefficient,
                            'log_value': coefficient * math.log(arg_val, base),
                            'expected': value,
                            'is_valid': True
                        })
                except:
                    continue
            
            result = {
                'template_id': template_id,
                'template_name': 'logarithmic_power',
                'template_name_ar': 'معادلة لوغاريتمية مع معامل',
                'input': {'base': base, 'coefficient': coefficient, 'argument': argument, 'value': value},
                'original_equation': f"{coefficient} log_{base}({argument}) = {value}",
                'transformed': f"log_{base}({argument}^{coefficient}) = {value}",
                'exponential_form': f"{argument}^{coefficient} = {base}^{value} = {rhs:.4f}",
                'solutions': valid_solutions,
                'domain_condition': f"{argument} > 0",
                'verification': verification,
                'method': 'استخدام خاصية n log M = log(M^n) ثم التحويل للصيغة الأسية'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def template_73_logarithmic_equating_arguments(self, base: float, arg1: str, arg2: str) -> Dict[str, Any]:
        """
        قالب 73: معادلة لوغاريتمية بتساوي اللوغاريتمات
        """
        template_id = 73
        self.stats['total_calls'] += 1
        
        try:
            # التحقق من الأساس
            if base <= 0 or base == 1:
                raise ValueError(f"الأساس {base} يجب أن يكون > 0 ولا يساوي 1")
            
            # تحويل التعبيرات
            A = self._safe_sympify(arg1)
            B = self._safe_sympify(arg2)
            
            # log(A) = log(B)  =>  A = B (مع مراعاة المجال)
            equation = sp.Eq(A, B)
            solutions = self._safe_solve(equation, self.x)
            
            # التحقق من المجال
            valid_solutions = []
            verification = []
            
            for sol in solutions:
                try:
                    A_val = float(sp.N(A.subs(self.x, sol)))
                    B_val = float(sp.N(B.subs(self.x, sol)))
                    
                    if A_val > 0 and B_val > 0:
                        valid_solutions.append(self._safe_float_conversion(sol))
                        verification.append({
                            'solution': self._safe_float_conversion(sol),
                            'A_value': A_val,
                            'B_value': B_val,
                            'log_A': math.log(A_val, base) if A_val > 0 else None,
                            'log_B': math.log(B_val, base) if B_val > 0 else None,
                            'are_equal': abs(A_val - B_val) < self.precision,
                            'is_valid': True
                        })
                except:
                    continue
            
            result = {
                'template_id': template_id,
                'template_name': 'logarithmic_equating_arguments',
                'template_name_ar': 'معادلة لوغاريتمية - تساوي اللوغاريتمات',
                'input': {'base': base, 'arg1': arg1, 'arg2': arg2},
                'equation': f"log_{base}({arg1}) = log_{base}({arg2})",
                'simplified': f"{arg1} = {arg2}",
                'solutions': valid_solutions,
                'domain_conditions': [f"{arg1} > 0", f"{arg2} > 0"],
                'verification': verification,
                'method': 'بما أن دالة اللوغاريتم متباينة، فإن تساوي اللوغاريتمات يعني تساوي الحجج'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def template_74_logarithmic_system(self, eq1: str, eq2: str) -> Dict[str, Any]:
        """
        قالب 74: نظام معادلات لوغاريتمية (مكتمل)
        """
        template_id = 74
        self.stats['total_calls'] += 1
        
        try:
            # تنظيف المعادلات
            eq1 = eq1.replace(' ', '')
            eq2 = eq2.replace(' ', '')
            
            # تحويل المعادلات إلى صيغ أسية
            # نفترض أن المعادلات على الصورة: log_base(expr) = value
            
            def parse_log_equation(eq_str):
                """تحليل معادلة لوغاريتمية"""
                lhs, rhs = eq_str.split('=')
                
                # البحث عن اللوغاريتم في الطرف الأيسر
                if 'log' in lhs:
                    # استخراج base والوسيط
                    import re
                    log_match = re.search(r'log_?([0-9]+)?\(([^)]+)\)', lhs)
                    if log_match:
                        base = float(log_match.group(1)) if log_match.group(1) else 10
                        arg = log_match.group(2)
                        value = float(rhs)
                        return {
                            'type': 'logarithmic',
                            'base': base,
                            'argument': arg,
                            'value': value,
                            'exponential_form': f"{arg} = {base}^{value}"
                        }
                return {'type': 'unknown'}
            
            parsed1 = parse_log_equation(eq1)
            parsed2 = parse_log_equation(eq2)
            
            # تحويل إلى معادلات أسية
            exp_eq1 = None
            exp_eq2 = None
            
            if parsed1['type'] == 'logarithmic':
                exp_eq1 = sp.Eq(
                    self._safe_sympify(parsed1['argument']),
                    parsed1['base'] ** parsed1['value']
                )
            
            if parsed2['type'] == 'logarithmic':
                exp_eq2 = sp.Eq(
                    self._safe_sympify(parsed2['argument']),
                    parsed2['base'] ** parsed2['value']
                )
            
            # حل النظام
            solutions = []
            if exp_eq1 and exp_eq2:
                system_sol = sp.solve([exp_eq1, exp_eq2], [self.x, self.y])
                
                # تنظيم الحلول
                if system_sol:
                    if isinstance(system_sol, list):
                        for sol in system_sol:
                            sol_dict = {}
                            if self.x in sol:
                                sol_dict['x'] = self._safe_float_conversion(sol[self.x])
                            if self.y in sol:
                                sol_dict['y'] = self._safe_float_conversion(sol[self.y])
                            solutions.append(sol_dict)
                    else:
                        sol_dict = {}
                        if self.x in system_sol:
                            sol_dict['x'] = self._safe_float_conversion(system_sol[self.x])
                        if self.y in system_sol:
                            sol_dict['y'] = self._safe_float_conversion(system_sol[self.y])
                        solutions.append(sol_dict)
            
            result = {
                'template_id': template_id,
                'template_name': 'logarithmic_system',
                'template_name_ar': 'نظام معادلات لوغاريتمية',
                'input': {'eq1': eq1, 'eq2': eq2},
                'parsed_equations': [parsed1, parsed2],
                'exponential_form': {
                    'eq1': str(exp_eq1) if exp_eq1 else eq1,
                    'eq2': str(exp_eq2) if exp_eq2 else eq2
                },
                'solutions': solutions,
                'num_solutions': len(solutions),
                'method': 'تحويل المعادلات اللوغاريتمية إلى صيغ أسية ثم حل النظام',
                'note': 'يجب مراعاة مجال الدوال اللوغاريتمية (الحجج > 0)',
                'domain_conditions': [
                    f"{parsed1['argument']} > 0" if parsed1['type'] == 'logarithmic' else '',
                    f"{parsed2['argument']} > 0" if parsed2['type'] == 'logarithmic' else ''
                ]
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    # =========================================================================
    # القسم 15: المعادلات الأسية (6 قوالب) - Templates 75-80
    # =========================================================================
    
    def template_75_exponential_simple(self, base: float, exponent: str, value: float) -> Dict[str, Any]:
        """
        قالب 75: معادلة أسية بسيطة
        """
        template_id = 75
        self.stats['total_calls'] += 1
        
        try:
            # التحقق من الشروط
            if base <= 0:
                raise ValueError(f"الأساس {base} يجب أن يكون موجباً")
            if base == 1:
                raise ValueError("الأساس لا يمكن أن يساوي 1")
            if value <= 0:
                raise ValueError(f"الطرف الأيمن {value} يجب أن يكون موجباً للمعادلات الأسية (في الأعداد الحقيقية)")
            
            # تحويل الأس
            exp_expr = self._safe_sympify(exponent)
            
            # base^(exponent) = value  =>  exponent = log_base(value)
            rhs = math.log(value, base)
            
            # حل المعادلة: exp_expr = rhs
            equation = sp.Eq(exp_expr, rhs)
            solutions = self._safe_solve(equation, self.x)
            
            # تحويل الحلول
            solutions_list = []
            verification = []
            
            for sol in solutions:
                if sol.is_real:
                    sol_val = float(sp.N(sol))
                    solutions_list.append(sol_val)
                    
                    # التحقق
                    left_val = base ** float(sp.N(exp_expr.subs(self.x, sol)))
                    verification.append({
                        'solution': sol_val,
                        'left_value': left_val,
                        'right_value': value,
                        'error': abs(left_val - value),
                        'is_valid': abs(left_val - value) < self.precision
                    })
            
            result = {
                'template_id': template_id,
                'template_name': 'exponential_simple',
                'template_name_ar': 'معادلة أسية بسيطة',
                'input': {'base': base, 'exponent': exponent, 'value': value},
                'equation': f"{base}^({exponent}) = {value}",
                'logarithmic_form': f"{exponent} = log_{base}({value}) = {rhs:.4f}",
                'solutions': solutions_list,
                'exact_solutions': [str(sol) for sol in solutions],
                'verification': verification,
                'domain': 'x ∈ ℝ'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def template_76_exponential_same_base(self, base: float, exp1: str, exp2: str) -> Dict[str, Any]:
        """
        قالب 76: معادلة أسية بنفس الأساس
        """
        template_id = 76
        self.stats['total_calls'] += 1
        
        try:
            # التحقق من الأساس
            if base <= 0:
                raise ValueError(f"الأساس {base} يجب أن يكون موجباً")
            if base == 1:
                raise ValueError("الأساس لا يمكن أن يساوي 1")
            
            # تحويل الأسس
            exp1_expr = self._safe_sympify(exp1)
            exp2_expr = self._safe_sympify(exp2)
            
            # base^(exp1) = base^(exp2)  =>  exp1 = exp2
            equation = sp.Eq(exp1_expr, exp2_expr)
            solutions = self._safe_solve(equation, self.x)
            
            # تحويل الحلول
            solutions_list = []
            verification = []
            
            for sol in solutions:
                if sol.is_real:
                    sol_val = float(sp.N(sol))
                    solutions_list.append(sol_val)
                    
                    # التحقق
                    left_val = base ** float(sp.N(exp1_expr.subs(self.x, sol)))
                    right_val = base ** float(sp.N(exp2_expr.subs(self.x, sol)))
                    verification.append({
                        'solution': sol_val,
                        'left_value': left_val,
                        'right_value': right_val,
                        'error': abs(left_val - right_val),
                        'is_valid': abs(left_val - right_val) < self.precision
                    })
            
            result = {
                'template_id': template_id,
                'template_name': 'exponential_same_base',
                'template_name_ar': 'معادلة أسية - نفس الأساس',
                'input': {'base': base, 'exponent1': exp1, 'exponent2': exp2},
                'equation': f"{base}^({exp1}) = {base}^({exp2})",
                'simplified': f"{exp1} = {exp2}",
                'solutions': solutions_list,
                'exact_solutions': [str(sol) for sol in solutions],
                'verification': verification,
                'method': 'بما أن الأساس متساوي، نساوي الأسس'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def template_77_exponential_different_base(self, a: float, b: float) -> Dict[str, Any]:
        """
        قالب 77: معادلة أسية بأسس مختلفة: a^x = b
        """
        template_id = 77
        self.stats['total_calls'] += 1
        
        try:
            # التحقق من الشروط
            if a <= 0:
                raise ValueError(f"الأساس a = {a} يجب أن يكون موجباً")
            if a == 1:
                raise ValueError("الأساس a لا يمكن أن يساوي 1")
            if b <= 0:
                raise ValueError(f"الطرف الأيمن b = {b} يجب أن يكون موجباً (في الأعداد الحقيقية)")
            
            # a^x = b  =>  x = log_a(b)
            x_exact = sp.log(b) / sp.log(a)
            x_decimal = float(sp.N(x_exact))
            
            # التحقق
            verification = abs(a ** x_decimal - b) < self.precision
            
            result = {
                'template_id': template_id,
                'template_name': 'exponential_different_base',
                'template_name_ar': 'معادلة أسية - أساس مختلف',
                'input': {'a': a, 'b': b},
                'equation': f"{a}^x = {b}",
                'solution': {
                    'exact': str(x_exact),
                    'decimal': x_decimal,
                    'logarithmic_form': f"x = log_{a}({b}) = ln({b})/ln({a})"
                },
                'verification': {
                    'substituted': a ** x_decimal,
                    'expected': b,
                    'error': abs(a ** x_decimal - b),
                    'is_valid': verification
                },
                'domain': 'x ∈ ℝ',
                'conditions': f'a > 0, a ≠ 1, b > 0'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def template_78_exponential_quadratic(self, a: float, b: float, c: float) -> Dict[str, Any]:
        """
        قالب 78: معادلة أسية تربيعية: a^(2x) + b·a^x + c = 0
        """
        template_id = 78
        self.stats['total_calls'] += 1
        
        try:
            # التحقق من الأساس
            if a <= 0:
                raise ValueError(f"الأساس a = {a} يجب أن يكون موجباً")
            if a == 1:
                raise ValueError("الأساس a لا يمكن أن يساوي 1")
            
            # تعويض y = a^x
            # المعادلة تصبح: y² + b·y + c = 0
            
            # حل المعادلة التربيعية في y
            discriminant = b**2 - 4*c
            
            solutions = []
            y_solutions = []
            steps = []
            
            steps.append(f"1. نعوض y = {a}^x")
            steps.append(f"2. المعادلة تصبح: y² + {b}y + {c} = 0")
            steps.append(f"3. المميز Δ = b² - 4c = {b}² - 4×{c} = {discriminant:.4f}")
            
            if discriminant < 0:
                steps.append("4. Δ < 0 → لا توجد حلول حقيقية لـ y")
                # حلول مركبة
                y1 = (-b + cmath.sqrt(discriminant)) / 2
                y2 = (-b - cmath.sqrt(discriminant)) / 2
                y_solutions = [y1, y2]
                steps.append(f"5. y = {y1:.4f} أو y = {y2:.4f} (حلول مركبة)")
            else:
                y1 = (-b + math.sqrt(discriminant)) / 2
                y2 = (-b - math.sqrt(discriminant)) / 2
                y_solutions = [y1, y2]
                steps.append(f"4. y = {y1:.4f} أو y = {y2:.4f}")
                
                # لكل y > 0، x = log_a(y)
                steps.append(f"5. نرجع إلى المتغير x: {a}^x = y")
                
                for i, y in enumerate([y1, y2], 1):
                    if y > 0:
                        x = math.log(y) / math.log(a)
                        solutions.append(x)
                        steps.append(f"   الحل {i}: {a}^x = {y:.4f}  ⇒  x = log_{a}({y:.4f}) = {x:.4f}")
                    elif y == 0:
                        steps.append(f"   y = 0 ليس له حل لأن {a}^x > 0 دائماً")
                    else:
                        steps.append(f"   y = {y:.4f} < 0 ليس له حل في الأعداد الحقيقية")
            
            result = {
                'template_id': template_id,
                'template_name': 'exponential_quadratic',
                'template_name_ar': 'معادلة أسية تربيعية',
                'input': {'a': a, 'b': b, 'c': c},
                'equation': f"{a}^(2x) + {b}·{a}^x + {c} = 0",
                'substitution': f"y = {a}^x",
                'quadratic': f"y² + {b}y + {c} = 0",
                'discriminant': discriminant,
                'y_solutions': [self._safe_float_conversion(y) for y in y_solutions],
                'x_solutions': solutions,
                'steps': steps,
                'condition': 'y > 0 للحصول على حلول حقيقية',
                'note': 'إذا كان y ≤ 0، فلا يوجد حل حقيقي لأن الدالة الأسية موجبة دائماً'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def template_79_exponential_system(self, eq1: str, eq2: str) -> Dict[str, Any]:
        """
        قالب 79: نظام معادلات أسية
        """
        template_id = 79
        self.stats['total_calls'] += 1
        
        try:
            # تنظيف المعادلات
            eq1 = eq1.replace(' ', '')
            eq2 = eq2.replace(' ', '')
            
            # تحليل المعادلات
            lhs1, rhs1 = eq1.split('=')
            lhs2, rhs2 = eq2.split('=')
            
            expr1 = sp.Eq(self._safe_sympify(lhs1), self._safe_sympify(rhs1))
            expr2 = sp.Eq(self._safe_sympify(lhs2), self._safe_sympify(rhs2))
            
            # حل النظام
            solution = sp.solve([expr1, expr2], [self.x, self.y])
            
            # تنظيم الحلول
            solutions_list = []
            if solution:
                if isinstance(solution, list):
                    for sol in solution:
                        sol_dict = {}
                        if self.x in sol:
                            sol_dict['x'] = self._safe_float_conversion(sol[self.x])
                        if self.y in sol:
                            sol_dict['y'] = self._safe_float_conversion(sol[self.y])
                        solutions_list.append(sol_dict)
                else:
                    sol_dict = {}
                    if self.x in solution:
                        sol_dict['x'] = self._safe_float_conversion(solution[self.x])
                    if self.y in solution:
                        sol_dict['y'] = self._safe_float_conversion(solution[self.y])
                    solutions_list.append(sol_dict)
            
            # التحقق من الحلول
            verification = []
            for sol_dict in solutions_list:
                try:
                    x_val = sol_dict.get('x')
                    y_val = sol_dict.get('y')
                    
                    if x_val is not None and y_val is not None:
                        # تعويض في المعادلة الأولى
                        left1 = float(sp.N(expr1.lhs.subs({self.x: x_val, self.y: y_val})))
                        right1 = float(sp.N(expr1.rhs.subs({self.x: x_val, self.y: y_val})))
                        
                        # تعويض في المعادلة الثانية
                        left2 = float(sp.N(expr2.lhs.subs({self.x: x_val, self.y: y_val})))
                        right2 = float(sp.N(expr2.rhs.subs({self.x: x_val, self.y: y_val})))
                        
                        verification.append({
                            'solution': sol_dict,
                            'eq1': {'left': left1, 'right': right1, 'error': abs(left1 - right1)},
                            'eq2': {'left': left2, 'right': right2, 'error': abs(left2 - right2)},
                            'is_valid': abs(left1 - right1) < self.precision and abs(left2 - right2) < self.precision
                        })
                except:
                    verification.append({
                        'solution': sol_dict,
                        'error': 'فشل التحقق'
                    })
            
            result = {
                'template_id': template_id,
                'template_name': 'exponential_system',
                'template_name_ar': 'نظام معادلات أسية',
                'input': {'eq1': eq1, 'eq2': eq2},
                'equations': [str(expr1), str(expr2)],
                'solutions': solutions_list,
                'num_solutions': len(solutions_list),
                'verification': verification,
                'method': 'حل نظام المعادلات باستخدام خواص الأسس واللوغاريتمات'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def template_80_exponential_word_problems(self, problem_type: str, values: Dict) -> Dict[str, Any]:
        """
        قالب 80: مسائل كلامية على المعادلات الأسية
        """
        template_id = 80
        self.stats['total_calls'] += 1
        
        try:
            problem_types = {
                'population_growth': {
                    'name': 'النمو السكاني',
                    'formula': 'P(t) = P₀ × e^(kt)',
                    'description': 'P(t): السكان بعد t سنة، P₀: السكان الابتدائي، k: معدل النمو',
                    'variables': ['P₀', 'k', 't', 'P(t)']
                },
                'radioactive_decay': {
                    'name': 'الاضمحلال الإشعاعي',
                    'formula': 'A(t) = A₀ × e^(-λt)',
                    'description': 'A(t): الكمية المتبقية بعد t زمن، A₀: الكمية الابتدائية، λ: ثابت الاضمحلال',
                    'variables': ['A₀', 'λ', 't', 'A(t)']
                },
                'compound_interest': {
                    'name': 'الفائدة المركبة',
                    'formula': 'A = P(1 + r/n)^(nt)',
                    'description': 'A: المبلغ النهائي، P: المبلغ الأصلي، r: معدل الفائدة، n: عدد مرات التحويل، t: الزمن',
                    'variables': ['P', 'r', 'n', 't', 'A']
                },
                'carbon_dating': {
                    'name': 'التأريخ بالكربون',
                    'formula': 't = (1/λ) × ln(A₀/A)',
                    'description': 't: العمر، λ: ثابت الاضمحلال، A₀: النسبة الابتدائية، A: النسبة الحالية',
                    'variables': ['λ', 'A₀', 'A', 't']
                }
            }
            
            if problem_type not in problem_types:
                raise ValueError(f'نوع المسألة غير معروف: {problem_type}. الأنواع المتاحة: {list(problem_types.keys())}')
            
            app = problem_types[problem_type]
            
            # حساب حسب المعطيات المتوفرة
            calculation = None
            steps = []
            
            if problem_type == 'population_growth':
                if 'P₀' in values and 'k' in values and 't' in values:
                    P0 = values['P₀']
                    k = values['k']
                    t = values['t']
                    P = P0 * math.exp(k * t)
                    steps = [
                        f"نطبق قانون النمو السكاني: P(t) = P₀ × e^(kt)",
                        f"P({t}) = {P0} × e^({k}×{t})",
                        f"P({t}) = {P0} × e^{k*t:.4f}",
                        f"P({t}) = {P:.4f}"
                    ]
                    calculation = {
                        'initial': P0,
                        'growth_rate': k,
                        'time': t,
                        'final': P,
                        'steps': steps
                    }
                elif 'P₀' in values and 'P' in values and 't' in values:
                    # إيجاد معدل النمو
                    P0 = values['P₀']
                    P = values['P']
                    t = values['t']
                    k = math.log(P / P0) / t
                    steps = [
                        f"نستخدم القانون: k = ln(P/P₀)/t",
                        f"k = ln({P}/{P0})/{t}",
                        f"k = ln({P/P0:.4f})/{t}",
                        f"k = {k:.4f}"
                    ]
                    calculation = {
                        'initial': P0,
                        'final': P,
                        'time': t,
                        'growth_rate': k,
                        'steps': steps
                    }
            
            elif problem_type == 'compound_interest':
                if all(k in values for k in ['P', 'r', 'n', 't']):
                    P = values['P']
                    r = values['r']
                    n = values['n']
                    t = values['t']
                    A = P * (1 + r/n) ** (n * t)
                    steps = [
                        f"نطبق قانون الفائدة المركبة: A = P(1 + r/n)^(nt)",
                        f"A = {P} × (1 + {r}/{n})^{{{n}×{t}}}",
                        f"A = {P} × ({1 + r/n:.4f})^{{{n*t}}}",
                        f"A = {A:.4f}"
                    ]
                    calculation = {
                        'principal': P,
                        'rate': r,
                        'compounding_per_year': n,
                        'time': t,
                        'final': A,
                        'steps': steps
                    }
            
            result = {
                'template_id': template_id,
                'template_name': 'exponential_word_problems',
                'template_name_ar': 'مسائل كلامية - معادلات أسية',
                'input': {'problem_type': problem_type, 'values': values},
                'problem_info': {
                    'name': app['name'],
                    'formula': app['formula'],
                    'description': app['description'],
                    'variables': app['variables']
                },
                'calculation': calculation,
                'examples': self._get_exponential_examples(problem_type),
                'note': 'تأكد من استخدام نفس الوحدات للزمن'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    # =========================================================================
    # القسم 16: المعادلات الكسرية (5 قوالب) - Templates 81-85
    # =========================================================================
    
    def template_81_rational_simple(self, numerator: str, denominator: str, value: float) -> Dict[str, Any]:
        """
        قالب 81: معادلة كسرية بسيطة
        """
        template_id = 81
        self.stats['total_calls'] += 1
        
        try:
            # تحويل البسط والمقام
            num_expr = self._safe_sympify(numerator)
            den_expr = self._safe_sympify(denominator)
            
            # (num)/(den) = value
            equation = sp.Eq(num_expr / den_expr, value)
            
            # ضرب الطرفين في المقام
            cleared = sp.Eq(num_expr, value * den_expr)
            
            # حل المعادلة
            solutions = self._safe_solve(cleared, self.x)
            
            # إيجاد قيم المقام
            den_solutions = sp.solve(den_expr, self.x)
            excluded = [float(sp.N(s)) for s in den_solutions if s.is_real]
            
            # استبعاد الحلول التي تجعل المقام صفراً
            valid_solutions = []
            verification = []
            
            for sol in solutions:
                try:
                    den_val = float(sp.N(den_expr.subs(self.x, sol)))
                    num_val = float(sp.N(num_expr.subs(self.x, sol)))
                    
                    if abs(den_val) > self.precision:
                        sol_val = float(sp.N(sol))
                        valid_solutions.append(sol_val)
                        verification.append({
                            'solution': sol_val,
                            'numerator': num_val,
                            'denominator': den_val,
                            'fraction_value': num_val / den_val,
                            'expected': value,
                            'error': abs(num_val/den_val - value),
                            'is_valid': abs(num_val/den_val - value) < self.precision
                        })
                except:
                    continue
            
            result = {
                'template_id': template_id,
                'template_name': 'rational_simple',
                'template_name_ar': 'معادلة كسرية بسيطة',
                'input': {'numerator': numerator, 'denominator': denominator, 'value': value},
                'equation': f"({numerator})/({denominator}) = {value}",
                'cleared_equation': f"{numerator} = {value}·({denominator})",
                'solutions': valid_solutions,
                'excluded_values': excluded,
                'domain': f"{denominator} ≠ 0",
                'verification': verification,
                'steps': [
                    f"1. المعادلة: ({numerator})/({denominator}) = {value}",
                    f"2. نضرب الطرفين في ({denominator}): {numerator} = {value}·({denominator})",
                    f"3. نحل المعادلة: {str(cleared)}",
                    f"4. نستبعد الحلول التي تجعل {denominator} = 0"
                ]
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def template_82_rational_sum(self, fractions: List[str], value: float) -> Dict[str, Any]:
        """
        قالب 82: معادلة كسرية بمجموع كسور - نسخة محسنة
        """
        template_id = 82
        self.stats['total_calls'] += 1
        
        try:
            # تحويل الكسور إلى تعبيرات
            frac_exprs = [self._safe_sympify(f) for f in fractions]
            
            # مجموع الكسور
            total = sp.Add(*frac_exprs)
            
            # تبسيط المجموع
            simplified = sp.simplify(total)
            equation = sp.Eq(simplified, value)
            
            # حل المعادلة
            solutions = self._safe_solve(equation, self.x)
            
            # استخراج جميع المقامات
            denominators = []
            for frac in frac_exprs:
                # البحث عن المقامات في الكسر
                if frac.is_Mul:
                    for arg in frac.args:
                        if isinstance(arg, sp.Pow) and arg.exp == -1:
                            denominators.append(arg.base)
                elif isinstance(frac, sp.Pow) and frac.exp == -1:
                    denominators.append(frac.base)
                elif frac.is_Add:
                    # قد يكون الكسر على صورة (A+B)/C
                    for term in frac.args:
                        if term.is_Pow and term.exp == -1:
                            denominators.append(term.base)
            
            # إيجاد القيم المستبعدة
            excluded = []
            for den in denominators:
                den_sols = sp.solve(den, self.x)
                for sol in den_sols:
                    if sol.is_real:
                        excluded.append(float(sp.N(sol)))
            
            # التحقق من الحلول
            valid_solutions = []
            verification = []
            
            for sol in solutions:
                try:
                    valid = True
                    total_val = float(sp.N(total.subs(self.x, sol)))
                    
                    # التحقق من المقامات
                    for den in denominators:
                        den_val = float(sp.N(den.subs(self.x, sol)))
                        if abs(den_val) < self.precision:
                            valid = False
                            break
                    
                    if valid:
                        sol_val = float(sp.N(sol))
                        valid_solutions.append(sol_val)
                        verification.append({
                            'solution': sol_val,
                            'total_value': total_val,
                            'expected': value,
                            'error': abs(total_val - value),
                            'is_valid': abs(total_val - value) < self.precision
                        })
                except:
                    continue
            
            result = {
                'template_id': template_id,
                'template_name': 'rational_sum',
                'template_name_ar': 'معادلة كسرية - مجموع كسور',
                'input': {'fractions': fractions, 'value': value},
                'equation': ' + '.join(fractions) + f" = {value}",
                'simplified': str(simplified),
                'solutions': valid_solutions,
                'excluded_values': list(set(excluded)),
                'denominators': [str(d) for d in set(denominators)],
                'verification': verification,
                'steps': [
                    f"1. نجمع الكسور: {' + '.join(fractions)}",
                    f"2. نبسط المجموع: {simplified}",
                    f"3. نحل المعادلة: {simplified} = {value}",
                    f"4. نستبعد الحلول التي تجعل أي مقام = 0"
                ]
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def template_83_rational_equality(self, frac1: str, frac2: str) -> Dict[str, Any]:
        """
        قالب 83: تساوي كسرين
        """
        template_id = 83
        self.stats['total_calls'] += 1
        
        try:
            # تحويل الكسور
            f1 = self._safe_sympify(frac1)
            f2 = self._safe_sympify(frac2)
            
            # f1 = f2
            equation = sp.Eq(f1, f2)
            
            # حل المعادلة
            solutions = self._safe_solve(equation, self.x)
            
            # استخراج المقامات
            denominators = []
            
            def extract_denominators(expr):
                if isinstance(expr, sp.Pow) and expr.exp == -1:
                    denominators.append(expr.base)
                elif expr.is_Mul:
                    for arg in expr.args:
                        extract_denominators(arg)
                elif expr.is_Add:
                    for arg in expr.args:
                        extract_denominators(arg)
            
            extract_denominators(f1)
            extract_denominators(f2)
            
            # إيجاد القيم المستبعدة
            excluded = []
            for den in set(denominators):
                den_sols = sp.solve(den, self.x)
                for sol in den_sols:
                    if sol.is_real:
                        excluded.append(float(sp.N(sol)))
            
            # التحقق من الحلول
            valid_solutions = []
            verification = []
            
            for sol in solutions:
                try:
                    valid = True
                    
                    # التحقق من المقامات
                    for den in set(denominators):
                        den_val = float(sp.N(den.subs(self.x, sol)))
                        if abs(den_val) < self.precision:
                            valid = False
                            break
                    
                    if valid:
                        sol_val = float(sp.N(sol))
                        valid_solutions.append(sol_val)
                        
                        # حساب قيم الكسرين
                        f1_val = float(sp.N(f1.subs(self.x, sol)))
                        f2_val = float(sp.N(f2.subs(self.x, sol)))
                        
                        verification.append({
                            'solution': sol_val,
                            'frac1_value': f1_val,
                            'frac2_value': f2_val,
                            'difference': abs(f1_val - f2_val),
                            'is_valid': abs(f1_val - f2_val) < self.precision
                        })
                except:
                    continue
            
            result = {
                'template_id': template_id,
                'template_name': 'rational_equality',
                'template_name_ar': 'تساوي كسرين',
                'input': {'frac1': frac1, 'frac2': frac2},
                'equation': f"{frac1} = {frac2}",
                'solutions': valid_solutions,
                'excluded_values': list(set(excluded)),
                'domain': f"{' ≠ 0 و '.join([str(d) for d in set(denominators)])} ≠ 0" if denominators else 'جميع الأعداد',
                'verification': verification,
                'method': 'ضرب الطرفين في المقامات المشتركة ثم حل المعادلة'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def template_84_rational_inequality(self, numerator: str, denominator: str, inequality: str) -> Dict[str, Any]:
        """
        قالب 84: متباينة كسرية
        """
        template_id = 84
        self.stats['total_calls'] += 1
        
        try:
            # تحويل البسط والمقام
            num = self._safe_sympify(numerator)
            den = self._safe_sympify(denominator)
            
            # التعبير الكسري
            rational_expr = num / den
            
            # إيجاد النقاط الحرجة (أصفار البسط والمقام)
            zeros_num = sp.solve(num, self.x)
            zeros_den = sp.solve(den, self.x)
            
            critical_points = []
            for z in zeros_num + zeros_den:
                if z.is_real:
                    critical_points.append(float(sp.N(z)))
            
            critical_points = sorted(set(critical_points))
            
            # إنشاء الفترات
            intervals = []
            if critical_points:
                intervals.append(('-inf', critical_points[0]))
                for i in range(len(critical_points)-1):
                    intervals.append((critical_points[i], critical_points[i+1]))
                intervals.append((critical_points[-1], 'inf'))
            else:
                intervals.append(('-inf', 'inf'))
            
            # اختبار الإشارات
            sign_chart = []
            solution_intervals = []
            
            for interval in intervals:
                # اختيار نقطة اختبار
                if interval[0] == '-inf':
                    test_x = critical_points[0] - 1 if critical_points else 0
                elif interval[1] == 'inf':
                    test_x = critical_points[-1] + 1 if critical_points else 0
                else:
                    test_x = (interval[0] + interval[1]) / 2
                
                # حساب قيمة التعبير
                try:
                    val = float(sp.N(rational_expr.subs(self.x, test_x)))
                    sign = 'موجب' if val > 0 else 'سالب' if val < 0 else 'صفر'
                    
                    sign_chart.append({
                        'interval': f"{interval[0]} < x < {interval[1]}",
                        'test_point': test_x,
                        'value': val,
                        'sign': sign
                    })
                    
                    # تحديد الحل حسب المتباينة
                    if inequality == '>0' and val > 0:
                        solution_intervals.append(f"{interval[0]} < x < {interval[1]}")
                    elif inequality == '≥0' and val >= 0:
                        solution_intervals.append(f"{interval[0]} < x < {interval[1]}")
                    elif inequality == '<0' and val < 0:
                        solution_intervals.append(f"{interval[0]} < x < {interval[1]}")
                    elif inequality == '≤0' and val <= 0:
                        solution_intervals.append(f"{interval[0]} < x < {interval[1]}")
                except:
                    continue
            
            # معالجة النقاط الحرجة للمتباينات غير الصارمة
            if inequality in ['≥0', '≤0']:
                for point in critical_points:
                    # التحقق مما إذا كانت النقطة في مجال الدالة
                    if point not in [float(sp.N(z)) for z in zeros_den]:
                        if (inequality == '≥0' and float(sp.N(num.subs(self.x, point))) >= 0) or \
                           (inequality == '≤0' and float(sp.N(num.subs(self.x, point))) <= 0):
                            # نضيف النقطة كحل منفرد
                            solution_intervals.append(f"x = {point}")
            
            # ترتيب الحلول
            solution_intervals = list(set(solution_intervals))
            
            result = {
                'template_id': template_id,
                'template_name': 'rational_inequality',
                'template_name_ar': 'متباينة كسرية',
                'input': {'numerator': numerator, 'denominator': denominator, 'inequality': inequality},
                'inequality': f"({numerator})/({denominator}) {inequality}",
                'critical_points': critical_points,
                'zeros_numerator': [float(sp.N(z)) for z in zeros_num if z.is_real],
                'zeros_denominator': [float(sp.N(z)) for z in zeros_den if z.is_real],
                'sign_chart': sign_chart,
                'solution': ' أو '.join(solution_intervals) if solution_intervals else 'لا يوجد حل',
                'interval_notation': solution_intervals,
                'excluded_values': [float(sp.N(z)) for z in zeros_den if z.is_real],
                'method': 'طريقة جدول الإشارات باستخدام النقاط الحرجة'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def template_85_rational_parametric(self, numerator: str, denominator: str, parameter: str) -> Dict[str, Any]:
        """
        قالب 85: معادلة كسرية مع باراميتر (محسنة)
        """
        template_id = 85
        self.stats['total_calls'] += 1
        
        try:
            # إنشاء رمز الباراميتر
            k = sp.Symbol(parameter, real=True)
            
            # تحويل التعبيرات مع استبدال الباراميتر
            num_expr = self._safe_sympify(numerator)
            den_expr = self._safe_sympify(denominator)
            
            # المعادلة: (num)/(den) = 0
            equation = sp.Eq(num_expr / den_expr, 0)
            
            # حل المعادلة بدلالة x
            x_solutions = sp.solve(equation, self.x)
            
            # تحليل قيم الباراميتر الخاصة
            special_values = []
            
            # 1. قيم k التي تجعل المقام صفراً
            denom_k = sp.solve(den_expr, k)
            for val in denom_k:
                special_values.append({
                    'value': self._safe_float_conversion(val),
                    'type': 'denominator_zero',
                    'description': f'عند {parameter} = {val}، المقام يصفر (خارج المجال)'
                })
            
            # 2. قيم k التي تجعل البسط والمقام يلغيان بعضهما
            # نبحث عن عوامل مشتركة
            try:
                gcd_expr = sp.gcd(num_expr, den_expr)
                if gcd_expr != 1:
                    # هناك عامل مشترك
                    cancel_k = sp.solve(gcd_expr, k)
                    for val in cancel_k:
                        special_values.append({
                            'value': self._safe_float_conversion(val),
                            'type': 'common_factor',
                            'description': f'عند {parameter} = {val}، يوجد عامل مشترك في البسط والمقام'
                        })
            except:
                pass
            
            # 3. قيم k التي تجعل الحل فريداً أو مستحيلاً
            # تحليل عدد الحلول بدلالة k
            solution_analysis = []
            for sol in x_solutions:
                # التحقق من شروط وجود الحل
                condition = f"{den_expr} ≠ 0"
                solution_analysis.append({
                    'solution': str(sol),
                    'condition': condition,
                    'note': f'الحل صالح عندما يتحقق الشرط'
                })
            
            result = {
                'template_id': template_id,
                'template_name': 'rational_parametric',
                'template_name_ar': 'معادلة كسرية مع باراميتر',
                'input': {'numerator': numerator, 'denominator': denominator, 'parameter': parameter},
                'equation': f"({numerator})/({denominator}) = 0",
                'parameter_analysis': {
                    'symbol': parameter,
                    'special_values': special_values,
                    'general_case': f'عندما {parameter} لا يأخذ القيم الخاصة'
                },
                'solutions': [str(s) for s in x_solutions] if x_solutions else ['لا يوجد حل عام'],
                'solution_analysis': solution_analysis,
                'domain_condition': f"{denominator} ≠ 0",
                'method': 'حل المعادلة مع اعتبار الباراميتر ثابتاً، ثم دراسة الحالات الخاصة'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {
                'template_id': template_id,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    # =========================================================================
    # القسم 17: المعادلات المطلقة (5 قوالب) - Templates 86-90
    # =========================================================================
    
    def template_86_absolute_simple(self, expression: str, value: float) -> Dict[str, Any]:
        """
        قالب 86: معادلة قيمة مطلقة بسيطة: |ax + b| = c (نسخة محسنة تماماً)
        """
        template_id = 86
        self.stats['total_calls'] += 1
        
        try:
            # تحويل التعبير إلى SymPy باستخدام Abs
            # نستبدل |expression| بـ Abs(expression)
            expr_str = expression.replace('|', 'Abs')
            expr = self._safe_sympify(expr_str)
            
            # استخراج التعبير داخل القيمة المطلقة
            inner_expr = None
            if isinstance(expr, sp.Abs):
                inner_expr = expr.args[0]
            else:
                # إذا كان التعبير معقداً، نحاول استخراج Abs
                for arg in sp.preorder_traversal(expr):
                    if isinstance(arg, sp.Abs):
                        inner_expr = arg.args[0]
                        break
            
            if inner_expr is None:
                # إذا لم نجد Abs، نفترض أن التعبير كله داخل Abs
                inner_expr = expr
                expr = sp.Abs(inner_expr)
            
            # معالجة الحالات المختلفة
            if value < 0:
                # القيمة المطلقة لا يمكن أن تكون سالبة
                solutions = []
                cases = []
                solution_type = 'no_solution'
                solution_message = "لا يوجد حل لأن القيمة المطلقة لا يمكن أن تكون سالبة"
                
            elif abs(value) < self.precision:
                # |expr| = 0  ⇒  expr = 0
                eq = sp.Eq(inner_expr, 0)
                solutions = self._safe_solve(eq, self.x)
                cases = [{
                    'case': f"{inner_expr} = 0", 
                    'solutions': [self._safe_float_conversion(s) for s in solutions if s.is_real]
                }]
                solution_type = 'single' if len(solutions) == 1 else 'multiple'
                solution_message = f"x = {', '.join([str(self._safe_float_conversion(s)) for s in solutions])}" if solutions else "لا يوجد حل"
                
            else:
                # |expr| = c  ⇒  expr = c أو expr = -c
                eq1 = sp.Eq(inner_expr, value)
                eq2 = sp.Eq(inner_expr, -value)
                
                sol1 = self._safe_solve(eq1, self.x)
                sol2 = self._safe_solve(eq2, self.x)
                
                solutions = sol1 + sol2
                cases = [
                    {
                        'case': f"{inner_expr} = {value}", 
                        'solutions': [self._safe_float_conversion(s) for s in sol1 if s.is_real]
                    },
                    {
                        'case': f"{inner_expr} = {-value}", 
                        'solutions': [self._safe_float_conversion(s) for s in sol2 if s.is_real]
                    }
                ]
                solution_type = 'two_solutions' if len(solutions) == 2 else 'multiple'
                solution_message = f"x = {', '.join([str(self._safe_float_conversion(s)) for s in solutions])}" if solutions else "لا يوجد حل"
            

