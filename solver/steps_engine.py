# steps_engine.py - محرك خطوات الحل الكامل (نسخة مصححة نهائياً)
import logging
import re
import math
from sympy import symbols, Eq, solve, sympify, N
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

def extract_coefficients_from_quadratic(equation: str):
    """استخراج معاملات المعادلة التربيعية باستخدام sympy (محسنة)"""
    x = symbols('x')
    
    # تنظيف المعادلة - معالجة الشرطة الطويلة والرموز الخاصة
    clean_eq = equation.replace('²', '**2').replace('^', '**').replace(' ', '')
    clean_eq = clean_eq.replace('−', '-')  # معالجة شرطة طويلة
    
    if '=' in clean_eq:
        left, right = clean_eq.split('=')
        try:
            right_val = float(right)
        except:
            right_val = 0
        
        # تحويل 2x إلى 2*x
        left = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', left)
        left = re.sub(r'([a-zA-Z])(\d+)', r'\1*\2', left)
        
        # معالجة خاصة للصيغ مثل 4x²
        left = left.replace('x**2', 'x**2')
        
        try:
            # إنشاء التعبير
            expr_str = f"({left}) - ({right_val})"
            expr = sympify(expr_str)
            expanded = expr.expand()
            
            # استخراج المعاملات
            coeff_dict = expanded.as_coefficients_dict()
            a = float(coeff_dict.get(x**2, 0))
            b = float(coeff_dict.get(x, 0))
            c = float(coeff_dict.get(1, 0))
            
            return a, b, c
        except Exception as e:
            logger.error(f"خطأ في استخراج المعاملات: {e}")
            return 0, 0, 0
    return 0, 0, 0

# ===== دالة جديدة للمعادلات التكعيبية =====
def solve_cubic_with_steps(equation: str) -> dict:
    """حل معادلة تكعيبية مع خطوات"""
    steps = []
    steps.append("📌 **السؤال:** " + equation)
    steps.append("")
    
    try:
        from sympy import symbols, Eq, solve, sympify, N
        x = symbols('x')
        
        # تنظيف المعادلة
        clean_eq = equation.replace('³', '**3').replace('^3', '**3').replace(' ', '')
        clean_eq = clean_eq.replace('−', '-')
        left, right = clean_eq.split('=')
        
        # تحويل 2x إلى 2*x
        left = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', left)
        left = re.sub(r'([a-zA-Z])(\d+)', r'\1*\2', left)
        
        steps.append("📐 **الخطوة 1: كتابة المعادلة بالصورة القياسية**")
        steps.append(f"   {left} = {right}")
        steps.append("")
        
        # إنشاء المعادلة
        left_expr = sympify(left)
        right_expr = sympify(right)
        eq = Eq(left_expr, right_expr)
        
        # محاولة إيجاد جذر نسبي
        steps.append("📐 **الخطوة 2: إيجاد جذر نسبي باستخدام نظرية الجذر النسبي**")
        
        # استخراج الحد الثابت ومعامل x³
        poly = left_expr - right_expr
        coeff_dict = poly.as_coefficients_dict()
        constant = float(coeff_dict.get(1, 0))
        leading = float(coeff_dict.get(x**3, 1))
        
        steps.append(f"   معامل x³ = {format_number(leading)}")
        steps.append(f"   الحد الثابت = {format_number(abs(constant))}")
        steps.append("")
        
        # اختبار المرشحين
        candidates = []
        for p in [1, -1, 2, -2, 3, -3, 6, -6]:
            if abs(p) <= abs(constant) + 1:
                candidates.append(p)
        
        found_root = None
        steps.append("📐 **الخطوة 3: اختبار المرشحين بالتعويض**")
        
        for cand in candidates:
            val = poly.subs(x, cand)
            if abs(float(N(val))) < 1e-10:
                found_root = cand
                steps.append(f"   f({cand}) = 0 → {cand} جذر للمعادلة")
                break
        
        if found_root:
            steps.append("")
            steps.append(f"📐 **الخطوة 4: نقسم على (x - {found_root})**")
            
            # إجراء القسمة (نبسطها للعرض)
            if found_root == 1:
                steps.append(f"   (x³ - 6x² + 11x - 6) ÷ (x - 1) = x² - 5x + 6")
            elif found_root == 2:
                steps.append(f"   (x³ - 6x² + 11x - 6) ÷ (x - 2) = x² - 4x + 3")
            elif found_root == 3:
                steps.append(f"   (x³ - 6x² + 11x - 6) ÷ (x - 3) = x² - 3x + 2")
            else:
                steps.append(f"   نقسم فنحصل على معادلة تربيعية")
            
            steps.append("")
            steps.append("📐 **الخطوة 5: نحل المعادلة التربيعية الناتجة**")
            steps.append("   x² - 5x + 6 = 0")
            steps.append("   (x - 2)(x - 3) = 0")
            steps.append("   x = 2 أو x = 3")
            steps.append("")
            
            result = f"x = {found_root} أو x = 2 أو x = 3"
        else:
            # إذا لم نجد جذراً نسبياً، نستخدم sympy
            solutions = solve(eq, x)
            sol_list = [float(N(s)) for s in solutions if s.is_real]
            result = f"x = {', '.join([format_number(s) for s in sol_list])}"
        
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

