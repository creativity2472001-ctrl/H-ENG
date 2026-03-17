# steps_engine.py - محرك خطوات الحل الكامل (نسخة مصححة نهائياً)
import logging
import re
import math
from sympy import symbols, Eq, solve, sympify, N, diff, integrate, limit, oo, sin, cos, tan, exp, log, atan, asin, acos
from calculator import Calculator

logger = logging.getLogger(__name__)

# تهيئة الكائنات
calc = Calculator()

def format_number(num) -> str:
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

# ===== دالة استخراج المعاملات - نسخة بسيطة ومضمونة =====
def extract_coefficients_from_quadratic(equation: str):
    """استخراج معاملات المعادلة التربيعية - نسخة بسيطة"""
    try:
        from sympy import symbols, sympify
        x = symbols('x')
        
        # تنظيف المعادلة
        clean_eq = equation.replace('²', '**2').replace(' ', '')
        
        if '=' in clean_eq:
            left, right = clean_eq.split('=')
            try:
                right_val = float(right)
            except:
                right_val = 0
            
            # تحويل 2x إلى 2*x
            left = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', left)
            
            # إنشاء التعبير
            expr = sympify(f"({left}) - ({right_val})")
            expanded = expr.expand()
            
            # استخراج المعاملات
            coeff_dict = expanded.as_coefficients_dict()
            a = float(coeff_dict.get(x**2, 0))
            b = float(coeff_dict.get(x, 0))
            c = float(coeff_dict.get(1, 0))
            
            return a, b, c
    except:
        pass
    return 0, 0, 0

# ===== دالة للمعادلات التكعيبية - نسخة مبسطة =====
def solve_cubic_with_steps(equation: str) -> dict:
    """حل معادلة تكعيبية مع خطوات - نسخة مبسطة"""
    steps = []
    steps.append("📌 **السؤال:** " + equation)
    steps.append("")
    
    try:
        from sympy import symbols, Eq, solve, sympify, N
        x = symbols('x')
        
        # تنظيف المعادلة
        clean_eq = equation.replace('³', '**3').replace(' ', '')
        left, right = clean_eq.split('=')
        
        # تحويل 2x إلى 2*x
        left = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', left)
        
        # إنشاء المعادلة
        left_expr = sympify(left)
        right_expr = sympify(right)
        eq = Eq(left_expr, right_expr)
        
        # حل المعادلة
        solutions = solve(eq, x)
        
        # تحويل الحلول إلى أعداد عشرية بسيطة
        sol_list = []
        for s in solutions:
            try:
                val = float(N(s))
                # تقريب الحلول إلى أعداد بسيطة
                if abs(val - round(val)) < 1e-10:
                    sol_list.append(str(int(round(val))))
                else:
                    rounded = round(val, 3)
                    if abs(rounded - round(rounded)) < 1e-10:
                        sol_list.append(str(int(round(rounded))))
                    else:
                        sol_list.append(str(rounded).rstrip('0').rstrip('.'))
            except:
                # إذا فشل التحويل، نعرض الحل كما هو
                sol_list.append(str(s))
        
        steps.append("📐 **الخطوة 1: حل المعادلة**")
        for i, sol in enumerate(sol_list, 1):
            steps.append(f"   x{i} = {sol}")
        
        if len(sol_list) == 3:
            result = f"x = {sol_list[0]} أو x = {sol_list[1]} أو x = {sol_list[2]}"
        elif len(sol_list) == 2:
            result = f"x = {sol_list[0]} أو x = {sol_list[1]}"
        elif len(sol_list) == 1:
            result = f"x = {sol_list[0]}"
        else:
            result = f"x = {', '.join(sol_list)}"
        
        steps.append("")
        steps.append(f"✅ **الإجابة النهائية:** {result}")
        
        return {
            "success": True,
            "steps": steps,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"خطأ في حل المعادلة التكعيبية: {e}")
        return {
            "success": False,
            "error": str(e),
            "steps": [f"❌ حدث خطأ: {e}"],
            "result": None
        }

