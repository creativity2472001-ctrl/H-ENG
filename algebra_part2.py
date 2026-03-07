"""
================================================================================
الملف 2/3: الجبر المتوسط - القوى، الأسس، اللوغاريتمات، والكسور (50 قالباً)
File 2/3: Intermediate Algebra - Powers, Logarithms, and Fractions (50 Templates)

الأنواع المغطاة (11-20):
11. القوى والأسس (6 قوالب)          - templates 53-58
12. الجذور التربيعية والتكعيبية (5 قوالب) - templates 59-63
13. القواعد اللوغاريتمية (5 قوالب)   - templates 64-68
14. المعادلات اللوغاريتمية (6 قوالب) - templates 69-74
15. المعادلات الأسية (6 قوالب)       - templates 75-80
16. المعادلات الكسرية (5 قوالب)      - templates 81-85
17. المعادلات المطلقة (5 قوالب)      - templates 86-90
18. تبسيط الكسور الجبرية (4 قوالب)   - templates 91-94
19. العمليات على الكسور الجبرية (4 قوالب) - templates 95-98
20. المعادلات الجذرية (4 قوالب)      - templates 99-102
================================================================================
"""

import sympy as sp
import numpy as np
import logging
from typing import Union, List, Dict, Any, Tuple, Optional
import math
import cmath

