# server.py - خادم الويب المتكامل (نسخة نهائية)
# ============================================================================
# هذا الملف يدمج جميع القوالب الجديدة مع النظام القديم
# الإصدار: 3.1.0 - نهائي ومستقر - مع تنسيق النتائج بشكل مفهوم
# ============================================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from pathlib import Path
import re
import math
import json
import ast
import logging
from typing import Optional, Dict, Any, List, Tuple, Union

# ===== إعداد التسجيل =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===== استيراد الحاسبة القديمة =====
from calculator import Calculator

# ===== استيراد القوالب الجديدة =====
from algebra_part1 import CompleteAlgebraSolver
from algebra_part2 import IntermediateAlgebraSolver
from algebra_part3 import AdvancedAlgebraSolver

# ===== تهيئة التطبيق =====
app = FastAPI(
    title="الآلة الحاسبة المتكاملة",
    description="نظام حلول رياضية متكامل بـ 152 قالباً",
    version="3.1.0"
)

# ===== إعداد CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== إنشاء كائنات الحلول =====
calc = Calculator()  # الحاسبة القديمة
solver1 = CompleteAlgebraSolver()  # القوالب 1-52
solver2 = IntermediateAlgebraSolver()  # القوالب 53-102
solver3 = AdvancedAlgebraSolver()  # القوالب 103-152

# ===== إعداد المجلد الثابت =====
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

# ===== نماذج البيانات =====
class ExpressionRequest(BaseModel):
    """نموذج طلب التعبير الرياضي"""
    expression: str

class TemplateRequest(BaseModel):
    """نموذج طلب قالب محدد"""
    template_id: int
    params: dict

class SystemRequest(BaseModel):
    """نموذج طلب نظام معادلات"""
    eq1: str
    eq2: str
    eq3: Optional[str] = None

# ===== دوال تحليل المعادلات =====
# ============================================================================