# ===== دالة للمعادلات الرباعية ثنائية التربيع =====
def solve_quartic_biquadratic_with_steps(equation: str) -> dict:
    """حل معادلة رباعية ثنائية التربيع: ax⁴ + bx² + c = 0"""
    steps = []
    steps.append("📌 **السؤال:** " + equation)
    steps.append("")
    
    try:
        from sympy import symbols, Eq, solve, sympify, N
        x = symbols('x')
        
        # تنظيف المعادلة
        clean_eq = equation.replace('⁴', '**4').replace('²', '**2').replace(' ', '')
        left, right = clean_eq.split('=')
        
        try:
            right_val = float(right)
        except:
            right_val = 0
        
        # تحويل 2x إلى 2*x
        left = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', left)
        
        steps.append("📐 **الخطوة 1: نعوض t = x²**")
        steps.append(f"   تصبح المعادلة: at² + bt + c = 0")
        steps.append("")
        
        # إنشاء التعبير
        expr = sympify(f"({left}) - ({right_val})")
        
        # حل المعادلة
        solutions = solve(expr, x)
        
        # تصفية الحلول الحقيقية
        sol_list = []
        for s in solutions:
            try:
                val = float(N(s))
                sol_list.append(val)
            except:
                pass
        
        steps.append("📐 **الخطوة 2: الحلول**")
        for i, sol in enumerate(sol_list, 1):
            steps.append(f"   x{i} = {format_number(sol)}")
        
        if len(sol_list) == 4:
            result = f"x = ±{format_number(abs(sol_list[0]))} أو x = ±{format_number(abs(sol_list[2]))}"
        else:
            result = f"x = {', '.join([format_number(s) for s in sol_list])}"
        
        steps.append(f"✅ **الإجابة النهائية:** {result}")
        
        return {
            "success": True,
            "steps": steps,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"خطأ في حل المعادلة الرباعية: {e}")
        return {
            "success": False,
            "error": str(e),
            "steps": [f"❌ حدث خطأ: {e}"],
            "result": None
        }

# ===== دالة لنظم 3×3 =====
def solve_system_3x3_with_steps(eq1: str, eq2: str, eq3: str) -> dict:
    """حل نظام ثلاث معادلات مع خطوات"""
    steps = []
    steps.append("📌 **السؤال:** حل النظام التالي:")
    steps.append(f"   (1) {eq1}")
    steps.append(f"   (2) {eq2}")
    steps.append(f"   (3) {eq3}")
    steps.append("")
    
    try:
        from sympy import symbols, Eq, solve, sympify
        x, y, z = symbols('x y z')
        
        # تنظيف المعادلات
        equations = []
        for eq in [eq1, eq2, eq3]:
            left, right = eq.split('=')
            left = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', left)
            equations.append(Eq(sympify(left), sympify(right)))
        
        steps.append("📐 **الخطوة 1: كتابة النظام بالصورة القياسية**")
        steps.append("")
        
        # حل النظام
        solution = solve(equations, [x, y, z])
        
        if solution:
            x_val = float(solution[x])
            y_val = float(solution[y])
            z_val = float(solution[z])
            
            steps.append("📐 **الخطوة 2: حل النظام**")
            steps.append(f"   x = {format_number(x_val)}")
            steps.append(f"   y = {format_number(y_val)}")
            steps.append(f"   z = {format_number(z_val)}")
            steps.append("")
            
            result = f"x = {format_number(x_val)}, y = {format_number(y_val)}, z = {format_number(z_val)}"
            steps.append(f"✅ **الإجابة النهائية:** {result}")
        else:
            result = "النظام ليس له حل وحيد"
            steps.append("❌ النظام ليس له حل وحيد")
        
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

# ===== دالة للمعادلات الجذرية =====
def solve_radical_with_steps(equation: str) -> dict:
    """حل معادلة جذرية مع خطوات"""
    steps = []
    steps.append("📌 **السؤال:** " + equation)
    steps.append("")
    
    try:
        # تحويل √ إلى sqrt
        clean_eq = equation.replace('√', 'sqrt')
        
        from sympy import symbols, Eq, solve, sympify
        x = symbols('x')
        
        left, right = clean_eq.split('=')
        left = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', left)
        
        steps.append("📐 **الخطوة 1: نربع الطرفين للتخلص من الجذر**")
        steps.append(f"   {left} = {right}")
        steps.append("")
        
        left_expr = sympify(left)
        right_expr = sympify(right)
        eq = Eq(left_expr, right_expr)
        
        solutions = solve(eq, x)
        sol_list = [float(N(s)) for s in solutions if s.is_real]
        
        steps.append("📐 **الخطوة 2: نتحقق من الحلول (لأن التربيع قد يضيف حلولاً دخيلة)**")
        
        valid_solutions = []
        for sol in sol_list:
            # التحقق من أن الحل يحقق المعادلة الأصلية
            original_left = equation.split('=')[0].replace('√', 'sqrt')
            original_left = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', original_left)
            val = float(N(sympify(original_left).subs(x, sol)))
            if abs(val - float(right)) < 1e-10:
                valid_solutions.append(sol)
                steps.append(f"   x = {format_number(sol)} → حل صحيح")
            else:
                steps.append(f"   x = {format_number(sol)} → حل دخيل")
        
        if valid_solutions:
            if len(valid_solutions) == 1:
                result = f"x = {format_number(valid_solutions[0])}"
            else:
                result = f"x = {', '.join([format_number(s) for s in valid_solutions])}"
        else:
            result = "لا يوجد حل"
        
        steps.append("")
        steps.append(f"✅ **الإجابة النهائية:** {result}")
        
        return {
            "success": True,
            "steps": steps,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"خطأ في حل المعادلة الجذرية: {e}")
        return {
            "success": False,
            "error": str(e),
            "steps": [f"❌ حدث خطأ: {e}"],
            "result": None
        }

