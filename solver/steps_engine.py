# steps_engine.py - محرك خطوات الحل الكامل
import logging
import re
import math
from math_engine.algebra.algebra_part1 import CompleteAlgebraSolver
from math_engine.algebra.algebra_part2 import IntermediateAlgebraSolver
from calculator import Calculator

logger = logging.getLogger(__name__)

# تهيئة الكائنات
solver1 = CompleteAlgebraSolver()
solver2 = IntermediateAlgebraSolver()
calc = Calculator()

def format_number(num: float) -> str:
    """تنسيق الأعداد للعرض"""
    try:
        if isinstance(num, float):
            if num.is_integer():
                return str(int(num))
            rounded = round(num, 3)
            if rounded.is_integer():
                return str(int(rounded))
            return str(rounded).rstrip('0').rstrip('.')
        return str(num)
    except:
        return str(num)

def solve_quadratic_with_steps(equation: str) -> dict:
    """حل معادلة تربيعية مع خطوات"""
    steps = []
    steps.append("📌 **السؤال:** " + equation)
    steps.append("")
    
    try:
        # تنظيف المعادلة
        clean_eq = equation.replace(' ', '').replace('²', '^2').replace('=', '=')
        
        # استخراج المعاملات
        left, right = clean_eq.split('=')
        right_val = float(right) if right else 0
        
        # تحويل الطرف الأيسر
        left = left.replace('^2', '**2')
        
        # استخراج a, b, c
        a = b = c = 0
        
        # استخراج a (معامل x²)
        a_match = re.search(r'([+-]?\d*\.?\d*)\*?x\*\*2', left)
        if a_match:
            a_str = a_match.group(1)
            a = 1.0 if a_str in ['', '+'] else -1.0 if a_str == '-' else float(a_str)
        
        # استخراج b (معامل x)
        b_match = re.search(r'([+-]?\d*\.?\d*)\*?x(?!\*\*)', left)
        if b_match:
            b_str = b_match.group(1)
            b = 1.0 if b_str in ['', '+'] else -1.0 if b_str == '-' else float(b_str)
        
        # استخراج c (ثابت)
        const_match = re.search(r'([+-]?\d+\.?\d*)(?![\dx\*\*])', left)
        if const_match:
            c = float(const_match.group(1))
        
        # تعديل حسب الطرف الأيمن
        c = c - right_val
        
        steps.append("📐 **الخطوة 1: كتابة المعادلة على الصورة القياسية**")
        steps.append(f"   {format_number(a)}x² + {format_number(b)}x + {format_number(c)} = 0")
        steps.append("")
        
        # حساب المميز
        discriminant = b**2 - 4*a*c
        steps.append("📐 **الخطوة 2: حساب المميز (Δ)**")
        steps.append(f"   Δ = b² - 4ac")
        steps.append(f"   Δ = ({format_number(b)})² - 4×({format_number(a)})×({format_number(c)})")
        steps.append(f"   Δ = {format_number(discriminant)}")
        steps.append("")
        
        # تحديد نوع الحلول
        if discriminant > 0:
            steps.append("📐 **الخطوة 3: Δ > 0 → للمعادلة جذران حقيقيان مختلفان**")
            steps.append("   نطبق القانون العام: x = [-b ± √Δ] / 2a")
            
            sqrt_disc = math.sqrt(discriminant)
            x1 = (-b + sqrt_disc) / (2*a)
            x2 = (-b - sqrt_disc) / (2*a)
            
            steps.append(f"   x₁ = [{-format_number(b)} + √{format_number(discriminant)}] / {format_number(2*a)}")
            steps.append(f"       = {format_number(-b + sqrt_disc)} / {format_number(2*a)}")
            steps.append(f"       = {format_number(x1)}")
            steps.append("")
            steps.append(f"   x₂ = [{-format_number(b)} - √{format_number(discriminant)}] / {format_number(2*a)}")
            steps.append(f"       = {format_number(-b - sqrt_disc)} / {format_number(2*a)}")
            steps.append(f"       = {format_number(x2)}")
            
            result = f"x = {format_number(x1)} أو x = {format_number(x2)}"
            
        elif discriminant == 0:
            steps.append("📐 **الخطوة 3: Δ = 0 → للمعادلة جذر مكرر (حل واحد)**")
            steps.append("   نطبق القانون: x = -b / 2a")
            
            x = -b / (2*a)
            steps.append(f"   x = {-format_number(b)} / {format_number(2*a)}")
            steps.append(f"   x = {format_number(x)}")
            
            result = f"x = {format_number(x)}"
            
        else:
            steps.append("📐 **الخطوة 3: Δ < 0 → للمعادلة جذران مركبان**")
            steps.append("   ليس للمعادلة حلول حقيقية")
            
            real = -b / (2*a)
            imag = math.sqrt(-discriminant) / (2*a)
            result = f"x = {format_number(real)} ± {format_number(imag)}i"
        
        steps.append("")
        steps.append(f"✅ **الإجابة النهائية:** {result}")
        
        return {
            "success": True,
            "steps": steps,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"خطأ في حل المعادلة التربيعية: {e}")
        return {
            "success": False,
            "error": str(e),
            "steps": [f"❌ حدث خطأ: {e}"],
            "result": None
        }

