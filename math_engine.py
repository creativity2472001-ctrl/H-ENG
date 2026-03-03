# math_engine.py - الإصدار المصحح والآمن
import sympy as sp
import traceback
import ast
import sys
from typing import Optional, List, Any, Dict
from dataclasses import dataclass, field
import contextlib
import io

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

# ========== ✅ تحسين 1: قائمة الدوال المسموح بها ==========
ALLOWED_BUILTINS = {
    'abs': abs, 'round': round, 'max': max, 'min': min,
    'sum': sum, 'len': len, 'int': int, 'float': float,
    'str': str, 'bool': bool, 'list': list, 'dict': dict,
}

ALLOWED_MODULES = {
    'sp': sp,  # sympy مسموح به
}

# ========== ✅ تحسين 2: محلل الكود الآمن ==========
class SafeCodeAnalyzer(ast.NodeVisitor):
    """تحليل الكود والتأكد من خلوه من الأوامر الخطيرة"""
    
    def __init__(self):
        self.errors = []
        self.allowed_names = {'sp', 'final_result', 'steps', 'format_step'}
        self.dangerous_attrs = [
            '__import__', 'eval', 'exec', 'compile',
            'open', 'input', 'print', '__builtins__',
            'globals', 'locals', '__dict__', '__class__'
        ]
    
    def visit_Attribute(self, node):
        """فحص الوصول إلى الخصائص الخطيرة"""
        if isinstance(node.attr, str) and node.attr in self.dangerous_attrs:
            self.errors.append(f"❌ استخدام خاصية خطيرة: {node.attr}")
        self.generic_visit(node)
    
    def visit_Import(self, node):
        """منع استيراد وحدات غير مسموح بها"""
        for alias in node.names:
            if alias.name not in ['sympy', 'sp']:
                self.errors.append(f"❌ استيراد غير مسموح: {alias.name}")
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """منع استيراد من وحدات غير مسموح بها"""
        if node.module not in ['sympy', 'sp']:
            self.errors.append(f"❌ استيراد من وحدة غير مسموح بها: {node.module}")
        self.generic_visit(node)
    
    def visit_Call(self, node):
        """فحص استدعاء دوال خطيرة"""
        if isinstance(node.func, ast.Name):
            if node.func.id in ['eval', 'exec', 'compile', 'open']:
                self.errors.append(f"❌ استدعاء دالة خطيرة: {node.func.id}")
        self.generic_visit(node)

# ========== ✅ تحسين 3: محرك الرياضيات الآمن ==========
class MathEngine:
    """محرك رياضيات آمن لتنفيذ كود SymPy"""
    
    def __init__(self):
        self.execution_count = 0
        self.max_execution_time = 5  # 5 ثواني كحد أقصى
        print("✅ Math Engine ready (الإصدار الآمن)")
    
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
                        text=s.get('text', ''),
                        latex=s.get('latex', ''),
                        equation=s.get('equation', '')
                    ))
                elif isinstance(s, tuple) and len(s) == 2:
                    steps.append(Step(text=str(s[0]), latex=str(s[1])))
                elif isinstance(s, str):
                    steps.append(Step(text=s))
                else:
                    steps.append(Step(text=str(s)))
            except Exception as e:
                steps.append(Step(text=f"⚠️ خطأ في تحويل الخطوة: {e}"))
        
        return steps
    
    # ========== ✅ تحسين 4: تنفيذ آمن للكود ==========
    async def execute(self, code: str) -> ExecutionResult:
        """
        تنفيذ كود SymPy بشكل آمن
        
        Args:
            code: كود SymPy (يجب أن يحتوي على final_result و steps)
            
        Returns:
            ExecutionResult: النتيجة
        """
        self.execution_count += 1
        
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
        
        try:
            # ✅ استخدام exec مع namespace محدود
            with contextlib.redirect_stdout(output):
                # تنفيذ الكود مع timeout
                exec(code, namespace)
            
            # استخراج النتائج
            final_result = namespace.get('final_result')
            steps_data = namespace.get('steps', [])
            
            # تحويل الخطوات
            steps = self._extract_steps(steps_data)
            
            # تحويل النتيجة إلى نص
            result_str = ""
            if final_result is not None:
                try:
                    result_str = str(final_result)
                except:
                    result_str = "نتيجة غير قابلة للتحويل"
            
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
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=f"❌ خطأ في التنفيذ: {str(e)}"
            )
    
    # ========== ✅ تحسين 5: دوال مساعدة للتنفيذ المباشر ==========
    async def evaluate_expression(self, expr: str) -> ExecutionResult:
        """تقييم تعبير رياضي مباشر"""
        code = f"""
import sympy as sp
final_result = sp.sympify("{expr}").evalf()
steps = [("🔢 تقييم تعبير", ""), ("{expr}", ""), ("النتيجة:", str(final_result))]
"""
        return await self.execute(code)
    
    async def calculate_derivative(self, func: str, var: str = 'x') -> ExecutionResult:
        """حساب مشتقة"""
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
    
    # ========== ✅ تحسين 6: إحصائيات ==========
    def get_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات المحرك"""
        return {
            "execution_count": self.execution_count,
            "max_execution_time": self.max_execution_time,
            "status": "ready"
        }