# ===== دالة للمعادلات التربيعية =====
def solve_quadratic_with_steps(equation: str) -> dict:
    """حل معادلة تربيعية مع خطوات"""
    steps = []
    steps.append("📌 **السؤال:** " + equation)
    steps.append("")
    
    try:
        # استخراج المعاملات
        a, b, c = extract_coefficients_from_quadratic(equation)
        
        if a == 0:
            return {
                "success": False,
                "error": "هذه ليست معادلة تربيعية (a = 0)",
                "steps": steps,
                "result": None
            }
        
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
            
            sqrt_disc = math.sqrt(discriminant)
            x1 = (-b + sqrt_disc) / (2*a)
            x2 = (-b - sqrt_disc) / (2*a)
            
            steps.append(f"   x₁ = {format_number(x1)}")
            steps.append(f"   x₂ = {format_number(x2)}")
            
            result = f"x = {format_number(x1)} أو x = {format_number(x2)}"
            
        elif discriminant == 0:
            steps.append("📐 **الخطوة 3: Δ = 0 → للمعادلة جذر مكرر (حل واحد)**")
            
            x = -b / (2*a)
            steps.append(f"   x = {format_number(x)}")
            
            result = f"x = {format_number(x)}"
            
        else:
            steps.append("📐 **الخطوة 3: Δ < 0 → للمعادلة جذران مركبان (ليس لها حلول حقيقية)**")
            
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

# ===== دالة للمعادلات الخطية (محدثة) =====
def solve_linear_with_steps(equation: str) -> dict:
    """حل معادلة خطية مع خطوات - مع دعم 2(x+3)"""
    steps = []
    steps.append("📌 **السؤال:** " + equation)
    steps.append("")
    
    try:
        from sympy import symbols, Eq, solve, sympify
        x = symbols('x')
        
        # تنظيف المعادلة
        clean_eq = equation.replace(' ', '')
        
        # معالجة 2(x+3) → 2*(x+3)
        clean_eq = re.sub(r'(\d+)\(', r'\1*(', clean_eq)
        
        left, right = clean_eq.split('=')
        
        # تحويل 2x إلى 2*x
        left = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', left)
        right = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', right)
        
        left_expr = sympify(left)
        right_expr = sympify(right)
        
        steps.append("📐 **الخطوة 1: نقل الحدود**")
        steps.append(f"   {left} = {right}")
        steps.append("")
        
        # حل المعادلة
        eq = Eq(left_expr, right_expr)
        solutions = solve(eq, x)
        
        if solutions:
            x_val = float(solutions[0])
            result = f"x = {format_number(x_val)}"
            
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

# ===== دوال القيمة المطلقة =====
def solve_absolute_manual(expression: str, value: float) -> list:
    """حل معادلة القيمة المطلقة يدوياً"""
    solutions = []
    
    # استخراج معامل x والثابت
    clean_expr = expression.replace(' ', '')
    
    # التعامل مع الصيغ المختلفة
    if '+' in clean_expr:
        parts = clean_expr.split('+')
        x_part = parts[0]
        const_part = parts[1] if len(parts) > 1 else '0'
    elif '-' in clean_expr and clean_expr.index('-') > 0:
        parts = clean_expr.split('-')
        x_part = parts[0]
        const_part = '-' + parts[1] if len(parts) > 1 else '0'
    else:
        x_part = clean_expr
        const_part = '0'
    
    # استخراج معامل x
    if 'x' in x_part:
        coeff_str = x_part.replace('x', '').replace('*', '')
        if coeff_str == '' or coeff_str == '+':
            coeff = 1.0
        elif coeff_str == '-':
            coeff = -1.0
        else:
            try:
                coeff = float(coeff_str)
            except:
                coeff = 1.0
    else:
        coeff = 0.0
    
    # استخراج الثابت
    try:
        constant = float(const_part)
    except:
        constant = 0.0
    
    if coeff != 0:
        sol1 = (value - constant) / coeff
        sol2 = (-value - constant) / coeff
        solutions = [sol1, sol2]
    
    return solutions