def solve_linear_with_steps(equation: str) -> dict:
    """حل معادلة خطية مع خطوات"""
    steps = []
    steps.append("📌 **السؤال:** " + equation)
    steps.append("")
    
    try:
        # تنظيف المعادلة
        clean_eq = equation.replace(' ', '')
        left, right = clean_eq.split('=')
        
        # تحويل 2x إلى 2*x
        left = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', left)
        
        # استخراج المعاملات
        from sympy import symbols, Eq, solve, sympify
        x = symbols('x')
        
        left_expr = sympify(left)
        right_expr = sympify(right)
        
        eq = Eq(left_expr, right_expr)
        solutions = solve(eq, x)
        
        if solutions:
            x_val = float(solutions[0])
            result = f"x = {format_number(x_val)}"
            
            steps.append("📐 **الخطوة 1: نقل الحدود**")
            steps.append(f"   {left} = {right}")
            steps.append("")
            steps.append("📐 **الخطوة 2: حل المعادلة**")
            steps.append(f"   x = {format_number(x_val)}")
            steps.append("")
            steps.append(f"✅ **الإجابة النهائية:** {result}")
        else:
            result = "لا يوجد حل"
            steps.append("❌ لا يوجد حل")
        
        return {
            "success": True,
            "steps": steps,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"خطأ في حل المعادلة الخطية: {e}")
        return {
            "success": False,
            "error": str(e),
            "steps": [f"❌ حدث خطأ: {e}"],
            "result": None
        }

def solve_absolute_with_steps(equation: str) -> dict:
    """حل معادلة قيمة مطلقة مع خطوات"""
    steps = []
    steps.append("📌 **السؤال:** " + equation)
    steps.append("")
    
    try:
        # استخراج التعبير والقيمة
        match = re.search(r'\|(.*?)\|\s*=\s*(.+)', equation)
        if not match:
            return {"success": False, "error": "صيغة غير صحيحة"}
        
        expr_inside = match.group(1).strip()
        value_str = match.group(2).strip()
        value = float(value_str)
        
        steps.append("📏 **قاعدة:** |تعبير| = قيمة ⇒ تعبير = قيمة أو تعبير = -قيمة")
        steps.append("")
        
        # استخراج معامل x والثابت
        clean_expr = expr_inside.replace(' ', '')
        x_coeff = 1.0
        constant = 0.0
        
        x_match = re.search(r'([+-]?\d*\.?\d*)\*?x', clean_expr)
        if x_match:
            coeff = x_match.group(1)
            x_coeff = 1.0 if coeff in ['', '+'] else -1.0 if coeff == '-' else float(coeff)
        
        const_match = re.search(r'([+-]?\d+\.?\d*)$', clean_expr.replace('x', ''))
        if const_match:
            constant = float(const_match.group(1))
        
        steps.append("📐 **الخطوة 1: كتابة الحالتين**")
        steps.append(f"   **الحالة الأولى:** {expr_inside} = {format_number(value)}")
        steps.append(f"   **الحالة الثانية:** {expr_inside} = -{format_number(value)}")
        steps.append("")
        
        # الحالة الأولى
        steps.append("📐 **الخطوة 2: حل الحالة الأولى**")
        steps.append(f"   {x_coeff}x + {constant} = {format_number(value)}")
        
        if constant >= 0:
            steps.append(f"   {x_coeff}x = {format_number(value)} - {format_number(constant)}")
        else:
            steps.append(f"   {x_coeff}x = {format_number(value)} + {format_number(-constant)}")
        
        right1 = value - constant
        steps.append(f"   {x_coeff}x = {format_number(right1)}")
        
        x1 = right1 / x_coeff
        steps.append(f"   x = {format_number(right1)} / {format_number(x_coeff)}")
        steps.append(f"   x₁ = {format_number(x1)}")
        steps.append("")
        
        # الحالة الثانية
        steps.append("📐 **الخطوة 3: حل الحالة الثانية**")
        steps.append(f"   {x_coeff}x + {constant} = -{format_number(value)}")
        
        if constant >= 0:
            steps.append(f"   {x_coeff}x = -{format_number(value)} - {format_number(constant)}")
        else:
            steps.append(f"   {x_coeff}x = -{format_number(value)} + {format_number(-constant)}")
        
        right2 = -value - constant
        steps.append(f"   {x_coeff}x = {format_number(right2)}")
        
        x2 = right2 / x_coeff
        steps.append(f"   x = {format_number(right2)} / {format_number(x_coeff)}")
        steps.append(f"   x₂ = {format_number(x2)}")
        steps.append("")
        
        result = f"x = {format_number(x1)} أو x = {format_number(x2)}"
        steps.append(f"✅ **الإجابة النهائية:** {result}")
        
        return {
            "success": True,
            "steps": steps,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"خطأ في حل معادلة القيمة المطلقة: {e}")
        return {
            "success": False,
            "error": str(e),
            "steps": [f"❌ حدث خطأ: {e}"],
            "result": None
        }

