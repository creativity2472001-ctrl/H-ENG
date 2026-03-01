# ============================================
# ملف: math_engine.py (الإصدار 2.1)
# الوظيفة: تنفيذ كود SymPy واستخراج النتائج والخطوات - الإصدار النهائي
# ============================================

"""
محرك رياضي متقدم لتنفيذ كود SymPy واستخراج النتائج والخطوات.

الميزات المحسنة:
✅ تنفيذ آمن مع Timeout باستخدام ProcessPoolExecutor
✅ توليد خطوات ذكي بتحليل AST
✅ دعم التعبيرات المعقدة (مشتقات، تكاملات، معادلات)
✅ تحويل LaTeX متعدد المستويات مع fallbacks
✅ تكامل كامل مع ai_engine.py
✅ إحصائيات أداء شاملة
✅ اختبارات متكاملة (unittest)
✅ معالجة دقيقة للأخطاء النحوية
✅ دعم متغيرات متعددة في evaluate_expression
✅ إدارة آمنة لـ Event Loop
"""

import sympy as sp
import traceback
import re
import ast
import time
from typing import Dict, Any, List, Tuple, Optional, Union
from dataclasses import dataclass, field
import logging
from enum import Enum
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, TimeoutError, ThreadPoolExecutor
import queue
import signal
from contextlib import contextmanager
import asyncio
import sys

from config import MAX_CODE_LENGTH, DANGEROUS_PATTERNS, DEBUG_MODE

# محاولة استيراد ai_engine للتحسين المتقدم
try:
    from ai_engine import AIEngine
    AI_ENGINE_AVAILABLE = True
except ImportError:
    AI_ENGINE_AVAILABLE = False
    if DEBUG_MODE:
        print("⚠️ AI Engine not available - AI assist features disabled")

# إعداد logging
logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """حالات تنفيذ الكود"""
    SUCCESS = "success"
    SYNTAX_ERROR = "syntax_error"
    SECURITY_ERROR = "security_error"
    RUNTIME_ERROR = "runtime_error"
    TIMEOUT = "timeout"
    AI_UNAVAILABLE = "ai_unavailable"


class MathExpressionType(Enum):
    """أنواع التعبيرات الرياضية"""
    SIMPLE = "simple"
    DERIVATIVE = "derivative"
    INTEGRAL = "integral"
    EQUATION = "equation"
    LIMIT = "limit"
    SERIES = "series"
    MATRIX = "matrix"
    UNKNOWN = "unknown"


@dataclass
class Step:
    """خطوة حل مع LaTeX ومعادلة"""
    text: str
    latex: str = ""
    equation: Optional[str] = None
    step_type: str = "general"
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "text": self.text,
            "latex": self.latex,
            "equation": self.equation or "",
            "step_type": self.step_type
        }


@dataclass
class ExecutionResult:
    """نتيجة تنفيذ الكود"""
    success: bool
    status: ExecutionStatus
    result: Any = None
    result_str: str = ""
    result_latex: str = ""
    steps: List[Step] = field(default_factory=list)
    error: Optional[str] = None
    traceback: Optional[str] = None
    execution_time: float = 0.0
    expression_type: MathExpressionType = MathExpressionType.UNKNOWN
    ai_assist: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "status": self.status.value,
            "result": self.result_str,
            "result_latex": self.result_latex,
            "steps": [s.to_dict() for s in self.steps],
            "error": self.error,
            "execution_time": round(self.execution_time, 4),
            "expression_type": self.expression_type.value,
            "ai_assist": self.ai_assist
        }