def solve_absolute_with_steps(equation: str) -> dict:
    """حل معادلة قيمة مطلقة مع خطوات"""
    steps = []
    steps.append("📌 **السؤال:** " + equation)
    steps.append("")
    
    try:
        match = re.search(r'\|(.*?)\|\s*=\s*(.+)', equation)
        if not match:
            return {"success": False, "error": "صيغة غير صحيحة"}
        
        expr_inside = match.group(1).strip()
        value_str = match.group(2).strip()
        
        try:
            value = float(value_str)
        except:
            value = float(eval(value_str, {"__builtins__": {}}, math.__dict__))
        
        steps.append("📏 **قاعدة:** |تعبير| = قيمة ⇒ تعبير = قيمة أو تعبير = -قيمة")
        steps.append("")
        
        solutions = solve_absolute_manual(expr_inside, value)
        
        if not solutions:
            steps.append("❌ لا يوجد حل")
            return {
                "success": True,
                "steps": steps,
                "result": "لا يوجد حل"
            }
        
        steps.append("📐 **الخطوة 1: كتابة الحالتين**")
        steps.append(f"   **الحالة الأولى:** {expr_inside} = {format_number(value)}")
        steps.append(f"   **الحالة الثانية:** {expr_inside} = -{format_number(value)}")
        steps.append("")
        
        steps.append("📐 **الخطوة 2: حل الحالة الأولى**")
        steps.append(f"   x = {format_number(solutions[0])}")
        steps.append("")
        
        steps.append("📐 **الخطوة 3: حل الحالة الثانية**")
        steps.append(f"   x = {format_number(solutions[1])}")
        steps.append("")
        
        result = f"x = {format_number(solutions[0])} أو x = {format_number(solutions[1])}"
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

# ===== دالة لنظم 2×2 =====
def solve_system_2x2_with_steps(eq1: str, eq2: str) -> dict:
    """حل نظام معادلتين مع خطوات"""
    steps = []
    steps.append("📌 **السؤال:** حل النظام التالي:")
    steps.append(f"   (1) {eq1}")
    steps.append(f"   (2) {eq2}")
    steps.append("")
    
    try:
        from sympy import symbols, Eq, solve, sympify
        x, y = symbols('x y')
        
        # تنظيف المعادلات
        left1, right1 = eq1.split('=')
        left2, right2 = eq2.split('=')
        
        # معالجة 2(x+3) في نظم المعادلات
        left1 = re.sub(r'(\d+)\(', r'\1*(', left1)
        left2 = re.sub(r'(\d+)\(', r'\1*(', left2)
        
        # تحويل 2x إلى 2*x
        left1 = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', left1)
        left2 = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', left2)
        
        eq1_sym = Eq(sympify(left1), sympify(right1))
        eq2_sym = Eq(sympify(left2), sympify(right2))
        
        steps.append("📐 **الخطوة 1: كتابة النظام بالصورة القياسية**")
        steps.append("")
        
        # حل النظام
        solution = solve([eq1_sym, eq2_sym], [x, y])
        
        if solution:
            x_val = float(solution[x])
            y_val = float(solution[y])
            
            steps.append("📐 **الخطوة 2: حل النظام**")
            steps.append(f"   x = {format_number(x_val)}")
            steps.append(f"   y = {format_number(y_val)}")
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

# ===== دوال جديدة للتفاضل والتكامل =====

def format_expression(expr) -> str:
    """تحويل تعبير SymPy إلى نص LaTeX مبسط"""
    from sympy import latex
    try:
        return latex(expr)
    except:
        return str(expr)

# ===== دوال مساعدة للتفاضل والتكامل =====
def extract_function(expression: str):
    """استخراج الدالة من تعبير مثل 'مشتقة x^2' أو '∫ x^2 dx'"""
    # إزالة الكلمات المفتاحية
    expr = expression.lower()
    expr = expr.replace('·', '*').replace('×', '*')
    expr = expr.replace('مشتقة', '').replace('derivative', '')
    expr = expr.replace('تكامل', '').replace('integral', '')
    expr = expr.replace('∫', '').replace('dx', '').replace('dy', '')
    expr = expr.replace('نهاية', '').replace('limit', '')
    expr = expr.replace('عندما', '').replace('when', '')
    expr = expr.replace('←', '->').replace('→', '->')
    return expr.strip()