def extract_coefficients_from_equation(eq: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    تحليل معادلة خطية إلى المعاملات a, b, c
    مثال: "2*x + 3*y = 8" -> (2, 3, 8)
    
    المعاملات:
        eq: المعادلة النصية
        
    المخرجات:
        (a, b, c) معاملات x, y والثابت
    """
    try:
        # تنظيف النص
        eq = eq.replace(' ', '').lower()
        
        # فصل الطرفين
        if '=' not in eq:
            logger.error(f"المعادلة لا تحتوي على علامة =: {eq}")
            return None, None, None
        
        left, right = eq.split('=')
        
        # تحويل الطرف الأيمن إلى عدد
        try:
            c = float(right)
        except ValueError:
            logger.error(f"الطرف الأيمن ليس رقماً صحيحاً: {right}")
            return None, None, None
        
        # تهيئة المعاملات
        a = 0.0
        b = 0.0
        
        # استخراج معامل x
        x_patterns = [
            r'([+-]?\d*\.?\d*)\*?x(?![a-zA-Z])',  # 2*x, 2x, +2x, -2x
            r'x\*([+-]?\d*\.?\d+)',                # x*2
            r'([+-]?)x(?!\d)'                       # x, +x, -x
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
                    except ValueError:
                        continue
                break
        
        # استخراج معامل y
        y_patterns = [
            r'([+-]?\d*\.?\d*)\*?y(?![a-zA-Z])',  # 3*y, 3y, +3y, -3y
            r'y\*([+-]?\d*\.?\d+)',                # y*3
            r'([+-]?)y(?!\d)'                       # y, +y, -y
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
                    except ValueError:
                        continue
                break
        
        # التحقق من صحة المعاملات
        if a is None or b is None or c is None:
            logger.error(f"فشل استخراج المعاملات من: {eq}")
            return None, None, None
            
        logger.info(f"تم تحليل المعادلة '{eq}' إلى: a={a}, b={b}, c={c}")
        return a, b, c
        
    except Exception as e:
        logger.error(f"خطأ في تحليل المعادلة '{eq}': {str(e)}")
        return None, None, None

def parse_system_equations(expr: str) -> Optional[Dict[str, Any]]:
    """
    تحليل صيغة نظام المعادلات
    مثال: "[2*x + 3*y = 8, 3*x - y = 1]"
    
    المخرجات:
        قاموس بنوع النظام والمعادلات
    """
    try:
        # إزالة الأقواس المربعة والمسافات
        expr = expr.strip()
        if not (expr.startswith('[') and expr.endswith(']')):
            return None
            
        expr = expr[1:-1].strip()
        
        # تقسيم على الفاصلة مع الحفاظ على المعادلات
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
        
        # إزالة أي أقواس متبقية
        equations = [eq.replace('[', '').replace(']', '').strip() for eq in equations]
        
        logger.info(f"تم تحليل النظام إلى {len(equations)} معادلات: {equations}")
        
        if len(equations) == 2:
            return {
                "type": "system_2x2",
                "eq1": equations[0],
                "eq2": equations[1]
            }
        elif len(equations) == 3:
            return {
                "type": "system_3x3",
                "eq1": equations[0],
                "eq2": equations[1],
                "eq3": equations[2]
            }
        else:
            logger.warning(f"عدد غير مناسب من المعادلات: {len(equations)}")
            return None
            
    except Exception as e:
        logger.error(f"خطأ في تحليل نظام المعادلات '{expr}': {str(e)}")
        return None

def format_system_result(result: Any) -> str:
    """
    تنسيق نتيجة نظام المعادلات للعرض بشكل مفهوم للمستخدم
    """
    try:
        if not result:
            return "لا يوجد حل"
        
        # حالة وجود خطأ
        if isinstance(result, dict) and 'error' in result:
            return f"خطأ: {result['error']}"
        
        # محاولة استخراج الحل من التنسيقات المختلفة
        if isinstance(result, dict):
            
            # 1. تنسيق القالب 21 (حل وحيد)
            if 'solution' in result and isinstance(result['solution'], dict):
                sol = result['solution']
                if 'x' in sol and 'y' in sol:
                    x = sol['x']
                    y = sol['y']
                    if x is not None and y is not None:
                        # تنسيق الأعداد (إزالة .0 إذا كان عدداً صحيحاً)
                        x_str = str(int(x)) if x.is_integer() else str(x)
                        y_str = str(int(y)) if y.is_integer() else str(y)
                        return f"x = {x_str}, y = {y_str}"
            
            # 2. تنسيق القالب 21 مع مفتاح sympy
            if 'solution' in result and isinstance(result['solution'], dict) and 'sympy' in result['solution']:
                sympy_sol = result['solution']['sympy']
                if 'x' in sympy_sol and 'y' in sympy_sol:
                    x = sympy_sol['x']
                    y = sympy_sol['y']
                    if x is not None and y is not None:
                        x_str = str(int(x)) if isinstance(x, float) and x.is_integer() else str(x)
                        y_str = str(int(y)) if isinstance(y, float) and y.is_integer() else str(y)
                        return f"x = {x_str}, y = {y_str}"
            
            # 3. تنسيق القالب 21 مع مفتاح cramer
            if 'solution' in result and isinstance(result['solution'], dict) and 'cramer' in result['solution']:
                cramer_sol = result['solution']['cramer']
                if 'x' in cramer_sol and 'y' in cramer_sol:
                    x = cramer_sol['x']
                    y = cramer_sol['y']
                    if x is not None and y is not None:
                        x_str = str(int(x)) if isinstance(x, float) and x.is_integer() else str(x)
                        y_str = str(int(y)) if isinstance(y, float) and y.is_integer() else str(y)
                        return f"x = {x_str}, y = {y_str}"
            
            # 4. تنسيق القالب 22 (عدد لا نهائي من الحلول)
            if result.get('is_dependent', False):
                general_sol = result.get('general_solution', '')
                return f"عدد لا نهائي من الحلول: {general_sol}"
            
            # 5. تنسيق القالب 23 (لا يوجد حل)
            if result.get('is_inconsistent', False):
                return "لا يوجد حل (نظام متناقض)"
            
            # 6. تنسيق القالب 27 (نظام 3×3)
            if 'solutions' in result and isinstance(result['solutions'], dict):
                if 'sympy_method' in result['solutions']:
                    sol = result['solutions']['sympy_method']
                    if sol:
                        parts = []
                        if 'x' in sol and sol['x'] is not None:
                            x = sol['x']
                            x_str = str(int(x)) if isinstance(x, float) and x.is_integer() else str(x)
                            parts.append(f"x = {x_str}")
                        if 'y' in sol and sol['y'] is not None:
                            y = sol['y']
                            y_str = str(int(y)) if isinstance(y, float) and y.is_integer() else str(y)
                            parts.append(f"y = {y_str}")
                        if 'z' in sol and sol['z'] is not None:
                            z = sol['z']
                            z_str = str(int(z)) if isinstance(z, float) and z.is_integer() else str(z)
                            parts.append(f"z = {z_str}")
                        if parts:
                            return ", ".join(parts)
            
            # 7. تنسيق القوالب الأخرى
            if 'roots' in result:
                roots = result['roots']
                if isinstance(roots, dict) and 'values' in roots:
                    values = roots['values']
                    if 'real' in values and values['real']:
                        real_roots = [str(int(r)) if isinstance(r, float) and r.is_integer() else str(r) for r in values['real']]
                        return f"x = {real_roots}"
                    elif 'decimal' in values:
                        decimals = [str(int(d)) if isinstance(d, float) and d.is_integer() else str(d) for d in values['decimal']]
                        return f"x = {decimals}"
            
            if 'solutions' in result and isinstance(result['solutions'], list):
                solutions = [str(int(s)) if isinstance(s, float) and s.is_integer() else str(s) for s in result['solutions']]
                return f"x = {solutions}"
        
        # إذا كان النتيجة نصاً أو رقماً
        if isinstance(result, (int, float)):
            if isinstance(result, float) and result.is_integer():
                return str(int(result))
            return str(result)
        
        if isinstance(result, list):
            formatted = []
            for item in result:
                if isinstance(item, (int, float)):
                    if isinstance(item, float) and item.is_integer():
                        formatted.append(str(int(item)))
                    else:
                        formatted.append(str(item))
                else:
                    formatted.append(str(item))
            return f"x = {formatted}"
        
        # إذا لم نتمكن من التنسيق، نعيد النتيجة كسلسلة نصية بسيطة
        return str(result)
        
    except Exception as e:
        logger.error(f"خطأ في تنسيق النتيجة: {str(e)}")
        # في حالة الخطأ، نعيد النتيجة الأصلية
        return str(result)

def solve_system_2x2(eq1: str, eq2: str) -> Dict[str, Any]:
    """
    حل نظام معادلتين 2×2 مع محاولة جميع التوابع المتاحة
    """
    try:
        # تحليل المعادلات إلى معاملات
        a1, b1, c1 = extract_coefficients_from_equation(eq1)
        a2, b2, c2 = extract_coefficients_from_equation(eq2)
        
        # التحقق من صحة المعاملات
        if None in [a1, b1, c1, a2, b2, c2]:
            return {
                "success": False,
                "error": "فشل تحليل المعادلات. تأكد من الصيغة: مثال صحيح: 2*x + 3*y = 8"
            }
        
        logger.info(f"محاولة حل النظام: ({a1},{b1},{c1}), ({a2},{b2},{c2})")
        
        # قائمة التوابع للمحاولة بالترتيب
        solvers = [
            ("template_21_system_2x2_unique", solver1.template_21_system_2x2_unique),
            ("template_22_system_2x2_infinite", solver1.template_22_system_2x2_infinite),
            ("template_23_system_2x2_no_solution", solver1.template_23_system_2x2_no_solution),
            ("template_04_system_2x2", getattr(solver1, 'template_04_system_2x2', None))
        ]
        
        last_error = None
        
        for solver_name, solver_func in solvers:
            if solver_func is None:
                continue
                
            try:
                logger.info(f"محاولة استخدام {solver_name}")
                result = solver_func(a1, b1, c1, a2, b2, c2)
                
                if result:
                    # تنسيق النتيجة للعرض
                    formatted = format_system_result(result)
                    return {
                        "success": True,
                        "result": formatted,  # نعيد النتيجة المنسقة فقط
                        "method": solver_name
                        # لا نعيد raw result لتجنب الإرباك
                    }
            except Exception as e:
                last_error = str(e)
                logger.warning(f"فشل {solver_name}: {e}")
                continue
        
        # إذا وصلنا إلى هنا، فجميع المحاولات فشلت
        return {
            "success": False,
            "error": f"فشل حل النظام. آخر خطأ: {last_error}"
        }
        
    except Exception as e:
        logger.error(f"خطأ غير متوقع في حل النظام: {str(e)}")
        return {
            "success": False,
            "error": f"خطأ غير متوقع: {str(e)}"
        }

def solve_system_3x3(eq1: str, eq2: str, eq3: str) -> Dict[str, Any]:
    """
    حل نظام ثلاث معادلات 3×3
    """
    try:
        # تحليل المعادلات (هذه نسخة مبسطة - تحتاج لتطوير)
        # في الإصدار الحالي، نمرر المعادلات كما هي
        
        solvers = [
            ("template_27_system_3x3_unique", solver1.template_27_system_3x3_unique),
            ("template_05_system_3x3", getattr(solver1, 'template_05_system_3x3', None)),
            ("template_28_system_3x3_gaussian", getattr(solver1, 'template_28_system_3x3_gaussian', None))
        ]
        
        for solver_name, solver_func in solvers:
            if solver_func is None:
                continue
                
            try:
                logger.info(f"محاولة استخدام {solver_name}")
                result = solver_func(eq1, eq2, eq3)
                
                if result:
                    formatted = format_system_result(result)
                    return {
                        "success": True,
                        "result": formatted,
                        "method": solver_name
                    }
            except Exception as e:
                logger.warning(f"فشل {solver_name}: {e}")
                continue
        
        return {
            "success": False,
            "error": "لم نتمكن من حل نظام 3×3 حالياً - قيد التطوير"
        }
        
    except Exception as e:
        logger.error(f"خطأ في حل نظام 3×3: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# ===== نقاط النهاية الرئيسية =====
# ============================================================================

@app.post("/calculate")
async def calculate(data: ExpressionRequest):
    """
    نقطة النهاية الرئيسية للحسابات
    تدعم: العمليات العادية، المعادلات، الدوال المثلثية، نظم المعادلات
    """
    try:
        expr = data.expression.strip()
        logger.info(f"طلب جديد: {expr}")
        
        # ===== 1. التعامل مع نظم المعادلات =====
        if expr.startswith('[') and expr.endswith(']') and ',' in expr:
            logger.info("اكتشاف نظام معادلات")
            system = parse_system_equations(expr)
            
            if system:
                if system["type"] == "system_2x2":
                    result = solve_system_2x2(system["eq1"], system["eq2"])
                    if result["success"]:
                        return {"success": True, "result": result["result"]}
                    else:
                        return {"success": False, "error": result["error"]}
                        
                elif system["type"] == "system_3x3":
                    result = solve_system_3x3(system["eq1"], system["eq2"], system["eq3"])
                    if result["success"]:
                        return {"success": True, "result": result["result"]}
                    else:
                        return {"success": False, "error": result["error"]}
        
        # ===== 2. التعامل مع الدوال المثلثية =====
        # sin(30)
        sin_match = re.search(r'sin\((\d+)\)', expr)
        if sin_match:
            angle = float(sin_match.group(1))
            result = calc.sin(angle)
            logger.info(f"sin({angle}) = {result}")
            # تنسيق النتيجة
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return {"success": True, "result": str(result)}
        
        # cos(60)
        cos_match = re.search(r'cos\((\d+)\)', expr)
        if cos_match:
            angle = float(cos_match.group(1))
            result = calc.cos(angle)
            logger.info(f"cos({angle}) = {result}")
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return {"success": True, "result": str(result)}
        
        # tan(45)
        tan_match = re.search(r'tan\((\d+)\)', expr)
        if tan_match:
            angle = float(tan_match.group(1))
            result = calc.tan(angle)
            logger.info(f"tan({angle}) = {result}")
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return {"success": True, "result": str(result)}
        
        # ===== 3. التعامل مع ln =====
        ln_match = re.search(r'ln\((\d+)\)', expr)
        if ln_match:
            num = float(ln_match.group(1))
            result = calc.ln(num)
            logger.info(f"ln({num}) = {result}")
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return {"success": True, "result": str(result)}
        
        # ===== 4. التعامل مع المعادلات (تحتوي على =) =====
        if '=' in expr:
            logger.info("اكتشاف معادلة")
            result = calc.solve_equation(expr)
            # محاولة تنسيق النتيجة
            if isinstance(result, str) and result.startswith('x = ['):
                # تبسيط تنسيق القوائم
                result = result.replace('x = [', '').replace(']', '')
            return {"success": True, "result": str(result)}
        
        # ===== 5. العمليات الحسابية العادية =====
        logger.info("عملية حسابية عادية")
        result = calc.calculate(expr)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return {"success": True, "result": str(result)}
        
    except Exception as e:
        logger.error(f"خطأ في المعالجة: {str(e)}")
        return {"success": False, "error": str(e)}

# ===== نقاط نهاية القوالب المتقدمة =====
# ============================================================================

@app.post("/algebra/template/{template_id}")
async def solve_template(template_id: int, request: TemplateRequest):
    """
    حل قالب رياضي محدد باستخدام المعاملات المعطاة
    """
    try:
        params = request.params
        result = None
        logger.info(f"طلب قالب {template_id} مع المعاملات: {params}")
        
        # ===== القوالب 1-52 (الملف الأول) =====
        if 1 <= template_id <= 52:
            if template_id == 1:
                # معادلة تربيعية
                result = solver1.template_01_quadratic_standard(
                    params.get('a'), params.get('b'), params.get('c')
                )
            elif template_id == 2:
                # معادلة خطية
                result = solver1.template_02_linear_equation(
                    params.get('equation')
                )
            elif template_id == 3:
                # معادلة متعددة الحدود
                result = solver1.template_03_polynomial_equation(
                    params.get('polynomial')
                )
            elif template_id == 4:
                # نظام 2×2
                a1 = params.get('a1')
                b1 = params.get('b1')
                c1 = params.get('c1')
                a2 = params.get('a2')
                b2 = params.get('b2')
                c2 = params.get('c2')
                
                if None not in [a1, b1, c1, a2, b2, c2]:
                    try:
                        result = solver1.template_21_system_2x2_unique(
                            a1, b1, c1, a2, b2, c2
                        )
                    except AttributeError:
                        result = solver1.template_04_system_2x2(
                            params.get('eq1'), params.get('eq2')
                        )
                else:
                    # محاولة باستخدام المعادلات النصية
                    result = solver1.template_04_system_2x2(
                        params.get('eq1'), params.get('eq2')
                    )
            elif template_id == 5:
                # نظام 3×3
                result = solver1.template_05_system_3x3(
                    params.get('eq1'), params.get('eq2'), params.get('eq3')
                )
            elif template_id == 6:
                # تبسيط تعبير
                result = solver1.template_06_simplify_expression(
                    params.get('expression'), params.get('method', 'auto')
                )
            elif template_id == 7:
                # GCD
                result = solver1.template_07_gcd(
                    params.get('expr1'), params.get('expr2')
                )
            elif template_id == 8:
                # LCM
                result = solver1.template_08_lcm(
                    params.get('expr1'), params.get('expr2')
                )
            elif template_id == 9:
                # توسيع
                result = solver1.template_09_expand(
                    params.get('expression'), params.get('fully', True)
                )
            elif template_id == 10:
                # تحليل
                result = solver1.template_10_factorize(
                    params.get('expression'), params.get('method', 'auto')
                )
            else:
                result = {"error": f"القالب {template_id} غير مضمن بعد في هذه النسخة"}
        
        # ===== القوالب 53-102 (الملف الثاني) =====
        elif 53 <= template_id <= 102:
            if template_id == 53:
                result = solver2.template_53_power_rules(
                    params.get('base'), params.get('exponent')
                )
            elif template_id == 54:
                result = solver2.template_54_power_equations_same_base(
                    params.get('base'), params.get('exp1'), params.get('exp2')
                )
            elif template_id == 55:
                result = solver2.template_55_power_equations_different_base(
                    params.get('a'), params.get('b')
                )
            elif template_id == 56:
                result = solver2.template_56_power_inequalities(
                    params.get('a'), params.get('b'), params.get('inequality')
                )
            elif template_id == 57:
                result = solver2.template_57_power_system(
                    params.get('eq1'), params.get('eq2')
                )
            elif template_id == 58:
                result = solver2.template_58_power_word_problems(
                    params.get('problem_type'), params.get('values', {})
                )
            elif template_id == 59:
                result = solver2.template_59_square_root_simplify(
                    params.get('number')
                )
            elif template_id == 60:
                result = solver2.template_60_cube_root_simplify(
                    params.get('number')
                )
            else:
                result = {"error": f"القالب {template_id} غير مضمن بعد في هذه النسخة"}
        
        # ===== القوالب 103-152 (الملف الثالث) =====
        elif 103 <= template_id <= 152:
            if template_id == 103:
                result = solver3.template_103_quartic_biquadratic(
                    params.get('a'), params.get('b'), params.get('c')
                )
            elif template_id == 104:
                result = solver3.template_104_quartic_depressed(
                    params.get('a'), params.get('b'), params.get('c'), 
                    params.get('d'), params.get('e')
                )
            elif template_id == 105:
                result = solver3.template_105_quartic_factorable(
                    params.get('coefficients')
                )
            elif template_id == 106:
                result = solver3.template_106_quartic_reciprocal(
                    params.get('a'), params.get('b'), params.get('c')
                )
            elif template_id == 107:
                result = solver3.template_107_quartic_quadratic_form(
                    params.get('a'), params.get('b'), params.get('c'), params.get('d')
                )
            elif template_id == 108:
                result = solver3.template_108_quartic_general(
                    params.get('a'), params.get('b'), params.get('c'), 
                    params.get('d'), params.get('e')
                )
            else:
                result = {"error": f"القالب {template_id} غير مضمن بعد في هذه النسخة"}
        
        else:
            return {"success": False, "error": "قالب غير موجود"}
        
        if result:
            logger.info(f"تم تنفيذ القالب {template_id} بنجاح")
            # تنسيق النتيجة
            if isinstance(result, dict):
                # محاولة تنسيق النتيجة
                formatted = format_system_result(result)
                return {"success": True, "result": formatted}
            return {"success": True, "result": str(result)}
        else:
            return {"success": False, "error": "فشل في تنفيذ القالب"}
            
    except Exception as e:
        logger.error(f"خطأ في تنفيذ القالب {template_id}: {str(e)}")
        return {"success": False, "error": str(e)}

@app.post("/algebra/system")
async def solve_system(request: SystemRequest):
    """
    نقطة نهاية مخصصة لنظم المعادلات
    """
    try:
        if request.eq3:
            # نظام 3×3
            result = solve_system_3x3(request.eq1, request.eq2, request.eq3)
        else:
            # نظام 2×2
            result = solve_system_2x2(request.eq1, request.eq2)
        
        if result["success"]:
            return {"success": True, "result": result["result"]}
        else:
            return {"success": False, "error": result["error"]}
            
    except Exception as e:
        logger.error(f"خطأ في /algebra/system: {str(e)}")
        return {"success": False, "error": str(e)}

@app.post("/algebra/search")
async def search_templates(query: dict):
    """
    البحث عن قوالب حسب النوع أو الكلمات المفتاحية
    """
    try:
        keyword = query.get('keyword', '').lower()
        results = []
        
        # البحث في القوالب الأساسية
        if keyword in ['تربيعية', 'quadratic', 'معادلة']:
            results.append({
                'template_id': 1,
                'name': 'المعادلة التربيعية',
                'description': 'ax² + bx + c = 0'
            })
        
        if keyword in ['خطية', 'linear', 'معادلة']:
            results.append({
                'template_id': 2,
                'name': 'المعادلة الخطية',
                'description': 'ax + b = 0'
            })
        
        if keyword in ['نظام', 'system']:
            results.extend([
                {'template_id': 4, 'name': 'نظام 2×2', 'description': 'معادلتين خطيتين'},
                {'template_id': 5, 'name': 'نظام 3×3', 'description': 'ثلاث معادلات خطية'}
            ])
        
        if keyword in ['تحليل', 'factor']:
            results.append({
                'template_id': 10,
                'name': 'تحليل العوامل',
                'description': 'تحليل تعبير جبري'
            })
        
        if keyword in ['أسية', 'exponential']:
            results.extend([
                {'template_id': 55, 'name': 'معادلة أسية', 'description': 'a^x = b'},
                {'template_id': 56, 'name': 'متباينة أسية', 'description': 'a^x > b'}
            ])
        
        if keyword in ['لوغاريتم', 'log']:
            results.extend([
                {'template_id': 64, 'name': 'أساسيات اللوغاريتم', 'description': 'log_b(a)'},
                {'template_id': 65, 'name': 'خصائص اللوغاريتم', 'description': 'قوانين اللوغاريتمات'}
            ])
        
        if keyword in ['جذر', 'root', 'radical']:
            results.extend([
                {'template_id': 59, 'name': 'تبسيط جذر تربيعي', 'description': '√n'},
                {'template_id': 60, 'name': 'تبسيط جذر تكعيبي', 'description': '∛n'},
                {'template_id': 99, 'name': 'معادلة جذرية', 'description': '√(ax+b) = c'}
            ])
        
        if keyword in ['رباعية', 'quartic']:
            results.extend([
                {'template_id': 103, 'name': 'معادلة رباعية ثنائية التربيع', 'description': 'ax⁴ + bx² + c = 0'},
                {'template_id': 108, 'name': 'معادلة رباعية عامة', 'description': 'ax⁴ + bx³ + cx² + dx + e = 0'}
            ])
        
        return {"success": True, "results": results}
        
    except Exception as e:
        logger.error(f"خطأ في البحث: {str(e)}")
        return {"success": False, "error": str(e)}

@app.get("/algebra/templates")
async def list_templates(category: str = None):
    """
    عرض جميع القوالب المتاحة (اختياري حسب الفئة)
    """
    templates = {
        "basic": [
            {"id": 1, "name": "المعادلة التربيعية", "params": ["a", "b", "c"]},
            {"id": 2, "name": "المعادلة الخطية", "params": ["equation"]},
            {"id": 3, "name": "معادلة متعددة الحدود", "params": ["polynomial"]},
            {"id": 4, "name": "نظام معادلتين 2×2", "params": ["eq1", "eq2"]},
            {"id": 5, "name": "نظام ثلاث معادلات 3×3", "params": ["eq1", "eq2", "eq3"]},
            {"id": 6, "name": "تبسيط تعبير جبري", "params": ["expression"]},
            {"id": 7, "name": "GCD", "params": ["expr1", "expr2"]},
            {"id": 8, "name": "LCM", "params": ["expr1", "expr2"]},
            {"id": 9, "name": "توسيع", "params": ["expression"]},
            {"id": 10, "name": "تحليل", "params": ["expression"]}
        ],
        "powers": [
            {"id": 53, "name": "قوانين القوى", "params": ["base", "exponent"]},
            {"id": 54, "name": "معادلة أسية - نفس الأساس", "params": ["base", "exp1", "exp2"]},
            {"id": 55, "name": "معادلة أسية - أساس مختلف", "params": ["a", "b"]},
            {"id": 56, "name": "متباينة أسية", "params": ["a", "b", "inequality"]},
            {"id": 59, "name": "تبسيط جذر تربيعي", "params": ["number"]},
            {"id": 60, "name": "تبسيط جذر تكعيبي", "params": ["number"]}
        ],
        "logs": [
            {"id": 64, "name": "أساسيات اللوغاريتم", "params": ["base", "argument"]},
            {"id": 65, "name": "خصائص اللوغاريتم", "params": ["operation", "a", "b"]},
            {"id": 66, "name": "تبسيط تعبير لوغاريتمي", "params": ["expression"]},
            {"id": 67, "name": "تغيير أساس اللوغاريتم", "params": ["value", "old_base", "new_base"]},
            {"id": 69, "name": "معادلة لوغاريتمية بسيطة", "params": ["base", "argument", "value"]}
        ],
        "quartic": [
            {"id": 103, "name": "معادلة رباعية ثنائية التربيع", "params": ["a", "b", "c"]},
            {"id": 104, "name": "معادلة رباعية ناقصة", "params": ["a", "b", "c", "d", "e"]},
            {"id": 105, "name": "معادلة رباعية قابلة للتحليل", "params": ["coefficients"]},
            {"id": 108, "name": "معادلة رباعية عامة", "params": ["a", "b", "c", "d", "e"]}
        ],
        "verification": [
            {"id": 144, "name": "التحقق من نوع المعادلة", "params": ["equation"]},
            {"id": 146, "name": "التحقق من مجال المعادلة", "params": ["equation"]},
            {"id": 149, "name": "التحقق من صحة جذر", "params": ["equation", "root"]},
            {"id": 150, "name": "التحقق من عدة جذور", "params": ["equation", "roots"]},
            {"id": 152, "name": "التحقق من دقة جذر", "params": ["equation", "root"]}
        ]
    }
    
    if category and category in templates:
        return {"success": True, "templates": templates[category]}
    elif category:
        return {"success": False, "error": "فئة غير موجودة"}
    else:
        return {"success": True, "templates": templates}

@app.get("/algebra/stats")
async def get_stats():
    """
    إحصائيات استخدام القوالب
    """
    try:
        stats = {
            "part1": solver1.get_stats(),
            "part2": solver2.get_stats(),
            "part3": solver3.get_stats(),
            "total_calls": (
                solver1.stats['total_calls'] + 
                solver2.stats['total_calls'] + 
                solver3.stats['total_calls']
            )
        }
        return {"success": True, "stats": stats}
    except Exception as e:
        logger.error(f"خطأ في جلب الإحصائيات: {str(e)}")
        return {"success": False, "error": str(e)}

@app.get("/")
async def root():
    """الصفحة الرئيسية"""
    return FileResponse(str(static_dir / "index.html"))

@app.get("/health")
async def health_check():
    """التحقق من صحة الخادم"""
    return {
        "status": "healthy",
        "version": "3.1.0",
        "templates": 152,
        "parts": ["part1 (1-52)", "part2 (53-102)", "part3 (103-152)"]
    }

# ===== تشغيل الخادم =====
if __name__ == "__main__":
    print("=" * 70)
    print("🚀 بسم الله الرحمن الرحيم")
    print("=" * 70)
    print("🧮 تشغيل خادم الويب المتكامل - النسخة النهائية v3.1.0")
    print("=" * 70)
    print(f"📍 العنوان المحلي: http://127.0.0.1:8000")
    print(f"🌐 العنوان الشبكي: http://localhost:8000")
    print("=" * 70)
    print(f"📊 القوالب المتاحة: 152 قالباً")
    print(f"   📁 الجزء الأول: القوالب 1-52 (الجبر الأساسي)")
    print(f"   📁 الجزء الثاني: القوالب 53-102 (الجبر المتوسط)")
    print(f"   📁 الجزء الثالث: القوالب 103-152 (الجبر المتقدم)")
    print("=" * 70)
    print("🔍 نقاط النهاية المتاحة:")
    print("   ✅ POST /calculate - الحسابات العامة")
    print("   ✅ POST /algebra/template/{id} - حل قالب محدد")
    print("   ✅ POST /algebra/system - حل نظم معادلات")
    print("   ✅ POST /algebra/search - بحث عن قوالب")
    print("   ✅ GET  /algebra/templates - عرض القوالب")
    print("   ✅ GET  /algebra/stats - إحصائيات")
    print("   ✅ GET  /health - فحص الصحة")
    print("=" * 70)
    print("📝 أمثلة للاستخدام:")
    print("   • [2*x + 3*y = 8, 3*x - y = 1]  → x = 1, y = 2")
    print("   • x^2 - 5*x + 6 = 0             → x = [2, 3]")
    print("   • sin(30)                        → 0.5")
    print("   • log(x, 2) + log(x-2, 2) = 3    → x = 4")
    print("=" * 70)
    print("✅ النظام جاهز للعمل - جميع النتائج مفهومة للمستخدم")
    print("=" * 70)
    
    # تشغيل الخادم
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8000,
        log_level="info"
    )