def solve_system_2x2_with_steps(eq1: str, eq2: str) -> dict:
    """حل نظام معادلتين مع خطوات"""
    steps = []
    steps.append("📌 **السؤال:** حل النظام التالي:")
    steps.append(f"   (1) {eq1}")
    steps.append(f"   (2) {eq2}")
    steps.append("")
    
    try:
        from sympy import symbols, Eq, solve
        x, y = symbols('x y')
        
        # تحليل المعادلات
        left1, right1 = eq1.split('=')
        left2, right2 = eq2.split('=')
        
        from sympy import sympify
        eq1_sym = Eq(sympify(left1), sympify(right1))
        eq2_sym = Eq(sympify(left2), sympify(right2))
        
        steps.append("📐 **الخطوة 1: نكتب النظام بالصورة القياسية**")
        steps.append("")
        
        # حل النظام
        solution = solve([eq1_sym, eq2_sym], [x, y])
        
        if solution:
            x_val = float(solution[x])
            y_val = float(solution[y])
            
            steps.append("📐 **الخطوة 2: نحل النظام باستخدام طريقة الحذف**")
            steps.append("")
            steps.append("📐 **الخطوة 3: نوجد قيمة x**")
            steps.append("📐 **الخطوة 4: نعوض لإيجاد قيمة y**")
            steps.append("")
            
            result = f"x = {format_number(x_val)}, y = {format_number(y_val)}"
            steps.append(f"✅ **الإجابة النهائية:** {result}")
        else:
            result = "النظام ليس له حل"
            steps.append("❌ النظام ليس له حل")
        
        return {
            "success": True,
            "steps": steps,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"خطأ في حل النظام: {e}")
        return {
            "success": False,
            "error": str(e),
            "steps": [f"❌ حدث خطأ: {e}"],
            "result": None
        }

def solve_with_steps(expression: str) -> dict:
    """الدالة الرئيسية - تحدد نوع المسألة وتوجهها للمعالج المناسب"""
    
    # 1. معادلات القيمة المطلقة
    if '|' in expression and '=' in expression:
        return solve_absolute_with_steps(expression)
    
    # 2. نظم المعادلات
    if expression.startswith('[') and expression.endswith(']') and ',' in expression:
        # استخراج المعادلتين
        inner = expression[1:-1].strip()
        if ',' in inner:
            eqs = [e.strip() for e in inner.split(',')]
            if len(eqs) == 2:
                return solve_system_2x2_with_steps(eqs[0], eqs[1])
    
    # 3. معادلات تربيعية
    if ('x²' in expression or 'x^2' in expression) and '=' in expression:
        return solve_quadratic_with_steps(expression)
    
    # 4. معادلات خطية
    if '=' in expression and 'x' in expression:
        return solve_linear_with_steps(expression)
    
    # 5. عمليات حسابية
    try:
        steps = []
        steps.append(f"📌 **العملية:** {expression}")
        steps.append("")
        
        result = calc.calculate(expression)
        
        steps.append(f"✅ **النتيجة:** {result}")
        
        return {
            "success": True,
            "steps": steps,
            "result": str(result)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "steps": [f"❌ حدث خطأ: {e}"],
            "result": None
        }