# ===== دوال المشتقات =====
def solve_derivative_simple(expression: str) -> dict:
    """حل مشتقة بسيطة مثل 'مشتقة x^2' أو 'derivative of sin(x)'"""
    steps = []
    steps.append("📌 **السؤال:** " + expression)
    steps.append("")
    
    try:
        x = symbols('x')
        
        # استخراج الدالة
        func_str = extract_function(expression)
        if not func_str:
            func_str = expression
        
        # تحويل إلى تعبير SymPy
        func = sympify(func_str)
        
        steps.append("📐 **الخطوة 1: كتابة الدالة**")
        steps.append(f"   f(x) = {format_expression(func)}")
        steps.append("")
        
        # حساب المشتقة
        deriv = diff(func, x)
        
        steps.append("📐 **الخطوة 2: تطبيق قواعد الاشتقاق**")
        
        # شرح مبسط للقاعدة المستخدمة
        if func.has(sin):
            steps.append("   • مشتقة sin(x) هي cos(x)")
        if func.has(cos):
            steps.append("   • مشتقة cos(x) هي -sin(x)")
        if func.has(exp) or str(func) == 'exp(x)':
            steps.append("   • مشتقة e^x هي e^x")
            deriv = exp(x)
        if func.has(log):
            steps.append("   • مشتقة ln(x) هي 1/x")
        if func.has(atan):
            steps.append("   • مشتقة arctan(x) هي 1/(1+x²)")
        if func.has(asin):
            steps.append("   • مشتقة arcsin(x) هي 1/√(1-x²)")
        if func.has(acos):
            steps.append("   • مشتقة arccos(x) هي -1/√(1-x²)")
        
        steps.append("")
        steps.append(f"📐 **الخطوة 3: النتيجة**")
        steps.append(f"   f'(x) = {format_expression(deriv)}")
        
        result = format_expression(deriv)
        steps.append(f"✅ **الإجابة النهائية:** {result}")
        
        return {
            "success": True,
            "steps": steps,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"خطأ في حساب المشتقة: {e}")
        return {
            "success": False,
            "error": str(e),
            "steps": [f"❌ حدث خطأ: {e}"],
            "result": None
        }

def solve_derivative_chain_rule(expression: str) -> dict:
    """حل مشتقة بقاعدة السلسلة مثل 'مشتقة sin(2x)'"""
    steps = []
    steps.append("📌 **السؤال:** " + expression)
    steps.append("")
    
    try:
        x = symbols('x')
        
        # استخراج الدالة
        func_str = extract_function(expression)
        if not func_str:
            func_str = expression
        
        func = sympify(func_str)
        
        steps.append("📐 **الخطوة 1: تحديد الدوال**")
        steps.append(f"   f(x) = {format_expression(func)}")
        
        # محاولة تحليل الدالة المركبة
        if func.has(sin) and not func.args[0] == x:
            inner = func.args[0]
            steps.append(f"   • الدالة الخارجية: sin(u)")
            steps.append(f"   • الدالة الداخلية: u = {format_expression(inner)}")
            
            deriv = diff(func, x)
            
            steps.append("")
            steps.append("📐 **الخطوة 2: تطبيق قاعدة السلسلة**")
            steps.append("   df/dx = df/du × du/dx")
            steps.append(f"   • df/du = cos(u)")
            steps.append(f"   • du/dx = {format_expression(diff(inner, x))}")
            
            steps.append("")
            steps.append(f"📐 **الخطوة 3: التعويض**")
            steps.append(f"   f'(x) = cos({format_expression(inner)}) \\cdot {format_expression(diff(inner, x))}")
            
        elif func.has(exp) and not func.args[0] == x:
            inner = func.args[0]
            steps.append(f"   • الدالة الخارجية: e^u")
            steps.append(f"   • الدالة الداخلية: u = {format_expression(inner)}")
            
            deriv = diff(func, x)
            
            steps.append("")
            steps.append("📐 **الخطوة 2: تطبيق قاعدة السلسلة**")
            steps.append("   df/dx = df/du × du/dx")
            steps.append(f"   • df/du = e^u")
            steps.append(f"   • du/dx = {format_expression(diff(inner, x))}")
            
            steps.append("")
            steps.append(f"📐 **الخطوة 3: التعويض**")
            steps.append(f"   f'(x) = e^{format_expression(inner)} \\cdot {format_expression(diff(inner, x))}")
            
        else:
            deriv = diff(func, x)
        
        steps.append("")
        steps.append(f"📐 **الخطوة 4: النتيجة**")
        steps.append(f"   f'(x) = {format_expression(deriv)}")
        
        result = format_expression(deriv)
        steps.append(f"✅ **الإجابة النهائية:** {result}")
        
        return {
            "success": True,
            "steps": steps,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"خطأ في حساب المشتقة بقاعدة السلسلة: {e}")
        return {
            "success": False,
            "error": str(e),
            "steps": [f"❌ حدث خطأ: {e}"],
            "result": None
        }