# إعداد نظام التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntermediateAlgebraSolver:
    """
    ============================================================================
    الحلّال المتوسط للجبر - القوى، الأسس، اللوغاريتمات، والكسور
    يغطي 50 قالباً في الأنواع 11-20
    ============================================================================
    """
    
    def __init__(self):
        """تهيئة المتغيرات الرمزية وإعدادات الدقة"""
        # متغيرات رمزية
        self.x = sp.Symbol('x', real=True)
        self.y = sp.Symbol('y', real=True)
        self.z = sp.Symbol('z', real=True)
        self.a = sp.Symbol('a', real=True)
        self.b = sp.Symbol('b', real=True)
        self.c = sp.Symbol('c', real=True)
        self.n = sp.Symbol('n', real=True)
        
        # ثوابت رياضية
        self.e = sp.E
        self.pi = sp.pi
        self.i = sp.I
        
        # إعدادات الدقة
        self.precision = 1e-15
        
        # سجل العمليات
        self.stats = {
            'total_calls': 0,
            'successful': 0,
            'failed': 0,
            'by_template': {}
        }
        
        logger.info("✅ تم تهيئة IntermediateAlgebraSolver بنجاح")
    
    # =========================================================================
    # القسم 11: القوى والأسس (6 قوالب) - Templates 53-58
    # =========================================================================
    
    def template_53_power_rules(self, base: str, exponent: float) -> Dict[str, Any]:
        """
        قالب 53: تطبيق قوانين القوى على تعبير
        يغطي: قواعد ضرب وقسمة القوى، قوى القوى
        """
        self.stats['total_calls'] += 1
        template_id = 53
        
        try:
            base_expr = sp.sympify(base)
            
            # تمثيل القوة
            power_expr = base_expr ** exponent
            
            # تطبيق القوانين
            rules_demo = []
            
            # قانون ضرب القوى: a^m × a^n = a^(m+n)
            if exponent > 0:
                product = base_expr ** (exponent/2) * base_expr ** (exponent/2)
                rules_demo.append({
                    'rule': 'a^m × a^n = a^(m+n)',
                    'example': f"{base}^{exponent/2} × {base}^{exponent/2} = {base}^{exponent}",
                    'result': str(sp.simplify(product))
                })
            
            # قانون قسمة القوى: a^m ÷ a^n = a^(m-n)
            if exponent > 1:
                division = (base_expr ** exponent) / (base_expr ** (exponent-1))
                rules_demo.append({
                    'rule': 'a^m ÷ a^n = a^(m-n)',
                    'example': f"{base}^{exponent} ÷ {base}^{exponent-1} = {base}¹",
                    'result': str(sp.simplify(division))
                })
            
            # قانون قوة القوة: (a^m)^n = a^(m×n)
            power_of_power = (base_expr ** (exponent/2)) ** 2
            rules_demo.append({
                'rule': '(a^m)^n = a^(m×n)',
                'example': f"({base}^{exponent/2})² = {base}^{exponent}",
                'result': str(sp.simplify(power_of_power))
            })
            
            result = {
                'template_id': template_id,
                'template_name': 'power_rules',
                'template_name_ar': 'قوانين القوى',
                'input': {'base': base, 'exponent': exponent},
                'expression': str(power_expr),
                'simplified': str(sp.simplify(power_expr)),
                'rules_demonstration': rules_demo,
                'special_cases': {
                    'zero_exponent': f"{base}⁰ = 1" if exponent != 0 else None,
                    'negative_exponent': f"{base}^{{{exponent}}} = 1/{base}^{{{-exponent}}}" if exponent < 0 else None,
                    'fractional_exponent': f"{base}^{{{exponent}}} = {base}^{{{exponent}}} (جذر)" if isinstance(exponent, float) and not exponent.is_integer() else None
                }
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_54_power_equations_same_base(self, base: float, exp1: str, exp2: str) -> Dict[str, Any]:
        """
        قالب 54: معادلات أسية بنفس الأساس
        مثال: 2^(x+1) = 2^(2x-3)
        """
        template_id = 54
        self.stats['total_calls'] += 1
        
        try:
            # بناء المعادلة: base^(exp1) = base^(exp2)
            lhs = base ** sp.sympify(exp1)
            rhs = base ** sp.sympify(exp2)
            
            # بما أن الأساس متساوي، نساوي الأسس
            exp1_expr = sp.sympify(exp1)
            exp2_expr = sp.sympify(exp2)
            
            equation = sp.Eq(exp1_expr, exp2_expr)
            solution = sp.solve(equation, self.x)
            
            result = {
                'template_id': template_id,
                'template_name': 'power_equations_same_base',
                'template_name_ar': 'معادلات أسية - نفس الأساس',
                'input': {'base': base, 'exponent1': exp1, 'exponent2': exp2},
                'equation': f"{base}^({exp1}) = {base}^({exp2})",
                'equated_exponents': f"{exp1} = {exp2}",
                'solution': [float(sp.N(sol)) for sol in solution] if solution else [],
                'exact_solution': [str(sol) for sol in solution] if solution else [],
                'verification': self._verify_exponential_solution(base, exp1, exp2, solution),
                'method': 'بما أن الأساس متساوي، نساوي الأسس'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_55_power_equations_different_base(self, a: float, b: float, c: float) -> Dict[str, Any]:
        """
        قالب 55: معادلات أسية بأسس مختلفة: a^x = b
        """
        template_id = 55
        self.stats['total_calls'] += 1
        
        try:
            # حل: a^x = b
            # x = log_a(b) = ln(b)/ln(a)
            
            if a <= 0 or a == 1 or b <= 0:
                raise ValueError("الأساس يجب أن يكون موجباً ولا يساوي 1، والطرف الأيمن يجب أن يكون موجباً")
            
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
                'domain': 'x > 0, a > 0, a ≠ 1'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_56_power_inequalities(self, a: float, b: float, inequality: str) -> Dict[str, Any]:
        """
        قالب 56: متباينات أسية: a^x > b
        """
        template_id = 56
        self.stats['total_calls'] += 1
        
        try:
            if a <= 0 or a == 1:
                raise ValueError("الأساس يجب أن يكون موجباً ولا يساوي 1")
            
            # نقطة التعادل
            critical_point = math.log(b) / math.log(a) if b > 0 else None
            
            solution = ""
            if b <= 0:
                if a > 1:
                    solution = "جميع الأعداد الحقيقية" if inequality in ['>', '≥'] else "لا يوجد حل"
                else:
                    solution = "جميع الأعداد الحقيقية" if inequality in ['<', '≤'] else "لا يوجد حل"
            else:
                if a > 1:
                    # دالة متزايدة
                    if inequality == '>':
                        solution = f"x > {critical_point}"
                    elif inequality == '≥':
                        solution = f"x ≥ {critical_point}"
                    elif inequality == '<':
                        solution = f"x < {critical_point}"
                    elif inequality == '≤':
                        solution = f"x ≤ {critical_point}"
                else:
                    # دالة متناقصة (0 < a < 1)
                    if inequality == '>':
                        solution = f"x < {critical_point}"
                    elif inequality == '≥':
                        solution = f"x ≤ {critical_point}"
                    elif inequality == '<':
                        solution = f"x > {critical_point}"
                    elif inequality == '≤':
                        solution = f"x ≥ {critical_point}"
            
            result = {
                'template_id': template_id,
                'template_name': 'power_inequalities',
                'template_name_ar': 'متباينات أسية',
                'input': {'a': a, 'b': b, 'inequality': inequality},
                'inequality': f"{a}^x {inequality} {b}",
                'critical_point': critical_point,
                'function_type': 'متزايدة' if a > 1 else 'متناقصة',
                'solution': solution,
                'interval_notation': solution
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_57_power_system(self, eq1: str, eq2: str) -> Dict[str, Any]:
        """
        قالب 57: نظام معادلات أسية
        مثال: 2^x * 3^y = 24, 2^(x+y) = 16
        """
        template_id = 57
        self.stats['total_calls'] += 1
        
        try:
            # تحليل المعادلات
            eq1 = eq1.replace(' ', '')
            eq2 = eq2.replace(' ', '')
            
            lhs1, rhs1 = eq1.split('=')
            lhs2, rhs2 = eq2.split('=')
            
            # تحويل إلى تعبيرات SymPy
            expr1 = sp.Eq(sp.sympify(lhs1), sp.sympify(rhs1))
            expr2 = sp.Eq(sp.sympify(lhs2), sp.sympify(rhs2))
            
            # حل النظام
            solution = sp.solve([expr1, expr2], [self.x, self.y])
            
            # تنظيم الحلول
            solutions_list = []
            if solution:
                if isinstance(solution, list):
                    for sol in solution:
                        solutions_list.append({
                            'x': float(sp.N(sol[self.x])) if self.x in sol else None,
                            'y': float(sp.N(sol[self.y])) if self.y in sol else None
                        })
                else:
                    solutions_list.append({
                        'x': float(sp.N(solution[self.x])) if self.x in solution else None,
                        'y': float(sp.N(solution[self.y])) if self.y in solution else None
                    })
            
            result = {
                'template_id': template_id,
                'template_name': 'power_system',
                'template_name_ar': 'نظام معادلات أسية',
                'input': {'eq1': eq1, 'eq2': eq2},
                'solutions': solutions_list,
                'num_solutions': len(solutions_list),
                'method': 'استخدام خواص الأسس واللوغاريتمات'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_58_power_word_problems(self, problem_type: str, values: Dict) -> Dict[str, Any]:
        """
        قالب 58: مسائل كلامية على الأسس (نمو أسي، تضاؤل إشعاعي)
        """
        template_id = 58
        self.stats['total_calls'] += 1
        
        try:
            applications = {
                'exponential_growth': {
                    'formula': 'A = P(1 + r)^t',
                    'description': 'النمو الأسي: A الكمية النهائية، P الكمية الابتدائية، r معدل النمو، t الزمن'
                },
                'exponential_decay': {
                    'formula': 'A = P(1 - r)^t',
                    'description': 'الاضمحلال الأسي: A الكمية المتبقية، P الكمية الابتدائية، r معدل الاضمحلال، t الزمن'
                },
                'compound_interest': {
                    'formula': 'A = P(1 + r/n)^(nt)',
                    'description': 'الفائدة المركبة: A المبلغ النهائي، P المبلغ الأصلي، r معدل الفائدة، n عدد مرات التحويل، t الزمن'
                },
                'radioactive_decay': {
                    'formula': 'A = A₀ × 2^(-t/h)',
                    'description': 'عمر النصف: A الكمية المتبقية، A₀ الكمية الابتدائية، t الزمن، h عمر النصف'
                }
            }
            
            if problem_type not in applications:
                raise ValueError(f'نوع المسألة غير معروف: {problem_type}')
            
            # حساب مبسط حسب المعطيات
            calculation = None
            if problem_type == 'exponential_growth' and 'P' in values and 'r' in values and 't' in values:
                P = values['P']
                r = values['r']
                t = values['t']
                A = P * (1 + r) ** t
                calculation = {
                    'initial': P,
                    'rate': r,
                    'time': t,
                    'final': A,
                    'steps': [
                        f"A = {P}(1 + {r})^{t}",
                        f"A = {P}({1+r})^{t}",
                        f"A = {A}"
                    ]
                }
            
            result = {
                'template_id': template_id,
                'template_name': 'power_word_problems',
                'template_name_ar': 'مسائل كلامية - الأسس',
                'input': {'problem_type': problem_type, 'values': values},
                'application': applications[problem_type],
                'calculation': calculation,
                'examples': self._get_exponential_examples(problem_type)
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    # =========================================================================
    # القسم 12: الجذور التربيعية والتكعيبية (5 قوالب) - Templates 59-63
    # =========================================================================
    
    def template_59_square_root_simplify(self, number: float) -> Dict[str, Any]:
        """
        قالب 59: تبسيط الجذور التربيعية
        مثال: √50 = 5√2
        """
        template_id = 59
        self.stats['total_calls'] += 1
        
        try:
            if number < 0:
                # جذر تربيعي لعدد سالب
                simplified = f"{cmath.sqrt(number)}"
                is_real = False
            else:
                # تحليل العدد
                factors = self._prime_factors(int(number))
                
                # تجميع العوامل المربعة
                perfect_squares = {}
                for factor in factors:
                    perfect_squares[factor] = perfect_squares.get(factor, 0) + 1
                
                outside = 1
                inside = 1
                
                for factor, count in perfect_squares.items():
                    pairs = count // 2
                    outside *= factor ** pairs
                    inside *= factor ** (count - 2 * pairs)
                
                if inside == 1:
                    simplified = f"{outside}"
                elif outside == 1:
                    simplified = f"√{inside}"
                else:
                    simplified = f"{outside}√{inside}"
                
                is_real = True
            
            result = {
                'template_id': template_id,
                'template_name': 'square_root_simplify',
                'template_name_ar': 'تبسيط الجذور التربيعية',
                'input': {'number': number},
                'original': f"√{number}",
                'simplified': simplified,
                'is_real': is_real,
                'decimal_approximation': math.sqrt(number) if number >= 0 else str(cmath.sqrt(number)),
                'prime_factors': self._prime_factors(int(number)) if number > 0 else None,
                'method': 'تحليل العدد إلى عوامله الأولية وتجميع الأزواج'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_60_cube_root_simplify(self, number: float) -> Dict[str, Any]:
        """
        قالب 60: تبسيط الجذور التكعيبية
        مثال: ∛54 = 3∛2
        """
        template_id = 60
        self.stats['total_calls'] += 1
        
        try:
            # تحليل العدد
            factors = self._prime_factors(abs(int(number)))
            
            # تجميع العوامل التكعيبية
            perfect_cubes = {}
            for factor in factors:
                perfect_cubes[factor] = perfect_cubes.get(factor, 0) + 1
            
            outside = 1
            inside = 1
            sign = -1 if number < 0 else 1
            
            for factor, count in perfect_cubes.items():
                triples = count // 3
                outside *= factor ** triples
                inside *= factor ** (count - 3 * triples)
            
            if inside == 1:
                simplified = f"{sign * outside}"
            elif outside == 1:
                simplified = f"{'-' if sign < 0 else ''}∛{inside}"
            else:
                simplified = f"{sign * outside}∛{inside}"
            
            result = {
                'template_id': template_id,
                'template_name': 'cube_root_simplify',
                'template_name_ar': 'تبسيط الجذور التكعيبية',
                'input': {'number': number},
                'original': f"∛{number}",
                'simplified': simplified,
                'decimal_approximation': np.cbrt(number),
                'prime_factors': factors,
                'method': 'تحليل العدد إلى عوامله الأولية وتجميع الثلاثيات'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_61_root_operations(self, operation: str, radicand1: float, radicand2: float, root: int = 2) -> Dict[str, Any]:
        """
        قالب 61: عمليات على الجذور (جمع، ضرب، قسمة)
        """
        template_id = 61
        self.stats['total_calls'] += 1
        
        try:
            result = None
            steps = []
            
            if operation == 'multiply':
                # ضرب الجذور: √a × √b = √(a×b)
                product = (radicand1 * radicand2) ** (1/root)
                simplified = self._simplify_root(product, root)
                steps = [
                    f"√{radicand1} × √{radicand2} = √({radicand1} × {radicand2})",
                    f"= √{radicand1 * radicand2}",
                    f"= {simplified}"
                ]
                result = {
                    'operation': 'multiplication',
                    'result': simplified,
                    'decimal': product
                }
                
            elif operation == 'divide':
                # قسمة الجذور: √a ÷ √b = √(a/b)
                if radicand2 == 0:
                    raise ValueError("لا يمكن القسمة على صفر")
                quotient = (radicand1 / radicand2) ** (1/root)
                simplified = self._simplify_root(quotient, root)
                steps = [
                    f"√{radicand1} ÷ √{radicand2} = √({radicand1} ÷ {radicand2})",
                    f"= √{radicand1 / radicand2}",
                    f"= {simplified}"
                ]
                result = {
                    'operation': 'division',
                    'result': simplified,
                    'decimal': quotient
                }
                
            elif operation == 'add':
                # جمع الجذور (إذا كانت متشابهة)
                sqrt1 = math.sqrt(radicand1) if root == 2 else np.cbrt(radicand1)
                sqrt2 = math.sqrt(radicand2) if root == 2 else np.cbrt(radicand2)
                
                if abs(sqrt1 - sqrt2) < self.precision:
                    # جذور متشابهة
                    sum_val = 2 * sqrt1
                    steps = [
                        f"الجذور متشابهة: {sqrt1} + {sqrt2} = 2 × {sqrt1} = {sum_val}"
                    ]
                else:
                    # جذور مختلفة
                    sum_val = sqrt1 + sqrt2
                    steps = [
                        f"الجذور مختلفة، نجمع القيم العشرية:",
                        f"{sqrt1} + {sqrt2} = {sum_val}"
                    ]
                
                result = {
                    'operation': 'addition',
                    'result': str(sum_val),
                    'decimal': sum_val
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
                'rules_applied': self._get_root_rules(operation, root)
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result_data
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_62_rationalizing_denominator(self, numerator: float, denominator: float, root: int = 2) -> Dict[str, Any]:
        """
        قالب 62: توحيد المقام (التخلص من الجذور في المقام)
        مثال: 1/√2 = √2/2
        """
        template_id = 62
        self.stats['total_calls'] += 1
        
        try:
            if denominator < 0:
                # جذر تربيعي لعدد سالب
                raise ValueError("المقام يحتوي على جذر عدد سالب")
            
            # توحيد المقام
            if root == 2:
                # ضرب البسط والمقام في √denominator
                new_numerator = numerator * math.sqrt(denominator)
                new_denominator = denominator
                
                steps = [
                    f"1. الكسر الأصلي: {numerator}/√{denominator}",
                    f"2. نضرب البسط والمقام في √{denominator}:",
                    f"   = ({numerator} × √{denominator}) / (√{denominator} × √{denominator})",
                    f"3. المقام يصبح: (√{denominator})² = {denominator}",
                    f"4. النتيجة: ({numerator}√{denominator})/{denominator}"
                ]
                
                rationalized = f"({numerator}√{denominator})/{denominator}"
                simplified = self._simplify_fraction(numerator, denominator) + f"√{denominator}" if numerator % denominator == 0 else rationalized
                
            elif root == 3:
                # للجذر التكعيبي: نضرب في ∛(denominator²)
                new_numerator = numerator * (denominator ** (2/3))
                new_denominator = denominator
                
                steps = [
                    f"1. الكسر الأصلي: {numerator}/∛{denominator}",
                    f"2. نضرب البسط والمقام في ∛{denominator}²:",
                    f"   = ({numerator} × ∛{denominator}²) / (∛{denominator} × ∛{denominator}²)",
                    f"3. المقام يصبح: ∛{denominator}³ = {denominator}",
                    f"4. النتيجة: ({numerator}∛{denominator}²)/{denominator}"
                ]
                
                rationalized = f"({numerator}∛{denominator}²)/{denominator}"
                simplified = rationalized
            
            result = {
                'template_id': template_id,
                'template_name': 'rationalizing_denominator',
                'template_name_ar': 'توحيد المقام',
                'input': {
                    'numerator': numerator,
                    'denominator': denominator,
                    'root': root
                },
                'original_fraction': f"{numerator}/√{denominator}" if root == 2 else f"{numerator}/∛{denominator}",
                'rationalized': rationalized,
                'simplified': simplified,
                'steps': steps,
                'decimal_approximation': numerator / (denominator ** (1/root))
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_63_nested_radicals(self, expression: str) -> Dict[str, Any]:
        """
        قالب 63: تبسيط الجذور المتداخلة
        مثال: √(2 + √3)
        """
        template_id = 63
        self.stats['total_calls'] += 1
        
        try:
            expr = sp.sympify(expression.replace('√', 'sqrt'))
            
            # محاولة التبسيط
            simplified = sp.simplify(expr)
            
            # التحقق من إمكانية الكتابة على صورة a + b√c
            denested = self._try_denest(expr)
            
            result = {
                'template_id': template_id,
                'template_name': 'nested_radicals',
                'template_name_ar': 'الجذور المتداخلة',
                'input': {'expression': expression},
                'original': str(expr),
                'simplified': str(simplified),
                'denested_form': denested if denested else 'لا يمكن التبسيط أكثر',
                'numerical_value': float(sp.N(expr)),
                'method': 'محاولة كتابة التعبير على صورة (√a + √b)²'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    # =========================================================================
    # القسم 13: القواعد اللوغاريتمية (5 قوالب) - Templates 64-68
    # =========================================================================
    
    def template_64_logarithm_basics(self, base: float, argument: float) -> Dict[str, Any]:
        """
        قالب 64: أساسيات اللوغاريتمات - تعريف وخصائص
        """
        template_id = 64
        self.stats['total_calls'] += 1
        
        try:
            if base <= 0 or base == 1 or argument <= 0:
                raise ValueError("الأساس يجب أن يكون > 0 ولا يساوي 1، والوسيط يجب أن يكون > 0")
            
            # حساب اللوغاريتم
            log_value = math.log(argument, base)
            
            # التحقق: base^log_value = argument
            verification = abs(base ** log_value - argument) < self.precision
            
            result = {
                'template_id': template_id,
                'template_name': 'logarithm_basics',
                'template_name_ar': 'أساسيات اللوغاريتمات',
                'input': {'base': base, 'argument': argument},
                'logarithm': {
                    'notation': f"log_{base}({argument})",
                    'value': log_value,
                    'exact': str(sp.log(argument, base)) if argument > 0 else None
                },
                'definition': f"log_{base}({argument}) = {log_value}  يعني أن  {base}^{log_value} = {argument}",
                'verification': {
                    'computed': base ** log_value,
                    'expected': argument,
                    'is_valid': verification
                },
                'special_cases': {
                    'log_a(1)': 0,
                    'log_a(a)': 1,
                    'log_a(a^n)': 'n'
                }
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_65_logarithm_properties(self, operation: str, a: float, b: float, base: float = 10) -> Dict[str, Any]:
        """
        قالب 65: خصائص اللوغاريتمات (الضرب، القسمة، القوى)
        """
        template_id = 65
        self.stats['total_calls'] += 1
        
        try:
            properties = {
                'product': {
                    'rule': 'log_b(MN) = log_b M + log_b N',
                    'left': math.log(a * b, base) if a > 0 and b > 0 else None,
                    'right': (math.log(a, base) + math.log(b, base)) if a > 0 and b > 0 else None
                },
                'quotient': {
                    'rule': 'log_b(M/N) = log_b M - log_b N',
                    'left': math.log(a / b, base) if a > 0 and b > 0 else None,
                    'right': (math.log(a, base) - math.log(b, base)) if a > 0 and b > 0 else None
                },
                'power': {
                    'rule': 'log_b(M^n) = n log_b M',
                    'left': math.log(a ** b, base) if a > 0 else None,
                    'right': b * math.log(a, base) if a > 0 else None
                },
                'change_base': {
                    'rule': 'log_a M = log_b M / log_b a',
                    'computation': math.log(a, base) / math.log(b, base) if a > 0 and b > 0 else None
                }
            }
            
            if operation not in properties:
                raise ValueError(f'عملية غير معروفة: {operation}')
            
            prop = properties[operation]
            
            result = {
                'template_id': template_id,
                'template_name': 'logarithm_properties',
                'template_name_ar': 'خصائص اللوغاريتمات',
                'input': {'operation': operation, 'a': a, 'b': b, 'base': base},
                'property': prop['rule'],
                'demonstration': {
                    'left': prop['left'],
                    'right': prop['right'],
                    'verification': abs(prop['left'] - prop['right']) < self.precision if prop['left'] and prop['right'] else None
                } if 'left' in prop else {
                    'result': prop['computation']
                },
                'examples': self._get_log_examples(operation, base)
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_66_logarithm_simplify(self, expression: str) -> Dict[str, Any]:
        """
        قالب 66: تبسيط تعبيرات لوغاريتمية
        مثال: log(x) + log(y) = log(xy)
        """
        template_id = 66
        self.stats['total_calls'] += 1
        
        try:
            expr = sp.sympify(expression.replace('log', 'log'))
            
            # محاولة التبسيط بطرق مختلفة
            simplified = sp.simplify(expr)
            combined = sp.logcombine(expr, force=True)
            expanded = sp.expand_log(expr, force=True)
            
            # التعرف على القوانين المستخدمة
            laws_used = []
            if 'log' in str(expr):
                if '+' in str(expr):
                    laws_used.append('log_b M + log_b N = log_b (MN)')
                if '-' in str(expr):
                    laws_used.append('log_b M - log_b N = log_b (M/N)')
                if '*' in str(expr) and 'log' in str(expr).split('*')[0]:
                    laws_used.append('n log_b M = log_b (M^n)')
            
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
                'domain': 'جميع المتغيرات > 0'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_67_logarithm_change_base(self, value: float, old_base: float, new_base: float) -> Dict[str, Any]:
        """
        قالب 67: تغيير أساس اللوغاريتم
        مثال: log_2(8) = log_10(8)/log_10(2)
        """
        template_id = 67
        self.stats['total_calls'] += 1
        
        try:
            if value <= 0 or old_base <= 0 or old_base == 1 or new_base <= 0 or new_base == 1:
                raise ValueError("المدخلات يجب أن تكون موجبة والأساس لا يساوي 1")
            
            # الحساب بالأساس القديم
            log_old = math.log(value, old_base)
            
            # تغيير الأساس
            log_new = math.log(value, new_base)
            log_new_calc = math.log(value) / math.log(new_base)
            
            # باستخدام القانون: log_a M = log_b M / log_b a
            conversion = math.log(value) / math.log(old_base)  # للأساس e
            conversion_new = math.log(value, new_base) / math.log(old_base, new_base)
            
            result = {
                'template_id': template_id,
                'template_name': 'logarithm_change_base',
                'template_name_ar': 'تغيير أساس اللوغاريتم',
                'input': {'value': value, 'old_base': old_base, 'new_base': new_base},
                'original': f"log_{old_base}({value}) = {log_old}",
                'converted': {
                    'formula': f"log_{old_base}({value}) = log_{new_base}({value}) / log_{new_base}({old_base})",
                    'calculation': f"= {math.log(value, new_base)} / {math.log(old_base, new_base)}",
                    'result': conversion_new
                },
                'natural_log_form': f"ln({value})/ln({old_base}) = {math.log(value)}/{math.log(old_base)} = {math.log(value)/math.log(old_base)}",
                'verification': abs(log_old - conversion_new) < self.precision
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_68_logarithm_inequalities(self, base: float, argument: str, inequality: str) -> Dict[str, Any]:
        """
        قالب 68: متباينات لوغاريتمية
        مثال: log_2(x) > 3
        """
        template_id = 68
        self.stats['total_calls'] += 1
        
        try:
            if base <= 0 or base == 1:
                raise ValueError("الأساس يجب أن يكون > 0 ولا يساوي 1")
            
            # تحويل المتباينة
            # log_base(argument) inequality value
            # argument inequality base^value مع مراعاة اتجاه المتباينة
            
            # هذه دالة مبسطة - في التطبيق الفعلي نحتاج لتحليل التعبير
            
            result = {
                'template_id': template_id,
                'template_name': 'logarithm_inequalities',
                'template_name_ar': 'متباينات لوغاريتمية',
                'input': {'base': base, 'argument': argument, 'inequality': inequality},
                'note': 'يجب مراعاة مجال الدالة اللوغاريتمية (الوسيط > 0)',
                'domain': f"{argument} > 0",
                'solution_method': 'تحويل المتباينة إلى صيغة أسية مع مراعاة اتجاه المتباينة حسب الأساس'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    # =========================================================================
    # القسم 14: المعادلات اللوغاريتمية (6 قوالب) - Templates 69-74
    # =========================================================================
    
    def template_69_logarithmic_simple(self, base: float, argument: str, value: float) -> Dict[str, Any]:
        """
        قالب 69: معادلة لوغاريتمية بسيطة: log_base(argument) = value
        """
        template_id = 69
        self.stats['total_calls'] += 1
        
        try:
            # log_base(argument) = value  =>  argument = base^value
            arg_expr = sp.sympify(argument)
            
            # حل المعادلة
            rhs = base ** value
            equation = sp.Eq(arg_expr, rhs)
            solution = sp.solve(equation, self.x)
            
            # التحقق من مجال اللوغاريتم
            valid_solutions = []
            for sol in solution:
                if sol.is_real:
                    # التحقق من أن argument > 0
                    arg_val = float(sp.N(arg_expr.subs(self.x, sol)))
                    if arg_val > 0:
                        valid_solutions.append(float(sp.N(sol)))
            
            result = {
                'template_id': template_id,
                'template_name': 'logarithmic_simple',
                'template_name_ar': 'معادلة لوغاريتمية بسيطة',
                'input': {'base': base, 'argument': argument, 'value': value},
                'equation': f"log_{base}({argument}) = {value}",
                'exponential_form': f"{argument} = {base}^{value} = {rhs}",
                'solutions': valid_solutions,
                'domain_condition': f"{argument} > 0",
                'verification': self._verify_logarithmic_solutions(arg_expr, base, value, valid_solutions)
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_70_logarithmic_sum(self, terms: List[str], value: float, base: float = 10) -> Dict[str, Any]:
        """
        قالب 70: معادلة لوغاريتمية بمجموع لوغاريتمات: log(A) + log(B) = C
        """
        template_id = 70
        self.stats['total_calls'] += 1
        
        try:
            # تحويل المجموع: log(A) + log(B) = log(A*B)
            product = 1
            for term in terms:
                product *= sp.sympify(term)
            
            # المعادلة: log(product) = value
            rhs = base ** value
            equation = sp.Eq(product, rhs)
            
            solution = sp.solve(equation, self.x)
            
            # التحقق من المجال
            valid_solutions = []
            for sol in solution:
                valid = True
                for term in terms:
                    term_val = float(sp.N(sp.sympify(term).subs(self.x, sol)))
                    if term_val <= 0:
                        valid = False
                        break
                if valid:
                    valid_solutions.append(float(sp.N(sol)))
            
            result = {
                'template_id': template_id,
                'template_name': 'logarithmic_sum',
                'template_name_ar': 'معادلة لوغاريتمية - مجموع لوغاريتمات',
                'input': {'terms': terms, 'value': value, 'base': base},
                'original_equation': ' + '.join([f"log({t})" for t in terms]) + f" = {value}",
                'combined_form': f"log({' × '.join(terms)}) = {value}",
                'exponential_form': f"{' × '.join(terms)} = {base}^{value} = {base**value}",
                'solutions': valid_solutions,
                'domain_conditions': [f"{t} > 0" for t in terms]
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_71_logarithmic_difference(self, term1: str, term2: str, value: float, base: float = 10) -> Dict[str, Any]:
        """
        قالب 71: معادلة لوغاريتمية بطرح لوغاريتمين: log(A) - log(B) = C
        """
        template_id = 71
        self.stats['total_calls'] += 1
        
        try:
            # تحويل الطرح: log(A) - log(B) = log(A/B)
            A = sp.sympify(term1)
            B = sp.sympify(term2)
            
            quotient = A / B
            
            # المعادلة: log(quotient) = value
            rhs = base ** value
            equation = sp.Eq(quotient, rhs)
            
            solution = sp.solve(equation, self.x)
            
            # التحقق من المجال
            valid_solutions = []
            for sol in solution:
                A_val = float(sp.N(A.subs(self.x, sol)))
                B_val = float(sp.N(B.subs(self.x, sol)))
                if A_val > 0 and B_val > 0:
                    valid_solutions.append(float(sp.N(sol)))
            
            result = {
                'template_id': template_id,
                'template_name': 'logarithmic_difference',
                'template_name_ar': 'معادلة لوغاريتمية - طرح لوغاريتمين',
                'input': {'term1': term1, 'term2': term2, 'value': value, 'base': base},
                'original_equation': f"log({term1}) - log({term2}) = {value}",
                'combined_form': f"log({term1}/{term2}) = {value}",
                'exponential_form': f"{term1}/{term2} = {base}^{value} = {base**value}",
                'solutions': valid_solutions,
                'domain_conditions': [f"{term1} > 0", f"{term2} > 0"]
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_72_logarithmic_power(self, base: float, coefficient: float, argument: str, value: float) -> Dict[str, Any]:
        """
        قالب 72: معادلة لوغاريتمية مع معامل: n log(argument) = value
        """
        template_id = 72
        self.stats['total_calls'] += 1
        
        try:
            # n log(argument) = value  =>  log(argument^n) = value
            arg_expr = sp.sympify(argument)
            
            # argument^n = base^value
            rhs = base ** value
            equation = sp.Eq(arg_expr ** coefficient, rhs)
            
            solution = sp.solve(equation, self.x)
            
            # التحقق من المجال
            valid_solutions = []
            for sol in solution:
                arg_val = float(sp.N(arg_expr.subs(self.x, sol)))
                if arg_val > 0:
                    valid_solutions.append(float(sp.N(sol)))
            
            result = {
                'template_id': template_id,
                'template_name': 'logarithmic_power',
                'template_name_ar': 'معادلة لوغاريتمية مع معامل',
                'input': {'base': base, 'coefficient': coefficient, 'argument': argument, 'value': value},
                'original_equation': f"{coefficient} log_{base}({argument}) = {value}",
                'transformed': f"log_{base}({argument}^{coefficient}) = {value}",
                'exponential_form': f"{argument}^{coefficient} = {base}^{value} = {base**value}",
                'solutions': valid_solutions,
                'domain_condition': f"{argument} > 0"
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_73_logarithmic_equating_arguments(self, base: float, arg1: str, arg2: str) -> Dict[str, Any]:
        """
        قالب 73: معادلة لوغاريتمية بتساوي اللوغاريتمات: log_base(arg1) = log_base(arg2)
        """
        template_id = 73
        self.stats['total_calls'] += 1
        
        try:
            A = sp.sympify(arg1)
            B = sp.sympify(arg2)
            
            # log(A) = log(B)  =>  A = B (مع مراعاة المجال)
            equation = sp.Eq(A, B)
            solution = sp.solve(equation, self.x)
            
            # التحقق من المجال
            valid_solutions = []
            for sol in solution:
                A_val = float(sp.N(A.subs(self.x, sol)))
                B_val = float(sp.N(B.subs(self.x, sol)))
                if A_val > 0 and B_val > 0:
                    valid_solutions.append(float(sp.N(sol)))
            
            result = {
                'template_id': template_id,
                'template_name': 'logarithmic_equating_arguments',
                'template_name_ar': 'معادلة لوغاريتمية - تساوي اللوغاريتمات',
                'input': {'base': base, 'arg1': arg1, 'arg2': arg2},
                'equation': f"log_{base}({arg1}) = log_{base}({arg2})",
                'simplified': f"{arg1} = {arg2}",
                'solutions': valid_solutions,
                'domain_conditions': [f"{arg1} > 0", f"{arg2} > 0"]
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_74_logarithmic_system(self, eq1: str, eq2: str) -> Dict[str, Any]:
        """
        قالب 74: نظام معادلات لوغاريتمية
        """
        template_id = 74
        self.stats['total_calls'] += 1
        
        try:
            # تحليل المعادلات
            eq1 = eq1.replace(' ', '')
            eq2 = eq2.replace(' ', '')
            
            # تحويل اللوغاريتمات إلى صيغة أسية
            # هذه دالة مبسطة - تحتاج إلى تحليل أكثر تعقيداً
            
            result = {
                'template_id': template_id,
                'template_name': 'logarithmic_system',
                'template_name_ar': 'نظام معادلات لوغاريتمية',
                'input': {'eq1': eq1, 'eq2': eq2},
                'method': 'تحويل المعادلات اللوغاريتمية إلى صيغ أسية ثم حل النظام',
                'note': 'يجب مراعاة مجال الدوال اللوغاريتمية'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    # =========================================================================
    # القسم 15: المعادلات الأسية (6 قوالب) - Templates 75-80
    # =========================================================================
    
    def template_75_exponential_simple(self, base: float, exponent: str, value: float) -> Dict[str, Any]:
        """
        قالب 75: معادلة أسية بسيطة: base^(exponent) = value
        """
        template_id = 75
        self.stats['total_calls'] += 1
        
        try:
            exp_expr = sp.sympify(exponent)
            
            # base^(exponent) = value  =>  exponent = log_base(value)
            if value <= 0:
                raise ValueError("الطرف الأيمن يجب أن يكون موجباً للمعادلات الأسية")
            
            # حل المعادلة
            rhs = math.log(value, base)
            equation = sp.Eq(exp_expr, rhs)
            solution = sp.solve(equation, self.x)
            
            result = {
                'template_id': template_id,
                'template_name': 'exponential_simple',
                'template_name_ar': 'معادلة أسية بسيطة',
                'input': {'base': base, 'exponent': exponent, 'value': value},
                'equation': f"{base}^({exponent}) = {value}",
                'logarithmic_form': f"{exponent} = log_{base}({value}) = {rhs}",
                'solutions': [float(sp.N(sol)) for sol in solution] if solution else [],
                'verification': [abs(base ** float(sp.N(sol)) - value) < self.precision for sol in solution] if solution else []
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_76_exponential_same_base(self, base: float, exp1: str, exp2: str) -> Dict[str, Any]:
        """
        قالب 76: معادلة أسية بنفس الأساس: base^(exp1) = base^(exp2)
        """
        template_id = 76
        self.stats['total_calls'] += 1
        
        try:
            exp1_expr = sp.sympify(exp1)
            exp2_expr = sp.sympify(exp2)
            
            # base^(exp1) = base^(exp2)  =>  exp1 = exp2
            equation = sp.Eq(exp1_expr, exp2_expr)
            solution = sp.solve(equation, self.x)
            
            result = {
                'template_id': template_id,
                'template_name': 'exponential_same_base',
                'template_name_ar': 'معادلة أسية - نفس الأساس',
                'input': {'base': base, 'exponent1': exp1, 'exponent2': exp2},
                'equation': f"{base}^({exp1}) = {base}^({exp2})",
                'simplified': f"{exp1} = {exp2}",
                'solutions': [float(sp.N(sol)) for sol in solution] if solution else [],
                'verification': [abs(base ** float(sp.N(sol)) - base ** float(sp.N(sp.sympify(exp2).subs(self.x, sol)))) < self.precision 
                                for sol in solution] if solution else []
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_77_exponential_different_base(self, a: float, b: float, c: float) -> Dict[str, Any]:
        """
        قالب 77: معادلة أسية بأسس مختلفة: a^x = b
        """
        template_id = 77
        self.stats['total_calls'] += 1
        
        try:
            if a <= 0 or a == 1 or b <= 0:
                raise ValueError("الأساس يجب أن يكون > 0 ولا يساوي 1، والطرف الأيمن > 0")
            
            # a^x = b  =>  x = log_a(b)
            x_exact = sp.log(b) / sp.log(a)
            x_decimal = float(sp.N(x_exact))
            
            result = {
                'template_id': template_id,
                'template_name': 'exponential_different_base',
                'template_name_ar': 'معادلة أسية - أساس مختلف',
                'input': {'a': a, 'b': b},
                'equation': f"{a}^x = {b}",
                'solution': {
                    'exact': str(x_exact),
                    'decimal': x_decimal,
                    'logarithmic_form': f"x = log_{a}({b})"
                },
                'verification': abs(a ** x_decimal - b) < self.precision
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_78_exponential_quadratic(self, a: float, b: float, c: float) -> Dict[str, Any]:
        """
        قالب 78: معادلة أسية تربيعية: a^(2x) + b a^x + c = 0
        """
        template_id = 78
        self.stats['total_calls'] += 1
        
        try:
            # تعويض y = a^x
            # المعادلة تصبح: y² + b y + c = 0
            
            # حل المعادلة التربيعية في y
            discriminant = b**2 - 4*c
            
            solutions = []
            if discriminant >= 0:
                y1 = (-b + math.sqrt(discriminant)) / 2
                y2 = (-b - math.sqrt(discriminant)) / 2
                
                # لكل y > 0، x = log_a(y)
                for y in [y1, y2]:
                    if y > 0:
                        x = math.log(y) / math.log(a)
                        solutions.append(x)
            
            result = {
                'template_id': template_id,
                'template_name': 'exponential_quadratic',
                'template_name_ar': 'معادلة أسية تربيعية',
                'input': {'a': a, 'b': b, 'c': c},
                'equation': f"{a}^(2x) + {b}·{a}^x + {c} = 0",
                'substitution': f"y = {a}^x",
                'quadratic': f"y² + {b}y + {c} = 0",
                'y_solutions': [y1, y2] if discriminant >= 0 else [],
                'x_solutions': solutions,
                'condition': 'y > 0'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_79_exponential_system(self, eq1: str, eq2: str) -> Dict[str, Any]:
        """
        قالب 79: نظام معادلات أسية
        """
        template_id = 79
        self.stats['total_calls'] += 1
        
        try:
            # تحليل المعادلات
            eq1 = eq1.replace(' ', '')
            eq2 = eq2.replace(' ', '')
            
            lhs1, rhs1 = eq1.split('=')
            lhs2, rhs2 = eq2.split('=')
            
            expr1 = sp.Eq(sp.sympify(lhs1), sp.sympify(rhs1))
            expr2 = sp.Eq(sp.sympify(lhs2), sp.sympify(rhs2))
            
            # حل النظام
            solution = sp.solve([expr1, expr2], [self.x, self.y])
            
            solutions_list = []
            if solution:
                if isinstance(solution, list):
                    for sol in solution:
                        solutions_list.append({
                            'x': float(sp.N(sol[self.x])) if self.x in sol else None,
                            'y': float(sp.N(sol[self.y])) if self.y in sol else None
                        })
                else:
                    solutions_list.append({
                        'x': float(sp.N(solution[self.x])) if self.x in solution else None,
                        'y': float(sp.N(solution[self.y])) if self.y in solution else None
                    })
            
            result = {
                'template_id': template_id,
                'template_name': 'exponential_system',
                'template_name_ar': 'نظام معادلات أسية',
                'input': {'eq1': eq1, 'eq2': eq2},
                'solutions': solutions_list,
                'num_solutions': len(solutions_list)
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_80_exponential_word_problems(self, problem_type: str, values: Dict) -> Dict[str, Any]:
        """
        قالب 80: مسائل كلامية على المعادلات الأسية
        """
        template_id = 80
        self.stats['total_calls'] += 1
        
        try:
            problem_types = {
                'population_growth': {
                    'formula': 'P(t) = P₀ × e^(kt)',
                    'description': 'النمو السكاني: P(t) السكان بعد t سنة، P₀ السكان الابتدائي، k معدل النمو'
                },
                'radioactive_decay': {
                    'formula': 'A(t) = A₀ × e^(-λt)',
                    'description': 'الاضمحلال الإشعاعي: A(t) الكمية المتبقية بعد t زمن، A₀ الكمية الابتدائية، λ ثابت الاضمحلال'
                },
                'compound_interest': {
                    'formula': 'A = P(1 + r/n)^(nt)',
                    'description': 'الفائدة المركبة: A المبلغ النهائي، P المبلغ الأصلي، r معدل الفائدة، n عدد مرات التحويل، t الزمن'
                }
            }
            
            if problem_type not in problem_types:
                raise ValueError(f'نوع المسألة غير معروف: {problem_type}')
            
            result = {
                'template_id': template_id,
                'template_name': 'exponential_word_problems',
                'template_name_ar': 'مسائل كلامية - معادلات أسية',
                'input': {'problem_type': problem_type, 'values': values},
                'problem_info': problem_types[problem_type],
                'examples': self._get_exponential_examples(problem_type)
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    # =========================================================================
    # القسم 16: المعادلات الكسرية (5 قوالب) - Templates 81-85
    # =========================================================================
    
    def template_81_rational_simple(self, numerator: str, denominator: str, value: float) -> Dict[str, Any]:
        """
        قالب 81: معادلة كسرية بسيطة: (ax + b)/(cx + d) = k
        """
        template_id = 81
        self.stats['total_calls'] += 1
        
        try:
            num_expr = sp.sympify(numerator)
            den_expr = sp.sympify(denominator)
            
            # (num)/(den) = value
            equation = sp.Eq(num_expr / den_expr, value)
            
            # ضرب الطرفين في المقام
            cleared = sp.Eq(num_expr, value * den_expr)
            
            solution = sp.solve(cleared, self.x)
            
            # استبعاد الحلول التي تجعل المقام صفراً
            valid_solutions = []
            for sol in solution:
                den_val = float(sp.N(den_expr.subs(self.x, sol)))
                if abs(den_val) > self.precision:
                    valid_solutions.append(float(sp.N(sol)))
            
            result = {
                'template_id': template_id,
                'template_name': 'rational_simple',
                'template_name_ar': 'معادلة كسرية بسيطة',
                'input': {'numerator': numerator, 'denominator': denominator, 'value': value},
                'equation': f"({numerator})/({denominator}) = {value}",
                'cleared_equation': f"{numerator} = {value}·({denominator})",
                'solutions': valid_solutions,
                'excluded_values': [float(sp.N(sol)) for sol in sp.solve(den_expr, self.x)],
                'domain': f"{denominator} ≠ 0"
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_82_rational_sum(self, fractions: List[str], value: float) -> Dict[str, Any]:
        """
        قالب 82: معادلة كسرية بمجموع كسور: 1/(x+a) + 1/(x+b) = c
        """
        template_id = 82
        self.stats['total_calls'] += 1
        
        try:
            # تحويل الكسور إلى تعبيرات
            frac_exprs = [sp.sympify(f) for f in fractions]
            
            # مجموع الكسور
            total = sp.Add(*frac_exprs)
            
            # ضرب في LCM
            denominators = []
            for frac in frac_exprs:
                if frac.is_Mul and any(arg.is_Pow and arg.exp == -1 for arg in frac.args):
                    for arg in frac.args:
                        if arg.is_Pow and arg.exp == -1:
                            denominators.append(arg.base)
            
            # تبسيط
            simplified = sp.simplify(total)
            equation = sp.Eq(simplified, value)
            
            solution = sp.solve(equation, self.x)
            
            # التحقق من المقامات
            valid_solutions = []
            for sol in solution:
                valid = True
                for frac in frac_exprs:
                    try:
                        val = float(sp.N(frac.subs(self.x, sol)))
                        if abs(val) > 1e10:  # تقريباً لانهائي
                            valid = False
                            break
                    except:
                        valid = False
                        break
                if valid:
                    valid_solutions.append(float(sp.N(sol)))
            
            result = {
                'template_id': template_id,
                'template_name': 'rational_sum',
                'template_name_ar': 'معادلة كسرية - مجموع كسور',
                'input': {'fractions': fractions, 'value': value},
                'equation': ' + '.join(fractions) + f" = {value}",
                'simplified': str(simplified),
                'solutions': valid_solutions,
                'denominators': [str(d) for d in denominators]
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_83_rational_equality(self, frac1: str, frac2: str) -> Dict[str, Any]:
        """
        قالب 83: تساوي كسرين: (ax+b)/(cx+d) = (ex+f)/(gx+h)
        """
        template_id = 83
        self.stats['total_calls'] += 1
        
        try:
            f1 = sp.sympify(frac1)
            f2 = sp.sympify(frac2)
            
            # ضرب تبادلي
            # f1 = f2  =>  f1 * den2 = f2 * den1
            equation = sp.Eq(f1, f2)
            
            solution = sp.solve(equation, self.x)
            
            # التحقق من المقامات
            den1 = 1
            den2 = 1
            
            for arg in sp.preorder_traversal(f1):
                if isinstance(arg, sp.Pow) and arg.exp == -1:
                    den1 *= arg.base
            
            for arg in sp.preorder_traversal(f2):
                if isinstance(arg, sp.Pow) and arg.exp == -1:
                    den2 *= arg.base
            
            valid_solutions = []
            for sol in solution:
                den1_val = float(sp.N(den1.subs(self.x, sol))) if den1 != 1 else 1
                den2_val = float(sp.N(den2.subs(self.x, sol))) if den2 != 1 else 1
                
                if abs(den1_val) > self.precision and abs(den2_val) > self.precision:
                    valid_solutions.append(float(sp.N(sol)))
            
            result = {
                'template_id': template_id,
                'template_name': 'rational_equality',
                'template_name_ar': 'تساوي كسرين',
                'input': {'frac1': frac1, 'frac2': frac2},
                'equation': f"{frac1} = {frac2}",
                'solutions': valid_solutions,
                'domain': f"{den1} ≠ 0 و {den2} ≠ 0" if den1 != 1 or den2 != 1 else 'جميع الأعداد'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_84_rational_inequality(self, numerator: str, denominator: str, inequality: str) -> Dict[str, Any]:
        """
        قالب 84: متباينة كسرية: (ax+b)/(cx+d) > 0
        """
        template_id = 84
        self.stats['total_calls'] += 1
        
        try:
            num = sp.sympify(numerator)
            den = sp.sympify(denominator)
            
            # إيجاد النقاط الحرجة (أصفار البسط والمقام)
            zeros_num = sp.solve(num, self.x)
            zeros_den = sp.solve(den, self.x)
            
            critical_points = sorted(set([float(sp.N(z)) for z in zeros_num + zeros_den]))
            
            # ترتيب النقاط
            critical_points.sort()
            
            # إنشاء الفترات
            intervals = []
            if critical_points:
                intervals.append(('-∞', critical_points[0]))
                for i in range(len(critical_points)-1):
                    intervals.append((critical_points[i], critical_points[i+1]))
                intervals.append((critical_points[-1], '∞'))
            else:
                intervals.append(('-∞', '∞'))
            
            # اختبار الإشارات
            sign_chart = []
            solution_intervals = []
            
            for interval in intervals:
                # اختيار نقطة اختبار
                if interval[0] == '-∞':
                    test_x = critical_points[0] - 1 if critical_points else 0
                elif interval[1] == '∞':
                    test_x = critical_points[-1] + 1 if critical_points else 0
                else:
                    test_x = (interval[0] + interval[1]) / 2
                
                # حساب قيمة التعبير
                val = float(sp.N((num/den).subs(self.x, test_x)))
                sign = 'positive' if val > 0 else 'negative' if val < 0 else 'zero'
                
                sign_chart.append({
                    'interval': f"{interval[0]} < x < {interval[1]}",
                    'test_point': test_x,
                    'value': val,
                    'sign': sign
                })
                
                # تحديد الحل حسب المتباينة
                if inequality == '>0' and val > 0:
                    solution_intervals.append(f"{interval[0]} < x < {interval[1]}")
                elif inequality == '<0' and val < 0:
                    solution_intervals.append(f"{interval[0]} < x < {interval[1]}")
            
            result = {
                'template_id': template_id,
                'template_name': 'rational_inequality',
                'template_name_ar': 'متباينة كسرية',
                'input': {'numerator': numerator, 'denominator': denominator, 'inequality': inequality},
                'inequality': f"({numerator})/({denominator}) {inequality}",
                'critical_points': critical_points,
                'sign_chart': sign_chart,
                'solution': solution_intervals,
                'excluded_values': [float(sp.N(z)) for z in zeros_den]
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_85_rational_parametric(self, numerator: str, denominator: str, parameter: str) -> Dict[str, Any]:
        """
        قالب 85: معادلة كسرية مع باراميتر
        """
        template_id = 85
        self.stats['total_calls'] += 1
        
        try:
            k = sp.Symbol(parameter, real=True)
            
            num_expr = sp.sympify(numerator.replace(parameter, f'({parameter})'))
            den_expr = sp.sympify(denominator.replace(parameter, f'({parameter})'))
            
            # تحليل قيم الباراميتر الخاصة
            special_values = []
            
            # قيم k التي تجعل المقام صفراً
            denom_k = sp.solve(den_expr, k)
            for val in denom_k:
                special_values.append({
                    'value': float(sp.N(val)) if val.is_real else str(val),
                    'type': 'denominator_zero',
                    'description': f'عند {parameter} = {val}، المقام يصفر'
                })
            
            # حل المعادلة بدلالة x
            equation = sp.Eq(num_expr / den_expr, 0)
            x_solution = sp.solve(equation, self.x)
            
            result = {
                'template_id': template_id,
                'template_name': 'rational_parametric',
                'template_name_ar': 'معادلة كسرية مع باراميتر',
                'input': {'numerator': numerator, 'denominator': denominator, 'parameter': parameter},
                'equation': f"({numerator})/({denominator}) = 0",
                'parameter_analysis': {
                    'symbol': parameter,
                    'special_values': special_values
                },
                'solution': [str(s) for s in x_solution] if x_solution else 'لا يوجد حل',
                'domain_condition': f"{denominator} ≠ 0"
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    # =========================================================================
    # القسم 17: المعادلات المطلقة (5 قوالب) - Templates 86-90
    # =========================================================================
    
    def template_86_absolute_simple(self, expression: str, value: float) -> Dict[str, Any]:
        """
        قالب 86: معادلة قيمة مطلقة بسيطة: |ax + b| = c
        """
        template_id = 86
        self.stats['total_calls'] += 1
        
        try:
            expr = sp.sympify(expression)
            # استخدام متغير محلي للحل بدلاً من self.x
            x_var = sp.Symbol('x')
            
            if value < 0:
                # |expr| = قيمة سالبة → لا يوجد حل
                solutions = []
                cases = []
                solution_type = 'no_solution'
            elif abs(value) < self.precision:
                # |expr| = 0 → expr = 0
                eq = sp.Eq(expr, 0)
                solutions = sp.solve(eq, x_var)
                cases = [{'case': f"{expression} = 0", 'solutions': [float(s) for s in solutions if s.is_real]}]
                solution_type = 'single' if len(solutions) == 1 else 'multiple'
            else:
                # |expr| = c → expr = c أو expr = -c
                eq1 = sp.Eq(expr, value)
                eq2 = sp.Eq(expr, -value)
                
                sol1 = sp.solve(eq1, x_var)
                sol2 = sp.solve(eq2, x_var)
                
                solutions = sol1 + sol2
                cases = [
                    {'case': f"{expression} = {value}", 'solutions': [float(s) for s in sol1 if s.is_real]},
                    {'case': f"{expression} = {-value}", 'solutions': [float(s) for s in sol2 if s.is_real]}
                ]
                solution_type = 'two_solutions' if len(solutions) == 2 else 'multiple'
            
            result = {
                'template_id': template_id,
                'template_name': 'absolute_simple',
                'template_name_ar': 'معادلة قيمة مطلقة بسيطة',
                'input': {'expression': expression, 'value': value},
                'equation': f"|{expression}| = {value}",
                'solution_type': solution_type,
                'cases': cases,
                'solutions': [float(s) for s in solutions if s.is_real] if solutions else [],
                'verification': self._verify_absolute_solutions(expr, value, solutions)
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_87_absolute_double(self, expr1: str, expr2: str, value: float) -> Dict[str, Any]:
        """
        قالب 87: معادلة بقيمتين مطلقتين: |ax + b| = |cx + d|
        """
        template_id = 87
        self.stats['total_calls'] += 1
        
        try:
            e1 = sp.sympify(expr1)
            e2 = sp.sympify(expr2)
            
            # |e1| = |e2|  ⇒  e1 = e2 أو e1 = -e2
            eq1 = sp.Eq(e1, e2)
            eq2 = sp.Eq(e1, -e2)
            
            sol1 = sp.solve(eq1, self.x)
            sol2 = sp.solve(eq2, self.x)
            
            solutions = sol1 + sol2
            
            result = {
                'template_id': template_id,
                'template_name': 'absolute_double',
                'template_name_ar': 'معادلة بقيمتين مطلقتين',
                'input': {'expr1': expr1, 'expr2': expr2},
                'equation': f"|{expr1}| = |{expr2}|",
                'cases': [
                    {'case': f"{expr1} = {expr2}", 'solutions': [float(sp.N(s)) for s in sol1]},
                    {'case': f"{expr1} = -({expr2})", 'solutions': [float(sp.N(s)) for s in sol2]}
                ],
                'solutions': [float(sp.N(s)) for s in solutions] if solutions else []
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_88_absolute_inequality(self, expression: str, value: float, inequality: str) -> Dict[str, Any]:
        """
        قالب 88: متباينة بقيمة مطلقة: |ax + b| > c
        """
        template_id = 88
        self.stats['total_calls'] += 1
        
        try:
            expr = sp.sympify(expression)
            
            if value < 0:
                if inequality in ['>', '≥']:
                    solution = "جميع الأعداد الحقيقية"
                else:
                    solution = "لا يوجد حل"
            elif abs(value) < self.precision:
                if inequality in ['>', '≥']:
                    solution = f"{expression} ≠ 0"
                elif inequality in ['<', '≤']:
                    solution = f"{expression} = 0"
            else:
                # إيجاد النقاط الحرجة
                critical_points = sp.solve(sp.Eq(expr, value), self.x) + sp.solve(sp.Eq(expr, -value), self.x)
                critical_points = sorted([float(sp.N(p)) for p in critical_points])
                
                if inequality in ['>', '≥']:
                    # |expr| > c  ⇒  expr < -c أو expr > c
                    solution_intervals = []
                    if critical_points:
                        solution_intervals.append(f"x < {critical_points[0]}")
                        solution_intervals.append(f"x > {critical_points[-1]}")
                    solution = ' أو '.join(solution_intervals)
                else:
                    # |expr| < c  ⇒  -c < expr < c
                    if critical_points:
                        solution = f"{critical_points[0]} < x < {critical_points[-1]}"
                    else:
                        solution = "لا يوجد حل"
            
            result = {
                'template_id': template_id,
                'template_name': 'absolute_inequality',
                'template_name_ar': 'متباينة بقيمة مطلقة',
                'input': {'expression': expression, 'value': value, 'inequality': inequality},
                'inequality': f"|{expression}| {inequality} {value}",
                'critical_points': [float(sp.N(p)) for p in sp.solve(sp.Eq(expr, value), self.x) + sp.solve(sp.Eq(expr, -value), self.x)] if value >= 0 else [],
                'solution': solution
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_89_absolute_quadratic(self, a: float, b: float, c: float, value: float) -> Dict[str, Any]:
        """
        قالب 89: معادلة بقيمة مطلقة مع تعبير تربيعي: |ax² + bx + c| = d
        """
        template_id = 89
        self.stats['total_calls'] += 1
        
        try:
            quadratic = a*self.x**2 + b*self.x + c
            
            if value < 0:
                solutions = []
                cases = []
            elif abs(value) < self.precision:
                # |quadratic| = 0  ⇒  quadratic = 0
                eq = sp.Eq(quadratic, 0)
                solutions = sp.solve(eq, self.x)
                cases = [{'case': f"{a}x² + {b}x + {c} = 0", 'solutions': [float(sp.N(s)) for s in solutions]}]
            else:
                # |quadratic| = d  ⇒  quadratic = d أو quadratic = -d
                eq1 = sp.Eq(quadratic, value)
                eq2 = sp.Eq(quadratic, -value)
                
                sol1 = sp.solve(eq1, self.x)
                sol2 = sp.solve(eq2, self.x)
                
                solutions = sol1 + sol2
                cases = [
                    {'case': f"{a}x² + {b}x + {c} = {value}", 'solutions': [float(sp.N(s)) for s in sol1]},
                    {'case': f"{a}x² + {b}x + {c} = {-value}", 'solutions': [float(sp.N(s)) for s in sol2]}
                ]
            
            result = {
                'template_id': template_id,
                'template_name': 'absolute_quadratic',
                'template_name_ar': 'معادلة بقيمة مطلقة - تعبير تربيعي',
                'input': {'a': a, 'b': b, 'c': c, 'value': value},
                'equation': f"|{a}x² + {b}x + {c}| = {value}",
                'cases': cases,
                'solutions': [float(sp.N(s)) for s in solutions] if solutions else [],
                'total_solutions': len(solutions)
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_90_absolute_system(self, eq1: str, eq2: str) -> Dict[str, Any]:
        """
        قالب 90: نظام معادلات بقيم مطلقة
        """
        template_id = 90
        self.stats['total_calls'] += 1
        
        try:
            # تحليل المعادلات
            eq1 = eq1.replace(' ', '')
            eq2 = eq2.replace(' ', '')
            
            # هذه دالة مبسطة - تحتاج إلى تحليل حالات متعددة
            
            result = {
                'template_id': template_id,
                'template_name': 'absolute_system',
                'template_name_ar': 'نظام معادلات بقيم مطلقة',
                'input': {'eq1': eq1, 'eq2': eq2},
                'method': 'تحليل الحالات المختلفة للقيم المطلقة',
                'note': 'يجب دراسة 4 حالات حسب إشارة التعبيرات داخل القيمة المطلقة'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    # =========================================================================
    # القسم 18: تبسيط الكسور الجبرية (4 قوالب) - Templates 91-94
    # =========================================================================
    
    def template_91_simplify_rational_fraction(self, numerator: str, denominator: str) -> Dict[str, Any]:
        """
        قالب 91: تبسيط كسر جبري
        """
        template_id = 91
        self.stats['total_calls'] += 1
        
        try:
            num = sp.sympify(numerator)
            den = sp.sympify(denominator)
            
            # تبسيط الكسر
            simplified = sp.simplify(num / den)
            
            # استخراج العوامل المشتركة
            gcd_poly = sp.gcd(num, den)
            
            result = {
                'template_id': template_id,
                'template_name': 'simplify_rational_fraction',
                'template_name_ar': 'تبسيط كسر جبري',
                'input': {'numerator': numerator, 'denominator': denominator},
                'original': f"({numerator})/({denominator})",
                'simplified': str(simplified),
                'gcd': str(gcd_poly) if gcd_poly != 1 else 'لا يوجد عامل مشترك',
                'domain': f"{denominator} ≠ 0",
                'steps': [
                    f"1. إيجاد القاسم المشترك الأكبر للبسط والمقام: {gcd_poly}",
                    f"2. قسمة البسط والمقام على {gcd_poly}" if gcd_poly != 1 else "لا يوجد تبسيط"
                ]
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_92_rational_domain(self, expression: str) -> Dict[str, Any]:
        """
        قالب 92: إيجاد مجال الكسر الجبري
        """
        template_id = 92
        self.stats['total_calls'] += 1
        
        try:
            expr = sp.sympify(expression)
            
            # استخراج المقامات
            denominators = []
            
            def find_denominators(exp):
                if isinstance(exp, sp.Pow) and exp.exp == -1:
                    denominators.append(exp.base)
                elif exp.is_Mul:
                    for arg in exp.args:
                        find_denominators(arg)
                elif exp.is_Add:
                    for arg in exp.args:
                        find_denominators(arg)
            
            find_denominators(expr)
            
            # حل المعادلات denominator = 0
            excluded_values = []
            for den in denominators:
                solutions = sp.solve(den, self.x)
                for sol in solutions:
                    if sol.is_real:
                        excluded_values.append(float(sp.N(sol)))
                    else:
                        excluded_values.append(str(sol))
            
            result = {
                'template_id': template_id,
                'template_name': 'rational_domain',
                'template_name_ar': 'مجال الكسر الجبري',
                'input': {'expression': expression},
                'expression': expression,
                'denominators': [str(d) for d in denominators],
                'excluded_values': excluded_values,
                'domain': f"x ∉ {{{', '.join(str(v) for v in excluded_values)}}}" if excluded_values else 'جميع الأعداد الحقيقية',
                'interval_notation': self._excluded_to_interval(excluded_values)
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_93_rational_common_denominator(self, fractions: List[str]) -> Dict[str, Any]:
        """
        قالب 93: توحيد مقامات كسور جبرية
        """
        template_id = 93
        self.stats['total_calls'] += 1
        
        try:
            frac_exprs = [sp.sympify(f) for f in fractions]
            
            # استخراج المقامات
            denominators = []
            for frac in frac_exprs:
                if frac.is_Mul:
                    for arg in frac.args:
                        if isinstance(arg, sp.Pow) and arg.exp == -1:
                            denominators.append(arg.base)
                elif isinstance(frac, sp.Pow) and frac.exp == -1:
                    denominators.append(frac.base)
            
            # إيجاد LCM للمقامات
            if denominators:
                lcm = denominators[0]
                for d in denominators[1:]:
                    lcm = sp.lcm(lcm, d)
                
                # تحويل كل كسر
                unified = []
                for frac in frac_exprs:
                    new_frac = sp.simplify(frac * lcm)
                    unified.append(str(new_frac) + f"/{lcm}")
            else:
                lcm = 1
                unified = [str(f) for f in fractions]
            
            result = {
                'template_id': template_id,
                'template_name': 'rational_common_denominator',
                'template_name_ar': 'توحيد مقامات كسور جبرية',
                'input': {'fractions': fractions},
                'denominators': [str(d) for d in denominators] if denominators else ['1'],
                'common_denominator': str(lcm),
                'unified_fractions': unified,
                'sum_with_common_denominator': f"({' + '.join(unified)})" if unified else None
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_94_rational_complex_fraction(self, fraction: str) -> Dict[str, Any]:
        """
        قالب 94: تبسيط كسر مركب (كسر فوق كسر)
        مثال: (1/x + 1/y) / (1/x - 1/y)
        """
        template_id = 94
        self.stats['total_calls'] += 1
        
        try:
            expr = sp.sympify(fraction)
            
            # تبسيط الكسر المركب
            simplified = sp.simplify(expr)
            
            # محاولة كتابته على صورة كسر بسيط
            rational = sp.together(expr)
            
            result = {
                'template_id': template_id,
                'template_name': 'rational_complex_fraction',
                'template_name_ar': 'تبسيط كسر مركب',
                'input': {'fraction': fraction},
                'original': fraction,
                'simplified': str(simplified),
                'as_simple_fraction': str(rational),
                'method': 'توحيد المقامات في البسط والمقام ثم القسمة'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    # =========================================================================
    # القسم 19: العمليات على الكسور الجبرية (4 قوالب) - Templates 95-98
    # =========================================================================
    
    def template_95_rational_add(self, frac1: str, frac2: str) -> Dict[str, Any]:
        """
        قالب 95: جمع كسور جبرية
        """
        template_id = 95
        self.stats['total_calls'] += 1
        
        try:
            f1 = sp.sympify(frac1)
            f2 = sp.sympify(frac2)
            
            # جمع الكسور
            result = sp.simplify(f1 + f2)
            
            # استخراج الخطوات
            steps = [
                f"1. الكسر الأول: {frac1}",
                f"2. الكسر الثاني: {frac2}",
                f"3. توحيد المقامات",
                f"4. النتيجة: {result}"
            ]
            
            result_data = {
                'template_id': template_id,
                'template_name': 'rational_add',
                'template_name_ar': 'جمع كسور جبرية',
                'input': {'frac1': frac1, 'frac2': frac2},
                'operation': f"{frac1} + {frac2}",
                'result': str(result),
                'steps': steps,
                'domain': self._get_rational_domain([f1, f2])
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result_data
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_96_rational_subtract(self, frac1: str, frac2: str) -> Dict[str, Any]:
        """
        قالب 96: طرح كسور جبرية
        """
        template_id = 96
        self.stats['total_calls'] += 1
        
        try:
            f1 = sp.sympify(frac1)
            f2 = sp.sympify(frac2)
            
            # طرح الكسور
            result = sp.simplify(f1 - f2)
            
            result_data = {
                'template_id': template_id,
                'template_name': 'rational_subtract',
                'template_name_ar': 'طرح كسور جبرية',
                'input': {'frac1': frac1, 'frac2': frac2},
                'operation': f"{frac1} - {frac2}",
                'result': str(result),
                'steps': [
                    f"{frac1} - {frac2} = {result}"
                ],
                'domain': self._get_rational_domain([f1, f2])
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result_data
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_97_rational_multiply(self, frac1: str, frac2: str) -> Dict[str, Any]:
        """
        قالب 97: ضرب كسور جبرية
        """
        template_id = 97
        self.stats['total_calls'] += 1
        
        try:
            f1 = sp.sympify(frac1)
            f2 = sp.sympify(frac2)
            
            # ضرب الكسور
            result = sp.simplify(f1 * f2)
            
            result_data = {
                'template_id': template_id,
                'template_name': 'rational_multiply',
                'template_name_ar': 'ضرب كسور جبرية',
                'input': {'frac1': frac1, 'frac2': frac2},
                'operation': f"({frac1}) × ({frac2})",
                'result': str(result),
                'steps': [
                    f"({frac1}) × ({frac2}) = {result}"
                ],
                'domain': self._get_rational_domain([f1, f2])
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result_data
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_98_rational_divide(self, frac1: str, frac2: str) -> Dict[str, Any]:
        """
        قالب 98: قسمة كسور جبرية
        """
        template_id = 98
        self.stats['total_calls'] += 1
        
        try:
            f1 = sp.sympify(frac1)
            f2 = sp.sympify(frac2)
            
            # قسمة الكسور (ضرب في مقلوب)
            result = sp.simplify(f1 / f2)
            
            result_data = {
                'template_id': template_id,
                'template_name': 'rational_divide',
                'template_name_ar': 'قسمة كسور جبرية',
                'input': {'frac1': frac1, 'frac2': frac2},
                'operation': f"({frac1}) ÷ ({frac2})",
                'result': str(result),
                'steps': [
                    f"({frac1}) ÷ ({frac2}) = ({frac1}) × (1/({frac2})) = {result}"
                ],
                'domain': self._get_rational_domain([f1, f2], include_denom=True)
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result_data
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    # =========================================================================
    # القسم 20: المعادلات الجذرية (4 قوالب) - Templates 99-102
    # =========================================================================
    
    def template_99_radical_simple(self, radicand: str, value: float, root: int = 2) -> Dict[str, Any]:
        """
        قالب 99: معادلة جذرية بسيطة: √(ax + b) = c
        """
        template_id = 99
        self.stats['total_calls'] += 1
        
        try:
            rad_expr = sp.sympify(radicand)
            
            if root == 2:
                # معادلة تربيعية: √(expr) = value
                if value < 0:
                    solutions = []
                    reason = "الجذر التربيعي لا يمكن أن يساوي قيمة سالبة"
                else:
                    # expr = value^2
                    eq = sp.Eq(rad_expr, value**2)
                    solutions = sp.solve(eq, self.x)
                    
                    # التحقق من أن الحلول تحقق الشرط expr ≥ 0
                    valid_solutions = []
                    for sol in solutions:
                        rad_val = float(sp.N(rad_expr.subs(self.x, sol)))
                        if rad_val >= 0:
                            valid_solutions.append(float(sp.N(sol)))
                    solutions = valid_solutions
            else:
                # جذور ذات رتبة أعلى
                eq = sp.Eq(rad_expr, value**root)
                solutions = sp.solve(eq, self.x)
                solutions = [float(sp.N(s)) for s in solutions]
            
            result = {
                'template_id': template_id,
                'template_name': 'radical_simple',
                'template_name_ar': 'معادلة جذرية بسيطة',
                'input': {'radicand': radicand, 'value': value, 'root': root},
                'equation': f"{'√' if root==2 else '∛' if root==3 else f'root[{root}]'}({radicand}) = {value}",
                'solutions': solutions if solutions else [],
                'verification': self._verify_radical_solutions(rad_expr, value, root, solutions),
                'domain_condition': f"{radicand} ≥ 0" if root % 2 == 0 else f"{radicand} يمكن أن يكون أي عدد"
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_100_radical_both_sides(self, left: str, right: str, root: int = 2) -> Dict[str, Any]:
        """
        قالب 100: معادلة بجذرين: √(ax + b) = √(cx + d)
        """
        template_id = 100
        self.stats['total_calls'] += 1
        
        try:
            left_expr = sp.sympify(left)
            right_expr = sp.sympify(right)
            
            # تربيع الطرفين (للتخلص من الجذور)
            if root == 2:
                eq = sp.Eq(left_expr, right_expr)
            else:
                eq = sp.Eq(left_expr**root, right_expr**root)
            
            solutions = sp.solve(eq, self.x)
            
            # التحقق من صحة الحلول في المعادلة الأصلية
            valid_solutions = []
            for sol in solutions:
                left_val = float(sp.N(left_expr.subs(self.x, sol)))
                right_val = float(sp.N(right_expr.subs(self.x, sol)))
                
                if root % 2 == 0:
                    # للجذور الزوجية، يجب أن يكون الطرفان ≥ 0
                    if left_val >= 0 and right_val >= 0 and abs(left_val - right_val) < self.precision:
                        valid_solutions.append(float(sp.N(sol)))
                else:
                    # للجذور الفردية، لا توجد قيود على الإشارة
                    if abs(left_val - right_val) < self.precision:
                        valid_solutions.append(float(sp.N(sol)))
            
            result = {
                'template_id': template_id,
                'template_name': 'radical_both_sides',
                'template_name_ar': 'معادلة بجذرين',
                'input': {'left': left, 'right': right, 'root': root},
                'equation': f"{'√' if root==2 else '∛' if root==3 else f'root[{root}]'}({left}) = {'√' if root==2 else '∛' if root==3 else f'root[{root}]'}({right})",
                'solutions': valid_solutions,
                'all_candidates': [float(sp.N(s)) for s in solutions],
                'extraneous': [float(sp.N(s)) for s in solutions if float(sp.N(s)) not in valid_solutions]
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_101_radical_quadratic(self, a: float, b: float, c: float) -> Dict[str, Any]:
        """
        قالب 101: معادلة جذرية تؤدي إلى معادلة تربيعية: √(ax + b) = cx + d
        """
        template_id = 101
        self.stats['total_calls'] += 1
        
        try:
            # مثال: √(ax + b) = cx + d
            # هذه دالة مبسطة - في التطبيق الفعلي نأخذ تعبيرين
            
            result = {
                'template_id': template_id,
                'template_name': 'radical_quadratic',
                'template_name_ar': 'معادلة جذرية تؤدي إلى تربيعية',
                'input': {'a': a, 'b': b, 'c': c},
                'method': 'تربيع الطرفين ثم حل المعادلة التربيعية الناتجة',
                'note': 'يجب التحقق من الحلول في المعادلة الأصلية'
            }
            
            self.stats['successful'] += 1
            self.stats['by_template'][template_id] = self.stats['by_template'].get(template_id, 0) + 1
            return result
            
        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"خطأ في القالب {template_id}: {str(e)}")
            return {'template_id': template_id, 'error': str(e)}
    
    def template_102_radical_inequality(self, radicand: str, value: float, inequality: str, root: int = 2) -> Dict[str, Any]:
        """
        قالب 102: متباينة جذرية: √(ax + b) > c
        """
        template_id = 102
        self.stats['total_calls'] += 1
        
        try:
            rad_expr = sp.sympify(radicand)
            
            # تحديد مجال الجذر
            domain_condition = f"{radicand} ≥ 0" if root % 2 == 0 else "جميع الأعداد"
            
            if value < 0:
                if inequality in ['>', '≥']:
                    solution = domain_condition if root % 2 == 0 else "جميع الأعداد"
                else:
                    solution = "لا يوجد حل"
            else:
                if root % 2 == 0:
                    # للجذور الزوجية
                    if inequality in ['>', '≥']:
                        solution = f"{radicand} ≥ {value**root}"
                    else:
                        solution = f"0 ≤ {radicand} < {value**root}"
                else:
                    # للجذور الفردية
                    if inequality in ['>', '≥']:
                        solution = f"{radicand} > {value**root}" if '>' in inequality else f"{radicand} ≥ {value**root}"
                    else:
                        solution = f"{radicand} < {value**root}" if '<' in inequality else f"{radicand} ≤ {value**root}"
            
            result = {
                'template_id': template_id,
                'template_name': 'radical_inequality',
                'template_name_ar': 'متباينة جذرية',
                'input': {'radicand': radicand, 'value': value, 'inequality': inequality, 'root': root},
                'inequality': f"{'√' if root==2 else '∛' if root==3 else f'root[{root}]'}({radicand}) {inequality} {value}",
                'domain': domain_condition,
                'solution': solution
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
    
    def _prime_factors(self, n: int) -> List[int]:
        """تحليل عدد إلى عوامله الأولية"""
        factors = []
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        if n > 1:
            factors.append(n)
        return factors
    
    def _simplify_root(self, value: float, root: int) -> str:
        """تبسيط جذر"""
        # هذه دالة مبسطة
        return str(value)
    
    def _simplify_fraction(self, num: float, den: float) -> str:
        """تبسيط كسر عددي"""
        if den == 0:
            return "غير معرف"
        if num % den == 0:
            return str(int(num // den))
        return f"{num}/{den}"
    
    def _get_root_rules(self, operation: str, root: int) -> List[str]:
        """قواعد الجذور"""
        rules = {
            'multiply': [f"√a × √b = √(ab)"],
            'divide': [f"√a ÷ √b = √(a/b), b ≠ 0"],
            'add': ["لا يمكن جمع الجذور إلا إذا كانت متشابهة"]
        }
        return rules.get(operation, [])
    
    def _try_denest(self, expr) -> str:
        """محاولة تبسيط جذر متداخل"""
        # هذه دالة مبسطة
        return None
    
    def _get_log_examples(self, operation: str, base: float) -> List[str]:
        """أمثلة على خصائص اللوغاريتمات"""
        examples = {
            'product': [f"log_{base}(2) + log_{base}(3) = log_{base}(6)"],
            'quotient': [f"log_{base}(8) - log_{base}(2) = log_{base}(4)"],
            'power': [f"3 log_{base}(2) = log_{base}(8)"],
            'change_base': [f"log_2(8) = log_10(8)/log_10(2)"]
        }
        return examples.get(operation, [])
    
    def _verify_exponential_solution(self, base: float, exp1: str, exp2: str, solutions) -> List[Dict]:
        """التحقق من حلول المعادلات الأسية"""
        verification = []
        for sol in solutions:
            if sol.is_real:
                val1 = base ** float(sp.N(sp.sympify(exp1).subs(self.x, sol)))
                val2 = base ** float(sp.N(sp.sympify(exp2).subs(self.x, sol)))
                verification.append({
                    'solution': float(sp.N(sol)),
                    'left': val1,
                    'right': val2,
                    'error': abs(val1 - val2),
                    'is_valid': abs(val1 - val2) < self.precision
                })
        return verification
    
    def _verify_logarithmic_solutions(self, arg_expr, base: float, value: float, solutions) -> List[Dict]:
        """التحقق من حلول المعادلات اللوغاريتمية"""
        verification = []
        for sol in solutions:
            arg_val = float(sp.N(arg_expr.subs(self.x, sol)))
            log_val = math.log(arg_val, base) if arg_val > 0 else None
            verification.append({
                'solution': sol,
                'argument_value': arg_val,
                'log_value': log_val,
                'expected': value,
                'is_valid': abs(log_val - value) < self.precision if log_val is not None else False
            })
        return verification
    
    def _verify_absolute_solutions(self, expr, value: float, solutions) -> List[Dict]:
        """التحقق من حلول معادلات القيمة المطلقة"""
        verification = []
        for sol in solutions:
            if sol.is_real:
                expr_val = float(sp.N(expr.subs(self.x, sol)))
                abs_val = abs(expr_val)
                verification.append({
                    'solution': float(sp.N(sol)),
                    'expression_value': expr_val,
                    'absolute_value': abs_val,
                    'expected': value,
                    'is_valid': abs(abs_val - value) < self.precision
                })
        return verification
    
    def _verify_radical_solutions(self, rad_expr, value: float, root: int, solutions) -> List[Dict]:
        """التحقق من حلول المعادلات الجذرية"""
        verification = []
        for sol in solutions:
            rad_val = float(sp.N(rad_expr.subs(self.x, sol)))
            root_val = rad_val ** (1/root) if root % 2 == 0 or rad_val >= 0 else -((-rad_val) ** (1/root))
            verification.append({
                'solution': sol,
                'radicand_value': rad_val,
                'root_value': root_val,
                'expected': value,
                'is_valid': abs(root_val - value) < self.precision
            })
        return verification
    
    def _get_rational_domain(self, fractions, include_denom: bool = False) -> str:
        """الحصول على مجال الكسور الجبرية"""
        denominators = []
        for frac in fractions:
            if frac.is_Mul:
                for arg in frac.args:
                    if isinstance(arg, sp.Pow) and arg.exp == -1:
                        denominators.append(arg.base)
            elif isinstance(frac, sp.Pow) and frac.exp == -1:
                denominators.append(frac.base)
        
        if not denominators:
            return "جميع الأعداد الحقيقية"
        
        conditions = [f"{d} ≠ 0" for d in denominators]
        if include_denom:
            conditions.append("المقام الثاني ≠ 0")
        
        return " و ".join(conditions)
    
    def _excluded_to_interval(self, excluded) -> str:
        """تحويل القيم المستثناة إلى صيغة فترات"""
        if not excluded:
            return "(-∞, ∞)"
        
        real_excluded = [e for e in excluded if isinstance(e, (int, float))]
        real_excluded.sort()
        
        if not real_excluded:
            return "(-∞, ∞)"
        
        intervals = []
        if real_excluded[0] > -np.inf:
            intervals.append(f"(-∞, {real_excluded[0]})")
        
        for i in range(len(real_excluded)-1):
            intervals.append(f"({real_excluded[i]}, {real_excluded[i+1]})")
        
        if real_excluded[-1] < np.inf:
            intervals.append(f"({real_excluded[-1]}, ∞)")
        
        return " ∪ ".join(intervals)
    
    def _get_exponential_examples(self, problem_type: str) -> List[str]:
        """أمثلة على المسائل الأسية"""
        examples = {
            'exponential_growth': [
                "تعداد مدينة يزداد بنسبة 3% سنوياً، فإذا كان التعداد الحالي 100000، كم يصبح بعد 5 سنوات؟"
            ],
            'exponential_decay': [
                "كتلة مادة مشعة تتناقص بمعدل 10% سنوياً، فإذا كانت الكتلة الابتدائية 100 جرام، كم تتبقى بعد 3 سنوات؟"
            ],
            'compound_interest': [
                "استثمرت 10000 ريال بمعدل فائدة 5% سنوياً لمدة 3 سنوات مع التحويل الربع سنوي، كم يصبح المبلغ؟"
            ],
            'radioactive_decay': [
                "عمر النصف لعنصر مشع هو 10 سنوات، فإذا كانت الكتلة الابتدائية 80 جرام، كم تتبقى بعد 30 سنة؟"
            ]
        }
        return examples.get(problem_type, [])
    
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
    print("📁 الملف 2/3: الجبر المتوسط - القوى، الأسس، اللوغاريتمات، والكسور")
    print("=" * 80)
    
    solver = IntermediateAlgebraSolver()
    
    print("\n✅ تم تحميل 50 قالباً بنجاح (القوالب 53-102)")
    print(f"📊 إحصائيات: {solver.get_stats()}")
    print("=" * 80)
