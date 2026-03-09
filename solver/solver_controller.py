# solver/solver_controller.py - يحتوي على كل منطق التحكم
import re
import math
import logging
from typing import Optional, Dict, Any, Tuple
from calculator import Calculator
from math_engine.algebra.algebra_part1 import CompleteAlgebraSolver
from math_engine.algebra.algebra_part2 import IntermediateAlgebraSolver
from math_engine.algebra.algebra_part3 import AdvancedAlgebraSolver

logger = logging.getLogger(__name__)

# تهيئة الكائنات
calc = Calculator()
solver1 = CompleteAlgebraSolver()
solver2 = IntermediateAlgebraSolver()
solver3 = AdvancedAlgebraSolver()

# ===== دوال مساعدة =====
def format_number(num: float) -> str:
    """تنسيق الأعداد"""
    try:
        if isinstance(num, float):
            if num.is_integer():
                return str(int(num))
            rounded = round(num, 2)
            if rounded.is_integer():
                return str(int(rounded))
            return str(rounded)
        return str(num)
    except:
        return str(num)

def extract_coefficients_from_equation(eq: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """تحليل معادلة خطية"""
    try:
        eq = eq.replace(' ', '').lower()
        if '=' not in eq:
            return None, None, None
        
        left, right = eq.split('=')
        try:
            c = float(right)
        except ValueError:
            return None, None, None
        
        a = 0.0
        b = 0.0
        
        # استخراج معامل x
        x_patterns = [
            r'([+-]?\d*\.?\d*)\*?x(?![a-zA-Z])',
            r'x\*([+-]?\d*\.?\d+)',
            r'([+-]?)x(?!\d)'
        ]
        for pattern in x_patterns:
            x_match = re.search(pattern, left)
            if x_match:
                coeff = x_match.group(1)
                if coeff == '' or coeff == '+':
                    a = 1.0
                elif coeff == '-':
                    a = -1.0
                else:
                    try:
                        a = float(coeff)
                    except:
                        continue
                break
        
        # استخراج معامل y
        y_patterns = [
            r'([+-]?\d*\.?\d*)\*?y(?![a-zA-Z])',
            r'y\*([+-]?\d*\.?\d+)',
            r'([+-]?)y(?!\d)'
        ]
        for pattern in y_patterns:
            y_match = re.search(pattern, left)
            if y_match:
                coeff = y_match.group(1)
                if coeff == '' or coeff == '+':
                    b = 1.0
                elif coeff == '-':
                    b = -1.0
                else:
                    try:
                        b = float(coeff)
                    except:
                        continue
                break
        
        return a, b, c
    except:
        return None, None, None

def extract_coefficients_3x3(eq: str) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
    """تحليل معادلة ثلاثية"""
    try:
        eq = eq.replace(' ', '').lower()
        if '=' not in eq:
            return None, None, None, None
        
        left, right = eq.split('=')
        try:
            d = float(right)
        except:
            return None, None, None, None
        
        a = b = c = 0.0
        
        # استخراج معامل x
        x_match = re.search(r'([+-]?\d*\.?\d*)\*?x', left)
        if x_match:
            coeff = x_match.group(1)
            a = 1.0 if coeff in ['', '+'] else -1.0 if coeff == '-' else float(coeff)
        
        # استخراج معامل y
        y_match = re.search(r'([+-]?\d*\.?\d*)\*?y', left)
        if y_match:
            coeff = y_match.group(1)
            b = 1.0 if coeff in ['', '+'] else -1.0 if coeff == '-' else float(coeff)
        
        # استخراج معامل z
        z_match = re.search(r'([+-]?\d*\.?\d*)\*?z', left)
        if z_match:
            coeff = z_match.group(1)
            c = 1.0 if coeff in ['', '+'] else -1.0 if coeff == '-' else float(coeff)
        
        return a, b, c, d
    except:
        return None, None, None, None

def parse_system_equations(expr: str) -> Optional[Dict]:
    """تحليل نظام معادلات"""
    try:
        expr = expr.strip()
        if not (expr.startswith('[') and expr.endswith(']')):
            return None
        
        expr = expr[1:-1].strip()
        equations = []
        current = ""
        depth = 0
        
        for char in expr:
            if char == '[':
                depth += 1
                current += char
            elif char == ']':
                depth -= 1
                current += char
            elif char == ',' and depth == 0:
                equations.append(current.strip())
                current = ""
            else:
                current += char
        
        if current:
            equations.append(current.strip())
        
        equations = [eq.replace('[', '').replace(']', '').strip() for eq in equations]
        
        if len(equations) == 2:
            return {"type": "system_2x2", "eq1": equations[0], "eq2": equations[1]}
        elif len(equations) == 3:
            return {"type": "system_3x3", "eq1": equations[0], "eq2": equations[1], "eq3": equations[2]}
        
        return None
    except:
        return None

def format_system_result(result: Any) -> str:
    """تنسيق نتيجة النظام"""
    try:
        if not result:
            return "لا يوجد حل"
        if isinstance(result, dict) and 'error' in result:
            return f"خطأ: {result['error']}"
        if isinstance(result, dict):
            if 'solution' in result and isinstance(result['solution'], dict):
                sol = result['solution']
                if 'x' in sol and 'y' in sol:
                    return f"x = {format_number(sol['x'])}, y = {format_number(sol['y'])}"
            if result.get('is_dependent', False):
                return f"عدد لا نهائي من الحلول: {result.get('general_solution', '')}"
            if result.get('is_inconsistent', False):
                return "لا يوجد حل (نظام متناقض)"
        if isinstance(result, (int, float)):
            return format_number(result)
        return str(result)
    except:
        return str(result)

def solve_system_2x2(eq1: str, eq2: str) -> Dict:
    """حل نظام 2×2"""
    try:
        a1, b1, c1 = extract_coefficients_from_equation(eq1)
        a2, b2, c2 = extract_coefficients_from_equation(eq2)
        
        if None in [a1, b1, c1, a2, b2, c2]:
            return {"success": False, "error": "فشل تحليل المعادلات"}
        
        # استخدام القوالب
        solvers = [
            solver1.template_21_system_2x2_unique,
            solver1.template_22_system_2x2_infinite,
            solver1.template_23_system_2x2_no_solution
        ]
        
        for solver_func in solvers:
            try:
                result = solver_func(a1, b1, c1, a2, b2, c2)
                if result:
                    return {"success": True, "result": format_system_result(result)}
            except:
                continue
        
        return {"success": False, "error": "فشل حل النظام"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def solve_system_3x3(eq1: str, eq2: str, eq3: str) -> Dict:
    """حل نظام 3×3"""
    try:
        a1, b1, c1, d1 = extract_coefficients_3x3(eq1)
        a2, b2, c2, d2 = extract_coefficients_3x3(eq2)
        a3, b3, c3, d3 = extract_coefficients_3x3(eq3)
        
        if None in [a1, b1, c1, d1, a2, b2, c2, d2, a3, b3, c3, d3]:
            return {"success": False, "error": "فشل تحليل المعادلات"}
        
        # حساب المحددات
        det_A = (a1*b2*c3 + b1*c2*a3 + c1*a2*b3) - (c1*b2*a3 + b1*a2*c3 + a1*c2*b3)
        
        if abs(det_A) < 1e-10:
            return {"success": False, "error": "النظام ليس له حل وحيد"}
        
        det_x = (d1*b2*c3 + b1*c2*d3 + c1*d2*b3) - (c1*b2*d3 + b1*d2*c3 + d1*c2*b3)
        det_y = (a1*d2*c3 + d1*c2*a3 + c1*a2*d3) - (c1*d2*a3 + d1*a2*c3 + a1*c2*d3)
        det_z = (a1*b2*d3 + b1*d2*a3 + d1*a2*b3) - (d1*b2*a3 + b1*a2*d3 + a1*d2*b3)
        
        x = det_x / det_A
        y = det_y / det_A
        z = det_z / det_A
        
        return {
            "success": True,
            "result": f"x = {format_number(x)}, y = {format_number(y)}, z = {format_number(z)}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== الدوال الرئيسية =====
def solve_calculate(expression: str) -> Dict:
    """معالجة طلب /calculate من الملف الأصلي"""
    try:
        expr = expression.strip()
        logger.info(f"معالجة: {expr}")
        
        # 1. القيمة المطلقة
        if '|' in expr and '=' in expr and not (expr.startswith('[') and expr.endswith(']')):
            match = re.search(r'\|(.*?)\|\s*=\s*(.+)', expr)
            if match:
                expr_inside = match.group(1).strip()
                value_str = match.group(2).strip()
                try:
                    value = float(value_str)
                except:
                    value = float(eval(value_str, {"__builtins__": {}}, math.__dict__))
                
                result = solver2.template_86_absolute_simple(expr_inside, value)
                if result:
                    solutions = []
                    if 'solutions' in result:
                        solutions = result['solutions']
                    elif 'cases' in result:
                        for case in result['cases']:
                            if 'solutions' in case:
                                solutions.extend(case['solutions'])
                    
                    if solutions:
                        formatted = [format_number(s) for s in solutions]
                        return {"success": True, "result": f"x = {formatted}"}
        
        # 2. نظم المعادلات
        if expr.startswith('[') and expr.endswith(']') and ',' in expr:
            system = parse_system_equations(expr)
            if system:
                if system["type"] == "system_2x2":
                    return solve_system_2x2(system["eq1"], system["eq2"])
                elif system["type"] == "system_3x3":
                    return solve_system_3x3(system["eq1"], system["eq2"], system["eq3"])
        
        # 3. الدوال المثلثية
        sin_match = re.search(r'sin\((\d+)\)', expr)
        if sin_match:
            angle = float(sin_match.group(1))
            result = calc.sin(angle)
            return {"success": True, "result": str(int(result)) if result.is_integer() else str(result)}
        
        cos_match = re.search(r'cos\((\d+)\)', expr)
        if cos_match:
            angle = float(cos_match.group(1))
            result = calc.cos(angle)
            return {"success": True, "result": str(int(result)) if result.is_integer() else str(result)}
        
        tan_match = re.search(r'tan\((\d+)\)', expr)
        if tan_match:
            angle = float(tan_match.group(1))
            result = calc.tan(angle)
            return {"success": True, "result": str(int(result)) if result.is_integer() else str(result)}
        
        ln_match = re.search(r'ln\((\d+)\)', expr)
        if ln_match:
            num = float(ln_match.group(1))
            result = calc.ln(num)
            return {"success": True, "result": str(int(result)) if result.is_integer() else str(result)}
        
        # 4. المعادلات
        if '=' in expr:
            result = calc.solve_equation(expr)
            if isinstance(result, str) and result.startswith('خطأ'):
                return {"success": False, "error": result}
            return {"success": True, "result": str(result)}
        
        # 5. عمليات حسابية
        result = calc.calculate(expr)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return {"success": True, "result": str(result)}
        
    except Exception as e:
        logger.error(f"خطأ: {e}")
        return {"success": False, "error": str(e)}

def solve_template(template_id: int, params: dict) -> Dict:
    """معالجة طلب قالب محدد"""
    try:
        result = None
        
        if 1 <= template_id <= 52:
            if template_id == 1:
                result = solver1.template_01_quadratic_standard(
                    params.get('a'), params.get('b'), params.get('c')
                )
            elif template_id == 2:
                result = solver1.template_02_linear_equation(params.get('equation'))
            elif template_id == 4:
                a1 = params.get('a1'); b1 = params.get('b1'); c1 = params.get('c1')
                a2 = params.get('a2'); b2 = params.get('b2'); c2 = params.get('c2')
                if None not in [a1, b1, c1, a2, b2, c2]:
                    result = solver1.template_21_system_2x2_unique(a1, b1, c1, a2, b2, c2)
            # باقي القوالب يمكن إضافتها لاحقاً
        
        elif 53 <= template_id <= 102:
            if template_id == 59:
                result = solver2.template_59_square_root_simplify(params.get('number'))
            elif template_id == 86:
                result = solver2.template_86_absolute_simple(
                    params.get('expression'), params.get('value')
                )
        
        elif 103 <= template_id <= 152:
            if template_id == 103:
                result = solver3.template_103_quartic_biquadratic(
                    params.get('a'), params.get('b'), params.get('c')
                )
        
        if result:
            if isinstance(result, dict):
                return {"success": True, "result": format_system_result(result)}
            return {"success": True, "result": str(result)}
        
        return {"success": False, "error": "فشل تنفيذ القالب"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def solve_system(eq1: str, eq2: str, eq3: str = None) -> Dict:
    """معالجة طلب نظام معادلات"""
    if eq3:
        return solve_system_3x3(eq1, eq2, eq3)
    return solve_system_2x2(eq1, eq2)

def search_templates(keyword: str) -> Dict:
    """بحث عن قوالب"""
    keyword = keyword.lower()
    results = []
    
    if keyword in ['تربيعية', 'quadratic']:
        results.append({'template_id': 1, 'name': 'المعادلة التربيعية'})
    if keyword in ['نظام', 'system']:
        results.extend([
            {'template_id': 4, 'name': 'نظام 2×2'},
            {'template_id': 5, 'name': 'نظام 3×3'}
        ])
    if keyword in ['جذر', 'root']:
        results.append({'template_id': 59, 'name': 'تبسيط جذر تربيعي'})
    
    return {"success": True, "results": results}

def list_templates(category: str = None) -> Dict:
    """عرض القوالب"""
    templates = {
        "basic": [
            {"id": 1, "name": "المعادلة التربيعية", "params": ["a", "b", "c"]},
            {"id": 2, "name": "المعادلة الخطية", "params": ["equation"]},
            {"id": 4, "name": "نظام 2×2", "params": ["eq1", "eq2"]},
            {"id": 5, "name": "نظام 3×3", "params": ["eq1", "eq2", "eq3"]}
        ],
        "roots": [
            {"id": 59, "name": "تبسيط جذر تربيعي", "params": ["number"]}
        ],
        "absolute": [
            {"id": 86, "name": "معادلة القيمة المطلقة", "params": ["expression", "value"]}
        ]
    }
    
    if category and category in templates:
        return {"success": True, "templates": templates[category]}
    return {"success": True, "templates": templates}

def get_stats() -> Dict:
    """إحصائيات"""
    try:
        stats = {
            "part1": solver1.get_stats() if hasattr(solver1, 'get_stats') else {"total_calls": 0},
            "part2": solver2.get_stats() if hasattr(solver2, 'get_stats') else {"total_calls": 0},
            "part3": solver3.get_stats() if hasattr(solver3, 'get_stats') else {"total_calls": 0},
        }
        stats["total_calls"] = sum(s['total_calls'] for s in stats.values())
        return {"success": True, "stats": stats}
    except Exception as e:
        return {"success": False, "error": str(e)}