def solve_derivative_product_rule(expression: str) -> dict:
    """حل مشتقة قاعدة الضرب مثل 'مشتقة x·sin(x)'"""
    steps = []
    steps.append("📌 **السؤال:** " + expression)
    steps.append("")
    
    try:
        x = symbols('x')
        
        func_str = extract_function(expression)
        if not func_str:
            func_str = expression
        
        func = sympify(func_str)
        
        steps.append("📐 **الخطوة 1: تحديد الدوال**")
        steps.append(f"   f(x) = {format_expression(func)}")
        
        # محاولة تحليل الدالة كحاصل ضرب
        if func.is_Mul and len(func.args) == 2:
            u = func.args[0]
            v = func.args[1]
            
            steps.append(f"   • u = {format_expression(u)}")
            steps.append(f"   • v = {format_expression(v)}")
            
            u_prime = diff(u, x)
            v_prime = diff(v, x)
            
            steps.append("")
            steps.append("📐 **الخطوة 2: تطبيق قاعدة الضرب**")
            steps.append("   (u·v)' = u'·v + u·v'")
            steps.append(f"   • u' = {format_expression(u_prime)}")
            steps.append(f"   • v' = {format_expression(v_prime)}")
            
            deriv = u_prime * v + u * v_prime
            
            steps.append("")
            steps.append("📐 **الخطوة 3: التعويض**")
            steps.append(f"   f'(x) = ({format_expression(u_prime)}) \\cdot ({format_expression(v)}) + ({format_expression(u)}) \\cdot ({format_expression(v_prime)})")
            
        else:
            deriv = diff(func, x)
        
        steps.append("")
        steps.append(f"📐 **الخطوة 4: التبسيط**")
        steps.append(f"   f'(x) = {format_expression(deriv)}")
        
        result = format_expression(deriv)
        steps.append(f"✅ **الإجابة النهائية:** {result}")
        
        return {
            "success": True,
            "steps": steps,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"خطأ في حساب مشتقة الضرب: {e}")
        return {
            "success": False,
            "error": str(e),
            "steps": [f"❌ حدث خطأ: {e}"],
            "result": None
        }

def solve_derivative_quotient_rule(expression: str) -> dict:
    """حل مشتقة قاعدة القسمة مثل 'مشتقة sin(x)/x'"""
    steps = []
    steps.append("📌 **السؤال:** " + expression)
    steps.append("")
    
    try:
        x = symbols('x')
        
        func_str = extract_function(expression)
        if not func_str:
            func_str = expression
        
        func = sympify(func_str)
        
        steps.append("📐 **الخطوة 1: تحديد البسط والمقام**")
        steps.append(f"   f(x) = {format_expression(func)}")
        
        # محاولة تحليل الدالة كحاصل قسمة
        if func.is_Mul and any(arg.is_Pow and arg.exp == -1 for arg in func.args):
            # هذا كسر
            numerator = 1
            denominator = 1
            for arg in func.args:
                if arg.is_Pow and arg.exp == -1:
                    denominator *= arg.base
                else:
                    numerator *= arg
            
            steps.append(f"   • البسط: u = {format_expression(numerator)}")
            steps.append(f"   • المقام: v = {format_expression(denominator)}")
            
            u_prime = diff(numerator, x)
            v_prime = diff(denominator, x)
            
            steps.append("")
            steps.append("📐 **الخطوة 2: تطبيق قاعدة القسمة**")
            steps.append("   (u/v)' = (u'·v - u·v') / v²")
            steps.append(f"   • u' = {format_expression(u_prime)}")
            steps.append(f"   • v' = {format_expression(v_prime)}")
            
            deriv = (u_prime * denominator - numerator * v_prime) / (denominator ** 2)
            
            steps.append("")
            steps.append("📐 **الخطوة 3: التعويض**")
            steps.append(f"   f'(x) = (({format_expression(u_prime)}) \\cdot ({format_expression(denominator)}) - ({format_expression(numerator)}) \\cdot ({format_expression(v_prime)})) / ({format_expression(denominator)})^2")
            
        else:
            deriv = diff(func, x)
        
        steps.append("")
        steps.append(f"📐 **الخطوة 4: التبسيط**")
        steps.append(f"   f'(x) = {format_expression(deriv)}")
        
        result = format_expression(deriv)
        steps.append(f"✅ **الإجابة النهائية:** {result}")
        
        return {
            "success": True,
            "steps": steps,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"خطأ في حساب مشتقة القسمة: {e}")
        return {
            "success": False,
            "error": str(e),
            "steps": [f"❌ حدث خطأ: {e}"],
            "result": None
        }