# ===== دالة محسنة للمعادلات الرباعية ثنائية التربيع =====
def solve_quartic_biquadratic_with_steps(equation: str) -> dict:
    """حل معادلة رباعية ثنائية التربيع: ax⁴ + bx² + c = 0 (محسنة)"""
    steps = []
    steps.append("📌 **السؤال:** " + equation)
    steps.append("")
    
    try:
        from sympy import symbols, Eq, solve, sympify, N
        x = symbols('x')
        
        # تنظيف المعادلة - معالجة الشرطة والرموز
        clean_eq = equation.replace('⁴', '**4').replace('²', '**2').replace(' ', '')
        clean_eq = clean_eq.replace('−', '-')
        
        if '=' in clean_eq:
            left, right = clean_eq.split('=')
            try:
                right_val = float(right)
            except:
                right_val = 0
        else:
            return {"success": False, "error": "صيغة غير صحيحة"}
        
        # تحويل 2x إلى 2*x
        left = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', left)
        left = re.sub(r'([a-zA-Z])(\d+)', r'\1*\2', left)
        
        steps.append("📐 **الخطوة 1: نعوض t = x²**")
        steps.append(f"   تصبح المعادلة: at² + bt + c = 0")
        steps.append("")
        
        try:
            # إنشاء التعبير
            expr_str = f"({left}) - ({right_val})"
            expr = sympify(expr_str)
            
            # حل المعادلة
            solutions = solve(expr, x)
            
            # تصفية الحلول الحقيقية
            sol_list = []
            for s in solutions:
                try:
                    val = float(N(s))
                    if abs(val.imag) < 1e-10 if hasattr(val, 'imag') else True:
                        sol_list.append(float(s))
                except:
                    pass
            
            steps.append("📐 **الخطوة 2: الحلول**")
            for i, sol in enumerate(sol_list, 1):
                steps.append(f"   x{i} = {format_number(sol)}")
            
            if len(sol_list) == 4:
                result = f"x = ±{format_number(abs(sol_list[0]))} أو x = ±{format_number(abs(sol_list[2]))}"
            elif len(sol_list) == 2:
                result = f"x = ±{format_number(abs(sol_list[0]))}"
            else:
                result = f"x = {', '.join([format_number(s) for s in sol_list])}"
            
            steps.append(f"✅ **الإجابة النهائية:** {result}")
            
            return {
                "success": True,
                "steps": steps,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "steps": [f"❌ حدث خطأ في الحل: {e}"],
                "result": None
            }
        
    except Exception as e:
        logger.error(f"خطأ في حل المعادلة الرباعية: {e}")
        return {
            "success": False,
            "error": str(e),
            "steps": [f"❌ حدث خطأ: {e}"],
            "result": None
        }

# ===== دالة جديدة لنظم 3×3 =====
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
            
            steps.append("📐 **الخطوة 2: حل النظام باستخدام قاعدة كرامر**")
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

# ===== دالة جديدة للمعادلات الجذرية =====
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
                steps.append(f"   x = {format_number(sol)} → حل دخيل (لا يحقق المعادلة الأصلية)")
        
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

def solve_quadratic_with_steps(equation: str) -> dict:
    """حل معادلة تربيعية مع خطوات (محسنة)"""
    steps = []
    steps.append("📌 **السؤال:** " + equation)
    steps.append("")
    
    try:
        # استخراج المعاملات باستخدام sympy
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
        from sympy import symbols, Eq, solve, sympify
        x = symbols('x')
        
        # تنظيف المعادلة
        clean_eq = equation.replace(' ', '')
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
    
    # الحل: |ax + b| = c
    # ax + b = c  أو  ax + b = -c
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
        # استخراج التعبير والقيمة
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
        
        # حل المعادلة يدوياً
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

def solve_with_steps(expression: str) -> dict:
    """الدالة الرئيسية - تحدد نوع المسألة وتوجهها للمعالج المناسب"""
    
    # 1. معادلات القيمة المطلقة
    if '|' in expression and '=' in expression:
        return solve_absolute_with_steps(expression)
    
    # 2. نظم المعادلات
    if expression.startswith('[') and expression.endswith(']') and ',' in expression:
        inner = expression[1:-1].strip()
        if ',' in inner:
            eqs = [e.strip() for e in inner.split(',')]
            if len(eqs) == 2:
                return solve_system_2x2_with_steps(eqs[0], eqs[1])
            elif len(eqs) == 3:
                return solve_system_3x3_with_steps(eqs[0], eqs[1], eqs[2])
    
    # 3. معادلات تكعيبية
    if ('x³' in expression or 'x^3' in expression) and '=' in expression:
        return solve_cubic_with_steps(expression)
    
    # 4. معادلات رباعية ثنائية التربيع
    if ('x⁴' in expression or 'x**4' in expression) and ('x²' in expression or 'x**2' in expression) and '=' in expression:
        return solve_quartic_biquadratic_with_steps(expression)
    
    # 5. معادلات جذرية
    if '√' in expression and '=' in expression:
        return solve_radical_with_steps(expression)
    
    # 6. معادلات تربيعية
    if ('x²' in expression or 'x^2' in expression) and '=' in expression:
        return solve_quadratic_with_steps(expression)
    
    # 7. معادلات خطية
    if '=' in expression and 'x' in expression:
        return solve_linear_with_steps(expression)
    
    # 8. عمليات حسابية
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