class CodeExecutor:
    """منفذ كود آمن مع Timeout باستخدام ProcessPool"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.executor = ProcessPoolExecutor(max_workers=1)
        self._shutdown = False
        self._active_tasks = 0
        self._lock = asyncio.Lock()
    
    def _execute_in_process(self, code: str, namespace: Dict) -> Tuple[bool, Any, List, str, Optional[str]]:
        """
        تنفيذ الكود في عملية منفصلة مع تمييز SyntaxError.
        
        Returns:
            (success, result, steps, error, error_type)
        """
        try:
            # التحقق من النحو أولاً
            compile(code, '<string>', 'exec')
            
            # تنفيذ الكود
            exec(code, namespace)
            result = namespace.get('final_result')
            steps = namespace.get('steps', [])
            return True, result, steps, "", None
            
        except SyntaxError as e:
            return False, None, [], str(e), "syntax_error"
        except Exception as e:
            return False, None, [], str(e), "runtime_error"
    
    async def execute_with_timeout(self, code: str, namespace: Dict) -> Tuple[bool, Any, List, str, Optional[str]]:
        """
        تنفيذ الكود مع Timeout وتمييز نوع الخطأ.
        
        Returns:
            (success, result, steps, error, error_type)
        """
        if self._shutdown:
            return False, None, [], "Executor has been shut down", "runtime_error"
        
        async with self._lock:
            self._active_tasks += 1
        
        loop = asyncio.get_event_loop()
        
        try:
            # تنفيذ في عملية منفصلة
            future = loop.run_in_executor(
                self.executor,
                self._execute_in_process,
                code,
                namespace
            )
            
            result = await asyncio.wait_for(future, timeout=self.timeout)
            return result
            
        except asyncio.TimeoutError:
            # إلغاء المهمة
            future.cancel()
            return False, None, [], f"Execution timeout after {self.timeout}s", "timeout"
        except Exception as e:
            return False, None, [], str(e), "runtime_error"
        finally:
            async with self._lock:
                self._active_tasks -= 1
    
    async def shutdown(self):
        """إيقاف المنفذ وتنظيف الموارد"""
        async with self._lock:
            if not self._shutdown:
                self._shutdown = True
                
                # انتظار انتهاء المهام النشطة
                timeout = 5.0
                start = time.time()
                while self._active_tasks > 0 and time.time() - start < timeout:
                    await asyncio.sleep(0.1)
                
                self.executor.shutdown(wait=False)
                logger.debug("CodeExecutor shutdown complete")


class MathExpressionAnalyzer:
    """محلل التعبيرات الرياضية لاستخراج الخطوات"""
    
    @staticmethod
    def detect_expression_type(code: str) -> MathExpressionType:
        """اكتشاف نوع التعبير الرياضي من الكود"""
        if 'sp.diff' in code:
            return MathExpressionType.DERIVATIVE
        elif 'sp.integrate' in code:
            return MathExpressionType.INTEGRAL
        elif 'sp.Eq' in code or 'solve' in code:
            return MathExpressionType.EQUATION
        elif 'sp.limit' in code:
            return MathExpressionType.LIMIT
        elif 'sp.series' in code:
            return MathExpressionType.SERIES
        elif 'sp.Matrix' in code:
            return MathExpressionType.MATRIX
        else:
            return MathExpressionType.SIMPLE
    
    @staticmethod
    def extract_operations_from_ast(code: str) -> List[Dict[str, Any]]:
        """
        استخراج العمليات الرياضية من AST.
        
        Returns:
            قائمة بالعمليات مع تفاصيلها
        """
        operations = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # البحث عن استدعاءات الدوال الرياضية
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr == 'diff':
                            operations.append({
                                'type': 'derivative',
                                'line': node.lineno,
                                'args': [ast.unparse(arg) for arg in node.args]
                            })
                        elif node.func.attr == 'integrate':
                            operations.append({
                                'type': 'integral',
                                'line': node.lineno,
                                'args': [ast.unparse(arg) for arg in node.args]
                            })
                        elif node.func.attr == 'solve':
                            operations.append({
                                'type': 'solve',
                                'line': node.lineno,
                                'args': [ast.unparse(arg) for arg in node.args]
                            })
                        elif node.func.attr == 'limit':
                            operations.append({
                                'type': 'limit',
                                'line': node.lineno,
                                'args': [ast.unparse(arg) for arg in node.args]
                            })
                
                # البحث عن المعادلات
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id == 'Eq':
                        operations.append({
                            'type': 'equation',
                            'line': node.lineno,
                            'args': [ast.unparse(arg) for arg in node.args]
                        })
        
        except Exception as e:
            logger.debug(f"AST analysis error: {e}")
        
        return operations
    
    @staticmethod
    def extract_variables_from_expression(expression: str) -> List[str]:
        """
        استخراج المتغيرات من تعبير رياضي.
        
        Args:
            expression: التعبير الرياضي
            
        Returns:
            قائمة بأسماء المتغيرات
        """
        variables = set()
        try:
            expr = sp.sympify(expression)
            variables = {str(s) for s in expr.free_symbols}
        except:
            # استخدام Regex كـ fallback
            var_pattern = r'[a-zA-Z_][a-zA-Z0-9_]*'
            matches = re.findall(var_pattern, expression)
            # استبعاد الكلمات المفتاحية
            keywords = {'sin', 'cos', 'tan', 'exp', 'log', 'sqrt', 'abs'}
            variables = {m for m in matches if m not in keywords and len(m) == 1}
        
        return list(variables)
    
    @staticmethod
    def generate_enhanced_steps(code: str, result: Any) -> List[Step]:
        """
        توليد خطوات محسنة باستخدام تحليل AST.
        
        Args:
            code: الكود المنفذ
            result: النتيجة النهائية
            
        Returns:
            قائمة محسنة من الخطوات
        """
        steps = []
        operations = MathExpressionAnalyzer.extract_operations_from_ast(code)
        
        # إضافة خطوات من العمليات المكتشفة
        for op in operations:
            if op['type'] == 'derivative':
                steps.append(Step(
                    text=f"Calculate derivative: {', '.join(op['args'])}",
                    latex=f"\\frac{{d}}{{dx}}({op['args'][0] if op['args'] else ''})",
                    step_type='derivative'
                ))
            elif op['type'] == 'integral':
                steps.append(Step(
                    text=f"Calculate integral: {', '.join(op['args'])}",
                    latex=f"\\int ({op['args'][0] if op['args'] else ''}) dx",
                    step_type='integral'
                ))
            elif op['type'] == 'solve':
                steps.append(Step(
                    text=f"Solve equation: {', '.join(op['args'])}",
                    step_type='solve'
                ))
        
        # إضافة تعريفات المتغيرات
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            value = ast.unparse(node.value)
                            steps.append(Step(
                                text=f"Define {target.id} = {value}",
                                latex=f"{target.id} = {value}",
                                step_type='assignment'
                            ))
        except:
            pass
        
        # إضافة النتيجة النهائية
        if result is not None:
            steps.append(Step(
                text="Final result",
                latex=MathExpressionAnalyzer._safe_latex_enhanced(result),
                step_type='result'
            ))
        
        return steps
    
    @staticmethod
    def _safe_latex_enhanced(expr) -> str:
        """تحويل محسن إلى LaTeX مع خيارات متعددة"""
        try:
            return sp.latex(expr)
        except:
            try:
                return sp.pretty(expr)
            except:
                try:
                    return str(expr)
                except:
                    return ""


class MathEngine:
    """
    محرك رياضي متقدم لتنفيذ كود SymPy واستخراج النتائج والخطوات.
    
    الميزات المحسنة:
    - تنفيذ آمن مع Timeout
    - توليد خطوات ذكي بتحليل AST
    - دعم التعبيرات المعقدة
    - تحويل LaTeX متعدد المستويات
    - تكامل مع AI Engine
    - معالجة دقيقة للـ SyntaxError
    - دعم متغيرات متعددة
    """
    
    # قائمة الوحدات المسموح بها
    ALLOWED_MODULES = {
        'sp': sp,
        'sympy': sp,
        'math': __import__('math'),
        'numpy': None  # سيتم إضافته فقط إذا كان متاحاً
    }
    
    # الدوال المضمنة المسموح بها
    ALLOWED_BUILTINS = {
        'print': print,
        'range': range,
        'len': len,
        'int': int,
        'float': float,
        'str': str,
        'list': list,
        'dict': dict,
        'tuple': tuple,
        'bool': bool,
        'abs': abs,
        'max': max,
        'min': min,
        'sum': sum,
        'round': round,
        'enumerate': enumerate,
        'zip': zip,
        'isinstance': isinstance,
        'type': type,
        'pow': pow,
        'divmod': divmod,
        'complex': complex,
        'all': all,
        'any': any,
        'chr': chr,
        'ord': ord,
        'sorted': sorted,
        'reversed': reversed
    }
    
    def __init__(self, execution_timeout: int = 10, enable_ai_assist: bool = True, ai_assist_probability: float = 0.1):
        """
        تهيئة المحرك الرياضي.
        
        Args:
            execution_timeout: مهلة تنفيذ الكود بالثواني
            enable_ai_assist: تفعيل مساعدة الذكاء الاصطناعي
            ai_assist_probability: احتمال طلب مساعدة AI (0.0 إلى 1.0)
        """
        self.executor = CodeExecutor(timeout=execution_timeout)
        self.analyzer = MathExpressionAnalyzer()
        self.ai_engine = None
        self.enable_ai_assist = enable_ai_assist and AI_ENGINE_AVAILABLE
        self.ai_assist_probability = max(0.0, min(1.0, ai_assist_probability))
        self._ai_engine_lock = asyncio.Lock()
        self._shutdown = False
        
        # محاولة إضافة numpy إذا كان متاحاً
        try:
            import numpy as np
            self.ALLOWED_MODULES['numpy'] = np
            self.ALLOWED_MODULES['np'] = np
        except ImportError:
            pass
        
        # تهيئة AI Engine إذا كان مطلوباً
        if self.enable_ai_assist:
            try:
                self.ai_engine = AIEngine()
                logger.info("AI Engine initialized for math engine")
            except Exception as e:
                logger.warning(f"Failed to initialize AI Engine: {e}")
                self.enable_ai_assist = False
        
        self.stats = {
            "executions": 0,
            "success": 0,
            "failed": 0,
            "syntax_errors": 0,
            "security_errors": 0,
            "runtime_errors": 0,
            "timeouts": 0,
            "latex_conversions": 0,
            "latex_failures": 0,
            "total_execution_time": 0.0,
            "ai_assists": 0,
            "ai_attempts": 0
        }
        
        logger.info(f"MathEngine initialized (timeout: {execution_timeout}s, AI assist: {self.enable_ai_assist}, prob: {ai_assist_probability})")
    
    def _check_code_length(self, code: str) -> Tuple[bool, Optional[str]]:
        """التحقق من طول الكود."""
        if len(code) > MAX_CODE_LENGTH:
            return False, f"Code length exceeds maximum ({MAX_CODE_LENGTH} chars)"
        return True, None
    
    def _check_dangerous_patterns(self, code: str) -> Tuple[bool, Optional[str]]:
        """التحقق من وجود أنماط خطيرة."""
        for pattern in DANGEROUS_PATTERNS:
            if pattern in code:
                return False, pattern
        return True, None
    
    def _validate_syntax(self, code: str) -> Tuple[bool, Optional[str]]:
        """التحقق من صحة النحو."""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        except Exception as e:
            return False, f"Validation error: {e}"
    
    def _is_code_safe(self, code: str) -> Tuple[bool, Optional[str], Optional[ExecutionStatus]]:
        """
        التحقق الشامل من أمان الكود مع تحديد نوع الخطأ.
        
        Returns:
            (safe, reason, status)
        """
        # التحقق من الطول
        safe, error = self._check_code_length(code)
        if not safe:
            return False, error, ExecutionStatus.SECURITY_ERROR
        
        # التحقق من الأنماط الخطيرة
        safe, pattern = self._check_dangerous_patterns(code)
        if not safe:
            return False, f"Dangerous pattern detected: {pattern}", ExecutionStatus.SECURITY_ERROR
        
        # التحقق من النحو
        valid, error = self._validate_syntax(code)
        if not valid:
            return False, error, ExecutionStatus.SYNTAX_ERROR
        
        return True, None, None
    
    def _create_safe_namespace(self) -> Dict[str, Any]:
        """إنشاء مساحة أسماء آمنة."""
        # نسخة آمنة من الدوال المضمنة
        safe_builtins = {}
        for name, func in self.ALLOWED_BUILTINS.items():
            if callable(func):
                safe_builtins[name] = func
        
        # إضافة الوحدات المسموح بها
        namespace = {
            '__builtins__': safe_builtins,
            **{k: v for k, v in self.ALLOWED_MODULES.items() if v is not None}
        }
        
        # منع الوصول إلى الخصائص الخطيرة
        namespace['__builtins__']['__dict__'] = None
        namespace['__builtins__']['__class__'] = None
        namespace['__builtins__']['__bases__'] = None
        namespace['__builtins__']['__subclasses__'] = None
        
        return namespace
    
    def _extract_final_result(self, namespace: Dict[str, Any]) -> Optional[Any]:
        """استخراج final_result."""
        return namespace.get('final_result')
    
    def _extract_steps(self, namespace: Dict[str, Any]) -> List[Step]:
        """استخراج steps من مساحة الأسماء."""
        steps_data = namespace.get('steps', [])
        steps = []
        
        if not isinstance(steps_data, list):
            return steps
        
        for s in steps_data:
            try:
                if isinstance(s, dict):
                    steps.append(Step(
                        text=str(s.get('text', '')),
                        latex=str(s.get('latex', '')),
                        equation=str(s.get('equation')) if s.get('equation') else None,
                        step_type=str(s.get('step_type', 'general'))
                    ))
                elif isinstance(s, str):
                    steps.append(Step(text=s, step_type='general'))
                elif isinstance(s, (list, tuple)) and len(s) >= 2:
                    steps.append(Step(
                        text=str(s[0]),
                        latex=str(s[1]),
                        step_type='general'
                    ))
                else:
                    steps.append(Step(text=str(s), step_type='general'))
            except Exception as e:
                logger.debug(f"Error processing step: {e}")
                steps.append(Step(text=str(s), step_type='general'))
        
        return steps
    
    def _to_latex_multi_level(self, expr: Any) -> str:
        """
        تحويل تعبير إلى LaTeX مع مستويات متعددة من fallbacks.
        
        المستويات:
        1. sp.latex العادي
        2. sp.pretty (نص منسق)
        3. str() العادي
        4. "" (فارغ)
        """
        if expr is None:
            return ""
        
        self.stats["latex_conversions"] += 1
        
        # المستوى 1: LaTeX
        try:
            return sp.latex(expr)
        except:
            pass
        
        # المستوى 2: Pretty print
        try:
            return sp.pretty(expr)
        except:
            pass
        
        # المستوى 3: String عادي
        try:
            return str(expr)
        except:
            self.stats["latex_failures"] += 1
            return ""
    
    async def _get_ai_assist(self, code: str, error: Optional[str] = None, force: bool = False) -> Optional[Dict[str, Any]]:
        """
        الحصول على مساعدة من AI Engine لتحليل الكود.
        
        Args:
            code: الكود المراد تحليله
            error: الخطأ الذي حدث (إن وجد)
            force: تجاهل الاحتمالية وطلب المساعدة فوراً
            
        Returns:
            اقتراحات AI أو None
        """
        if self._shutdown:
            return None
        
        if not self.enable_ai_assist or not self.ai_engine:
            return None
        
        self.stats["ai_attempts"] += 1
        
        # تطبيق الاحتمالية إذا لم يكن force=True
        if not force and random.random() > self.ai_assist_probability:
            return None
        
        async with self._ai_engine_lock:
            try:
                self.stats["ai_assists"] += 1
                
                # بناء سؤال مناسب لـ AI
                if error:
                    question = f"Fix this SymPy code error: {error}\n\nCode:\n{code}"
                else:
                    question = f"Analyze this SymPy code and suggest improvements:\n{code}"
                
                # التأكد من أن AI Engine قيد التشغيل
                if hasattr(self.ai_engine, 'start'):
                    await self.ai_engine.start()
                
                # الحصول على مساعدة
                result = await self.ai_engine.generate_code(question, domain="calculus")
                
                if result and result.get("success"):
                    return {
                        "suggestion": result.get("code"),
                        "confidence": result.get("confidence", 0),
                        "model": result.get("model"),
                        "time": result.get("time", 0)
                    }
                
            except Exception as e:
                logger.debug(f"AI assist failed: {e}")
        
        return None
    
    async def execute(self, code: str, use_ai_assist: bool = True) -> ExecutionResult:
        """
        تنفيذ كود SymPy مع Timeout ومساعدة AI.
        
        Args:
            code: الكود المراد تنفيذه
            use_ai_assist: تفعيل مساعدة AI
            
        Returns:
            ExecutionResult: كائن النتيجة الكامل
        """
        if self._shutdown:
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.RUNTIME_ERROR,
                error="Engine has been shut down"
            )
        
        start_time = time.time()
        self.stats["executions"] += 1
        
        # إنشاء كائن النتيجة
        result = ExecutionResult(
            success=False,
            status=ExecutionStatus.RUNTIME_ERROR
        )
        
        # تحديد نوع التعبير
        result.expression_type = self.analyzer.detect_expression_type(code)
        
        # التحقق من أمان الكود (مع تحديد نوع الخطأ)
        safe, reason, status = self._is_code_safe(code)
        if not safe:
            result.status = status or ExecutionStatus.SECURITY_ERROR
            result.error = reason
            if status == ExecutionStatus.SYNTAX_ERROR:
                self.stats["syntax_errors"] += 1
            else:
                self.stats["security_errors"] += 1
            self.stats["failed"] += 1
            result.execution_time = time.time() - start_time
            return result
        
        # إنشاء مساحة أسماء آمنة
        namespace = self._create_safe_namespace()
        
        # تنفيذ الكود مع Timeout
        success, final_result, steps_data, error, error_type = await self.executor.execute_with_timeout(code, namespace)
        
        if not success:
            # تحديد نوع الخطأ
            if error_type == "timeout":
                result.status = ExecutionStatus.TIMEOUT
                self.stats["timeouts"] += 1
            elif error_type == "syntax_error":
                result.status = ExecutionStatus.SYNTAX_ERROR
                self.stats["syntax_errors"] += 1
            else:
                result.status = ExecutionStatus.RUNTIME_ERROR
                self.stats["runtime_errors"] += 1
            
            result.error = error
            self.stats["failed"] += 1
            
            # طلب مساعدة AI إذا كان مطلوباً
            if use_ai_assist and self.enable_ai_assist:
                result.ai_assist = await self._get_ai_assist(code, error, force=True)
            
        else:
            # تحويل الخطوات إلى كائنات Step
            steps = self._extract_steps({'steps': steps_data})
            
            # توليد خطوات محسنة إذا لم توجد
            if not steps and final_result is not None:
                steps = self.analyzer.generate_enhanced_steps(code, final_result)
            
            # تجهيز النتيجة
            result.success = True
            result.status = ExecutionStatus.SUCCESS
            result.result = final_result
            result.result_str = str(final_result) if final_result is not None else ""
            result.result_latex = self._to_latex_multi_level(final_result) if final_result is not None else ""
            result.steps = steps
            
            self.stats["success"] += 1
            
            # طلب تحسينات من AI (اختياري)
            if use_ai_assist and self.enable_ai_assist:
                result.ai_assist = await self._get_ai_assist(code, force=False)
        
        # تحديث وقت التنفيذ
        result.execution_time = time.time() - start_time
        self.stats["total_execution_time"] += result.execution_time
        
        return result
    
    async def execute_and_format(self, code: str, use_ai_assist: bool = True) -> Dict[str, Any]:
        """
        تنفيذ الكود وإرجاع نتيجة منسقة.
        
        Args:
            code: كود SymPy
            use_ai_assist: تفعيل مساعدة AI
            
        Returns:
            قاموس بالنتائج المنسقة
        """
        result = await self.execute(code, use_ai_assist)
        return result.to_dict()
    
    def evaluate_expression(self, expression: str, 
                           subs: Optional[Dict[str, float]] = None,
                           operation: Optional[str] = None,
                           variable: Optional[str] = None) -> Dict[str, Any]:
        """
        تقييم تعبير رياضي مع دعم العمليات المتقدمة والمتغيرات المخصصة.
        
        Args:
            expression: التعبير الرياضي
            subs: التعويضات
            operation: العملية المطلوبة (derivative, integral, solve)
            variable: المتغير المستقل (للاشتقاق والتكامل)
            
        Returns:
            قاموس بالنتيجة
        """
        start_time = time.time()
        
        try:
            expr = sp.sympify(expression)
            steps = []
            result_expr = expr
            
            # تحديد المتغير الافتراضي أو المستخدم
            if variable:
                var = sp.Symbol(variable)
            else:
                # محاولة استخراج المتغيرات من التعبير
                variables = self.analyzer.extract_variables_from_expression(expression)
                var = sp.Symbol(variables[0]) if variables else sp.Symbol('x')
            
            # تنفيذ العملية المطلوبة
            if operation == "derivative":
                result_expr = sp.diff(expr, var)
                steps.append(Step(
                    text=f"Differentiate {expression} with respect to {var}",
                    latex=f"\\frac{{d}}{{d{var}}}({expression})",
                    step_type='derivative'
                ))
                
            elif operation == "integral":
                result_expr = sp.integrate(expr, var)
                steps.append(Step(
                    text=f"Integrate {expression} with respect to {var}",
                    latex=f"\\int {expression} d{var}",
                    step_type='integral'
                ))
                
            elif operation == "solve":
                solutions = sp.solve(expr, var)
                result_expr = solutions
                steps.append(Step(
                    text=f"Solve equation: {expression} = 0 for {var}",
                    latex=f"{expression} = 0",
                    step_type='solve'
                ))
                steps.append(Step(
                    text=f"Solutions: {solutions}",
                    latex=f"{var} = {solutions}",
                    step_type='result'
                ))
            
            # تطبيق التعويضات
            if subs:
                result_expr = result_expr.subs(subs)
                steps.append(Step(
                    text=f"Substitute: {subs}",
                    latex=", ".join(f"{k}={v}" for k, v in subs.items()),
                    step_type='substitution'
                ))
            
            # إضافة الخطوات الأساسية
            if not steps:
                steps.append(Step(
                    text=f"Expression: {expression}",
                    latex=self._to_latex_multi_level(expr),
                    step_type='expression'
                ))
            
            if operation != "solve":
                steps.append(Step(
                    text="Result",
                    latex=self._to_latex_multi_level(result_expr),
                    step_type='result'
                ))
            
            result = ExecutionResult(
                success=True,
                status=ExecutionStatus.SUCCESS,
                result=result_expr,
                result_str=str(result_expr),
                result_latex=self._to_latex_multi_level(result_expr),
                steps=steps,
                expression_type=MathExpressionType.SIMPLE,
                execution_time=time.time() - start_time
            )
            
            return result.to_dict()
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.RUNTIME_ERROR,
                error=str(e),
                execution_time=time.time() - start_time
            ).to_dict()
    
    def validate_code(self, code: str) -> Dict[str, Any]:
        """التحقق من صحة الكود دون تنفيذه."""
        # التحقق من الطول
        safe, error = self._check_code_length(code)
        if not safe:
            return {
                "valid": False,
                "error": error,
                "type": "length_error"
            }
        
        # التحقق من الأنماط الخطيرة
        safe, pattern = self._check_dangerous_patterns(code)
        if not safe:
            return {
                "valid": False,
                "error": f"Dangerous pattern: {pattern}",
                "type": "security_error",
                "pattern": pattern
            }
        
        # التحقق من النحو
        valid, error = self._validate_syntax(code)
        if not valid:
            return {
                "valid": False,
                "error": error,
                "type": "syntax_error"
            }
        
        # التحقق من وجود final_result
        if 'final_result' not in code:
            return {
                "valid": False,
                "error": "Code must define 'final_result' variable",
                "type": "missing_final_result"
            }
        
        # تحليل AST للكشف عن المشاكل المحتملة
        operations = self.analyzer.extract_operations_from_ast(code)
        
        return {
            "valid": True,
            "type": "valid",
            "operations": operations,
            "expression_type": self.analyzer.detect_expression_type(code).value
        }
    
    def extract_variables(self, code: str) -> List[str]:
        """استخراج أسماء المتغيرات المستخدمة."""
        variables = set()
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    variables.add(node.id)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            variables.add(target.id)
                            
        except Exception as e:
            logger.debug(f"Error extracting variables: {e}")
        
        return list(variables)
    
    def simplify_expression(self, expression: str) -> Dict[str, Any]:
        """تبسيط تعبير رياضي."""
        try:
            expr = sp.sympify(expression)
            simplified = sp.simplify(expr)
            
            steps = [
                Step(
                    text=f"Original: {expression}",
                    latex=self._to_latex_multi_level(expr),
                    step_type='original'
                ),
                Step(
                    text="Apply simplification rules",
                    step_type='simplification'
                ),
                Step(
                    text=f"Simplified: {simplified}",
                    latex=self._to_latex_multi_level(simplified),
                    step_type='result'
                )
            ]
            
            return {
                "success": True,
                "original": expression,
                "original_latex": self._to_latex_multi_level(expr),
                "simplified": str(simplified),
                "simplified_latex": self._to_latex_multi_level(simplified),
                "steps": [s.to_dict() for s in steps]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """إحصائيات أداء المحرك."""
        total = self.stats["executions"]
        success_rate = (self.stats["success"] / max(total, 1)) * 100
        avg_time = self.stats["total_execution_time"] / max(total, 1)
        
        return {
            "executions": self.stats["executions"],
            "success": self.stats["success"],
            "failed": self.stats["failed"],
            "syntax_errors": self.stats["syntax_errors"],
            "security_errors": self.stats["security_errors"],
            "runtime_errors": self.stats["runtime_errors"],
            "timeouts": self.stats["timeouts"],
            "latex_conversions": self.stats["latex_conversions"],
            "latex_failures": self.stats["latex_failures"],
            "ai_assists": self.stats["ai_assists"],
            "ai_attempts": self.stats["ai_attempts"],
            "ai_success_rate": f"{(self.stats['ai_assists'] / max(self.stats['ai_attempts'], 1)) * 100:.1f}%",
            "success_rate": f"{success_rate:.1f}%",
            "avg_execution_time": f"{avg_time:.3f}s",
            "total_execution_time": f"{self.stats['total_execution_time']:.3f}s"
        }
    
    def reset_stats(self):
        """إعادة تعيين الإحصائيات."""
        self.stats = {
            "executions": 0,
            "success": 0,
            "failed": 0,
            "syntax_errors": 0,
            "security_errors": 0,
            "runtime_errors": 0,
            "timeouts": 0,
            "latex_conversions": 0,
            "latex_failures": 0,
            "total_execution_time": 0.0,
            "ai_assists": 0,
            "ai_attempts": 0
        }
        logger.info("Statistics reset")
    
    async def shutdown(self):
        """إيقاف المحرك وتنظيف الموارد."""
        if self._shutdown:
            return
        
        logger.info("Shutting down MathEngine...")
        self._shutdown = True
        
        # إيقاف CodeExecutor
        await self.executor.shutdown()
        
        # إيقاف AI Engine إذا كان موجوداً
        if self.ai_engine:
            async with self._ai_engine_lock:
                try:
                    if hasattr(self.ai_engine, 'stop'):
                        # التحقق من وجود loop نشط
                        try:
                            loop = asyncio.get_running_loop()
                            # إذا كان هناك loop نشط، نستخدمه
                            await self.ai_engine.stop()
                        except RuntimeError:
                            # لا يوجد loop نشط، ننشئ واحداً مؤقتاً
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                loop.run_until_complete(self.ai_engine.stop())
                            finally:
                                loop.close()
                except Exception as e:
                    logger.error(f"Error stopping AI Engine: {e}")
        
        logger.info("MathEngine shutdown complete")


# ========== اختبارات وحدة (Unit Tests) ==========
import unittest
import asyncio
import random


class TestMathEngine(unittest.TestCase):
    """اختبارات وحدة لمحرك MathEngine"""
    
    @classmethod
    def setUpClass(cls):
        cls.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls.loop)
        cls.engine = MathEngine(execution_timeout=5, enable_ai_assist=False)
    
    @classmethod
    def tearDownClass(cls):
        cls.loop.run_until_complete(cls.engine.shutdown())
        cls.loop.close()
    
    def test_1_valid_code_with_steps(self):
        """اختبار كود صحيح مع steps"""
        code = '''
import sympy as sp
x = sp.symbols('x')
f = x**3 + 2*x**2 - 5*x + 7
final_result = sp.diff(f, x)
steps = [
    {"text": "Define function", "latex": sp.latex(f)},
    {"text": "Apply power rule", "latex": sp.latex(sp.diff(f, x))}
]
'''
        result = self.loop.run_until_complete(self.engine.execute(code))
        self.assertTrue(result.success)
        self.assertEqual(result.status, ExecutionStatus.SUCCESS)
        self.assertGreater(len(result.steps), 0)
    
    def test_2_code_without_steps(self):
        """اختبار كود بدون steps (توليد تلقائي)"""
        code = '''
import sympy as sp
x = sp.symbols('x')
f = x**2 + 2*x + 1
final_result = sp.diff(f, x)
'''
        result = self.loop.run_until_complete(self.engine.execute(code))
        self.assertTrue(result.success)
        self.assertGreater(len(result.steps), 0)
    
    def test_3_syntax_error(self):
        """اختبار خطأ نحوي"""
        code = '''
import sympy as sp
x = sp.symbols('x')
f = x**2 + 
final_result = sp.diff(f, x)
'''
        result = self.loop.run_until_complete(self.engine.execute(code))
        self.assertFalse(result.success)
        self.assertEqual(result.status, ExecutionStatus.SYNTAX_ERROR)
    
    def test_4_security_error(self):
        """اختبار كود غير آمن"""
        code = '''
import os
os.system('ls')
final_result = None
'''
        result = self.loop.run_until_complete(self.engine.execute(code))
        self.assertFalse(result.success)
        self.assertEqual(result.status, ExecutionStatus.SECURITY_ERROR)
    
    def test_5_evaluate_expression(self):
        """اختبار تقييم تعبير مباشر"""
        result = self.engine.evaluate_expression("x**2 + 2*x + 1", {"x": 2})
        self.assertTrue(result['success'])
        self.assertEqual(result['result'], '9')
    
    def test_6_evaluate_expression_with_variable(self):
        """اختبار تقييم تعبير مع متغير مخصص"""
        result = self.engine.evaluate_expression("y**2 + 2*y + 1", {"y": 3}, variable="y")
        self.assertTrue(result['success'])
        self.assertEqual(result['result'], '16')
    
    def test_7_validate_code(self):
        """اختبار التحقق من الكود"""
        code = '''
import sympy as sp
x = sp.symbols('x')
final_result = sp.diff(x**2, x)
'''
        validation = self.engine.validate_code(code)
        self.assertTrue(validation['valid'])
    
    def test_8_simplify_expression(self):
        """اختبار تبسيط تعبير"""
        result = self.engine.simplify_expression("(x**2 - 1)/(x - 1)")
        self.assertTrue(result['success'])
        self.assertIn('x + 1', result['simplified'])
    
    def test_9_extract_variables(self):
        """اختبار استخراج المتغيرات"""
        code = '''
a = 5
b = a + 3
c = a * b
final_result = c
'''
        vars = self.engine.extract_variables(code)
        self.assertIn('a', vars)
        self.assertIn('b', vars)
        self.assertIn('c', vars)
    
    def test_10_detect_expression_type(self):
        """اختبار اكتشاف نوع التعبير"""
        code = "sp.diff(x**2, x)"
        expr_type = self.engine.analyzer.detect_expression_type(code)
        self.assertEqual(expr_type, MathExpressionType.DERIVATIVE)
    
    def test_11_derivative_operation(self):
        """اختبار عملية الاشتقاق"""
        result = self.engine.evaluate_expression("x**3", operation="derivative", variable="x")
        self.assertTrue(result['success'])
        self.assertIn('3*x**2', result['result'])
    
    def test_12_integral_operation(self):
        """اختبار عملية التكامل"""
        result = self.engine.evaluate_expression("x**2", operation="integral", variable="x")
        self.assertTrue(result['success'])
        self.assertIn('x**3/3', result['result'])
    
    def test_13_solve_operation(self):
        """اختبار حل معادلة"""
        result = self.engine.evaluate_expression("x**2 - 4", operation="solve", variable="x")
        self.assertTrue(result['success'])
        self.assertIn('2', str(result['result']))


def run_tests():
    """تشغيل جميع الاختبارات"""
    # تعيين seed ثابت للاختبارات
    random.seed(42)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMathEngine)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


# ========== اختبار سريع للتكامل مع AI ==========
async def integration_test():
    """اختبار التكامل مع AI Engine"""
    print("\n" + "="*70)
    print("🧪 MathEngine - Integration Test with AI")
    print("="*70)
    
    engine = MathEngine(enable_ai_assist=True, ai_assist_probability=1.0)  # force AI for testing
    
    # كود به خطأ بسيط
    code_with_error = '''
import sympy as sp
x = sp.symbols('x')
f = x**2 + 
final_result = sp.diff(f, x)
'''
    
    print("\n📌 Testing with AI assist (error correction)...")
    result = await engine.execute(code_with_error, use_ai_assist=True)
    print(f"   Success: {result.success}")
    print(f"   Status: {result.status.value}")
    print(f"   Error: {result.error}")
    if result.ai_assist:
        print(f"   🤖 AI Suggestion: {result.ai_assist.get('suggestion', '')[:100]}...")
    
    # كود صحيح مع طلب تحسينات
    good_code = '''
import sympy as sp
x = sp.symbols('x')
f = x**3 + 2*x**2 - 5*x + 7
final_result = sp.diff(f, x)
'''
    
    print("\n📌 Testing with AI assist (optimization)...")
    result = await engine.execute(good_code, use_ai_assist=True)
    print(f"   Success: {result.success}")
    print(f"   Steps: {len(result.steps)}")
    print(f"   Result: {result.result_str}")
    
    print("\n📊 Final Statistics:")
    stats = engine.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    await engine.shutdown()
    print("\n" + "="*70)


# ========== Main Test ==========
if __name__ == "__main__":
    import sys
    import random
    
    print("\n" + "="*70)
    print("🚀 MathEngine - Advanced Mathematical Engine v2.1")
    print("="*70)
    
    # تعيين seed للاختبارات
    random.seed(42)
    
    # تشغيل الاختبارات
    print("\n📋 Running Unit Tests...")
    tests_passed = run_tests()
    
    if tests_passed:
        print("\n✅ All unit tests passed!")
        
        # تشغيل اختبار التكامل
        if AI_ENGINE_AVAILABLE:
            asyncio.run(integration_test())
        else:
            print("\n⚠️ AI Engine not available - skipping integration test")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