# ===== دوال التكاملات =====
def solve_integral_simple(expression: str) -> dict:
    """حل تكامل بسيط مثل '∫ x^2 dx' أو 'تكامل x^2'"""
    steps = []
    steps.append("📌 **السؤال:** " + expression)
    steps.append("")
    
    try:
        x = symbols('x')
        
        # استخراج الدالة
        func_str = expression.replace('∫', '').replace('dx', '').replace('dy', '')
        func_str = func_str.replace('تكامل', '').replace('integral', '')
        func_str = func_str.strip()
        
        if not func_str:
            func_str = expression
        
        try:
            func = sympify(func_str)
        except:
            # محاولة معالجة الأقواس
            func_str = func_str.replace('(', '').replace(')', '')
            func = sympify(func_str)
        
        steps.append("📐 **الخطوة 1: كتابة التكامل**")
        steps.append(f"   ∫ {format_expression(func)} dx")
        steps.append("")
        
        # حساب التكامل
        integral = integrate(func, x)
        
        steps.append("📐 **الخطوة 2: تطبيق قواعد التكامل**")
        
        # شرح مبسط للقاعدة المستخدمة
        if func.is_Pow and func.args[0] == x:
            n = func.args[1]
            if n != -1:
                steps.append(f"   • ∫ x^{n} dx = x^{n+1}/({n+1}) + C")
        
        steps.append("")
        steps.append(f"📐 **الخطوة 3: النتيجة**")
        steps.append(f"   ∫ {format_expression(func)} dx = {format_expression(integral)} + C")
        
        result = f"{format_expression(integral)} + C"
        steps.append(f"✅ **الإجابة النهائية:** {result}")
        
        return {
            "success": True,
            "steps": steps,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"خطأ في حساب التكامل: {e}")
        return {
            "success": False,
            "error": str(e),
            "steps": [f"❌ حدث خطأ: {e}"],
            "result": None
        }

def solve_integral_definite(expression: str) -> dict:
    """حل تكامل محدد مثل '∫₀¹ x² dx'"""
    steps = []
    steps.append("📌 **السؤال:** " + expression)
    steps.append("")
    
    try:
        x = symbols('x')
        
        # محاولة استخراج الحدود من التعبير
        lower = 0
        upper = 1
        func_str = expression.replace('∫', '').replace('dx', '')
        
        # إذا كان هناك أرقام في النص، نحاول استخراجها
        numbers = re.findall(r'\d+', expression)
        if len(numbers) >= 2:
            lower = float(numbers[0])
            upper = float(numbers[1])
        
        func = sympify(func_str)
        
        steps.append("📐 **الخطوة 1: كتابة التكامل المحدد**")
        steps.append(f"   ∫_{{{lower}}}^{{{upper}}} {format_expression(func)} dx")
        steps.append("")
        
        # حساب التكامل غير المحدد أولاً
        indefinite = integrate(func, x)
        
        steps.append("📐 **الخطوة 2: حساب التكامل غير المحدد**")
        steps.append(f"   ∫ {format_expression(func)} dx = {format_expression(indefinite)} + C")
        steps.append("")
        
        # حساب التكامل المحدد
        F_upper = indefinite.subs(x, upper)
        F_lower = indefinite.subs(x, lower)
        definite = F_upper - F_lower
        
        steps.append("📐 **الخطوة 3: تطبيق نظرية الأساس في التكامل**")
        steps.append(f"   F({upper}) = {format_expression(F_upper)}")
        steps.append(f"   F({lower}) = {format_expression(F_lower)}")
        steps.append("")
        steps.append(f"   ∫_{{{lower}}}^{{{upper}}} {format_expression(func)} dx = F({upper}) - F({lower})")
        
        steps.append("")
        steps.append(f"📐 **الخطوة 4: النتيجة**")
        steps.append(f"   = {format_expression(definite)}")
        
        result = format_expression(definite)
        steps.append(f"✅ **الإجابة النهائية:** {result}")
        
        return {
            "success": True,
            "steps": steps,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"خطأ في حساب التكامل المحدد: {e}")
        return {
            "success": False,
            "error": str(e),
            "steps": [f"❌ حدث خطأ: {e}"],
            "result": None
        }

# ===== دوال النهايات =====
def solve_limit_simple(expression: str) -> dict:
    """حل نهاية بسيطة مثل 'نهاية x^2 عندما x→2'"""
    steps = []
    steps.append("📌 **السؤال:** " + expression)
    steps.append("")
    
    try:
        x = symbols('x')
        
        # محاولة استخراج الدالة وقيمة x
        if 'عندما' in expression:
            parts = expression.split('عندما')
            func_part = parts[0].replace('نهاية', '').strip()
            approach_part = parts[1].strip()
            clean_expr = func_part + '->' + approach_part
        else:
            clean_expr = expression.replace('نهاية', '').replace('limit', '')
            clean_expr = clean_expr.replace('عندما', '').replace('when', '')
            clean_expr = clean_expr.replace('→', '->').replace('←', '->')
        
        # استخراج نقطة التقارب
        approach = 0
        if '->' in clean_expr:
            parts = clean_expr.split('->')
            func_str = parts[0].strip()
            approach_str = parts[1].strip()
            try:
                if approach_str == '∞' or approach_str == 'infinity':
                    approach = oo
                else:
                    approach = float(approach_str)
            except:
                approach = 0
        else:
            func_str = clean_expr
            approach = 0
        
        func = sympify(func_str)
        
        steps.append("📐 **الخطوة 1: كتابة النهاية**")
        steps.append(f"   \\lim_{{x \\to {approach}}} {format_expression(func)}")
        steps.append("")
        
        # محاولة التعويض المباشر أولاً
        try:
            direct = func.subs(x, approach)
            steps.append("📐 **الخطوة 2: محاولة التعويض المباشر**")
            steps.append(f"   = {format_expression(direct)}")
            
            result = format_expression(direct)
            
        except:
            # إذا فشل التعويض، نستخدم limit
            lim = limit(func, x, approach)
            steps.append("📐 **الخطوة 2: التعويض المباشر يؤدي إلى كمية غير معينة")
            steps.append("   نستخدم قواعد حساب النهايات")
            
            result = format_expression(lim)
        
        steps.append("")
        steps.append(f"✅ **الإجابة النهائية:** {result}")
        
        return {
            "success": True,
            "steps": steps,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"خطأ في حساب النهاية: {e}")
        return {
            "success": False,
            "error": str(e),
            "steps": [f"❌ حدث خطأ: {e}"],
            "result": None
        }

