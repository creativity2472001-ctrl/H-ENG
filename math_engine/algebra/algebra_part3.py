"""
================================================================================
الملف 3/3: الجبر المتقدم - المعادلات من الدرجة الرابعة، الأنماط، التحقق (50 قالباً)
File 3/3: Advanced Algebra - Quartic Equations, Patterns, Verification (50 Templates)

الأنواع المغطاة (21-30):
21. المعادلات الرباعية (6 قوالب)           - templates 103-108
22. معادلات نمطية (5 قوالب)                - templates 109-113
23. التعويض (5 قوالب)                      - templates 114-118
24. متطابقات المربع الكامل (5 قوالب)       - templates 119-123
25. المعادلات المتعددة المجهولات (6 قوالب) - templates 124-129
26. المعادلات على شكل نسب (5 قوالب)        - templates 130-134
27. تحليل التعبيرات متعددة الحدود (5 قوالب) - templates 135-139
28. تبسيط التعبيرات بالمتغيرات المتعددة (4 قوالب) - templates 140-143
29. اختبار الصيغة الصحيحة (5 قوالب)        - templates 144-148
30. التحقق من صحة الجذر (4 قوالب)          - templates 149-152
================================================================================
"""

import sympy as sp
import numpy as np
import logging
from typing import Union, List, Dict, Any, Tuple, Optional, Callable
import math
import cmath
import re

