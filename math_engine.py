# math_engine.py - الإصدار النهائي الكامل مع جميع التحسينات
import sympy as sp
import traceback
import ast
import sys
import time
from typing import Optional, List, Any, Dict, Union
from dataclasses import dataclass, field
import contextlib
import io
import signal

@dataclass
class Step:
    """خطوة حل مع LaTeX"""
    text: str
    latex: str = ""
    equation: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "text": self.text, 
            "latex": self.latex, 
            "equation": self.equation or ""
        }

@dataclass
class ExecutionResult:
    """نتيجة تنفيذ الكود"""
    success: bool
    result: Any = None
    result_str: str = ""
    steps: List[Step] = field(default_factory=list)
    error: Optional[str] = None

# ========== قائمة الدوال المسموح بها ==========
ALLOWED_BUILTINS = {
    'abs': abs, 'round': round, 'max': max, 'min': min,
    'sum': sum, 'len': len, 'int': int, 'float': float,
    'str': str, 'bool': bool, 'list': list, 'dict': dict,
}

ALLOWED_MODULES = {
    'sp': sp,  # sympy مسموح به
}

# ========== محلل الكود الآمن ==========
class SafeCodeAnalyzer(ast.NodeVisitor):
    """تحليل الكود والتأكد من خلوه من الأوامر الخطيرة"""
    
    def __init__(self):
        self.errors = []
        self.allowed_names = {'sp', 'final_result', 'steps', 'format_step'}
        self.dangerous_attrs = [
            '__import__', 'eval', 'exec', 'compile',
            'open', 'input', 'print', '__builtins__',
            'globals', 'locals', '__dict__', '__class__',
            'write', 'read', 'system', 'popen', 'subprocess'
        ]
        self.dangerous_modules = [
            'os', 'sys', 'subprocess', 'socket', 'requests',
            'urllib', 'pathlib', 'shutil', 'glob', 'pickle'
        ]
    
    def visit_Attribute(self, node):
        """فحص الوصول إلى الخصائص الخطيرة"""
        if isinstance(node.attr, str) and node.attr in self.dangerous_attrs:
            self.errors.append(f"❌ استخدام خاصية خطيرة: {node.attr}")
        self.generic_visit(node)
    
    def visit_Import(self, node):
        """منع استيراد وحدات غير مسموح بها"""
        for alias in node.names:
            if alias.name not in ['sympy', 'sp'] and alias.name not in self.dangerous_modules:
                # نسمح فقط بـ sympy
                if alias.name != 'sympy' and alias.name != 'sp':
                    self.errors.append(f"❌ استيراد غير مسموح: {alias.name}")
            if alias.name in self.dangerous_modules:
                self.errors.append(f"❌ استيراد وحدة خطيرة: {alias.name}")
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """منع استيراد من وحدات غير مسموح بها"""
        if node.module not in ['sympy', 'sp']:
            if node.module in self.dangerous_modules:
                self.errors.append(f"❌ استيراد من وحدة خطيرة: {node.module}")
            else:
                self.errors.append(f"❌ استيراد من وحدة غير مسموح بها: {node.module}")
        self.generic_visit(node)
    
    def visit_Call(self, node):
        """فحص استدعاء دوال خطيرة"""
        if isinstance(node.func, ast.Name):
            if node.func.id in ['eval', 'exec', 'compile', 'open', 'input']:
                self.errors.append(f"❌ استدعاء دالة خطيرة: {node.func.id}")
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in ['system', 'popen', 'call', 'run']:
                self.errors.append(f"❌ استدعاء دالة خطيرة: {node.func.attr}")
        self.generic_visit(node)
    
    def visit_For(self, node):
        """السماح بالحلقات التكرارية"""
        self.generic_visit(node)
    
    def visit_While(self, node):
        """السماح بالحلقات التكرارية"""
        self.generic_visit(node)