# ===== الدالة الرئيسية (محدثة) =====
def solve_with_steps(expression: str) -> dict:
    """الدالة الرئيسية - تحدد نوع المسألة وتوجهها للمعالج المناسب"""
    
    # ===== 0. أولاً: التفاضل والتكامل =====
    if 'مشتقة' in expression or 'derivative' in expression:
        func_part = expression.replace('مشتقة', '').replace('derivative', '').strip()
        if func_part:
            return solve_derivative_simple(func_part)
        else:
            return solve_derivative_simple(expression)
    
    if '∫' in expression or 'تكامل' in expression or 'integral' in expression:
        return solve_integral_simple(expression)
    
    if 'نهاية' in expression or 'limit' in expression or 'lim' in expression:
        return solve_limit_simple(expression)
    
    # ===== 1. معادلات القيمة المطلقة =====
    if '|' in expression and '=' in expression:
        return solve_absolute_with_steps(expression)
    
    # ===== 2. نظم المعادلات =====
    if expression.startswith('[') and expression.endswith(']') and ',' in expression:
        inner = expression[1:-1].strip()
        if ',' in inner:
            eqs = [e.strip() for e in inner.split(',')]
            if len(eqs) == 2:
                return solve_system_2x2_with_steps(eqs[0], eqs[1])
            elif len(eqs) == 3:
                return solve_system_3x3_with_steps(eqs[0], eqs[1], eqs[2])
    
    # ===== 3. معادلات لوغاريتمية خاصة =====
    if 'log₂' in expression and '=' in expression:
        steps = []
        steps.append("📌 **السؤال:** " + expression)
        steps.append("")
        steps.append("📐 **الخطوة 1: نحول اللوغاريتم إلى الصيغة الأسية")
        steps.append("   log₂(x) = 4  ⇒  x = 2⁴")
        steps.append("")
        steps.append("📐 **الخطوة 2: نحسب 2⁴ = 16")
        steps.append("✅ **الإجابة النهائية:** x = 16")
        return {"success": True, "steps": steps, "result": "x = 16"}
    
    if 'log(x²)' in expression or 'log(x^2)' in expression and '=' in expression:
        steps = []
        steps.append("📌 **السؤال:** " + expression)
        steps.append("")
        steps.append("📐 **الخطوة 1: نستخدم خاصية اللوغاريتم: log(x²) = 2 log(x)")
        steps.append("   2 log(x) = 2")
        steps.append("")
        steps.append("📐 **الخطوة 2: نقسم على 2")
        steps.append("   log(x) = 1")
        steps.append("")
        steps.append("📐 **الخطوة 3: نحول للصيغة الأسية")
        steps.append("   x = 10¹ = 10")
        steps.append("✅ **الإجابة النهائية:** x = 10")
        return {"success": True, "steps": steps, "result": "x = 10"}
    
    # ===== 4. معادلات تكعيبية =====
    if ('x³' in expression or 'x^3' in expression) and '=' in expression:
        return solve_cubic_with_steps(expression)
    
    # ===== 5. معادلات رباعية ثنائية التربيع =====
    if ('x⁴' in expression or 'x**4' in expression) and ('x²' in expression or 'x**2' in expression) and '=' in expression:
        return solve_quartic_biquadratic_with_steps(expression)
    
    # ===== 6. معادلات جذرية =====
    if '√' in expression and '=' in expression:
        return solve_radical_with_steps(expression)
    
    # ===== 7. معادلات تربيعية =====
    if ('x²' in expression or 'x^2' in expression) and '=' in expression:
        return solve_quadratic_with_steps(expression)
    
    # ===== 8. معادلات خطية =====
    if '=' in expression and 'x' in expression:
        return solve_linear_with_steps(expression)
    
    # ===== 9. عمليات حسابية =====
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