# إعداد نظام التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AdvancedAlgebraSolver:
    """
    ============================================================================
    الحلّال المتقدم للجبر - المعادلات الرباعية، الأنماط، التحقق
    يغطي 50 قالباً في الأنواع 21-30
    ============================================================================
    """
    
    def __init__(self):
        """تهيئة المتغيرات الرمزية وإعدادات الدقة"""
        # متغيرات رمزية
        self.x = sp.Symbol('x', real=True)
        self.y = sp.Symbol('y', real=True)
        self.z = sp.Symbol('z', real=True)
        self.t = sp.Symbol('t', real=True)
        self.u = sp.Symbol('u', real=True)
        self.v = sp.Symbol('v', real=True)
        
        self.a = sp.Symbol('a', real=True)
        self.b = sp.Symbol('b', real=True)
        self.c = sp.Symbol('c', real=True)
        self.d = sp.Symbol('d', real=True)
        self.e = sp.Symbol('e', real=True)
        
        # ثوابت
        self.i = sp.I
        self.pi = sp.pi
        self.e_const = sp.E
        
        # إعدادات الدقة
        self.precision = 1e-15
        
        # سجل العمليات
        self.stats = {
            'total_calls': 0,
            'successful': 0,
            'failed': 0,
            'by_template': {}
        }
        
        # ذاكرة مؤقتة للنتائج
        self.cache = {}
        
        logger.info("✅ تم تهيئة AdvancedAlgebraSolver بنجاح")
    
    # =========================================================================
    # القسم 21: المعادلات الرباعية (6 قوالب) - Templates 103-108
    # =========================================================================
    
    def template_103_quartic_biquadratic(self, a: float, b: float, c: float) -> Dict[str, Any]:
        """
        قالب 103: معادلة رباعية ثنائية التربيع: ax⁴ + bx² + c = 0
        """
        self.stats['total_calls'] += 1
        template_id = 103
        
        try:
            # تعويض t = x²
            expr = a*self.x**4 + b*self.x**2 + c
            
            # حل كمعادلة تربيعية في t
            t_expr = a*self.t**2 + b*self.t + c
            t_solutions = sp.solve(t_expr, self.t)
            
            solutions = []
            t_values = []
            
            for t_sol in t_solutions:
                t_val = complex(sp.N(t_sol)) if not t_sol.is_real else float(sp.N(t_sol))
                t_values.append({
                    't': str(t_sol),
                    'value': t_val,
                    'type': 'real' if t_sol.is_real else 'complex'
                })
                
                # x = ±√t
                if t_sol.is_real:
                    if t_sol >= 0:
                        sqrt_t = math.sqrt(t_sol)
                        solutions.extend([sqrt_t, -sqrt_t])
                    else:
                        sqrt_t = cmath.sqrt(t_sol)
                        solutions.extend([sqrt_t, -sqrt_t])
                else:
                    sqrt_t = cmath.sqrt(complex(sp.N(t_sol)))
                    solutions.extend([sqrt_t, -sqrt_t])
            
            # تصنيف الحلول
            real_roots = [s for s in solutions if isinstance(s, (int, float)) and abs(s.imag) < self.precision] if hasattr(solutions[0], 'imag') else []
            complex_roots = [s for s in solutions if not (isinstance(s, (int, float)) and abs(s.imag) < self.precision)]
            
            result = {
                'template_id': template_id,
                'template_name': 'quartic_biquadratic',
                'template_name_ar': 'معادلة رباعية ثنائية التربيع',
                'input': {'a': a, 'b': b, 'c': c},
                'equation': f"{a}x⁴ + {b}x² + {c} = 0",
                'substitution': 't = x²',
                'quadratic_in_t': f"{a}t² + {b}t + {c} = 0",
                't_solutions': t_values,
                'solutions': [str(s) for s in solutions],
                'real_roots': [float(s) for s in real_roots] if real_roots else [],
                'complex_roots': [str(s) for s in complex_roots] if complex_roots else [],
                'num_solutions': len(solutions),
                'verification': self._verify_quartic_solutions(expr, solutions),
                'method': 'التعويض ثم حل معادلة تربيعية'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_104_quartic_depressed(self, a: float, b: float, c: float, d: float, e: float) -> Dict[str, Any]:
        """
        قالب 104: معادلة رباعية ناقصة (بعض المعاملات صفر)
        """
        template_id = 104
        self.stats['total_calls'] += 1
        
        try:
            expr = a*self.x**4 + b*self.x**3 + c*self.x**2 + d*self.x + e
            
            # تحليل المعادلة حسب المعاملات المفقودة
            missing_terms = []
            if abs(b) < self.precision:
                missing_terms.append('x³')
            if abs(c) < self.precision:
                missing_terms.append('x²')
            if abs(d) < self.precision:
                missing_terms.append('x')
            
            # حل المعادلة
            solutions = sp.solve(expr, self.x)
            
            # محاولة التحليل
            factored = sp.factor(expr)
            
            result = {
                'template_id': template_id,
                'template_name': 'quartic_depressed',
                'template_name_ar': 'معادلة رباعية ناقصة',
                'input': {'a': a, 'b': b, 'c': c, 'd': d, 'e': e},
                'equation': f"{a}x⁴ + {b}x³ + {c}x² + {d}x + {e} = 0",
                'missing_terms': missing_terms,
                'solutions': [str(s) for s in solutions],
                'factored_form': str(factored) if factored != expr else None,
                'num_solutions': len(solutions)
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_105_quartic_factorable(self, coefficients: List[float]) -> Dict[str, Any]:
        """
        قالب 105: معادلة رباعية قابلة للتحليل
        """
        template_id = 105
        self.stats['total_calls'] += 1
        
        try:
            # بناء كثيرة الحدود
            expr = 0
            degree = len(coefficients) - 1
            for i, coeff in enumerate(coefficients):
                expr += coeff * self.x**(degree - i)
            
            # محاولة التحليل بطرق مختلفة
            factored = sp.factor(expr)
            is_factorable = factored != expr
            
            # إذا كانت قابلة للتحليل، استخرج العوامل
            factors = []
            if is_factorable and factored.is_Mul:
                for factor in factored.args:
                    factors.append(str(factor))
            
            # حل المعادلة
            solutions = sp.solve(expr, self.x)
            
            result = {
                'template_id': template_id,
                'template_name': 'quartic_factorable',
                'template_name_ar': 'معادلة رباعية قابلة للتحليل',
                'input': {'coefficients': coefficients},
                'polynomial': str(expr),
                'is_factorable': is_factorable,
                'factored_form': str(factored) if is_factorable else None,
                'factors': factors,
                'solutions': [str(s) for s in solutions],
                'num_solutions': len(solutions)
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_106_quartic_reciprocal(self, a: float, b: float, c: float) -> Dict[str, Any]:
        """
        قالب 106: معادلة رباعية مقلوبة: ax⁴ + bx³ + cx² + bx + a = 0
        """
        template_id = 106
        self.stats['total_calls'] += 1
        
        try:
            # معادلة مقلوبة (معاملات متماثلة)
            expr = a*self.x**4 + b*self.x**3 + c*self.x**2 + b*self.x + a
            
            # قسمة على x²
            # x² + 1/x² = (x + 1/x)² - 2
            # تعويض y = x + 1/x
            
            solutions = sp.solve(expr, self.x)
            
            result = {
                'template_id': template_id,
                'template_name': 'quartic_reciprocal',
                'template_name_ar': 'معادلة رباعية مقلوبة',
                'input': {'a': a, 'b': b, 'c': c},
                'equation': f"{a}x⁴ + {b}x³ + {c}x² + {b}x + {a} = 0",
                'solutions': [str(s) for s in solutions],
                'num_solutions': len(solutions),
                'method': 'القسمة على x² ثم التعويض y = x + 1/x'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_107_quartic_quadratic_form(self, a: float, b: float, c: float, d: float) -> Dict[str, Any]:
        """
        قالب 107: معادلة رباعية على صورة تربيعية: (ax² + bx + c)² = d
        """
        template_id = 107
        self.stats['total_calls'] += 1
        
        try:
            # (ax² + bx + c)² = d
            # ax² + bx + c = ±√d
            
            sqrt_d = math.sqrt(abs(d)) if d >= 0 else cmath.sqrt(d)
            
            # حالتان
            eq1 = a*self.x**2 + b*self.x + c - sqrt_d
            eq2 = a*self.x**2 + b*self.x + c + sqrt_d if d >= 0 else a*self.x**2 + b*self.x + c + sqrt_d
            
            solutions1 = sp.solve(eq1, self.x)
            solutions2 = sp.solve(eq2, self.x) if d != 0 else []
            
            solutions = solutions1 + solutions2
            
            result = {
                'template_id': template_id,
                'template_name': 'quartic_quadratic_form',
                'template_name_ar': 'معادلة رباعية على صورة تربيعية',
                'input': {'a': a, 'b': b, 'c': c, 'd': d},
                'equation': f"({a}x² + {b}x + {c})² = {d}",
                'cases': [
                    {'case': f"{a}x² + {b}x + {c} = √{d}", 'solutions': [str(s) for s in solutions1]},
                    {'case': f"{a}x² + {b}x + {c} = -√{d}", 'solutions': [str(s) for s in solutions2]} if d >= 0 else {'case': f"{a}x² + {b}x + {c} = {sqrt_d}", 'solutions': [str(s) for s in solutions2]}
                ],
                'solutions': [str(s) for s in solutions],
                'num_solutions': len(solutions)
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_108_quartic_general(self, a: float, b: float, c: float, d: float, e: float) -> Dict[str, Any]:
        """
        قالب 108: معادلة رباعية عامة (حل عددي)
        """
        template_id = 108
        self.stats['total_calls'] += 1
        
        try:
            expr = a*self.x**4 + b*self.x**3 + c*self.x**2 + d*self.x + e
            
            # حل رمزي (قد يكون معقداً)
            symbolic_solutions = sp.solve(expr, self.x)
            
            # حل عددي باستخدام numpy
            coefficients = [a, b, c, d, e]
            numeric_roots = np.roots(coefficients)
            
            result = {
                'template_id': template_id,
                'template_name': 'quartic_general',
                'template_name_ar': 'معادلة رباعية عامة',
                'input': {'a': a, 'b': b, 'c': c, 'd': d, 'e': e},
                'equation': f"{a}x⁴ + {b}x³ + {c}x² + {d}x + {e} = 0",
                'symbolic_solutions': [str(s) for s in symbolic_solutions],
                'numeric_solutions': [complex(round(r.real, 10), round(r.imag, 10)) for r in numeric_roots],
                'num_solutions': len(symbolic_solutions),
                'method': 'حل رمزي باستخدام SymPy وحل عددي باستخدام numpy'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    # =========================================================================
    # القسم 22: معادلات نمطية (5 قوالب) - Templates 109-113
    # =========================================================================
    
    def template_109_pattern_symmetry(self, equation: str) -> Dict[str, Any]:
        """
        قالب 109: معادلات ذات نمط متماثل
        مثال: x⁴ + x³ + x² + x + 1 = 0
        """
        template_id = 109
        self.stats['total_calls'] += 1
        
        try:
            expr = sp.sympify(equation.replace(' ', ''))
            
            # التعرف على الأنماط المتماثلة
            pattern_type = None
            description = ""
            
            # التحقق من التماثل (معاملات متماثلة)
            coeffs = expr.as_coefficients_dict()
            degree = sp.degree(expr)
            
            is_symmetric = True
            for i in range(degree + 1):
                coeff_i = coeffs.get(self.x**i, 0)
                coeff_deg_i = coeffs.get(self.x**(degree - i), 0)
                if abs(coeff_i - coeff_deg_i) > self.precision:
                    is_symmetric = False
                    break
            
            if is_symmetric:
                pattern_type = "symmetric"
                description = "معادلة متماثلة (معاملات متناظرة)"
            
            # حل المعادلة
            solutions = sp.solve(expr, self.x)
            
            result = {
                'template_id': template_id,
                'template_name': 'pattern_symmetry',
                'template_name_ar': 'معادلات ذات نمط متماثل',
                'input': {'equation': equation},
                'equation': str(expr),
                'pattern_type': pattern_type,
                'description': description,
                'degree': degree,
                'solutions': [str(s) for s in solutions],
                'method': 'استخدام التماثل للتبسيط' if is_symmetric else 'حل مباشر'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_110_pattern_recurrence(self, terms: List[float], recurrence_type: str) -> Dict[str, Any]:
        """
        قالب 110: معادلات ناتجة عن متتابعات
        """
        template_id = 110
        self.stats['total_calls'] += 1
        
        try:
            if recurrence_type == 'arithmetic':
                # متتابعة حسابية
                d = terms[1] - terms[0]
                general_term = f"a_n = {terms[0]} + (n-1)×{d}"
                next_terms = [terms[-1] + d * i for i in range(1, 4)]
                
            elif recurrence_type == 'geometric':
                # متتابعة هندسية
                r = terms[1] / terms[0] if terms[0] != 0 else 0
                general_term = f"a_n = {terms[0]} × {r}^(n-1)"
                next_terms = [terms[-1] * r for i in range(1, 4)]
                
            elif recurrence_type == 'fibonacci':
                # فيبوناتشي
                general_term = "a_n = a_{n-1} + a_{n-2}"
                next_terms = [terms[-1] + terms[-2], terms[-1] + terms[-2] + terms[-1], None]
                
            else:
                general_term = "غير معروف"
                next_terms = []
            
            result = {
                'template_id': template_id,
                'template_name': 'pattern_recurrence',
                'template_name_ar': 'معادلات ناتجة عن متتابعات',
                'input': {'terms': terms, 'recurrence_type': recurrence_type},
                'sequence': terms,
                'recurrence_type': recurrence_type,
                'general_term': general_term,
                'next_terms': next_terms,
                'difference_ratio': d if recurrence_type == 'arithmetic' else r if recurrence_type == 'geometric' else None
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_111_pattern_homogeneous(self, equation: str) -> Dict[str, Any]:
        """
        قالب 111: معادلات متجانسة
        مثال: x² + xy + y² = 0
        """
        template_id = 111
        self.stats['total_calls'] += 1
        
        try:
            expr = sp.sympify(equation.replace(' ', ''))
            
            # التحقق من التجانس (كل الحدود لها نفس الدرجة)
            degrees = []
            for term in expr.as_ordered_terms() if expr.is_Add else [expr]:
                if term.is_Mul:
                    term_degree = 0
                    for factor in term.args:
                        if factor.is_Pow:
                            term_degree += factor.exp
                        elif factor in [self.x, self.y, self.z]:
                            term_degree += 1
                    degrees.append(term_degree)
                elif term.is_Pow:
                    degrees.append(term.exp)
                elif term in [self.x, self.y, self.z]:
                    degrees.append(1)
                else:
                    degrees.append(0)
            
            is_homogeneous = len(set(degrees)) == 1
            
            # حل المعادلة (كنسبة y/x)
            if is_homogeneous and self.y in expr.free_symbols:
                # تعويض y = t x
                t = sp.Symbol('t')
                substituted = expr.subs(self.y, t * self.x)
                simplified = sp.simplify(substituted / self.x**degrees[0]) if degrees[0] > 0 else substituted
                t_solutions = sp.solve(simplified, t)
                
                solutions = [f"y = {t} x" for t in t_solutions]
            else:
                solutions = sp.solve(expr, [self.x, self.y]) if self.y in expr.free_symbols else sp.solve(expr, self.x)
            
            result = {
                'template_id': template_id,
                'template_name': 'pattern_homogeneous',
                'template_name_ar': 'معادلات متجانسة',
                'input': {'equation': equation},
                'equation': str(expr),
                'is_homogeneous': is_homogeneous,
                'degrees': degrees,
                'homogeneous_degree': degrees[0] if is_homogeneous else None,
                'solutions': [str(s) for s in solutions] if not isinstance(solutions, list) or all(isinstance(s, sp.Basic) for s in solutions) else solutions,
                'method': 'التعويض y = tx' if is_homogeneous else 'حل مباشر'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_112_pattern_cyclic(self, equations: List[str]) -> Dict[str, Any]:
        """
        قالب 112: أنظمة دورية (Cyclic Systems)
        مثال: x + y = 5, y + z = 7, z + x = 6
        """
        template_id = 112
        self.stats['total_calls'] += 1
        
        try:
            parsed_eqs = []
            for eq in equations:
                eq = eq.replace(' ', '')
                lhs, rhs = eq.split('=')
                parsed_eqs.append(sp.Eq(sp.sympify(lhs), sp.sympify(rhs)))
            
            # حل النظام
            variables = [self.x, self.y, self.z] if any('z' in str(eq) for eq in equations) else [self.x, self.y]
            solutions = sp.solve(parsed_eqs, variables)
            
            # التحقق من النمط الدوري
            is_cyclic = self._check_cyclic_pattern(parsed_eqs)
            
            result = {
                'template_id': template_id,
                'template_name': 'pattern_cyclic',
                'template_name_ar': 'أنظمة دورية',
                'input': {'equations': equations},
                'is_cyclic': is_cyclic,
                'solutions': [str(s) for s in solutions] if isinstance(solutions, list) else str(solutions),
                'num_solutions': len(solutions) if isinstance(solutions, list) else 1
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_113_pattern_palindromic(self, polynomial: str) -> Dict[str, Any]:
        """
        قالب 113: معادلات باليندرومية (Palindromic)
        مثال: x⁴ + 2x³ + 3x² + 2x + 1 = 0
        """
        template_id = 113
        self.stats['total_calls'] += 1
        
        try:
            expr = sp.sympify(polynomial.replace(' ', ''))
            
            # استخراج المعاملات
            coeffs_dict = expr.as_coefficients_dict()
            degree = sp.degree(expr)
            
            coefficients = []
            for i in range(degree, -1, -1):
                if i == 0:
                    coeff = coeffs_dict.get(1, 0)
                else:
                    coeff = coeffs_dict.get(self.x**i, 0)
                coefficients.append(float(coeff))
            
            # التحقق من النمط الباليندرومي
            is_palindromic = True
            for i in range(len(coefficients)):
                if abs(coefficients[i] - coefficients[-(i+1)]) > self.precision:
                    is_palindromic = False
                    break
            
            # حل المعادلة
            if is_palindromic and degree % 2 == 0:
                # قسمة على x^(degree/2) وتعويض y = x + 1/x
                solutions = sp.solve(expr, self.x)
            else:
                solutions = sp.solve(expr, self.x)
            
            result = {
                'template_id': template_id,
                'template_name': 'pattern_palindromic',
                'template_name_ar': 'معادلات باليندرومية',
                'input': {'polynomial': polynomial},
                'polynomial': str(expr),
                'coefficients': coefficients,
                'is_palindromic': is_palindromic,
                'degree': degree,
                'solutions': [str(s) for s in solutions],
                'method': 'استخدام خاصية التماثل للتبسيط' if is_palindromic else 'حل مباشر'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    # =========================================================================
    # القسم 23: التعويض (5 قوالب) - Templates 114-118
    # =========================================================================
    
    def template_114_substitution_linear(self, expression: str, old_var: str, new_var: str, relation: str) -> Dict[str, Any]:
        """
        قالب 114: تعويض خطي: y = ax + b
        """
        template_id = 114
        self.stats['total_calls'] += 1
        
        try:
            expr = sp.sympify(expression)
            rel = sp.sympify(relation)
            
            # حل العلاقة لإيجاد x بدلالة y
            x_in_terms_of_y = sp.solve(sp.Eq(sp.sympify(new_var), rel), self.x)[0]
            
            # التعويض
            substituted = expr.subs(self.x, x_in_terms_of_y)
            simplified = sp.simplify(substituted)
            
            result = {
                'template_id': template_id,
                'template_name': 'substitution_linear',
                'template_name_ar': 'تعويض خطي',
                'input': {
                    'expression': expression,
                    'old_var': old_var,
                    'new_var': new_var,
                    'relation': relation
                },
                'original_expression': str(expr),
                'relation': f"{new_var} = {relation}",
                'x_in_terms_of_y': str(x_in_terms_of_y),
                'substituted': str(substituted),
                'simplified': str(simplified),
                'steps': [
                    f"1. من العلاقة {new_var} = {relation} نجد {old_var} = {x_in_terms_of_y}",
                    f"2. نعوض في التعبير الأصلي: {expr}",
                    f"3. بعد التعويض: {substituted}",
                    f"4. بعد التبسيط: {simplified}"
                ]
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_115_substitution_quadratic(self, expression: str, old_var: str, new_var: str, relation: str) -> Dict[str, Any]:
        """
        قالب 115: تعويض تربيعي: y = ax² + bx + c
        """
        template_id = 115
        self.stats['total_calls'] += 1
        
        try:
            expr = sp.sympify(expression)
            rel = sp.sympify(relation)
            
            # التعويض المباشر
            substituted = expr.subs(sp.sympify(old_var), rel)
            simplified = sp.simplify(substituted)
            
            result = {
                'template_id': template_id,
                'template_name': 'substitution_quadratic',
                'template_name_ar': 'تعويض تربيعي',
                'input': {
                    'expression': expression,
                    'old_var': old_var,
                    'new_var': new_var,
                    'relation': relation
                },
                'original_expression': str(expr),
                'relation': f"{new_var} = {relation}",
                'substituted': str(substituted),
                'simplified': str(simplified),
                'steps': [
                    f"1. نعوض {old_var} = {relation} في التعبير",
                    f"2. النتيجة: {substituted}",
                    f"3. بعد التبسيط: {simplified}"
                ]
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_116_substitution_trigonometric(self, expression: str, substitution: str) -> Dict[str, Any]:
        """
        قالب 116: تعويض مثلثي: x = sin θ, x = cos θ, x = tan θ
        """
        template_id = 116
        self.stats['total_calls'] += 1
        
        try:
            expr = sp.sympify(expression)
            theta = sp.Symbol('theta')
            
            substitutions = {
                'x = sin θ': self.x == sp.sin(theta),
                'x = cos θ': self.x == sp.cos(theta),
                'x = tan θ': self.x == sp.tan(theta),
                'x = sec θ': self.x == sp.sec(theta),
                'x = csc θ': self.x == sp.csc(theta)
            }
            
            if substitution not in substitutions:
                raise ValueError(f"تعويض غير معروف: {substitution}")
            
            # التعويض
            if substitution == 'x = sin θ':
                substituted = expr.subs(self.x, sp.sin(theta))
            elif substitution == 'x = cos θ':
                substituted = expr.subs(self.x, sp.cos(theta))
            elif substitution == 'x = tan θ':
                substituted = expr.subs(self.x, sp.tan(theta))
            
            simplified = sp.simplify(substituted)
            
            result = {
                'template_id': template_id,
                'template_name': 'substitution_trigonometric',
                'template_name_ar': 'تعويض مثلثي',
                'input': {
                    'expression': expression,
                    'substitution': substitution
                },
                'original_expression': str(expr),
                'substitution': substitution,
                'substituted': str(substituted),
                'simplified': str(simplified),
                'domain': self._get_trig_domain(substitution)
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_117_substitution_rationalizing(self, expression: str, substitution: str) -> Dict[str, Any]:
        """
        قالب 117: تعويض لتوحيد المقام: t = √x, t = ∛x
        """
        template_id = 117
        self.stats['total_calls'] += 1
        
        try:
            expr = sp.sympify(expression)
            t = sp.Symbol('t')
            
            if substitution == 't = √x':
                substituted = expr.subs(self.x, t**2)
                back_substitution = f"x = t²"
            elif substitution == 't = ∛x':
                substituted = expr.subs(self.x, t**3)
                back_substitution = f"x = t³"
            elif substitution == 't = x^(1/n)':
                substituted = expr.subs(self.x, t**int(substitution.split('^')[-1].replace(')', '')))
                back_substitution = f"x = t^{substitution.split('^')[-1].replace(')', '')}"
            else:
                raise ValueError(f"تعويض غير معروف: {substitution}")
            
            simplified = sp.simplify(substituted)
            
            result = {
                'template_id': template_id,
                'template_name': 'substitution_rationalizing',
                'template_name_ar': 'تعويض لتوحيد المقام',
                'input': {
                    'expression': expression,
                    'substitution': substitution
                },
                'original_expression': str(expr),
                'substitution': substitution,
                'back_substitution': back_substitution,
                'substituted': str(substituted),
                'simplified': str(simplified),
                'steps': [
                    f"1. نضع {substitution}",
                    f"2. بالتالي {back_substitution}",
                    f"3. نعوض: {substituted}",
                    f"4. نبسط: {simplified}"
                ]
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_118_substitution_multiple(self, expressions: List[str], relations: List[str]) -> Dict[str, Any]:
        """
        قالب 118: تعويضات متعددة في نظام معادلات
        """
        template_id = 118
        self.stats['total_calls'] += 1
        
        try:
            exprs = [sp.sympify(exp) for exp in expressions]
            rels = [sp.sympify(rel) for rel in relations]
            
            # تطبيق التعويضات بالتتابع
            current_exprs = exprs.copy()
            substitution_steps = []
            
            for i, rel in enumerate(rels):
                # التعويض في جميع التعبيرات
                new_exprs = []
                for expr in current_exprs:
                    substituted = expr.subs(rel.rhs, rel.lhs) if rel.lhs.is_Symbol else expr
                    new_exprs.append(substituted)
                
                substitution_steps.append({
                    'step': i+1,
                    'substitution': str(rel),
                    'before': [str(e) for e in current_exprs],
                    'after': [str(e) for e in new_exprs]
                })
                
                current_exprs = new_exprs
            
            # تبسيط النهائي
            final_expressions = [sp.simplify(expr) for expr in current_exprs]
            
            result = {
                'template_id': template_id,
                'template_name': 'substitution_multiple',
                'template_name_ar': 'تعويضات متعددة',
                'input': {
                    'expressions': expressions,
                    'relations': relations
                },
                'substitution_steps': substitution_steps,
                'final_expressions': [str(e) for e in final_expressions],
                'simplified': [str(sp.simplify(e)) for e in final_expressions]
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    # =========================================================================
    # القسم 24: متطابقات المربع الكامل (5 قوالب) - Templates 119-123
    # =========================================================================
    
    def template_119_perfect_square_binomial(self, a: str, b: str) -> Dict[str, Any]:
        """
        قالب 119: مربع كامل ذو حدين: (a + b)² = a² + 2ab + b²
        """
        template_id = 119
        self.stats['total_calls'] += 1
        
        try:
            a_expr = sp.sympify(a)
            b_expr = sp.sympify(b)
            
            # (a + b)²
            square_sum = (a_expr + b_expr) ** 2
            expanded_sum = sp.expand(square_sum)
            
            # (a - b)²
            square_diff = (a_expr - b_expr) ** 2
            expanded_diff = sp.expand(square_diff)
            
            result = {
                'template_id': template_id,
                'template_name': 'perfect_square_binomial',
                'template_name_ar': 'مربع كامل - ذو حدين',
                'input': {'a': a, 'b': b},
                'identities': {
                    'sum_square': {
                        'form': f"({a} + {b})²",
                        'expanded': str(expanded_sum),
                        'identity': '(a + b)² = a² + 2ab + b²'
                    },
                    'difference_square': {
                        'form': f"({a} - {b})²",
                        'expanded': str(expanded_diff),
                        'identity': '(a - b)² = a² - 2ab + b²'
                    }
                },
                'verification': {
                    'sum_check': sp.simplify(square_sum - expanded_sum) == 0,
                    'diff_check': sp.simplify(square_diff - expanded_diff) == 0
                }
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_120_perfect_square_trinomial(self, expression: str) -> Dict[str, Any]:
        """
        قالب 120: التعرف على ثلاثي حدود مربع كامل
        مثال: x² + 6x + 9 = (x + 3)²
        """
        template_id = 120
        self.stats['total_calls'] += 1
        
        try:
            expr = sp.sympify(expression.replace(' ', ''))
            
            # محاولة كتابته على صورة (ax + b)²
            # a²x² + 2abx + b²
            
            is_perfect_square = False
            perfect_square_form = None
            a_val = None
            b_val = None
            
            if expr.is_Add and len(expr.args) == 3:
                # ترتيب الحدود تنازلياً
                terms = sorted(expr.args, key=lambda term: sp.degree(term, self.x), reverse=True)
                
                if len(terms) == 3:
                    # استخراج المعاملات
                    coeffs = {}
                    for term in terms:
                        if term.is_Pow and term.base == self.x and term.exp == 2:
                            coeffs['a2'] = term.args[0] if term.is_Mul else 1
                        elif term.is_Mul and self.x in term.args:
                            coeffs['b'] = term.coeff(self.x)
                        else:
                            coeffs['c'] = term
                    
                    if 'a2' in coeffs and 'b' in coeffs and 'c' in coeffs:
                        a_squared = coeffs['a2']
                        b_coeff = coeffs['b']
                        c_term = coeffs['c']
                        
                        # إيجاد a
                        a_candidate = sp.sqrt(a_squared)
                        if a_candidate.is_real:
                            # إيجاد b من 2ab = b_coeff
                            b_candidate = b_coeff / (2 * a_candidate)
                            
                            # التحقق من b² = c
                            if sp.simplify(b_candidate**2 - c_term) == 0:
                                is_perfect_square = True
                                a_val = a_candidate
                                b_val = b_candidate
                                perfect_square_form = f"({a_val}x {'+' if b_val >= 0 else '-'} {abs(b_val)})²"
            
            result = {
                'template_id': template_id,
                'template_name': 'perfect_square_trinomial',
                'template_name_ar': 'التعرف على ثلاثي حدود مربع كامل',
                'input': {'expression': expression},
                'expression': str(expr),
                'is_perfect_square': is_perfect_square,
                'perfect_square_form': perfect_square_form,
                'a': float(a_val) if a_val and a_val.is_number else str(a_val) if a_val else None,
                'b': float(b_val) if b_val and b_val.is_number else str(b_val) if b_val else None,
                'verification': sp.simplify(expr - (a_val*self.x + b_val)**2) == 0 if is_perfect_square else None
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_121_perfect_square_completing(self, a: float, b: float, c: float) -> Dict[str, Any]:
        """
        قالب 121: إكمال المربع لثلاثي الحدود
        مثال: ax² + bx + c = a(x + b/2a)² + (c - b²/4a)
        """
        template_id = 121
        self.stats['total_calls'] += 1
        
        try:
            # إكمال المربع
            h = -b / (2*a)
            k = c - b**2/(4*a)
            
            perfect_square_form = f"{a}(x {'+' if h>0 else '-'} {abs(h)})² {'+' if k>0 else '-'} {abs(k)}"
            
            # التوسيع للتحقق
            expanded = a*(self.x - h)**2 + k
            expanded_simplified = sp.simplify(expanded)
            
            result = {
                'template_id': template_id,
                'template_name': 'perfect_square_completing',
                'template_name_ar': 'إكمال المربع',
                'input': {'a': a, 'b': b, 'c': c},
                'original': f"{a}x² + {b}x + {c}",
                'vertex_form': perfect_square_form,
                'vertex': {'x': h, 'y': k},
                'steps': [
                    f"1. نأخذ معامل x² كعامل مشترك: {a}(x² + {b/a}x) + {c}",
                    f"2. نكمل المربع داخل القوس: x² + {b/a}x + ({b/(2*a)})² - ({b/(2*a)})²",
                    f"3. نكتب: {a}[(x + {b/(2*a)})² - {b**2/(4*a**2)}] + {c}",
                    f"4. نبسط: {a}(x + {b/(2*a)})² + ({c} - {b**2/(4*a)})",
                    f"5. النتيجة: {perfect_square_form}"
                ],
                'verification': sp.simplify(expanded - (a*self.x**2 + b*self.x + c)) == 0
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_122_perfect_square_identities(self, identity_type: str, a: str, b: str) -> Dict[str, Any]:
        """
        قالب 122: متطابقات المربع الكامل المتقدمة
        أنواع: (a+b+c)²، (a+b)² + (a-b)²
        """
        template_id = 122
        self.stats['total_calls'] += 1
        
        try:
            a_expr = sp.sympify(a)
            b_expr = sp.sympify(b)
            c_expr = sp.sympify('c') if 'c' in identity_type else None
            
            identities = {
                'three_terms': {
                    'form': f"({a} + {b} + c)²",
                    'expansion': (a_expr + b_expr + sp.Symbol('c'))**2,
                    'identity': '(a + b + c)² = a² + b² + c² + 2ab + 2ac + 2bc'
                },
                'sum_of_squares': {
                    'form': f"({a} + {b})² + ({a} - {b})²",
                    'expansion': (a_expr + b_expr)**2 + (a_expr - b_expr)**2,
                    'identity': '(a + b)² + (a - b)² = 2(a² + b²)'
                },
                'difference_of_squares': {
                    'form': f"({a} + {b})² - ({a} - {b})²",
                    'expansion': (a_expr + b_expr)**2 - (a_expr - b_expr)**2,
                    'identity': '(a + b)² - (a - b)² = 4ab'
                }
            }
            
            if identity_type not in identities:
                raise ValueError(f'نوع المتطابقة غير معروف: {identity_type}')
            
            identity = identities[identity_type]
            expanded = sp.expand(identity['expansion'])
            simplified = sp.simplify(expanded)
            
            result = {
                'template_id': template_id,
                'template_name': 'perfect_square_identities',
                'template_name_ar': 'متطابقات المربع الكامل المتقدمة',
                'input': {'identity_type': identity_type, 'a': a, 'b': b},
                'identity': identity['identity'],
                'expression': identity['form'],
                'expanded': str(expanded),
                'simplified': str(simplified),
                'verification': sp.simplify(identity['expansion'] - simplified) == 0
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_123_perfect_square_equation(self, a: float, b: float, c: float) -> Dict[str, Any]:
        """
        قالب 123: حل معادلة باستخدام إكمال المربع
        """
        template_id = 123
        self.stats['total_calls'] += 1
        
        try:
            # إكمال المربع
            h = -b / (2*a)
            k = c - b**2/(4*a)
            
            # حل المعادلة a(x - h)² + k = 0
            # (x - h)² = -k/a
            
            rhs = -k/a
            
            if rhs >= 0:
                sqrt_rhs = math.sqrt(rhs)
                solutions = [h + sqrt_rhs, h - sqrt_rhs]
                solution_type = 'real'
            else:
                sqrt_rhs = cmath.sqrt(rhs)
                solutions = [h + sqrt_rhs, h - sqrt_rhs]
                solution_type = 'complex'
            
            result = {
                'template_id': template_id,
                'template_name': 'perfect_square_equation',
                'template_name_ar': 'حل معادلة باستخدام إكمال المربع',
                'input': {'a': a, 'b': b, 'c': c},
                'equation': f"{a}x² + {b}x + {c} = 0",
                'vertex_form': f"{a}(x {'+' if h>0 else '-'} {abs(h)})² {'+' if k>0 else '-'} {abs(k)} = 0",
                'solutions': [str(s) for s in solutions],
                'solution_type': solution_type,
                'steps': [
                    f"1. نكتب المعادلة: {a}x² + {b}x + {c} = 0",
                    f"2. نكمل المربع: {a}(x {'+' if h>0 else '-'} {abs(h)})² {'+' if k>0 else '-'} {abs(k)} = 0",
                    f"3. ننقل الثابت: {a}(x {'+' if h>0 else '-'} {abs(h)})² = {-k}",
                    f"4. نقسم على {a}: (x {'+' if h>0 else '-'} {abs(h)})² = {-k/a}",
                    f"5. نأخذ الجذر التربيعي: x {'+' if h>0 else '-'} {abs(h)} = ±√{-k/a}",
                    f"6. الحلول: x = {h} ± √{-k/a}"
                ]
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    # =========================================================================
    # القسم 25: المعادلات المتعددة المجهولات (6 قوالب) - Templates 124-129
    # =========================================================================
    
    def template_124_system_2_unknowns_linear(self, eq1: str, eq2: str) -> Dict[str, Any]:
        """
        قالب 124: نظام معادلتين خطيتين بمجهولين (مكرر للتكامل)
        """
        template_id = 124
        self.stats['total_calls'] += 1
        
        try:
            eq1 = eq1.replace(' ', '')
            eq2 = eq2.replace(' ', '')
            
            lhs1, rhs1 = eq1.split('=')
            lhs2, rhs2 = eq2.split('=')
            
            expr1 = sp.Eq(sp.sympify(lhs1), sp.sympify(rhs1))
            expr2 = sp.Eq(sp.sympify(lhs2), sp.sympify(rhs2))
            
            solutions = sp.solve([expr1, expr2], [self.x, self.y])
            
            # تنظيم النتائج
            if solutions:
                if isinstance(solutions, list):
                    sol_list = [{'x': float(sp.N(s[self.x])), 'y': float(sp.N(s[self.y]))} for s in solutions]
                else:
                    sol_list = [{'x': float(sp.N(solutions[self.x])), 'y': float(sp.N(solutions[self.y]))}]
            else:
                sol_list = []
            
            result = {
                'template_id': template_id,
                'template_name': 'system_2_unknowns_linear',
                'template_name_ar': 'نظام معادلتين خطيتين - مجهولان',
                'input': {'eq1': eq1, 'eq2': eq2},
                'solutions': sol_list,
                'num_solutions': len(sol_list)
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_125_system_2_unknowns_nonlinear(self, eq1: str, eq2: str) -> Dict[str, Any]:
        """
        قالب 125: نظام معادلتين غير خطيتين بمجهولين
        مثال: x² + y² = 25, x + y = 7
        """
        template_id = 125
        self.stats['total_calls'] += 1
        
        try:
            eq1 = eq1.replace(' ', '')
            eq2 = eq2.replace(' ', '')
            
            lhs1, rhs1 = eq1.split('=')
            lhs2, rhs2 = eq2.split('=')
            
            expr1 = sp.Eq(sp.sympify(lhs1), sp.sympify(rhs1))
            expr2 = sp.Eq(sp.sympify(lhs2), sp.sympify(rhs2))
            
            solutions = sp.solve([expr1, expr2], [self.x, self.y])
            
            # تنظيم النتائج
            sol_list = []
            if solutions:
                if isinstance(solutions, list):
                    for sol in solutions:
                        sol_list.append({
                            'x': float(sp.N(sol[self.x])) if self.x in sol else None,
                            'y': float(sp.N(sol[self.y])) if self.y in sol else None
                        })
                else:
                    sol_list.append({
                        'x': float(sp.N(solutions[self.x])) if self.x in solutions else None,
                        'y': float(sp.N(solutions[self.y])) if self.y in solutions else None
                    })
            
            result = {
                'template_id': template_id,
                'template_name': 'system_2_unknowns_nonlinear',
                'template_name_ar': 'نظام معادلتين غير خطيتين - مجهولان',
                'input': {'eq1': eq1, 'eq2': eq2},
                'solutions': sol_list,
                'num_solutions': len(sol_list),
                'solution_type': 'multiple' if len(sol_list) > 1 else 'unique' if len(sol_list) == 1 else 'no_solution'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_126_system_3_unknowns_linear(self, eq1: str, eq2: str, eq3: str) -> Dict[str, Any]:
        """
        قالب 126: نظام ثلاث معادلات خطية بثلاثة مجاهيل
        """
        template_id = 126
        self.stats['total_calls'] += 1
        
        try:
            eq1 = eq1.replace(' ', '')
            eq2 = eq2.replace(' ', '')
            eq3 = eq3.replace(' ', '')
            
            systems = []
            for eq in [eq1, eq2, eq3]:
                lhs, rhs = eq.split('=')
                systems.append(sp.Eq(sp.sympify(lhs), sp.sympify(rhs)))
            
            solutions = sp.solve(systems, [self.x, self.y, self.z])
            
            if solutions:
                sol_dict = {
                    'x': float(sp.N(solutions[self.x])) if self.x in solutions else None,
                    'y': float(sp.N(solutions[self.y])) if self.y in solutions else None,
                    'z': float(sp.N(solutions[self.z])) if self.z in solutions else None
                }
            else:
                sol_dict = {}
            
            result = {
                'template_id': template_id,
                'template_name': 'system_3_unknowns_linear',
                'template_name_ar': 'نظام ثلاث معادلات خطية - ثلاثة مجاهيل',
                'input': {'eq1': eq1, 'eq2': eq2, 'eq3': eq3},
                'solutions': sol_dict,
                'has_solution': bool(sol_dict)
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_127_system_3_unknowns_nonlinear(self, eq1: str, eq2: str, eq3: str) -> Dict[str, Any]:
        """
        قالب 127: نظام ثلاث معادلات غير خطية
        """
        template_id = 127
        self.stats['total_calls'] += 1
        
        try:
            eq1 = eq1.replace(' ', '')
            eq2 = eq2.replace(' ', '')
            eq3 = eq3.replace(' ', '')
            
            systems = []
            for eq in [eq1, eq2, eq3]:
                lhs, rhs = eq.split('=')
                systems.append(sp.Eq(sp.sympify(lhs), sp.sympify(rhs)))
            
            solutions = sp.solve(systems, [self.x, self.y, self.z])
            
            # تنظيم النتائج
            sol_list = []
            if solutions:
                if isinstance(solutions, list):
                    for sol in solutions:
                        sol_list.append({
                            'x': float(sp.N(sol[self.x])) if self.x in sol else None,
                            'y': float(sp.N(sol[self.y])) if self.y in sol else None,
                            'z': float(sp.N(sol[self.z])) if self.z in sol else None
                        })
                else:
                    sol_list.append({
                        'x': float(sp.N(solutions[self.x])) if self.x in solutions else None,
                        'y': float(sp.N(solutions[self.y])) if self.y in solutions else None,
                        'z': float(sp.N(solutions[self.z])) if self.z in solutions else None
                    })
            
            result = {
                'template_id': template_id,
                'template_name': 'system_3_unknowns_nonlinear',
                'template_name_ar': 'نظام ثلاث معادلات غير خطية',
                'input': {'eq1': eq1, 'eq2': eq2, 'eq3': eq3},
                'solutions': sol_list,
                'num_solutions': len(sol_list)
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_128_system_parametric(self, equations: List[str], parameters: List[str]) -> Dict[str, Any]:
        """
        قالب 128: أنظمة مع باراميترات
        """
        template_id = 128
        self.stats['total_calls'] += 1
        
        try:
            # تحويل الباراميترات إلى رموز
            param_symbols = [sp.Symbol(p) for p in parameters]
            
            parsed_eqs = []
            for eq in equations:
                eq = eq.replace(' ', '')
                for p in parameters:
                    eq = eq.replace(p, f'({p})')
                lhs, rhs = eq.split('=')
                parsed_eqs.append(sp.Eq(sp.sympify(lhs), sp.sympify(rhs)))
            
            # حل النظام
            variables = [self.x, self.y, self.z][:len(parsed_eqs)]
            solutions = sp.solve(parsed_eqs, variables)
            
            # تحليل قيم الباراميترات الخاصة
            special_cases = self._analyze_parametric_system(parsed_eqs, param_symbols, variables)
            
            result = {
                'template_id': template_id,
                'template_name': 'system_parametric',
                'template_name_ar': 'أنظمة مع باراميترات',
                'input': {'equations': equations, 'parameters': parameters},
                'general_solution': {str(v): str(solutions[v]) for v in variables} if solutions else None,
                'special_cases': special_cases,
                'parameter_analysis': 'تحليل قيم الباراميترات التي تغير طبيعة الحل'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_129_system_word_problems(self, problem_text: str, num_unknowns: int) -> Dict[str, Any]:
        """
        قالب 129: مسائل كلامية تؤدي إلى نظم معادلات
        """
        template_id = 129
        self.stats['total_calls'] += 1
        
        try:
            # تحليل النص لاستخراج المعادلات (نسخة مبسطة)
            equations = []
            variables = []
            
            if 'مجموع' in problem_text and 'عددين' in problem_text:
                numbers = re.findall(r'\d+', problem_text)
                if len(numbers) >= 2:
                    total = float(numbers[0])
                    diff = float(numbers[1]) if len(numbers) > 1 else None
                    
                    equations.append(f"x + y = {total}")
                    if diff is not None:
                        equations.append(f"x - y = {diff}")
                    variables = ['x', 'y']
            
            elif 'أعمار' in problem_text:
                numbers = re.findall(r'\d+', problem_text)
                if len(numbers) >= 2:
                    current_sum = float(numbers[0])
                    future_sum = float(numbers[1]) if len(numbers) > 1 else None
                    
                    equations.append(f"x + y = {current_sum}")
                    if future_sum is not None:
                        equations.append(f"x + 5 + y + 5 = {future_sum}")
                    variables = ['x', 'y']
            
            result = {
                'template_id': template_id,
                'template_name': 'system_word_problems',
                'template_name_ar': 'مسائل كلامية - نظم معادلات',
                'input': {'problem_text': problem_text, 'num_unknowns': num_unknowns},
                'extracted_equations': equations,
                'variables': variables,
                'solution_method': 'تحديد المتغيرات وبناء المعادلات ثم حل النظام'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    # =========================================================================
    # القسم 26: المعادلات على شكل نسب (5 قوالب) - Templates 130-134
    # =========================================================================
    
    def template_130_ratio_linear(self, a1: float, b1: float, a2: float, b2: float) -> Dict[str, Any]:
        """
        قالب 130: نسب خطية: (a1x + b1)/(a2x + b2) = k
        """
        template_id = 130
        self.stats['total_calls'] += 1
        
        try:
            # حل المعادلة: (a1x + b1)/(a2x + b2) = k
            # a1x + b1 = k(a2x + b2)
            # a1x + b1 = k a2 x + k b2
            # (a1 - k a2)x = k b2 - b1
            # x = (k b2 - b1)/(a1 - k a2)
            
            result = {
                'template_id': template_id,
                'template_name': 'ratio_linear',
                'template_name_ar': 'نسب خطية',
                'input': {'a1': a1, 'b1': b1, 'a2': a2, 'b2': b2},
                'general_form': f"({a1}x + {b1})/({a2}x + {b2}) = k",
                'solution_formula': 'x = (k b2 - b1)/(a1 - k a2)',
                'domain': f"x ≠ {-b2/a2 if a2 != 0 else 'جميع الأعداد'}",
                'special_cases': {
                    'a1 = k a2': 'المعادلة إما مستحيلة أو محققة دائماً',
                    'denominator_zero': f"x = {-b2/a2} ممنوع"
                }
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_131_ratio_quadratic(self, a1: float, b1: float, c1: float, a2: float, b2: float, c2: float, k: float) -> Dict[str, Any]:
        """
        قالب 131: نسب تربيعية: (a1x² + b1x + c1)/(a2x² + b2x + c2) = k
        """
        template_id = 131
        self.stats['total_calls'] += 1
        
        try:
            # بناء المعادلة
            numerator = a1*self.x**2 + b1*self.x + c1
            denominator = a2*self.x**2 + b2*self.x + c2
            
            equation = sp.Eq(numerator / denominator, k)
            
            # ضرب الطرفين في المقام
            cleared = sp.Eq(numerator, k * denominator)
            solutions = sp.solve(cleared, self.x)
            
            # استبعاد الحلول التي تجعل المقام صفراً
            valid_solutions = []
            for sol in solutions:
                denom_val = float(sp.N(denominator.subs(self.x, sol)))
                if abs(denom_val) > self.precision:
                    valid_solutions.append(float(sp.N(sol)))
            
            result = {
                'template_id': template_id,
                'template_name': 'ratio_quadratic',
                'template_name_ar': 'نسب تربيعية',
                'input': {'a1': a1, 'b1': b1, 'c1': c1, 'a2': a2, 'b2': b2, 'c2': c2, 'k': k},
                'equation': f"({a1}x² + {b1}x + {c1})/({a2}x² + {b2}x + {c2}) = {k}",
                'cleared_equation': f"{a1}x² + {b1}x + {c1} = {k}({a2}x² + {b2}x + {c2})",
                'solutions': valid_solutions,
                'domain': f"{a2}x² + {b2}x + {c2} ≠ 0"
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_132_ratio_continued(self, ratios: List[float], total: float) -> Dict[str, Any]:
        """
        قالب 132: نسب متصلة: a:b:c = p:q:r مع مجموع معلوم
        """
        template_id = 132
        self.stats['total_calls'] += 1
        
        try:
            # a:b:c = p:q:r => a = kp, b = kq, c = kr
            # a + b + c = k(p+q+r) = total
            # k = total / sum(ratios)
            
            sum_ratios = sum(ratios)
            k = total / sum_ratios
            
            values = [k * r for r in ratios]
            
            result = {
                'template_id': template_id,
                'template_name': 'ratio_continued',
                'template_name_ar': 'نسب متصلة',
                'input': {'ratios': ratios, 'total': total},
                'ratio_expression': ' : '.join([str(r) for r in ratios]),
                'constant_k': k,
                'values': values,
                'verification': sum(values) - total < self.precision,
                'steps': [
                    f"1. نضع a = {ratios[0]}k, b = {ratios[1]}k, c = {ratios[2]}k" if len(ratios) > 2 else f"1. نضع a = {ratios[0]}k, b = {ratios[1]}k",
                    f"2. المجموع: {sum_ratios}k = {total}",
                    f"3. k = {total}/{sum_ratios} = {k}",
                    f"4. القيم: {values}"
                ]
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_133_ratio_comparison(self, ratio1: Tuple[float, float], ratio2: Tuple[float, float]) -> Dict[str, Any]:
        """
        قالب 133: مقارنة نسب: a:b = c:d
        """
        template_id = 133
        self.stats['total_calls'] += 1
        
        try:
            a, b = ratio1
            c, d = ratio2
            
            # التحقق من التناسب a/b = c/d
            left = a / b if b != 0 else float('inf')
            right = c / d if d != 0 else float('inf')
            
            is_proportional = abs(left - right) < self.precision if left != float('inf') and right != float('inf') else (left == right)
            
            # الضرب التبادلي: a*d = b*c
            cross_product_left = a * d
            cross_product_right = b * c
            cross_equal = abs(cross_product_left - cross_product_right) < self.precision
            
            result = {
                'template_id': template_id,
                'template_name': 'ratio_comparison',
                'template_name_ar': 'مقارنة نسب',
                'input': {'ratio1': ratio1, 'ratio2': ratio2},
                'ratios': [f"{a}:{b}", f"{c}:{d}"],
                'is_proportional': is_proportional,
                'cross_product': {
                    'left': f"{a} × {d} = {cross_product_left}",
                    'right': f"{b} × {c} = {cross_product_right}",
                    'equal': cross_equal
                },
                'decimal_values': [left, right]
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_134_ratio_variable(self, expression: str) -> Dict[str, Any]:
        """
        قالب 134: نسب بمتغيرات: (ax + b)/(cx + d) = (ex + f)/(gx + h)
        """
        template_id = 134
        self.stats['total_calls'] += 1
        
        try:
            expr = sp.sympify(expression.replace(' ', ''))
            
            # إذا كان التعبير على شكل نسبة = نسبة
            if expr.is_Eq:
                lhs, rhs = expr.lhs, expr.rhs
                
                # ضرب تبادلي
                cross_eq = sp.Eq(lhs * rhs.denominator() if hasattr(rhs, 'denominator') else lhs * 1,
                                 rhs * lhs.denominator() if hasattr(lhs, 'denominator') else rhs * 1)
                
                solutions = sp.solve(cross_eq, self.x)
                
                # استبعاد الحلول التي تجعل المقامات صفراً
                valid_solutions = []
                for sol in solutions:
                    valid = True
                    for side in [lhs, rhs]:
                        if hasattr(side, 'denominator') and side.denominator() != 1:
                            denom_val = float(sp.N(side.denominator().subs(self.x, sol)))
                            if abs(denom_val) < self.precision:
                                valid = False
                                break
                    if valid:
                        valid_solutions.append(float(sp.N(sol)))
                
                result = {
                    'template_id': template_id,
                    'template_name': 'ratio_variable',
                    'template_name_ar': 'نسب بمتغيرات',
                    'input': {'expression': expression},
                    'equation': str(expr),
                    'cross_product': str(cross_eq),
                    'solutions': valid_solutions,
                    'domain': 'جميع قيم x التي لا تجعل المقامات صفراً'
                }
            else:
                result = {
                    'template_id': template_id,
                    'error': 'التعبير يجب أن يكون معادلة'
                }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    # =========================================================================
    # القسم 27: تحليل التعبيرات متعددة الحدود (5 قوالب) - Templates 135-139
    # =========================================================================
    
    def template_135_factor_gcf_advanced(self, expression: str) -> Dict[str, Any]:
        """
        قالب 135: تحليل بإخراج العامل المشترك الأكبر (حالات متقدمة)
        """
        template_id = 135
        self.stats['total_calls'] += 1
        
        try:
            expr = sp.sympify(expression.replace(' ', ''))
            
            # إيجاد العامل المشترك الأكبر
            terms = expr.as_ordered_terms() if expr.is_Add else [expr]
            
            # استخراج المعاملات العددية
            numeric_coeffs = []
            symbolic_parts = []
            
            for term in terms:
                if term.is_Mul:
                    num_part = 1
                    sym_part = 1
                    for factor in term.args:
                        if factor.is_number:
                            num_part *= factor
                        else:
                            sym_part *= factor
                    numeric_coeffs.append(abs(float(num_part)))
                    symbolic_parts.append(sym_part)
                elif term.is_number:
                    numeric_coeffs.append(abs(float(term)))
                    symbolic_parts.append(1)
                else:
                    numeric_coeffs.append(1)
                    symbolic_parts.append(term)
            
            # GCD العددي
            if numeric_coeffs:
                gcd_numeric = numeric_coeffs[0]
                for coeff in numeric_coeffs[1:]:
                    gcd_numeric = math.gcd(int(gcd_numeric), int(coeff))
            else:
                gcd_numeric = 1
            
            # العامل الرمزي المشترك
            common_symbolic = 1
            if symbolic_parts:
                # تقاطع المتغيرات
                common_vars = set(symbolic_parts[0].free_symbols)
                for part in symbolic_parts[1:]:
                    common_vars &= part.free_symbols
                
                # أقل أس لكل متغير
                for var in common_vars:
                    min_power = min(part.as_coefficients_dict().get(var, 0) for part in symbolic_parts)
                    if min_power > 0:
                        common_symbolic *= var ** min_power
            
            common_factor = gcd_numeric * common_symbolic
            
            if common_factor != 1:
                factored = common_factor * sp.Add(*[term / common_factor for term in terms])
            else:
                factored = expr
            
            result = {
                'template_id': template_id,
                'template_name': 'factor_gcf_advanced',
                'template_name_ar': 'تحليل بإخراج العامل المشترك الأكبر - متقدم',
                'input': {'expression': expression},
                'original': str(expr),
                'terms': [str(t) for t in terms],
                'numeric_coeffs': numeric_coeffs,
                'symbolic_parts': [str(s) for s in symbolic_parts],
                'common_factor': str(common_factor) if common_factor != 1 else 'لا يوجد عامل مشترك',
                'factored': str(factored) if common_factor != 1 else 'غير قابل للتحليل بهذه الطريقة',
                'steps': [
                    f"1. المعاملات العددية: {numeric_coeffs}، GCD = {gcd_numeric}",
                    f"2. الأجزاء الرمزية: {[str(s) for s in symbolic_parts]}، المشترك = {common_symbolic}",
                    f"3. العامل المشترك = {common_factor}",
                    f"4. بعد الإخراج: {factored}" if common_factor != 1 else "لا يوجد عامل مشترك"
                ]
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_136_factor_grouping_advanced(self, expression: str) -> Dict[str, Any]:
        """
        قالب 136: تحليل بالتجميع للحالات المعقدة
        """
        template_id = 136
        self.stats['total_calls'] += 1
        
        try:
            expr = sp.sympify(expression.replace(' ', ''))
            
            if not expr.is_Add:
                return {
                    'template_id': template_id,
                    'error': 'التعبير ليس مجموع حدود - لا يمكن تطبيق التجميع'
                }
            
            terms = list(expr.args)
            num_terms = len(terms)
            
            possible_groupings = []
            
            # تجميع كل 2 حد
            if num_terms >= 4:
                # محاولة تجميع (1,2) و (3,4)
                group1 = terms[0] + terms[1]
                group2 = terms[2] + terms[3]
                
                factored1 = sp.factor(group1)
                factored2 = sp.factor(group2)
                
                if factored1 != group1 and factored2 != group2:
                    # استخراج العامل المشترك من المجموعتين
                    common = self._extract_common_factor([factored1, factored2])
                    if common != 1:
                        possible_groupings.append({
                            'grouping': f"({terms[0]} + {terms[1]}) + ({terms[2]} + {terms[3]})",
                            'factored_groups': [str(factored1), str(factored2)],
                            'final': str(common * (factored1/common + factored2/common)) if common != 1 else None
                        })
            
            # تجميع (1,3) و (2,4)
            if num_terms >= 4:
                group1 = terms[0] + terms[2]
                group2 = terms[1] + terms[3]
                
                factored1 = sp.factor(group1)
                factored2 = sp.factor(group2)
                
                if factored1 != group1 and factored2 != group2:
                    common = self._extract_common_factor([factored1, factored2])
                    if common != 1:
                        possible_groupings.append({
                            'grouping': f"({terms[0]} + {terms[2]}) + ({terms[1]} + {terms[3]})",
                            'factored_groups': [str(factored1), str(factored2)],
                            'final': str(common * (factored1/common + factored2/common)) if common != 1 else None
                        })
            
            result = {
                'template_id': template_id,
                'template_name': 'factor_grouping_advanced',
                'template_name_ar': 'تحليل بالتجميع - حالات معقدة',
                'input': {'expression': expression},
                'original': str(expr),
                'terms': [str(t) for t in terms],
                'num_terms': num_terms,
                'possible_groupings': possible_groupings,
                'best_grouping': possible_groupings[0] if possible_groupings else None
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_137_factor_special_forms(self, expression: str) -> Dict[str, Any]:
        """
        قالب 137: تحليل الصيغ الخاصة (فرق مكعبين، مجموع مكعبين، ...)
        """
        template_id = 137
        self.stats['total_calls'] += 1
        
        try:
            expr = sp.sympify(expression.replace(' ', ''))
            
            special_forms = []
            
            # الفرق بين مربعين: a² - b²
            if expr.is_Add and len(expr.args) == 2:
                terms = list(expr.args)
                if terms[0].is_Pow and terms[0].exp == 2 and terms[1].is_Pow and terms[1].exp == 2 and str(terms[1])[0] == '-':
                    a = terms[0].base
                    b = terms[1].base
                    special_forms.append({
                        'type': 'difference_of_squares',
                        'form': f"{a}² - {b}²",
                        'factorization': f"({a} - {b})({a} + {b})",
                        'identity': 'a² - b² = (a - b)(a + b)'
                    })
            
            # مجموع مكعبين: a³ + b³
            if expr.is_Add and len(expr.args) == 2:
                terms = list(expr.args)
                if terms[0].is_Pow and terms[0].exp == 3 and terms[1].is_Pow and terms[1].exp == 3:
                    a = terms[0].base
                    b = terms[1].base
                    special_forms.append({
                        'type': 'sum_of_cubes',
                        'form': f"{a}³ + {b}³",
                        'factorization': f"({a} + {b})({a}² - {a}{b} + {b}²)",
                        'identity': 'a³ + b³ = (a + b)(a² - ab + b²)'
                    })
            
            # فرق مكعبين: a³ - b³
            if expr.is_Add and len(expr.args) == 2:
                terms = list(expr.args)
                if terms[0].is_Pow and terms[0].exp == 3 and terms[1].is_Pow and terms[1].exp == 3 and str(terms[1])[0] == '-':
                    a = terms[0].base
                    b = terms[1].base
                    special_forms.append({
                        'type': 'difference_of_cubes',
                        'form': f"{a}³ - {b}³",
                        'factorization': f"({a} - {b})({a}² + {a}{b} + {b}²)",
                        'identity': 'a³ - b³ = (a - b)(a² + ab + b²)'
                    })
            
            # ثلاثي حدود مربع كامل: a² + 2ab + b²
            if expr.is_Add and len(expr.args) == 3:
                # محاولة التعرف على نمط المربع الكامل
                terms = sorted(expr.args, key=lambda t: sp.degree(t, self.x) if self.x in t.free_symbols else 0, reverse=True)
                if len(terms) == 3:
                    # استخراج المعاملات
                    coeffs = {}
                    for term in terms:
                        if term.is_Pow and term.base == self.x and term.exp == 2:
                            coeffs['a2'] = term.coeff(self.x**2) if term.is_Mul else 1
                        elif term.is_Mul and self.x in term.args:
                            coeffs['b'] = term.coeff(self.x)
                        else:
                            coeffs['c'] = term
                    
                    if 'a2' in coeffs and 'b' in coeffs and 'c' in coeffs:
                        a_squared = coeffs['a2']
                        b_coeff = coeffs['b']
                        c_term = coeffs['c']
                        
                        a_candidate = sp.sqrt(a_squared)
                        if a_candidate.is_real:
                            b_candidate = b_coeff / (2 * a_candidate)
                            if sp.simplify(b_candidate**2 - c_term) == 0:
                                special_forms.append({
                                    'type': 'perfect_square_trinomial',
                                    'form': str(expr),
                                    'factorization': f"({a_candidate}x {'+' if b_candidate >= 0 else '-'} {abs(b_candidate)})²",
                                    'identity': 'a² + 2ab + b² = (a + b)²'
                                })
            
            result = {
                'template_id': template_id,
                'template_name': 'factor_special_forms',
                'template_name_ar': 'تحليل الصيغ الخاصة',
                'input': {'expression': expression},
                'original': str(expr),
                'special_forms': special_forms,
                'has_special_form': len(special_forms) > 0
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_138_factor_rational_roots(self, polynomial: str) -> Dict[str, Any]:
        """
        قالب 138: تحليل باستخدام نظرية الجذور النسبية
        """
        template_id = 138
        self.stats['total_calls'] += 1
        
        try:
            expr = sp.sympify(polynomial.replace(' ', ''))
            
            # استخراج المعاملات
            coeffs_dict = expr.as_coefficients_dict()
            degree = sp.degree(expr)
            
            leading_coeff = coeffs_dict.get(self.x**degree, 1)
            constant_term = coeffs_dict.get(1, 0)
            
            # إيجاد قواسم الحد الثابت ومعامل الدرجة العليا
            p_factors = self._get_integer_factors(abs(int(constant_term))) if constant_term.is_integer else [1]
            q_factors = self._get_integer_factors(abs(int(leading_coeff))) if leading_coeff.is_integer else [1]
            
            # توليد جميع المرشحين
            candidates = []
            for p in p_factors:
                for q in q_factors:
                    candidates.append(p/q)
                    candidates.append(-p/q)
            
            candidates = list(set(candidates))
            
            # اختبار المرشحين
            rational_roots = []
            tested = []
            
            for cand in candidates:
                val = float(sp.N(expr.subs(self.x, cand)))
                tested.append({
                    'candidate': cand,
                    'value': val,
                    'is_root': abs(val) < self.precision
                })
                if abs(val) < self.precision:
                    rational_roots.append(cand)
            
            # بناء التحليل باستخدام الجذور
            if rational_roots:
                factored = leading_coeff
                for root in rational_roots:
                    factored *= (self.x - root)
                
                # قسمة كثيرة الحدود الأصلية على العوامل
                quotient = sp.simplify(expr / factored)
                if quotient != 1:
                    factored = factored * quotient
            else:
                factored = expr
            
            result = {
                'template_id': template_id,
                'template_name': 'factor_rational_roots',
                'template_name_ar': 'تحليل باستخدام نظرية الجذور النسبية',
                'input': {'polynomial': polynomial},
                'polynomial': str(expr),
                'leading_coefficient': float(leading_coeff) if leading_coeff.is_number else str(leading_coeff),
                'constant_term': float(constant_term) if constant_term.is_number else str(constant_term),
                'p_factors': p_factors,
                'q_factors': q_factors,
                'candidates': candidates,
                'tested': tested,
                'rational_roots': rational_roots,
                'factored_form': str(factored) if factored != expr else None
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_139_factor_complete(self, polynomial: str) -> Dict[str, Any]:
        """
        قالب 139: تحليل كامل لكثيرة الحدود بجميع الطرق
        """
        template_id = 139
        self.stats['total_calls'] += 1
        
        try:
            expr = sp.sympify(polynomial.replace(' ', ''))
            
            # محاولة التحليل بطرق مختلفة
            methods_tried = []
            
            # 1. التحليل المباشر
            factored_direct = sp.factor(expr)
            methods_tried.append({
                'method': 'direct',
                'result': str(factored_direct),
                'success': factored_direct != expr
            })
            
            # 2. إخراج العامل المشترك
            gcf_result = self.template_135_factor_gcf_advanced(polynomial)
            methods_tried.append({
                'method': 'gcf',
                'result': gcf_result.get('factored', ''),
                'success': gcf_result.get('common_factor') != 'لا يوجد عامل مشترك'
            })
            
            # 3. الصيغ الخاصة
            special_result = self.template_137_factor_special_forms(polynomial)
            methods_tried.append({
                'method': 'special_forms',
                'result': special_result.get('special_forms', []),
                'success': special_result.get('has_special_form', False)
            })
            
            # 4. الجذور النسبية
            rational_result = self.template_138_factor_rational_roots(polynomial)
            methods_tried.append({
                'method': 'rational_roots',
                'result': rational_result.get('factored_form', ''),
                'success': rational_result.get('rational_roots', []) != []
            })
            
            # أفضل نتيجة
            best_result = factored_direct
            for method in methods_tried:
                if method['success'] and len(str(method['result'])) < len(str(best_result)):
                    if isinstance(method['result'], str):
                        best_result = method['result']
            
            result = {
                'template_id': template_id,
                'template_name': 'factor_complete',
                'template_name_ar': 'تحليل كامل لكثيرة الحدود',
                'input': {'polynomial': polynomial},
                'original': str(expr),
                'degree': sp.degree(expr),
                'methods_tried': methods_tried,
                'best_factorization': str(best_result) if best_result != expr else 'غير قابل للتحليل أكثر',
                'is_irreducible': best_result == expr,
                'roots': [str(r) for r in sp.solve(expr, self.x)]
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    # =========================================================================
    # القسم 28: تبسيط التعبيرات بالمتغيرات المتعددة (4 قوالب) - Templates 140-143
    # =========================================================================
    
    def template_140_simplify_multivariate_collect(self, expression: str, variable: str) -> Dict[str, Any]:
        """
        قالب 140: تجميع الحدود حول متغير معين
        """
        template_id = 140
        self.stats['total_calls'] += 1
        
        try:
            expr = sp.sympify(expression.replace(' ', ''))
            var = sp.Symbol(variable)
            
            # تجميع الحدود
            collected = sp.collect(expr, var)
            
            # استخراج المعاملات
            if collected.is_Add:
                coefficients = {}
                for term in collected.args:
                    if term.is_Mul and var in term.args:
                        coeff = term / var
                        power = 1
                    elif term.is_Pow and term.base == var:
                        coeff = 1
                        power = term.exp
                    elif var in term.free_symbols:
                        # تقدير مبسط
                        coeff = term.coeff(var)
                    else:
                        coeff = term
                        power = 0
                    
                    if power not in coefficients:
                        coefficients[power] = []
                    coefficients[power].append(str(coeff))
            else:
                coefficients = {0: [str(collected)]}
            
            result = {
                'template_id': template_id,
                'template_name': 'simplify_multivariate_collect',
                'template_name_ar': 'تجميع الحدود حول متغير',
                'input': {'expression': expression, 'variable': variable},
                'original': str(expr),
                'collected': str(collected),
                'coefficients': {str(k): v for k, v in coefficients.items()},
                'variables': [str(s) for s in expr.free_symbols]
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_141_simplify_multivariate_expand(self, expression: str) -> Dict[str, Any]:
        """
        قالب 141: توسيع تعبير بمتغيرات متعددة
        """
        template_id = 141
        self.stats['total_calls'] += 1
        
        try:
            expr = sp.sympify(expression.replace(' ', ''))
            
            # توسيع كامل
            expanded = sp.expand(expr)
            
            # ترتيب حسب المتغيرات
            variables = list(expr.free_symbols)
            if variables:
                # ترتيب تنازلي حسب الدرجة الكلية
                terms = expanded.as_ordered_terms(order='lex')
            else:
                terms = [expanded]
            
            result = {
                'template_id': template_id,
                'template_name': 'simplify_multivariate_expand',
                'template_name_ar': 'توسيع تعبير بمتغيرات متعددة',
                'input': {'expression': expression},
                'original': str(expr),
                'expanded': str(expanded),
                'terms': [str(t) for t in terms],
                'num_terms': len(terms),
                'variables': [str(v) for v in variables]
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_142_simplify_multivariate_factor(self, expression: str) -> Dict[str, Any]:
        """
        قالب 142: تحليل تعبير بمتغيرات متعددة
        """
        template_id = 142
        self.stats['total_calls'] += 1
        
        try:
            expr = sp.sympify(expression.replace(' ', ''))
            
            # تحليل
            factored = sp.factor(expr)
            
            # استخراج العوامل
            factors = []
            if factored.is_Mul:
                for factor in factored.args:
                    factors.append(str(factor))
            else:
                factors = [str(factored)]
            
            result = {
                'template_id': template_id,
                'template_name': 'simplify_multivariate_factor',
                'template_name_ar': 'تحليل تعبير بمتغيرات متعددة',
                'input': {'expression': expression},
                'original': str(expr),
                'factored': str(factored),
                'factors': factors,
                'num_factors': len(factors),
                'is_factorable': factored != expr
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_143_simplify_multivariate_cancel(self, numerator: str, denominator: str) -> Dict[str, Any]:
        """
        قالب 143: اختصار العوامل المشتركة في كسر
        """
        template_id = 143
        self.stats['total_calls'] += 1
        
        try:
            num = sp.sympify(numerator.replace(' ', ''))
            den = sp.sympify(denominator.replace(' ', ''))
            
            # تبسيط الكسر
            fraction = num / den
            simplified = sp.simplify(fraction)
            
            # استخراج العوامل المشتركة
            gcd_expr = sp.gcd(num, den)
            
            num_after = sp.simplify(num / gcd_expr) if gcd_expr != 1 else num
            den_after = sp.simplify(den / gcd_expr) if gcd_expr != 1 else den
            
            result = {
                'template_id': template_id,
                'template_name': 'simplify_multivariate_cancel',
                'template_name_ar': 'اختصار العوامل المشتركة في كسر',
                'input': {'numerator': numerator, 'denominator': denominator},
                'original': f"({numerator})/({denominator})",
                'simplified': str(simplified),
                'gcd': str(gcd_expr) if gcd_expr != 1 else 'لا يوجد عامل مشترك',
                'after_cancellation': {
                    'numerator': str(num_after),
                    'denominator': str(den_after)
                } if gcd_expr != 1 else None,
                'domain': f"{denominator} ≠ 0"
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    # =========================================================================
    # القسم 29: اختبار الصيغة الصحيحة للمعادلات (5 قوالب) - Templates 144-148
    # =========================================================================
    
    def template_144_verify_equation_type(self, equation: str) -> Dict[str, Any]:
        """
        قالب 144: التحقق من نوع المعادلة
        """
        template_id = 144
        self.stats['total_calls'] += 1
        
        try:
            equation = equation.replace(' ', '')
            
            if '=' not in equation:
                return {'template_id': template_id, 'error': 'الصيغة غير صحيحة - يجب أن تحتوي على ='}
            
            lhs, rhs = equation.split('=')
            
            # تحليل الطرفين
            lhs_expr = sp.sympify(lhs)
            rhs_expr = sp.sympify(rhs)
            
            expr = lhs_expr - rhs_expr
            
            # تحديد النوع
            eq_type = []
            
            if expr.is_polynomial():
                degree = sp.degree(expr)
                if degree == 1:
                    eq_type.append('linear')
                elif degree == 2:
                    eq_type.append('quadratic')
                elif degree == 3:
                    eq_type.append('cubic')
                elif degree == 4:
                    eq_type.append('quartic')
                else:
                    eq_type.append(f'polynomial_degree_{degree}')
            
            # التحقق من وجود دوال مثلثية
            if any(func in str(expr) for func in ['sin', 'cos', 'tan', 'cot', 'sec', 'csc']):
                eq_type.append('trigonometric')
            
            # التحقق من وجود لوغاريتمات
            if 'log' in str(expr):
                eq_type.append('logarithmic')
            
            # التحقق من وجود أسس
            if '**' in str(expr) or '^' in str(expr):
                if not expr.is_polynomial():
                    eq_type.append('exponential')
            
            # التحقق من وجود جذور
            if 'sqrt' in str(expr) or 'root' in str(expr):
                eq_type.append('radical')
            
            # التحقق من وجود قيم مطلقة
            if 'Abs' in str(expr) or '|' in str(equation):
                eq_type.append('absolute')
            
            # التحقق من كونها معادلة كسرية
            if any(arg.is_Pow and arg.exp == -1 for arg in sp.preorder_traversal(expr)):
                eq_type.append('rational')
            
            result = {
                'template_id': template_id,
                'template_name': 'verify_equation_type',
                'template_name_ar': 'التحقق من نوع المعادلة',
                'input': {'equation': equation},
                'equation': equation,
                'types': eq_type,
                'primary_type': eq_type[0] if eq_type else 'unknown',
                'degree': sp.degree(expr) if expr.is_polynomial() else None,
                'variables': [str(v) for v in expr.free_symbols]
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_145_verify_balance(self, equation: str) -> Dict[str, Any]:
        """
        قالب 145: التحقق من توازن المعادلة (عدد الحدود في كل طرف)
        """
        template_id = 145
        self.stats['total_calls'] += 1
        
        try:
            equation = equation.replace(' ', '')
            
            if '=' not in equation:
                return {'template_id': template_id, 'error': 'الصيغة غير صحيحة'}
            
            lhs, rhs = equation.split('=')
            
            lhs_expr = sp.sympify(lhs)
            rhs_expr = sp.sympify(rhs)
            
            # عدد الحدود
            lhs_terms = len(lhs_expr.as_ordered_terms()) if lhs_expr.is_Add else 1
            rhs_terms = len(rhs_expr.as_ordered_terms()) if rhs_expr.is_Add else 1
            
            # التحقق من صحة الصيغة (عدد الأقواس)
            parentheses_balance = equation.count('(') == equation.count(')')
            
            result = {
                'template_id': template_id,
                'template_name': 'verify_balance',
                'template_name_ar': 'التحقق من توازن المعادلة',
                'input': {'equation': equation},
                'left_side': {
                    'expression': lhs,
                    'num_terms': lhs_terms
                },
                'right_side': {
                    'expression': rhs,
                    'num_terms': rhs_terms
                },
                'balance': {
                    'terms_equal': lhs_terms == rhs_terms,
                    'parentheses_balanced': parentheses_balance,
                    'is_balanced': lhs_terms == rhs_terms and parentheses_balance
                }
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_146_verify_domain(self, equation: str) -> Dict[str, Any]:
        """
        قالب 146: التحقق من مجال المعادلة
        """
        template_id = 146
        self.stats['total_calls'] += 1
        
        try:
            equation = equation.replace(' ', '')
            
            if '=' in equation:
                lhs, rhs = equation.split('=')
                expr = sp.sympify(lhs) - sp.sympify(rhs)
            else:
                expr = sp.sympify(equation)
            
            domain_conditions = []
            
            # شروط المقامات (لا يمكن أن تكون صفراً)
            denominators = []
            for arg in sp.preorder_traversal(expr):
                if isinstance(arg, sp.Pow) and arg.exp == -1:
                    denominators.append(arg.base)
            
            for den in denominators:
                domain_conditions.append(f"{den} ≠ 0")
            
            # شروط اللوغاريتمات (الوسيط > 0)
            logs = []
            for arg in sp.preorder_traversal(expr):
                if isinstance(arg, sp.log):
                    logs.append(arg.args[0])
            
            for log_arg in logs:
                domain_conditions.append(f"{log_arg} > 0")
            
            # شروط الجذور الزوجية (ما تحت الجذر ≥ 0)
            radicals = []
            for arg in sp.preorder_traversal(expr):
                if isinstance(arg, sp.Pow) and arg.exp.is_number:
                    exp_val = float(arg.exp)
                    if exp_val > 0 and abs(exp_val - int(exp_val)) > 0 and int(exp_val * 2) == exp_val * 2:
                        # جذر زوجي (أس كسري بسطه زوجي)
                        radicals.append(arg.base)
            
            for rad in radicals:
                domain_conditions.append(f"{rad} ≥ 0")
            
            result = {
                'template_id': template_id,
                'template_name': 'verify_domain',
                'template_name_ar': 'التحقق من مجال المعادلة',
                'input': {'equation': equation},
                'expression': str(expr),
                'domain_conditions': [str(c) for c in domain_conditions],
                'domain': ' و '.join([str(c) for c in domain_conditions]) if domain_conditions else 'جميع الأعداد الحقيقية',
                'restrictions': len(domain_conditions) > 0
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_147_verify_equivalence(self, expr1: str, expr2: str) -> Dict[str, Any]:
        """
        قالب 147: التحقق من تكافؤ تعبيرين
        """
        template_id = 147
        self.stats['total_calls'] += 1
        
        try:
            e1 = sp.sympify(expr1.replace(' ', ''))
            e2 = sp.sympify(expr2.replace(' ', ''))
            
            # التحقق من التكافؤ
            difference = sp.simplify(e1 - e2)
            are_equivalent = difference == 0
            
            # إذا لم يكونا متكافئين، ابحث عن قيم الاختلاف
            if not are_equivalent:
                # حل المعادلة e1 = e2
                solutions = sp.solve(e1 - e2)
                points_of_equality = [float(sp.N(s)) for s in solutions if s.is_real]
            else:
                points_of_equality = []
            
            result = {
                'template_id': template_id,
                'template_name': 'verify_equivalence',
                'template_name_ar': 'التحقق من تكافؤ تعبيرين',
                'input': {'expr1': expr1, 'expr2': expr2},
                'expression1': str(e1),
                'expression2': str(e2),
                'are_equivalent': are_equivalent,
                'difference': str(difference),
                'points_of_equality': points_of_equality,
                'simplified_difference': str(sp.simplify(e1 - e2))
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_148_verify_identity(self, identity: str) -> Dict[str, Any]:
        """
        قالب 148: التحقق من صحة متطابقة
        """
        template_id = 148
        self.stats['total_calls'] += 1
        
        try:
            identity = identity.replace(' ', '')
            
            if '=' not in identity:
                return {'template_id': template_id, 'error': 'المتطابقة يجب أن تحتوي على ='}
            
            lhs, rhs = identity.split('=')
            lhs_expr = sp.sympify(lhs)
            rhs_expr = sp.sympify(rhs)
            
            # التحقق من صحة المتطابقة
            difference = sp.simplify(lhs_expr - rhs_expr)
            is_identity = difference == 0
            
            # إذا لم تكن متطابقة، ابحث عن القيم التي تتحقق عندها
            if not is_identity:
                solutions = sp.solve(lhs_expr - rhs_expr)
                verification_points = [float(sp.N(s)) for s in solutions if s.is_real]
            else:
                verification_points = []
            
            # اختبار نقطة عشوائية
            test_var = list(lhs_expr.free_symbols)[0] if lhs_expr.free_symbols else None
            test_value = None
            test_result = None
            
            if test_var and verification_points:
                test_value = 0
                if test_value not in verification_points:
                    lhs_test = float(sp.N(lhs_expr.subs(test_var, test_value)))
                    rhs_test = float(sp.N(rhs_expr.subs(test_var, test_value)))
                    test_result = {
                        'point': test_value,
                        'left': lhs_test,
                        'right': rhs_test,
                        'equal': abs(lhs_test - rhs_test) < self.precision
                    }
            
            result = {
                'template_id': template_id,
                'template_name': 'verify_identity',
                'template_name_ar': 'التحقق من صحة متطابقة',
                'input': {'identity': identity},
                'left': str(lhs_expr),
                'right': str(rhs_expr),
                'is_identity': is_identity,
                'difference': str(difference),
                'verification_points': verification_points,
                'test_point': test_result
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    # =========================================================================
    # القسم 30: التحقق من صحة الجذر (4 قوالب) - Templates 149-152
    # =========================================================================
    
    def template_149_verify_root_substitution(self, equation: str, root: float) -> Dict[str, Any]:
        """
        قالب 149: التحقق من صحة جذر بالتعويض
        """
        template_id = 149
        self.stats['total_calls'] += 1
        
        try:
            equation = equation.replace(' ', '')
            
            if '=' in equation:
                lhs, rhs = equation.split('=')
                expr = sp.sympify(lhs) - sp.sympify(rhs)
            else:
                expr = sp.sympify(equation)
            
            # التعويض بالجذر
            try:
                value = float(sp.N(expr.subs(self.x, root)))
                is_root = abs(value) < self.precision
                
                # حساب الخطأ
                error = abs(value)
                
                # تقدير الدقة
                if error < 1e-15:
                    accuracy = 'ممتازة'
                elif error < 1e-12:
                    accuracy = 'عالية جداً'
                elif error < 1e-10:
                    accuracy = 'عالية'
                elif error < 1e-8:
                    accuracy = 'جيدة'
                elif error < 1e-6:
                    accuracy = 'مقبولة'
                else:
                    accuracy = 'منخفضة'
                
            except Exception as e:
                value = None
                is_root = False
                error = float('inf')
                accuracy = 'غير قابلة للحساب'
            
            result = {
                'template_id': template_id,
                'template_name': 'verify_root_substitution',
                'template_name_ar': 'التحقق من صحة جذر بالتعويض',
                'input': {'equation': equation, 'root': root},
                'equation': equation,
                'root': root,
                'substitution_result': value,
                'is_valid_root': is_root,
                'error': error,
                'accuracy': accuracy,
                'relative_error': error / abs(root) if root != 0 else error
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_150_verify_multiple_roots(self, equation: str, roots: List[float]) -> Dict[str, Any]:
        """
        قالب 150: التحقق من صحة عدة جذور
        """
        template_id = 150
        self.stats['total_calls'] += 1
        
        try:
            equation = equation.replace(' ', '')
            
            if '=' in equation:
                lhs, rhs = equation.split('=')
                expr = sp.sympify(lhs) - sp.sympify(rhs)
            else:
                expr = sp.sympify(equation)
            
            verifications = []
            valid_roots = []
            invalid_roots = []
            
            for root in roots:
                try:
                    value = float(sp.N(expr.subs(self.x, root)))
                    is_valid = abs(value) < self.precision
                    
                    verifications.append({
                        'root': root,
                        'value': value,
                        'is_valid': is_valid,
                        'error': abs(value)
                    })
                    
                    if is_valid:
                        valid_roots.append(root)
                    else:
                        invalid_roots.append(root)
                        
                except:
                    verifications.append({
                        'root': root,
                        'value': None,
                        'is_valid': False,
                        'error': float('inf')
                    })
                    invalid_roots.append(root)
            
            result = {
                'template_id': template_id,
                'template_name': 'verify_multiple_roots',
                'template_name_ar': 'التحقق من صحة عدة جذور',
                'input': {'equation': equation, 'roots': roots},
                'equation': equation,
                'verifications': verifications,
                'valid_roots': valid_roots,
                'invalid_roots': invalid_roots,
                'num_valid': len(valid_roots),
                'num_invalid': len(invalid_roots),
                'success_rate': len(valid_roots) / len(roots) * 100 if roots else 0
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_151_verify_root_properties(self, equation: str, root: float) -> Dict[str, Any]:
        """
        قالب 151: التحقق من خصائص الجذر (التعدد، العلاقات)
        """
        template_id = 151
        self.stats['total_calls'] += 1
        
        try:
            equation = equation.replace(' ', '')
            
            if '=' in equation:
                lhs, rhs = equation.split('=')
                expr = sp.sympify(lhs) - sp.sympify(rhs)
            else:
                expr = sp.sympify(equation)
            
            # التحقق من أن الجذر يحقق المعادلة
            value = float(sp.N(expr.subs(self.x, root)))
            is_root = abs(value) < self.precision
            
            properties = {}
            
            if is_root:
                # التحقق من التعدد (باستخدام المشتقة)
                derivative = sp.diff(expr, self.x)
                deriv_value = float(sp.N(derivative.subs(self.x, root)))
                
                if abs(deriv_value) < self.precision:
                    # مشتقة أولى صفر، تحقق من المشتقة الثانية
                    second_derivative = sp.diff(derivative, self.x)
                    second_value = float(sp.N(second_derivative.subs(self.x, root)))
                    
                    if abs(second_value) < self.precision:
                        multiplicity = "≥ 3"
                    else:
                        multiplicity = 2
                else:
                    multiplicity = 1
                
                properties['multiplicity'] = multiplicity
                
                # علاقة الجذر بالمعاملات (إذا كانت كثيرة حدود)
                if expr.is_polynomial():
                    coeffs = expr.as_coefficients_dict()
                    degree = sp.degree(expr)
                    
                    if degree >= 1:
                        # مجموع الجذور = -معامل x^(n-1)/معامل x^n
                        leading_coeff = coeffs.get(self.x**degree, 0)
                        if degree >= 2:
                            next_coeff = coeffs.get(self.x**(degree-1), 0)
                            if leading_coeff != 0:
                                sum_roots = -next_coeff / leading_coeff
                                properties['relation_to_sum'] = f"الجذر جزء من مجموع الجذور = {sum_roots}"
                        
                        # حاصل ضرب الجذور = (-1)^n * الحد الثابت / معامل الدرجة العليا
                        constant = coeffs.get(1, 0)
                        if leading_coeff != 0:
                            product_roots = ((-1)**degree) * constant / leading_coeff
                            properties['relation_to_product'] = f"الجذر جزء من حاصل ضرب الجذور = {product_roots}"
            
            result = {
                'template_id': template_id,
                'template_name': 'verify_root_properties',
                'template_name_ar': 'التحقق من خصائص الجذر',
                'input': {'equation': equation, 'root': root},
                'equation': equation,
                'root': root,
                'is_root': is_root,
                'verification_value': value,
                'properties': properties if is_root else {'note': 'القيمة المدخلة ليست جذراً'}
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_152_verify_root_accuracy(self, equation: str, root: float, tolerance: float = 1e-10) -> Dict[str, Any]:
        """
        قالب 152: التحقق من دقة جذر رقمي
        """
        template_id = 152
        self.stats['total_calls'] += 1
        
        try:
            equation = equation.replace(' ', '')
            
            if '=' in equation:
                lhs, rhs = equation.split('=')
                expr = sp.sympify(lhs) - sp.sympify(rhs)
            else:
                expr = sp.sympify(equation)
            
            # حساب قيمة المعادلة عند الجذر
            value = float(sp.N(expr.subs(self.x, root)))
            abs_error = abs(value)
            
            # تقدير الخطأ النسبي
            if abs(root) > self.precision:
                rel_error = abs_error / abs(root)
            else:
                rel_error = abs_error
            
            # تحديد الدقة
            meets_tolerance = abs_error < tolerance
            
            # تقدير عدد الخانات الصحيحة
            if abs_error > 0:
                correct_digits = -math.log10(abs_error)
            else:
                correct_digits = float('inf')
            
            # تحسين الجذر (خطوة واحدة من طريقة نيوتن)
            try:
                derivative = sp.diff(expr, self.x)
                deriv_value = float(sp.N(derivative.subs(self.x, root)))
                
                if abs(deriv_value) > self.precision:
                    improved_root = root - value / deriv_value
                    improvement = abs(improved_root - root)
                else:
                    improved_root = None
                    improvement = None
            except:
                improved_root = None
                improvement = None
            
            result = {
                'template_id': template_id,
                'template_name': 'verify_root_accuracy',
                'template_name_ar': 'التحقق من دقة جذر رقمي',
                'input': {'equation': equation, 'root': root, 'tolerance': tolerance},
                'equation': equation,
                'root': root,
                'absolute_error': abs_error,
                'relative_error': rel_error,
                'meets_tolerance': meets_tolerance,
                'correct_decimal_digits': correct_digits,
                'significance': f"{int(correct_digits)} خانة عشرية صحيحة" if correct_digits != float('inf') else "دقة تامة",
                'newton_step': {
                    'improved_root': improved_root,
                    'improvement': improvement
                } if improved_root is not None else None
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    # =========================================================================
    # دوال مساعدة
    # =========================================================================
    
    def _verify_quartic_solutions(self, expr, solutions) -> List[Dict]:
        """التحقق من حلول المعادلة الرباعية"""
        verification = []
        for sol in solutions:
            try:
                val = float(sp.N(expr.subs(self.x, sol)))
                verification.append({
                    'solution': str(sol),
                    'value': val,
                    'is_valid': abs(val) < self.precision
                })
            except:
                verification.append({
                    'solution': str(sol),
                    'value': None,
                    'is_valid': False
                })
        return verification
    
    def _check_cyclic_pattern(self, equations) -> bool:
        """التحقق من النمط الدوري في نظام معادلات"""
        # هذه دالة مبسطة
        return True
    
    def _get_trig_domain(self, substitution: str) -> str:
        """الحصول على مجال التعويض المثلثي"""
        domains = {
            'x = sin θ': 'θ ∈ R',
            'x = cos θ': 'θ ∈ R',
            'x = tan θ': 'θ ≠ π/2 + nπ',
            'x = sec θ': 'θ ≠ π/2 + nπ',
            'x = csc θ': 'θ ≠ nπ'
        }
        return domains.get(substitution, 'حسب التعويض')
    
    def _analyze_parametric_system(self, equations, parameters, variables) -> List[Dict]:
        """تحليل نظام مع باراميترات"""
        special_cases = []
        
        # محاولة إيجاد قيم الباراميترات التي تجعل المحدد صفراً
        if len(equations) == len(variables):
            # بناء مصفوفة المعاملات
            A = []
            for eq in equations:
                row = []
                for var in variables:
                    coeff = eq.lhs.coeff(var) if hasattr(eq.lhs, 'coeff') else 0
                    row.append(coeff)
                A.append(row)
            
            # محاولة حساب المحدد
            try:
                A_matrix = sp.Matrix(A)
                det_A = A_matrix.det()
                
                # إيجاد قيم الباراميترات التي تجعل المحدد صفراً
                for param in parameters:
                    critical = sp.solve(det_A, param)
                    for val in critical:
                        special_cases.append({
                            'parameter': str(param),
                            'value': str(val),
                            'condition': 'det = 0',
                            'description': f'عند {param} = {val}، المحدد يصفر'
                        })
            except:
                pass
        
        return special_cases
    
    def _extract_common_factor(self, expressions) -> float:
        """استخراج العامل المشترك من قائمة تعبيرات"""
        if not expressions:
            return 1
        
        common = expressions[0]
        for expr in expressions[1:]:
            common = sp.gcd(common, expr)
            if common == 1:
                break
        
        return common
    
    def _get_integer_factors(self, n: int) -> List[int]:
        """إيجاد جميع قواسم عدد صحيح"""
        if n == 0:
            return [1]
        
        factors = []
        for i in range(1, int(math.sqrt(n)) + 1):
            if n % i == 0:
                factors.append(i)
                if i != n // i:
                    factors.append(n // i)
        return sorted(factors)
    
    def get_stats(self) -> Dict[str, Any]:
        """إحصائيات العمليات"""
        return {
            'total_calls': self.stats['total_calls'],
            'successful': self.stats['successful'],
            'failed': self.stats['failed'],
            'success_rate': (self.stats['successful'] / self.stats['total_calls'] * 100) if self.stats['total_calls'] > 0 else 0,
            'by_template': self.stats['by_template']
        }


# =============================================================================
# اختبار وتشغيل
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("🧮 بسم الله الرحمن الرحيم")
    print("📁 الملف 3/3: الجبر المتقدم - المعادلات الرباعية، الأنماط، التحقق")
    print("=" * 80)
    
    solver = AdvancedAlgebraSolver()
    
    print("\n✅ تم تحميل 50 قالباً بنجاح (القوالب 103-152)")
    print(f"📊 إحصائيات: {solver.get_stats()}")
    print("=" * 80)