# ========== محرك الرياضيات الآمن مع دعم المتغيرات المتعددة ==========
class MathEngine:
    """محرك رياضيات آمن لتنفيذ كود SymPy مع دعم المتغيرات المتعددة"""
    
    def __init__(self):
        self.execution_count = 0
        self.max_execution_time = 5  # 5 ثواني كحد أقصى
        self.timeout_occurred = False
        print("✅ Math Engine ready - الإصدار النهائي مع دعم المتغيرات المتعددة")
    
    async def shutdown(self):
        """تنظيف الموارد"""
        print("🛑 Math Engine تم إيقافه")
    
    def _validate_code(self, code: str) -> List[str]:
        """
        التحقق من صحة وأمان الكود
        
        Returns:
            List[str]: قائمة بالأخطاء إن وجدت
        """
        try:
            # تحويل الكود إلى AST
            tree = ast.parse(code)
            
            # تحليل الأمان
            analyzer = SafeCodeAnalyzer()
            analyzer.visit(tree)
            
            return analyzer.errors
            
        except SyntaxError as e:
            return [f"❌ خطأ في تركيب الكود: {str(e)}"]
        except Exception as e:
            return [f"❌ خطأ في تحليل الكود: {str(e)}"]
    
    def _create_safe_namespace(self) -> Dict[str, Any]:
        """إنشاء namespace آمن للتنفيذ"""
        namespace = {
            'sp': sp,
            '__builtins__': ALLOWED_BUILTINS,  # فقط الدوال المسموح بها
        }
        
        # إضافة الدوال المساعدة
        namespace['format_step'] = lambda text, latex="": (text, latex)
        
        # إضافة المتغيرات الشائعة
        namespace['x'] = sp.symbols('x')
        namespace['y'] = sp.symbols('y')
        namespace['z'] = sp.symbols('z')
        namespace['t'] = sp.symbols('t')
        
        return namespace
    
    def _extract_steps(self, steps_data: List[Any]) -> List[Step]:
        """استخراج الخطوات بشكل آمن"""
        steps = []
        
        for s in steps_data:
            try:
                if isinstance(s, Step):
                    steps.append(s)
                elif isinstance(s, dict):
                    steps.append(Step(
                        text=s.get('text', s.get('description', '')),
                        latex=s.get('latex', ''),
                        equation=s.get('equation', '')
                    ))
                elif isinstance(s, tuple) and len(s) == 2:
                    steps.append(Step(text=str(s[0]), latex=str(s[1])))
                elif isinstance(s, tuple) and len(s) == 3:
                    steps.append(Step(text=str(s[0]), latex=str(s[1]), equation=str(s[2])))
                elif isinstance(s, str):
                    steps.append(Step(text=s))
                else:
                    steps.append(Step(text=str(s)))
            except Exception as e:
                steps.append(Step(text=f"⚠️ خطأ في تحويل الخطوة: {e}"))
        
        return steps
    
    def _extract_variables_from_code(self, code: str) -> List[str]:
        """استخراج المتغيرات المستخدمة في الكود"""
        variables = []
        try:
            # البحث عن تعريفات المتغيرات
            var_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*sp\.symbols'
            matches = re.findall(var_pattern, code)
            variables.extend(matches)
            
            # البحث عن المتغيرات المستخدمة مباشرة
            for var in ['x', 'y', 'z', 't']:
                if f'sp.symbols(\'{var}\')' in code or f'sp.Symbol(\'{var}\')' in code:
                    if var not in variables:
                        variables.append(var)
        except:
            pass
        
        return variables if variables else ['x']  # افتراضي x إذا لم نجد
    
    # ========== تنفيذ آمن للكود مع دعم المتغيرات المتعددة ==========
    async def execute(self, code: str) -> ExecutionResult:
        """
        تنفيذ كود SymPy بشكل آمن مع دعم المتغيرات المتعددة
        
        Args:
            code: كود SymPy (يجب أن يحتوي على final_result و steps)
            
        Returns:
            ExecutionResult: النتيجة
        """
        self.execution_count += 1
        self.timeout_occurred = False
        
        # التحقق من الكود أولاً
        errors = self._validate_code(code)
        if errors:
            return ExecutionResult(
                success=False,
                error=f"⚠️ الكود غير آمن:\n" + "\n".join(errors)
            )
        
        # إنشاء namespace آمن
        namespace = self._create_safe_namespace()
        
        # التقاط المخرجات
        output = io.StringIO()
        
        # إعداد معالج timeout
        def timeout_handler(signum, frame):
            self.timeout_occurred = True
            raise TimeoutError("انتهى وقت التنفيذ")
        
        try:
            with contextlib.redirect_stdout(output):
                # تنفيذ الكود مع timeout
                if hasattr(signal, 'SIGALRM'):
                    # لأنظمة Unix
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(self.max_execution_time)
                
                try:
                    # تنفيذ الكود
                    exec(code, namespace)
                finally:
                    if hasattr(signal, 'SIGALRM'):
                        signal.alarm(0)  # إلغاء التنبيه
            
            # استخراج النتائج
            final_result = namespace.get('final_result')
            steps_data = namespace.get('steps', [])
            
            # تحويل الخطوات
            steps = self._extract_steps(steps_data)
            
            # تحويل النتيجة إلى نص
            result_str = ""
            if final_result is not None:
                try:
                    # محاولة تحويل النتيجة الرياضية إلى LaTeX
                    if hasattr(final_result, '_sympy_'):
                        result_str = sp.latex(final_result)
                    else:
                        result_str = str(final_result)
                except:
                    try:
                        result_str = str(final_result)
                    except:
                        result_str = "نتيجة غير قابلة للتحويل"
            
            if self.timeout_occurred:
                return ExecutionResult(
                    success=False,
                    error=f"❌ انتهت مهلة التنفيذ ({self.max_execution_time} ثانية)"
                )
            
            return ExecutionResult(
                success=True,
                result=final_result,
                result_str=result_str,
                steps=steps
            )
            
        except MemoryError:
            return ExecutionResult(
                success=False,
                error="❌ استهلاك كبير للذاكرة - تم إيقاف التنفيذ"
            )
        except RecursionError:
            return ExecutionResult(
                success=False,
                error="❌ استدعاء متكرر عميق جداً"
            )
        except TimeoutError as e:
            return ExecutionResult(
                success=False,
                error=f"❌ {str(e)}"
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=f"❌ خطأ في التنفيذ: {str(e)}"
            )
    
    # ========== دوال مساعدة للتنفيذ المباشر مع دعم المتغيرات المتعددة ==========
    async def evaluate_expression(self, expr: str, variables: Optional[List[str]] = None) -> ExecutionResult:
        """
        تقييم تعبير رياضي مع دعم المتغيرات
        
        Args:
            expr: التعبير الرياضي
            variables: قائمة المتغيرات (اختياري)
        """
        if variables is None:
            # محاولة استخراج المتغيرات من التعبير
            try:
                sym_expr = sp.sympify(expr)
                variables = [str(var) for var in sym_expr.free_symbols]
            except:
                variables = ['x']
        
        # إنشاء تعريفات المتغيرات
        var_defs = "\n".join([f"{var} = sp.symbols('{var}')" for var in variables])
        
        code = f"""
import sympy as sp
{var_defs}
expr = sp.sympify("{expr}")
final_result = expr.evalf()
steps = [
    ("🔢 تقييم تعبير", ""),
    ("التعبير: {expr}", ""),
    ("النتيجة:", str(final_result))
]
"""
        return await self.execute(code)
    
    async def calculate_derivative(self, func: str, var: str = 'x') -> ExecutionResult:
        """
        حساب مشتقة مع دعم المتغير
        
        Args:
            func: الدالة
            var: متغير الاشتقاق
        """
        code = f"""
import sympy as sp
{var} = sp.symbols('{var}')
f = sp.sympify("{func}")
final_result = sp.diff(f, {var})
steps = [
    ("📐 حساب المشتقة", ""),
    (f"f({var}) = {func}", ""),
    (f"f'({var}) = " + str(final_result), "")
]
"""
        return await self.execute(code)
    
    async def calculate_integral(self, func: str, var: str = 'x', definite: Optional[tuple] = None) -> ExecutionResult:
        """
        حساب تكامل مع دعم المتغيرات المتعددة
        
        Args:
            func: الدالة
            var: متغير التكامل
            definite: (حد سفلي, حد علوي) للتكامل المحدد
        """
        if definite:
            lower, upper = definite
            code = f"""
import sympy as sp
{var} = sp.symbols('{var}')
f = sp.sympify("{func}")
final_result = sp.integrate(f, ({var}, {lower}, {upper}))
steps = [
    ("📊 تكامل محدد", ""),
    (f"∫_{{ {lower} }}^{{ {upper} }} {func} d{var}", ""),
    ("النتيجة:", str(final_result))
]
"""
        else:
            code = f"""
import sympy as sp
{var} = sp.symbols('{var}')
f = sp.sympify("{func}")
final_result = sp.integrate(f, {var})
steps = [
    ("📊 تكامل غير محدد", ""),
    (f"∫ {func} d{var}", ""),
    ("النتيجة:", str(final_result) + " + C")
]
"""
        return await self.execute(code)
    
    async def solve_equation(self, eq: str, var: str = 'x') -> ExecutionResult:
        """
        حل معادلة مع دعم المتغيرات
        
        Args:
            eq: المعادلة
            var: المتغير المطلوب حله
        """
        code = f"""
import sympy as sp
{var} = sp.symbols('{var}')
left, right = sp.sympify("{eq.split('=')[0] if '=' in eq else eq}"), sp.sympify("{eq.split('=')[1] if '=' in eq else '0'}")
expr = left - right
final_result = sp.solve(expr, {var})
steps = [
    ("⚖️ حل معادلة", ""),
    (f"{eq}", ""),
    ("الحلول:", str(final_result))
]
"""
        return await self.execute(code)
    
    # ========== دالة متعددة الاستخدامات تحدد نوع العملية تلقائياً ==========
    async def process_math_query(self, query: str, operation: str = "auto") -> ExecutionResult:
        """
        معالجة استعلام رياضي مع تحديد نوع العملية تلقائياً
        
        Args:
            query: الاستعلام الرياضي
            operation: نوع العملية (auto, derivative, integral, equation, expression)
        """
        query_lower = query.lower()
        
        if operation == "derivative" or any(word in query_lower for word in ["مشتق", "derivative", "diff"]):
            # محاولة استخراج الدالة
            import re
            func_match = re.search(r'[\(\s]*([a-zA-Z0-9\*\-\+\/\(\)\^]+)[\)\s]*', query)
            if func_match:
                return await self.calculate_derivative(func_match.group(1))
        
        elif operation == "integral" or any(word in query_lower for word in ["تكامل", "integral"]):
            func_match = re.search(r'[\(\s]*([a-zA-Z0-9\*\-\+\/\(\)\^]+)[\)\s]*', query)
            if func_match:
                return await self.calculate_integral(func_match.group(1))
        
        elif operation == "equation" or any(word in query_lower for word in ["حل", "solve"]) or "=" in query:
            return await self.solve_equation(query)
        
        else:
            # افترض أنه تعبير
            return await self.evaluate_expression(query)
    
    # ========== إحصائيات ==========
    def get_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات المحرك"""
        return {
            "execution_count": self.execution_count,
            "max_execution_time": self.max_execution_time,
            "status": "ready",
            "timeout_occurred": self.timeout_occurred
        }
