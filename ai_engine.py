class SymbolicMath:
    """محرك الرياضيات الرمزية"""
    
    def __init__(self):
        self.x, self.y, self.z = sp.symbols('x y z')
    
    def calculator(self, expr: str) -> Tuple[str, List[tuple]]:
        """آلة حاسبة آمنة"""
        try:
            result_expr = safe_sympify(expr)
            result = result_expr.evalf()
            result_latex = to_latex(result)
            expr_latex = to_latex(result_expr)
            
            steps = [
                ("🔢 عملية حسابية", ""),
                (f"التعبير: {expr_latex}", expr_latex),
                (f"النتيجة: {result_latex}", result_latex),
                ("✅ الإجابة النهائية:", f"\\boxed{{{result_latex}}}")
            ]
            return str(result), steps
        except Exception as e:
            return "خطأ", [(f"❌ {str(e)}", "")]
    
    def derivative(self, func: str) -> Tuple[str, List[tuple]]:
        """حساب المشتقة"""
        try:
            expr = safe_sympify(func)
            var = extract_variable(expr)
            result = sp.diff(expr, var)
            var_name = var.name
            
            result_str = str(result)
            
            steps = [
                (f"📐 مشتقة بالنسبة لـ {var_name}", ""),
                (f"f({var_name}) = {to_latex(expr)}", to_latex(expr)),
                ("نطبق قواعد الاشتقاق:", ""),
                (f"f'({var_name}) = {to_latex(result)}", to_latex(result)),
                ("✅ الإجابة النهائية:", f"\\boxed{{{to_latex(result)}}}")
            ]
            return result_str, steps
        except Exception as e:
            return "خطأ", [(f"❌ {str(e)}", "")]
    
    def integral(self, func: str) -> Tuple[str, List[tuple]]:
        """حساب التكامل"""
        try:
            expr = safe_sympify(func)
            var = extract_variable(expr)
            result = sp.integrate(expr, var)
            var_name = var.name
            
            # ✅ التأكد من أن النتيجة نصية
            result_str = str(result)
            if result_str and result_str != "0":
                result_str = result_str + " + C"
            else:
                result_str = "خطأ في التكامل"
            
            steps = [
                (f"📊 تكامل بالنسبة لـ {var_name}", ""),
                (f"∫ {to_latex(expr)} d{var_name}", f"∫ {to_latex(expr)} d{var_name}"),
                ("نطبق قواعد التكامل:", ""),
                (f"= {to_latex(result)} + C", f"{to_latex(result)} + C"),
                ("✅ الإجابة النهائية:", f"\\boxed{{{to_latex(result)} + C}}")
            ]
            return result_str, steps
        except Exception as e:
            return "خطأ", [(f"❌ {str(e)}", "")]
    
    def equation(self, eq: str) -> Tuple[str, List[tuple]]:
        """حل المعادلة"""
        try:
            if "=" in eq:
                left, right = eq.split("=")
                left_expr = safe_sympify(left)
                right_expr = safe_sympify(right)
                expr = left_expr - right_expr
            else:
                left_expr = safe_sympify(eq)
                right_expr = 0
                expr = left_expr
            
            var = extract_variable(expr)
            solutions = sp.solve(expr, var)
            var_name = var.name
            
            sol_list = []
            for sol in solutions:
                if sol.is_real:
                    sol_list.append(f"{var_name} = {to_latex(sol)}")
                else:
                    sol_list.append(f"{var_name} = {to_latex(sol)} (مركب)")
            
            sol_str = '  أو  '.join(sol_list) if sol_list else "لا يوجد حل حقيقي"
            
            steps = [
                ("⚖️ معادلة", ""),
                (f"{to_latex(left_expr)} = {to_latex(right_expr)}", f"{to_latex(left_expr)} = {to_latex(right_expr)}"),
                ("ننقل الحدود:", ""),
                (f"{to_latex(expr)} = 0", f"{to_latex(expr)} = 0"),
                ("الحلول:", ""),
                (sol_str, sol_str),
                ("✅ الإجابة النهائية:", f"\\boxed{{{sol_str}}}")
            ]
            return sol_str, steps
        except Exception as e:
            return "خطأ", [(f"❌ {str(e)}", "")]
