# ai_engine.py - الإصدار المحسّن مع خطوات عرض نظيفة (v8.0)
import re
import hashlib
import json
import logging
import asyncio
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# تحويلات SymPy المحسنة
transformations = (standard_transformations + (implicit_multiplication_application,))

# ========== ثوابت الأمان ==========
MAX_INPUT_LENGTH = 300  # الحد الأقصى لطول الإدخال
TIMEOUT_SECONDS = 5     # مهلة الحسابات الثقيلة

# ========== البيئة الآمنة لـ SymPy ==========
ALLOWED_SYMBOLS = {
    # متغيرات
    'x': sp.Symbol('x'),
    'y': sp.Symbol('y'),
    'z': sp.Symbol('z'),
    't': sp.Symbol('t'),
    'n': sp.Symbol('n'),
    'k': sp.Symbol('k'),
    
    # ثوابت
    'pi': sp.pi,
    'E': sp.E,
    'I': sp.I,
    'oo': sp.oo,
    
    # دوال مثلثية
    'sin': sp.sin,
    'cos': sp.cos,
    'tan': sp.tan,
    'cot': sp.cot,
    'sec': sp.sec,
    'csc': sp.csc,
    'asin': sp.asin,
    'acos': sp.acos,
    'atan': sp.atan,
    'acot': sp.acot,
    
    # دوال زائدية
    'sinh': sp.sinh,
    'cosh': sp.cosh,
    'tanh': sp.tanh,
    'asinh': sp.asinh,
    'acosh': sp.acosh,
    'atanh': sp.atanh,
    
    # دوال لوغاريتمية وأسية
    'log': sp.log,
    'ln': sp.log,
    'exp': sp.exp,
    'sqrt': sp.sqrt,
    
    # دوال أخرى
    'Abs': sp.Abs,
    'sign': sp.sign,
    'floor': sp.floor,
    'ceiling': sp.ceiling,
    
    # دالة الجاما
    'gamma': sp.gamma,
    'beta': sp.beta,
}

# الأسماء المسموح بها في التعبيرات
ALLOWED_NAMES = set(ALLOWED_SYMBOLS.keys())

# ========== كلاس الخطوات للتنسيق النظيف ==========
@dataclass
class Step:
    """خطوة حل واحدة مع أيقونة وتنسيق نظيف"""
    icon: str  # 📥, 🔍, 📝, 🧮, ✅, ⚠️, 📐, ∫, ∑, etc.
    title: str
    content: str
    latex: Optional[str] = None
    
    def to_dict(self) -> dict:
        """تحويل الخطوة إلى قاموس للتخزين"""
        return {
            "icon": self.icon,
            "title": self.title,
            "content": self.content,
            "latex": self.latex
        }
    
    def __str__(self) -> str:
        """تمثيل نصي للخطوة"""
        if self.latex:
            return f"{self.icon} **{self.title}**: {self.content} \[{self.latex}\]"
        return f"{self.icon} **{self.title}**: {self.content}"

@dataclass
class StepResult:
    """نتيجة مع خطوات الحل"""
    success: bool
    result: Any = None
    result_str: str = ""
    steps: List[Step] = field(default_factory=list)
    error: Optional[str] = None
    model: str = ""
    extracted_data: Optional[Dict] = None
    
    def to_dict(self) -> dict:
        """تحويل النتيجة إلى قاموس للتخزين والعرض"""
        return {
            "success": self.success,
            "result": str(self.result) if self.result is not None else None,
            "result_str": self.result_str,
            "steps": [step.to_dict() for step in self.steps],
            "error": self.error,
            "model": self.model,
            "extracted_data": self.extracted_data
        }

def safe_sympify(expr_str: str) -> Optional[sp.Expr]:
    """
    تحويل آمن وقوي للتعبيرات الرياضية باستخدام SymPy
    مع بيئة مقيدة تمامًا للإنتاج
    """
    if not expr_str or len(expr_str) > MAX_INPUT_LENGTH:
        logger.warning(f"Input length exceeded: {len(expr_str) if expr_str else 0} chars")
        return None
    
    try:
        # تنظيف التعبير
        expr_str = expr_str.replace('^', '**')
        expr_str = expr_str.replace(' ', '')
        
        # تحويل إلى تعبير SymPy في بيئة آمنة
        expr = parse_expr(
            expr_str,
            transformations=transformations,
            local_dict=ALLOWED_SYMBOLS,
            global_dict={}  # منع الوصول لأي شيء خارج المسموح
        )
        return expr
    except Exception as e:
        logger.debug(f"Safe sympify error: {e}")
        return None

async def run_with_timeout(coro, timeout=TIMEOUT_SECONDS):
    """تشغيل عملية مع مهلة زمنية"""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.warning(f"Operation timed out after {timeout} seconds")
        return None
    except Exception as e:
        logger.error(f"Error in timed operation: {e}")
        return None

def extract_equation_parts(text: str) -> Optional[Tuple[str, str]]:
    """استخراج طرفي المعادلة"""
    if len(text) > MAX_INPUT_LENGTH:
        return None
    
    if '=' in text:
        parts = text.split('=')
        if len(parts) == 2:
            return parts[0].strip(), parts[1].strip()
    return None

def extract_system_equations(text: str) -> Optional[List[Tuple[str, str]]]:
    """استخراج نظام معادلات"""
    if len(text) > MAX_INPUT_LENGTH:
        return None
    
    equations = []
    # دعم الفواصل والفاصلة المنقوطة والسطر الجديد
    parts = re.split(r'[,\n;]', text)
    
    for part in parts:
        if '=' in part:
            left, right = part.split('=', 1)
            equations.append((left.strip(), right.strip()))
    
    return equations if len(equations) >= 2 else None

def extract_limit(text: str) -> Optional[Dict]:
    """استخراج معلومات النهاية"""
    if len(text) > MAX_INPUT_LENGTH:
        return None
    
    patterns = [
        r'نهاية\s*([^ا]+?)\s*عندما\s*([xyzt])\s*→\s*(-?\d+\.?\d*|∞|infinity)',
        r'limit\s*\(\s*([^,]+?)\s*,\s*([xyzt])\s*,\s*(-?\d+\.?\d*|∞|infinity)\s*\)',
        r'lim_\{([xyzt])\s*→\s*(-?\d+\.?\d*|∞)\}\s*([^}]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            groups = match.groups()
            if len(groups) == 3:
                # تحديد المتغير وقيمة النهاية والدالة
                if '→' in text or '→' in text:
                    # نمط عربي
                    return {
                        "function": groups[0].strip(),
                        "variable": groups[1],
                        "value": groups[2]
                    }
                else:
                    # نمط انجليزي
                    return {
                        "function": groups[0].strip(),
                        "variable": groups[1],
                        "value": groups[2]
                    }
    return None

def extract_sum(text: str) -> Optional[Dict]:
    """استخراج معلومات المجموع - نسخة مصححة"""
    if len(text) > MAX_INPUT_LENGTH:
        return None
    
    patterns = [
        # نمط عربي: مجموع k^2 من 1 إلى 10
        r'مجموع\s*([^من]+?)\s*من\s*(-?\d+\.?\d*)\s*إلى\s*(-?\d+\.?\d*|∞|infinity)',
        
        # نمط إنجليزي: sum(k^2, k, 1, 10)
        r'sum\s*\(\s*([^,]+?)\s*,\s*([xyztk])\s*=\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*|∞|infinity)\s*\)',
        
        # نمط ∑: ∑_{k=1}^{10} k^2
        r'∑_\{([xyztk])\s*=\s*(-?\d+\.?\d*)\}\^\{(-?\d+\.?\d*|∞)\}\s*([^}]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            groups = match.groups()
            
            if len(groups) == 4 and pattern == patterns[0]:  # نمط عربي
                return {
                    "function": groups[0].strip(),
                    "variable": 'k',  # افتراضي
                    "start": groups[1],
                    "end": groups[2]
                }
            elif len(groups) == 4 and pattern == patterns[1]:  # نمط إنجليزي
                return {
                    "function": groups[0].strip(),
                    "variable": groups[1],
                    "start": groups[2],
                    "end": groups[3]
                }
            elif len(groups) == 4 and pattern == patterns[2]:  # نمط ∑
                return {
                    "function": groups[3].strip(),
                    "variable": groups[0],
                    "start": groups[1],
                    "end": groups[2]
                }
    
    return None

def extract_matrix_safe(text: str) -> Optional[List[sp.Matrix]]:
    """استخراج المصفوفات بطريقة آمنة"""
    if len(text) > MAX_INPUT_LENGTH:
        return None
    
    matrices = []
    
    # البحث عن أنماط المصفوفات
    # نمط JSON: [[1,2],[3,4]]
    json_pattern = r'\[\[(.*?)\]\](?:\s*[+\-*/]\s*\[\[(.*?)\]\])?'
    matches = re.finditer(json_pattern, text)
    
    for match in matches:
        for group in match.groups():
            if not group:
                continue
            
            try:
                # تقسيم الصفوف
                rows_str = group.split('],[')
                matrix_rows = []
                
                for row_str in rows_str:
                    # استخراج العناصر
                    elements_str = re.findall(r'-?\d+\.?\d*|[a-zA-Z]+', row_str)
                    row = []
                    
                    for elem_str in elements_str:
                        if elem_str in ALLOWED_NAMES:
                            # عنصر رمزي
                            row.append(ALLOWED_SYMBOLS.get(elem_str, sp.Symbol(elem_str)))
                        else:
                            try:
                                # عنصر رقمي
                                row.append(float(elem_str))
                            except ValueError:
                                # عنصر غير معروف
                                row.append(sp.Symbol(elem_str))
                    
                    if row:
                        matrix_rows.append(row)
                
                if matrix_rows:
                    matrices.append(sp.Matrix(matrix_rows))
            except Exception as e:
                logger.debug(f"Matrix parsing error: {e}")
                continue
    
    return matrices if matrices else None

class Memory:
    """ذاكرة ذكية مع إحصائيات"""
    
    def __init__(self, max_size=1000):
        self.cache = {}
        self.max_size = max_size
        self.stats = {"hits": 0, "misses": 0}
        self.history = []
    
    def _make_key(self, text: str) -> str:
        """إنشاء مفتاح ذاكرة آمن"""
        return hashlib.md5(text.encode()).hexdigest()[:16]  # استخدام أول 16 حرف فقط
    
    def get(self, text: str) -> Optional[Dict]:
        if len(text) > MAX_INPUT_LENGTH:
            return None
        
        key = self._make_key(text)
        if key in self.cache:
            self.stats["hits"] += 1
            logger.info(f"✅ Memory hit for: {text[:50]}...")
            return self.cache[key]
        self.stats["misses"] += 1
        return None
    
    def set(self, text: str, value: Dict):
        if len(text) > MAX_INPUT_LENGTH:
            return
        
        key = self._make_key(text)
        
        # إدارة حجم الذاكرة
        if len(self.cache) >= self.max_size:
            # حذف أقدم عنصر
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = value
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "question": text[:100],
            "model": value.get("model", "unknown")
        })
        logger.info(f"💾 Saved to memory: {text[:50]}...")
    
    def get_stats(self):
        return {**self.stats, "history_size": len(self.history), "cache_size": len(self.cache)}

class AIEngine:
    """محرك الرياضيات الهندسي المتكامل - نسخة الإنتاج الآمنة مع خطوات عرض نظيفة"""
    
    def __init__(self):
        self.memory = Memory()
        self.processing_count = 0
        # تعريف المتغيرات الرمزية الشائعة
        self.x, self.y, self.z, self.t, self.n, self.k = sp.symbols('x y z t n k')
        print("✅ AI Engine v8.0 - محرك رياضي آمن مع خطوات عرض نظيفة")
        logger.info("AI Engine v8.0 initialized with security measures and clean steps")
    
    def _log_processing(self, question: str, template: str, result: StepResult):
        """تسجيل معالجة سؤال"""
        self.processing_count += 1
        logger.info(f"📝 Processed #{self.processing_count}: {template} - {question[:50]}...")
    
    def _get_symbols_from_expr(self, expr: sp.Expr) -> List[sp.Symbol]:
        """استخراج المتغيرات من تعبير"""
        return list(expr.free_symbols)
    
    def _validate_input(self, question: str) -> bool:
        """التحقق من صحة المدخلات"""
        if not question or len(question) > MAX_INPUT_LENGTH:
            logger.warning(f"Invalid input length: {len(question) if question else 0}")
            return False
        return True
    
    # ========== القوالب الأساسية ==========
    
    async def template_calculator(self, question: str) -> Optional[StepResult]:
        """
        قالب الآلة الحاسبة المتقدمة
        أمثلة: "2+2", "sin(pi/2)", "sqrt(2)", "2^3 + 4*2"
        """
        if not self._validate_input(question):
            return None
        
        # إزالة الكلمات غير المرغوب فيها
        clean_q = re.sub(r'(احسب|حساب|قيمة|كم|أوجد|calculate|value of|find)', '', question.lower()).strip()
        
        async def calculate():
            expr = safe_sympify(clean_q)
            if expr is None:
                return None
            
            # تقييم التعبير
            result = expr.evalf()
            result_float = float(result)
            
            steps = [
                Step("📥", "السؤال", f"حساب: {clean_q}"),
                Step("🔍", "التحليل", "تعبير رياضي بسيط يتطلب عمليات حسابية")
            ]
            
            # محاولة التبسيط إن أمكن
            try:
                simplified = sp.simplify(expr)
                if simplified != expr:
                    steps.append(Step("📝", "التبسيط", f"تبسيط التعبير إلى {simplified}", sp.latex(simplified)))
            except:
                pass
            
            # إظهار النتيجة الدقيقة إن وجدت
            if result.is_Rational and result.q != 1:
                steps.append(Step("🧮", "الحساب", f"{clean_q} = {expr}", sp.latex(expr)))
                steps.append(Step("📊", "القيمة التقريبية", f"≈ {result_float:.6f}"))
            else:
                steps.append(Step("🧮", "الحساب", f"{clean_q} = {result_float}"))
            
            steps.append(Step("✅", "النتيجة", str(result_float)))
            
            self._log_processing(question, "calculator", None)
            return StepResult(
                success=True,
                result=result_float,
                result_str=str(result_float),
                steps=steps,
                model="calculator",
                extracted_data={"expression": clean_q}
            )
        
        # تنفيذ مع مهلة زمنية
        return await run_with_timeout(calculate())
    
    async def template_sqrt(self, question: str) -> Optional[StepResult]:
        """
        قالب الجذر التربيعي - نسخة مصححة
        أمثلة: "جذر 16", "sqrt 25", "√2", "sqrt(2)"
        """
        if not self._validate_input(question):
            return None
        
        patterns = [
            # نمط: جذر 16
            (r'(جذر|sqrt|جذ|√)\s*(-?\d+\.?\d*|\([^)]+\)|[a-zA-Z]+)', 2),
            
            # نمط: sqrt(16)
            (r'sqrt\s*\(\s*(-?\d+\.?\d*|[^)]+)\s*\)', 1),
            
            # نمط: square root of 16
            (r'square\s*root\s*of\s*(-?\d+\.?\d*|[^)]+)', 1)
        ]
        
        for pattern, group_idx in patterns:
            match = re.search(pattern, question.lower())
            if match:
                arg = match.group(group_idx).strip()
                
                async def calculate_sqrt():
                    expr = safe_sympify(arg)
                    if expr is None:
                        return None
                    
                    result = sp.sqrt(expr)
                    simplified = sp.simplify(result)
                    
                    steps = [
                        Step("📥", "السؤال", f"إيجاد الجذر التربيعي لـ {arg}"),
                        Step("🔍", "التحليل", f"نريد حساب √{arg}"),
                        Step("📝", "القانون", "الجذر التربيعي: √a = a^(1/2)")
                    ]
                    
                    # قيمة تقريبية إن أمكن
                    try:
                        float_val = float(simplified.evalf())
                        if simplified != float_val:
                            steps.append(Step("🧮", "الحساب", f"√({arg}) = {simplified}", sp.latex(simplified)))
                            steps.append(Step("📊", "القيمة التقريبية", f"≈ {float_val:.6f}"))
                        else:
                            steps.append(Step("🧮", "الحساب", f"√({arg}) = {simplified}", sp.latex(simplified)))
                    except:
                        steps.append(Step("🧮", "الحساب", f"√({arg}) = {simplified}", sp.latex(simplified)))
                    
                    steps.append(Step("✅", "النتيجة", str(simplified)))
                    
                    self._log_processing(question, "sqrt", None)
                    return StepResult(
                        success=True,
                        result=simplified,
                        result_str=str(simplified),
                        steps=steps,
                        model="sqrt",
                        extracted_data={"argument": arg}
                    )
                
                return await run_with_timeout(calculate_sqrt())
        return None
    
    async def template_power(self, question: str) -> Optional[StepResult]:
        """
        قالب الرفع للقوة
        أمثلة: "2^3", "5^2", "2 أس 3", "2^0.5", "x^2"
        """
        if not self._validate_input(question):
            return None
        
        patterns = [
            r'([^=\s]+)\s*[\^أس]\s*([^=\s]+)',
            r'power\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, question.lower())
            if match:
                base_str = match.group(1).strip()
                exp_str = match.group(2).strip()
                
                async def calculate_power():
                    base = safe_sympify(base_str)
                    exp = safe_sympify(exp_str)
                    
                    if base is None or exp is None:
                        return None
                    
                    result = sp.Pow(base, exp, evaluate=False)
                    simplified = sp.simplify(result)
                    
                    steps = [
                        Step("📥", "السؤال", f"حساب {base_str} ^ {exp_str}"),
                        Step("🔍", "التحليل", f"رفع {base_str} إلى القوة {exp_str}"),
                        Step("📝", "القانون", f"a^b = a مرفوعة للقوة b")
                    ]
                    
                    # قيمة تقريبية إن أمكن
                    try:
                        float_val = float(simplified.evalf())
                        if simplified != float_val:
                            steps.append(Step("🧮", "الحساب", f"{base_str}^{exp_str} = {simplified}", sp.latex(simplified)))
                            steps.append(Step("📊", "القيمة التقريبية", f"≈ {float_val:.6f}"))
                        else:
                            steps.append(Step("🧮", "الحساب", f"{base_str}^{exp_str} = {simplified}", sp.latex(simplified)))
                    except:
                        steps.append(Step("🧮", "الحساب", f"{base_str}^{exp_str} = {simplified}", sp.latex(simplified)))
                    
                    steps.append(Step("✅", "النتيجة", str(simplified)))
                    
                    self._log_processing(question, "power", None)
                    return StepResult(
                        success=True,
                        result=simplified,
                        result_str=str(simplified),
                        steps=steps,
                        model="power",
                        extracted_data={"base": base_str, "exponent": exp_str}
                    )
                
                return await run_with_timeout(calculate_power())
        return None
    
    # ========== قوالب المعادلات ==========
    
    async def template_solve_equation(self, question: str) -> Optional[StepResult]:
        """
        قالب حل المعادلات (يدعم أي متغيرات)
        أمثلة: "2x + 3 = 7", "2y + 3 = 7", "x^2 - 5x + 6 = 0", "sin(x) = 0.5"
        """
        if not self._validate_input(question):
            return None
        
        equation = extract_equation_parts(question)
        if not equation:
            return None
        
        left, right = equation
        
        async def solve():
            # تحويل الطرفين إلى تعابير SymPy
            left_expr = safe_sympify(left)
            right_expr = safe_sympify(right)
            
            if left_expr is None or right_expr is None:
                return None
            
            # تكوين المعادلة: left - right = 0
            equation_expr = left_expr - right_expr
            
            # استخراج المتغيرات المستخدمة
            symbols = self._get_symbols_from_expr(equation_expr)
            
            steps = [
                Step("📥", "السؤال", f"حل المعادلة: {left} = {right}"),
                Step("🔍", "التحليل", f"المعادلة تحتوي على المتغيرات: {', '.join([str(s) for s in symbols]) if symbols else 'لا يوجد متغيرات'}")
            ]
            
            if not symbols:
                # معادلة بدون متغيرات (تحقق من صحة)
                if equation_expr == 0:
                    steps.append(Step("✅", "التحقق", "المعادلة صحيحة دائماً (تطابق)"))
                    return StepResult(
                        success=True,
                        result="المعادلة صحيحة دائماً",
                        result_str="المعادلة صحيحة دائماً",
                        steps=steps,
                        model="solve_equation",
                        extracted_data={"left": left, "right": right}
                    )
                else:
                    steps.append(Step("❌", "التحقق", f"المعادلة خاطئة: {equation_expr} ≠ 0"))
                    return StepResult(
                        success=False,
                        error="المعادلة غير صحيحة",
                        steps=steps,
                        model="solve_equation",
                        extracted_data={"left": left, "right": right}
                    )
            
            steps.append(Step("📝", "إعادة الترتيب", f"{left} - {right} = 0 → {equation_expr}", sp.latex(equation_expr)))
            
            # حل المعادلة لجميع المتغيرات
            solutions = sp.solve(equation_expr, symbols)
            
            if not solutions:
                steps.append(Step("⚠️", "نتيجة", "لا يوجد حل للمعادلة"))
                return StepResult(
                    success=False,
                    error="لا يوجد حل للمعادلة",
                    steps=steps,
                    model="solve_equation",
                    extracted_data={"left": left, "right": right}
                )
            
            # تنسيق النتائج
            if isinstance(solutions, dict):
                # حلول متعددة لمتغيرات متعددة
                result_parts = []
                for var, val in solutions.items():
                    result_parts.append(f"{var} = {val}")
                result_str = ', '.join(result_parts)
                steps.append(Step("🧮", "الحل", result_str))
            elif isinstance(solutions, list):
                # قائمة حلول
                if len(symbols) == 1:
                    var = symbols[0]
                    if len(solutions) == 1:
                        result_str = f"{var} = {solutions[0]}"
                    else:
                        result_str = f"{var} ∈ {solutions}"
                    steps.append(Step("🧮", "الحل", result_str))
                else:
                    result_str = str(solutions)
                    steps.append(Step("🧮", "الحلول", result_str))
            else:
                # حل وحيد
                var = symbols[0]
                result_str = f"{var} = {solutions}"
                steps.append(Step("🧮", "الحل", result_str))
            
            steps.append(Step("✅", "النتيجة النهائية", result_str))
            
            self._log_processing(question, "solve_equation", None)
            return StepResult(
                success=True,
                result=result_str,
                result_str=result_str,
                steps=steps,
                model="solve_equation",
                extracted_data={"left": left, "right": right, "symbols": [str(s) for s in symbols]}
            )
        
        return await run_with_timeout(solve())
    
    async def template_quadratic_formula(self, question: str) -> Optional[StepResult]:
        """
        قالب عرض القانون العام للمعادلة التربيعية (ميزة تعليمية)
        أمثلة: "قانون المعادلة التربيعية", "quadratic formula"
        """
        if not self._validate_input(question):
            return None
        
        if any(kw in question.lower() for kw in ['قانون', 'formula', 'quadratic', 'تربيعية', 'القانون']):
            steps = [
                Step("📥", "السؤال", "طلب عرض القانون العام للمعادلة التربيعية"),
                Step("🔍", "الشرح", "المعادلة التربيعية هي معادلة من الدرجة الثانية على الصورة: ax² + bx + c = 0"),
                Step("📝", "القانون العام", "x = (-b ± √(b² - 4ac)) / (2a)", 
                     "x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}"),
                Step("📊", "حيث", 
                     "• a: معامل x²\n• b: معامل x\n• c: الحد الثابت\n• Δ = b² - 4ac: المميز"),
                Step("📈", "تحليل المميز",
                     "• إذا كان Δ > 0: حلان حقيقيان مختلفان\n• إذا كان Δ = 0: حل حقيقي مكرر\n• إذا كان Δ < 0: حلان مركبان"),
                Step("✅", "الخلاصة", "القانون العام يحل أي معادلة تربيعية")
            ]
            
            return StepResult(
                success=True,
                result="القانون العام للمعادلة التربيعية",
                result_str="القانون العام للمعادلة التربيعية",
                steps=steps,
                model="quadratic_formula"
            )
        return None
    
    async def template_system_equations(self, question: str) -> Optional[StepResult]:
        """
        قالب نظام معادلات
        أمثلة: "2x+3y=5, 4x-2y=10", "x+y+z=6, 2x-y+z=3, x+2y-z=2"
        """
        if not self._validate_input(question):
            return None
        
        equations = extract_system_equations(question)
        if not equations:
            return None
        
        async def solve_system():
            # تحويل المعادلات إلى تعابير SymPy
            exprs = []
            all_symbols = set()
            
            steps = [Step("📥", "السؤال", f"حل نظام المعادلات: {', '.join([f'{l}={r}' for l, r in equations])}")]
            
            for left, right in equations:
                left_expr = safe_sympify(left)
                right_expr = safe_sympify(right)
                
                if left_expr is None or right_expr is None:
                    return None
                
                exprs.append(left_expr - right_expr)
                
                # جمع المتغيرات
                for symbol in left_expr.free_symbols:
                    all_symbols.add(symbol)
                for symbol in right_expr.free_symbols:
                    all_symbols.add(symbol)
            
            symbols_list = list(all_symbols)
            steps.append(Step("🔍", "التحليل", f"المتغيرات في النظام: {', '.join([str(s) for s in symbols_list])}"))
            
            # حل النظام
            solution = sp.solve(exprs, symbols_list)
            
            if not solution:
                steps.append(Step("⚠️", "نتيجة", "لا يوجد حل للنظام"))
                return StepResult(
                    success=False,
                    error="لا يوجد حل للنظام",
                    steps=steps,
                    model="system_equations"
                )
            
            # تنسيق النتائج
            if isinstance(solution, list):
                # عدة حلول
                steps.append(Step("📊", "عدد الحلول", f"تم إيجاد {len(solution)} حلول"))
                for i, sol in enumerate(solution):
                    sol_str = ', '.join([f"{var} = {sol[var]}" for var in symbols_list])
                    steps.append(Step(f"🔢", f"الحل {i+1}", sol_str))
                result_str = f"تم إيجاد {len(solution)} حلول"
            else:
                # حل وحيد
                result_parts = []
                for var, val in solution.items():
                    result_parts.append(f"{var} = {val}")
                result_str = ', '.join(result_parts)
                steps.append(Step("🧮", "الحل", result_str))
            
            steps.append(Step("✅", "النتيجة النهائية", result_str))
            
            self._log_processing(question, "system_equations", None)
            return StepResult(
                success=True,
                result=result_str,
                result_str=result_str,
                steps=steps,
                model="system_equations",
                extracted_data={"equations": [(l, r) for l, r in equations]}
            )
        
        return await run_with_timeout(solve_system())
    
    # ========== قوالب التفاضل والتكامل ==========
    
    async def template_derivative(self, question: str) -> Optional[StepResult]:
        """
        قالب المشتقات
        أمثلة: "اشتق x^2", "مشتقة sin(x)", "derivative of x^3", "d/dx (x^2 + 2x)"
        """
        if not self._validate_input(question):
            return None
        
        patterns = [
            r'(اشتق|مشتقة|derivative|d/dx)\s*(?:of)?\s*(.+)',
            r'(مشتق)\s*(.+)',
            r'\'?\s*\(\s*(.+)\s*\)\''
        ]
        
        func_str = None
        for pattern in patterns:
            match = re.search(pattern, question.lower())
            if match:
                func_str = match.group(2).strip() if len(match.groups()) > 1 else match.group(1).strip()
                func_str = re.sub(r'بالنسبة\s+ل[ـx]', '', func_str)
                break
        
        if not func_str:
            return None
        
        async def calculate_derivative():
            # تحويل الدالة إلى تعبير SymPy
            expr = safe_sympify(func_str)
            if expr is None:
                return None
            
            # استخراج المتغيرات
            symbols = self._get_symbols_from_expr(expr)
            if not symbols:
                var = self.x
            else:
                var = symbols[0]  # المشتقة بالنسبة لأول متغير
            
            steps = [
                Step("📥", "السؤال", f"إيجاد مشتقة: {func_str}"),
                Step("🔍", "التحليل", f"نريد حساب المشتقة بالنسبة للمتغير {var}"),
                Step("📝", "قاعدة الاشتقاق", "تطبيق قواعد الاشتقاق المناسبة")
            ]
            
            # حساب المشتقة
            derivative = sp.diff(expr, var)
            simplified = sp.simplify(derivative)
            
            steps.append(Step("🧮", "الحساب", f"d/d{var} ({func_str}) = {simplified}", sp.latex(simplified)))
            steps.append(Step("✅", "النتيجة", str(simplified)))
            
            self._log_processing(question, "derivative", None)
            return StepResult(
                success=True,
                result=simplified,
                result_str=str(simplified),
                steps=steps,
                model="derivative",
                extracted_data={"function": func_str, "variable": str(var)}
            )
        
        return await run_with_timeout(calculate_derivative())
    
    async def template_integral(self, question: str) -> Optional[StepResult]:
        """
        قالب التكامل (يدعم المحدد وغير المحدد)
        أمثلة: "∫ x^2 dx", "تكامل x^2", "∫_0^1 x^2 dx"
        """
        if not self._validate_input(question):
            return None
        
        # محاولة استخراج تكامل محدد
        definite_patterns = [
            r'∫[_\^]?\{?(-?\d+\.?\d*)\}?\^?\{?(-?\d+\.?\d*|∞)\}?\s*([^d]+)d\w',
            r'(تكامل|integral).*من\s*(-?\d+\.?\d*)\s*إلى\s*(-?\d+\.?\d*|∞)\s*([^d]+)',
            r'\[(-?\d+\.?\d*),(-?\d+\.?\d*)\]\s*([^d]+)d\w'
        ]
        
        for pattern in definite_patterns:
            match = re.search(pattern, question.lower())
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    lower, upper, func_str = groups
                else:
                    func_str = groups[3]
                    lower, upper = groups[0], groups[1]
                
                async def calculate_definite():
                    expr = safe_sympify(func_str)
                    if expr is None:
                        return None
                    
                    # تحويل قيمة النهاية
                    if upper in ['∞', 'infinity']:
                        upper_val = sp.oo
                        upper_display = "∞"
                    else:
                        upper_val = float(upper)
                        upper_display = upper
                    
                    lower_val = float(lower)
                    
                    steps = [
                        Step("📥", "السؤال", f"تكامل محدد: ∫ من {lower} إلى {upper} لـ {func_str} dx"),
                        Step("🔍", "التحليل", f"إيجاد التكامل المحدد للدالة {func_str} على الفترة [{lower}, {upper_display}]"),
                        Step("📝", "القانون", "∫ f(x) dx من a إلى b = F(b) - F(a)")
                    ]
                    
                    x = sp.Symbol('x')
                    integral = sp.integrate(expr, (x, lower_val, upper_val))
                    
                    steps.append(Step("🧮", "الحساب", f"∫ {func_str} dx = {integral}", sp.latex(integral)))
                    
                    # قيمة تقريبية
                    try:
                        float_val = float(integral.evalf())
                        if integral != float_val:
                            steps.append(Step("📊", "القيمة التقريبية", f"≈ {float_val:.6f}"))
                    except:
                        pass
                    
                    steps.append(Step("✅", "النتيجة", str(integral)))
                    
                    self._log_processing(question, "integral_definite", None)
                    return StepResult(
                        success=True,
                        result=integral,
                        result_str=str(integral),
                        steps=steps,
                        model="integral_definite",
                        extracted_data={"function": func_str, "lower": lower, "upper": upper}
                    )
                
                return await run_with_timeout(calculate_definite())
        
        # تكامل غير محدد
        indefinite_patterns = [
            r'(تكامل|integral)\s*([^d]+)\s*d\w',
            r'∫\s*([^d]+)\s*d\w',
            r'integrate\s*\(\s*([^,)]+)'
        ]
        
        for pattern in indefinite_patterns:
            match = re.search(pattern, question.lower())
            if match:
                func_str = match.group(1).strip() if len(match.groups()) == 1 else match.group(2).strip()
                
                async def calculate_indefinite():
                    expr = safe_sympify(func_str)
                    if expr is None:
                        return None
                    
                    steps = [
                        Step("📥", "السؤال", f"تكامل غير محدد: ∫ {func_str} dx"),
                        Step("🔍", "التحليل", f"إيجاد الدالة الأصلية للدالة {func_str}"),
                        Step("📝", "القانون", "∫ f(x) dx = F(x) + C")
                    ]
                    
                    x = sp.Symbol('x')
                    integral = sp.integrate(expr, x)
                    
                    steps.append(Step("🧮", "الحساب", f"∫ {func_str} dx = {integral} + C", sp.latex(integral)))
                    steps.append(Step("✅", "النتيجة", f"{integral} + C"))
                    steps.append(Step("ℹ️", "ملاحظة", "C هو ثابت التكامل"))
                    
                    self._log_processing(question, "integral_indefinite", None)
                    return StepResult(
                        success=True,
                        result=f"{integral} + C",
                        result_str=f"{integral} + C",
                        steps=steps,
                        model="integral_indefinite",
                        extracted_data={"function": func_str}
                    )
                
                return await run_with_timeout(calculate_indefinite())
        
        return None
    
    async def template_limit(self, question: str) -> Optional[StepResult]:
        """
        قالب النهايات
        أمثلة: "نهاية x^2 عندما x → 2", "limit sin(x)/x as x→0", "lim_{x→0} sin(x)/x"
        """
        if not self._validate_input(question):
            return None
        
        limit_data = extract_limit(question)
        
        if not limit_data:
            return None
        
        async def calculate_limit():
            func_str = limit_data["function"]
            var_str = limit_data["variable"]
            val_str = limit_data["value"]
            
            expr = safe_sympify(func_str)
            if expr is None:
                return None
            
            var = ALLOWED_SYMBOLS.get(var_str, sp.Symbol(var_str))
            
            # تحويل قيمة النهاية
            if val_str in ['∞', 'infinity']:
                val = sp.oo
                val_display = "∞"
            elif val_str in ['-∞', '-infinity']:
                val = -sp.oo
                val_display = "-∞"
            else:
                val = float(val_str)
                val_display = val_str
            
            steps = [
                Step("📥", "السؤال", f"إيجاد نهاية {func_str} عندما {var_str} → {val_display}"),
                Step("🔍", "التحليل", f"حساب lim_{{{var_str}→{val_display}}} {func_str}"),
                Step("📝", "القانون", "النهاية هي قيمة الدالة عندما يقترب المتغير من قيمة معينة")
            ]
            
            # حساب النهاية
            limit_val = sp.limit(expr, var, val)
            
            steps.append(Step("🧮", "الحساب", f"lim_{{{var_str}→{val_display}}} {func_str} = {limit_val}", sp.latex(limit_val)))
            steps.append(Step("✅", "النتيجة", str(limit_val)))
            
            self._log_processing(question, "limit", None)
            return StepResult(
                success=True,
                result=limit_val,
                result_str=str(limit_val),
                steps=steps,
                model="limit",
                extracted_data={"function": func_str, "variable": var_str, "approach": val_display}
            )
        
        return await run_with_timeout(calculate_limit())
    
    async def template_sum(self, question: str) -> Optional[StepResult]:
        """
        قالب المجموع - نسخة مصححة
        أمثلة: "مجموع k^2 من 1 إلى 10", "sum_{i=1}^{n} i", "∑_{k=1}^{∞} 1/k^2"
        """
        if not self._validate_input(question):
            return None
        
        sum_data = extract_sum(question)
        
        if not sum_data:
            return None
        
        async def calculate_sum():
            func_str = sum_data["function"]
            var_str = sum_data.get("variable", 'k')
            start = sum_data.get("start", 1)
            end = sum_data.get("end", 10)
            
            expr = safe_sympify(func_str)
            if expr is None:
                return None
            
            var = ALLOWED_SYMBOLS.get(var_str, sp.Symbol(var_str))
            
            steps = [
                Step("📥", "السؤال", f"حساب المجموع: ∑ {func_str} من {var_str}={start} إلى {end}"),
                Step("🔍", "التحليل", f"إيجاد مجموع قيم {func_str} عندما {var_str} يأخذ القيم من {start} إلى {end}")
            ]
            
            # حساب المجموع
            if end in ['∞', 'infinity']:
                end_display = "∞"
                sum_val = sp.Sum(expr, (var, sp.Integer(start), sp.oo)).doit()
            else:
                end_val = float(end) if isinstance(end, (int, float, str)) and str(end).replace('.', '').replace('-', '').isdigit() else end
                end_display = end
                sum_val = sp.Sum(expr, (var, sp.Integer(start), sp.Integer(end_val))).doit()
            
            steps.append(Step("🧮", "الحساب", f"∑ {func_str} = {sum_val}", sp.latex(sum_val)))
            
            # قيمة تقريبية
            try:
                float_val = float(sum_val.evalf())
                if sum_val != float_val:
                    steps.append(Step("📊", "القيمة التقريبية", f"≈ {float_val:.6f}"))
            except:
                pass
            
            steps.append(Step("✅", "النتيجة", str(sum_val)))
            
            self._log_processing(question, "sum", None)
            return StepResult(
                success=True,
                result=sum_val,
                result_str=str(sum_val),
                steps=steps,
                model="sum",
                extracted_data={"function": func_str, "variable": var_str, "start": start, "end": end_display}
            )
        
        return await run_with_timeout(calculate_sum())
    
    # ========== قوالب المصفوفات ==========
    
    async def template_matrix_operations(self, question: str) -> Optional[StepResult]:
        """
        قالب عمليات المصفوفات
        أمثلة: 
        - "محدد [[1,2],[3,4]]"
        - "معكوس [[1,2],[3,4]]"
        - "مدور [[1,2],[3,4]]"
        - "[[1,2],[3,4]] * [[5,6],[7,8]]"
        - "قيم ذاتية [[1,2],[3,4]]"
        """
        if not self._validate_input(question):
            return None
        
        matrices = extract_matrix_safe(question)
        
        if not matrices:
            return None
        
        async def calculate_matrix():
            steps = []
            result = None
            operation = ""
            
            q_lower = question.lower()
            
            if len(matrices) == 2:
                if '+' in question or 'جمع' in q_lower:
                    operation = "جمع"
                    steps = [
                        Step("📥", "السؤال", f"عملية جمع مصفوفتين"),
                        Step("🔍", "التحليل", "جمع المصفوفتين عنصراً بعنصر")
                    ]
                    steps.append(Step("📊", "المصفوفة الأولى", f"{matrices[0]}", sp.latex(matrices[0])))
                    steps.append(Step("📊", "المصفوفة الثانية", f"{matrices[1]}", sp.latex(matrices[1])))
                    result = matrices[0] + matrices[1]
                    
                elif '-' in question and 'معكوس' not in q_lower:
                    operation = "طرح"
                    steps = [
                        Step("📥", "السؤال", f"عملية طرح مصفوفتين"),
                        Step("🔍", "التحليل", "طرح المصفوفتين عنصراً من عنصر")
                    ]
                    steps.append(Step("📊", "المصفوفة الأولى", f"{matrices[0]}", sp.latex(matrices[0])))
                    steps.append(Step("📊", "المصفوفة الثانية", f"{matrices[1]}", sp.latex(matrices[1])))
                    result = matrices[0] - matrices[1]
                    
                elif '*' in question or 'ضرب' in q_lower:
                    operation = "ضرب"
                    steps = [
                        Step("📥", "السؤال", f"عملية ضرب مصفوفتين"),
                        Step("🔍", "التحليل", "ضرب المصفوفتين (صف × عمود)")
                    ]
                    steps.append(Step("📊", "المصفوفة الأولى", f"{matrices[0]}", sp.latex(matrices[0])))
                    steps.append(Step("📊", "المصفوفة الثانية", f"{matrices[1]}", sp.latex(matrices[1])))
                    result = matrices[0] * matrices[1]
                    
            elif len(matrices) == 1:
                M = matrices[0]
                
                if 'محدد' in q_lower or 'det' in q_lower:
                    operation = "محدد"
                    steps = [
                        Step("📥", "السؤال", f"إيجاد محدد المصفوفة"),
                        Step("🔍", "التحليل", "حساب محدد المصفوفة (للمصفوفات المربعة فقط)")
                    ]
                    steps.append(Step("📊", "المصفوفة", f"{M}", sp.latex(M)))
                    if M.rows == M.cols:
                        result = M.det()
                        steps.append(Step("📝", "القانون", "det(A) = مجموع حاصل ضرب العناصر مع الإشارات المناسبة"))
                    else:
                        return StepResult(
                            success=False,
                            error="المحدد يُحسب فقط للمصفوفات المربعة",
                            steps=steps,
                            model="matrix_operations"
                        )
                        
                elif 'معكوس' in q_lower or 'inverse' in q_lower:
                    operation = "معكوس"
                    steps = [
                        Step("📥", "السؤال", f"إيجاد معكوس المصفوفة"),
                        Step("🔍", "التحليل", "إيجاد المصفوفة A⁻¹ حيث A × A⁻¹ = I")
                    ]
                    steps.append(Step("📊", "المصفوفة", f"{M}", sp.latex(M)))
                    if M.rows == M.cols:
                        try:
                            result = M.inv()
                            steps.append(Step("📝", "الشرط", "المصفوفة قابلة للعكس لأن محددها ≠ 0"))
                        except Exception as e:
                            return StepResult(
                                success=False,
                                error="المصفوفة غير قابلة للعكس (محددها صفر)",
                                steps=steps,
                                model="matrix_operations"
                            )
                    else:
                        return StepResult(
                            success=False,
                            error="المعكوس يُحسب فقط للمصفوفات المربعة",
                            steps=steps,
                            model="matrix_operations"
                        )
                        
                elif 'مدور' in q_lower or 'transpose' in q_lower:
                    operation = "مدور"
                    steps = [
                        Step("📥", "السؤال", f"إيجاد مدور المصفوفة"),
                        Step("🔍", "التحليل", "تبديل الأعمدة بالصفوف")
                    ]
                    steps.append(Step("📊", "المصفوفة", f"{M}", sp.latex(M)))
                    result = M.T
                    
                elif 'قيم' in q_lower and 'ذاتية' in q_lower or 'eigenvalue' in q_lower:
                    operation = "قيم ذاتية"
                    steps = [
                        Step("📥", "السؤال", f"إيجاد القيم الذاتية للمصفوفة"),
                        Step("🔍", "التحليل", "إيجاد λ حيث det(A - λI) = 0")
                    ]
                    steps.append(Step("📊", "المصفوفة", f"{M}", sp.latex(M)))
                    if M.rows == M.cols:
                        eigenvals = M.eigenvals()
                        result = str(eigenvals)
                    else:
                        return StepResult(
                            success=False,
                            error="القيم الذاتية تُحسب فقط للمصفوفات المربعة",
                            steps=steps,
                            model="matrix_operations"
                        )
            
            if result is not None:
                steps.append(Step("🧮", "الحساب", f"النتيجة = {result}", sp.latex(result) if hasattr(result, 'shape') else None))
                steps.append(Step("✅", "النتيجة النهائية", str(result)))
                
                self._log_processing(question, "matrix_operations", None)
                return StepResult(
                    success=True,
                    result=result,
                    result_str=str(result),
                    steps=steps,
                    model=f"matrix_{operation}",
                    extracted_data={"operation": operation}
                )
            
            return None
        
        return await run_with_timeout(calculate_matrix())
    
    # ========== قوالب التحويلات ==========
    
    async def template_laplace(self, question: str) -> Optional[StepResult]:
        """
        قالب تحويل لابلاس
        أمثلة: "لاپلاس sin(t)", "laplace of e^(at)", "L{ t^2 }"
        """
        if not self._validate_input(question):
            return None
        
        patterns = [
            r'لاپلاس\s*ل?\s*([^(]+)',
            r'laplace\s*(?:of|transform)?\s*\(\s*([^,)]+)',
            r'L\s*\{\s*([^}]+)\s*\}'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, question.lower())
            if match:
                func_str = match.group(1).strip()
                
                async def calculate_laplace():
                    expr = safe_sympify(func_str)
                    if expr is None:
                        return None
                    
                    steps = [
                        Step("📥", "السؤال", f"إيجاد تحويل لابلاس للدالة: {func_str}"),
                        Step("🔍", "التحليل", f"حساب L{{{func_str}}} = ∫₀^∞ {func_str}·e^(-st) dt"),
                        Step("📝", "القانون", "تحويل لابلاس: L{f(t)} = F(s)")
                    ]
                    
                    t = sp.Symbol('t')
                    s = sp.Symbol('s')
                    
                    # تحويل لابلاس
                    laplace_transform = sp.laplace_transform(expr, t, s)
                    
                    steps.append(Step("🧮", "الحساب", f"L{{{func_str}}} = {laplace_transform[0]}", sp.latex(laplace_transform[0])))
                    steps.append(Step("📊", "شرط الوجود", f"Re(s) > {laplace_transform[1]}"))
                    steps.append(Step("✅", "النتيجة", str(laplace_transform[0])))
                    
                    self._log_processing(question, "laplace", None)
                    return StepResult(
                        success=True,
                        result=laplace_transform[0],
                        result_str=str(laplace_transform[0]),
                        steps=steps,
                        model="laplace",
                        extracted_data={"function": func_str}
                    )
                
                return await run_with_timeout(calculate_laplace())
        
        return None
    
    async def template_inverse_laplace(self, question: str) -> Optional[StepResult]:
        """
        قالب تحويل لابلاس العكسي
        أمثلة: "لاپلاس عكسي 1/(s^2+1)", "inverse laplace of 1/(s-a)"
        """
        if not self._validate_input(question):
            return None
        
        patterns = [
            r'لاپلاس\s*عكسي\s*ل?\s*([^(]+)',
            r'inverse\s*laplace\s*(?:of|transform)?\s*\(\s*([^,)]+)',
            r'L\^\{-1\}\s*\{\s*([^}]+)\s*\}'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, question.lower())
            if match:
                func_str = match.group(1).strip()
                
                async def calculate_inverse_laplace():
                    expr = safe_sympify(func_str)
                    if expr is None:
                        return None
                    
                    steps = [
                        Step("📥", "السؤال", f"إيجاد تحويل لابلاس العكسي للدالة: {func_str}"),
                        Step("🔍", "التحليل", f"حساب L⁻¹{{{func_str}}}"),
                        Step("📝", "القانون", "تحويل لابلاس العكسي: L⁻¹{F(s)} = f(t)")
                    ]
                    
                    s = sp.Symbol('s')
                    t = sp.Symbol('t')
                    
                    # تحويل لابلاس العكسي
                    inverse_laplace = sp.inverse_laplace_transform(expr, s, t)
                    
                    steps.append(Step("🧮", "الحساب", f"L⁻¹{{{func_str}}} = {inverse_laplace}", sp.latex(inverse_laplace)))
                    steps.append(Step("✅", "النتيجة", str(inverse_laplace)))
                    
                    self._log_processing(question, "inverse_laplace", None)
                    return StepResult(
                        success=True,
                        result=inverse_laplace,
                        result_str=str(inverse_laplace),
                        steps=steps,
                        model="inverse_laplace",
                        extracted_data={"function": func_str}
                    )
                
                return await run_with_timeout(calculate_inverse_laplace())
        
        return None
    
    # ========== قوالب المعادلات التفاضلية ==========
    
    async def template_differential_equation(self, question: str) -> Optional[StepResult]:
        """
        قالب حل المعادلات التفاضلية - نسخة محسنة
        أمثلة: 
        - "حل dy/dx = 2x"
        - "solve y' + y = 0"
        - "y'' - 2y' + y = 0"
        - "y'' + 4y = 0, y(0)=1, y'(0)=0"
        """
        if not self._validate_input(question):
            return None
        
        q_lower = question.lower()
        
        async def solve_de():
            # محاولة استخراج المعادلة التفاضلية
            x = sp.Symbol('x')
            y = sp.Function('y')(x)
            
            # تنظيف السؤال
            clean_q = q_lower.replace(' ', '')
            
            steps = [Step("📥", "السؤال", f"حل المعادلة التفاضلية: {question}")]
            
            # أنماط متعددة للمعادلات التفاضلية
            patterns = [
                # dy/dx = f(x,y)
                r'dy/dx=(.+)',
                
                # y' = f(x,y)
                r"y'=(.+)",
                
                # y'' + ay' + by = 0
                r"y''([+-]\d*)y'([+-]\d*)y=0",
                
                # معادلة تفاضلية خطية من الدرجة الثانية عامة
                r"([+-]?\d*)y''([+-]?\d*)y'([+-]?\d*)y=0",
                
                # y'' + ay = 0
                r"y''([+-]\d*)y=0"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, clean_q)
                if match:
                    if pattern == r'dy/dx=(.+)' or pattern == r"y'=(.+)":
                        # معادلة من الدرجة الأولى
                        rhs = match.group(1)
                        expr = safe_sympify(rhs)
                        if expr is None:
                            continue
                        
                        steps.append(Step("🔍", "التحليل", f"معادلة تفاضلية من الدرجة الأولى: dy/dx = {rhs}"))
                        steps.append(Step("📝", "القانون", "الحل: ∫ dy = ∫ f(x) dx"))
                        
                        diff_eq = sp.Eq(y.diff(x), expr)
                        solution = sp.dsolve(diff_eq, y)
                        
                        # محاولة استخراج الشروط الابتدائية
                        ics = {}
                        if 'y(0)' in q_lower:
                            ics_val = re.search(r'y\(0\)=([^,)\s]+)', q_lower)
                            if ics_val:
                                ics[y.subs(x, 0)] = float(ics_val.group(1))
                                steps.append(Step("📊", "الشرط الابتدائي", f"y(0) = {ics_val.group(1)}"))
                        
                        if "y'(0)" in q_lower:
                            ics_deriv_val = re.search(r"y'\(0\)=([^,)\s]+)", q_lower)
                            if ics_deriv_val:
                                ics[y.diff(x).subs(x, 0)] = float(ics_deriv_val.group(1))
                                steps.append(Step("📊", "الشرط الابتدائي", f"y'(0) = {ics_deriv_val.group(1)}"))
                        
                        if ics:
                            solution_with_ics = sp.dsolve(diff_eq, y, ics=ics)
                            steps.append(Step("🧮", "الحل الخاص", str(solution_with_ics), sp.latex(solution_with_ics)))
                            steps.append(Step("✅", "النتيجة", str(solution_with_ics.rhs)))
                            
                            return StepResult(
                                success=True,
                                result=str(solution_with_ics.rhs),
                                result_str=str(solution_with_ics.rhs),
                                steps=steps,
                                model="differential_equation",
                                extracted_data={"equation": question, "ics": ics}
                            )
                        else:
                            steps.append(Step("🧮", "الحل العام", str(solution), sp.latex(solution)))
                            steps.append(Step("✅", "النتيجة", str(solution.rhs)))
                            
                            return StepResult(
                                success=True,
                                result=str(solution.rhs),
                                result_str=str(solution.rhs),
                                steps=steps,
                                model="differential_equation",
                                extracted_data={"equation": question}
                            )
                    
                    elif pattern == r"y''([+-]\d*)y'([+-]\d*)y=0":
                        # معادلة من الدرجة الثانية
                        b = 0 if match.group(1) == '' else float(match.group(1))
                        c = float(match.group(2))
                        
                        steps.append(Step("🔍", "التحليل", f"معادلة تفاضلية من الدرجة الثانية: y'' + {b}y' + {c}y = 0"))
                        steps.append(Step("📝", "القانون", "المعادلة المميزة: r² + br + c = 0"))
                        
                        # بناء المعادلة: y'' + b*y' + c*y = 0
                        diff_eq = sp.Eq(y.diff(x, 2) + b*y.diff(x) + c*y, 0)
                        solution = sp.dsolve(diff_eq, y)
                        
                        steps.append(Step("🧮", "الحل العام", str(solution), sp.latex(solution)))
                        steps.append(Step("✅", "النتيجة", str(solution.rhs)))
                        
                        return StepResult(
                            success=True,
                            result=str(solution.rhs),
                            result_str=str(solution.rhs),
                            steps=steps,
                            model="differential_equation",
                            extracted_data={"equation": question}
                        )
                    
                    elif pattern == r"y''([+-]\d*)y=0":
                        # معادلة من الدرجة الثانية بدون حد y'
                        c = float(match.group(1))
                        
                        steps.append(Step("🔍", "التحليل", f"معادلة تفاضلية من الدرجة الثانية: y'' + {c}y = 0"))
                        steps.append(Step("📝", "القانون", "المعادلة المميزة: r² + c = 0"))
                        
                        diff_eq = sp.Eq(y.diff(x, 2) + c*y, 0)
                        solution = sp.dsolve(diff_eq, y)
                        
                        steps.append(Step("🧮", "الحل العام", str(solution), sp.latex(solution)))
                        steps.append(Step("✅", "النتيجة", str(solution.rhs)))
                        
                        return StepResult(
                            success=True,
                            result=str(solution.rhs),
                            result_str=str(solution.rhs),
                            steps=steps,
                            model="differential_equation",
                            extracted_data={"equation": question}
                        )
            
            return None
        
        return await run_with_timeout(solve_de())
    
    # ========== قوالب التبسيط والتحليل ==========
    
    async def template_simplify(self, question: str) -> Optional[StepResult]:
        """
        قالب تبسيط التعبيرات
        أمثلة: "بسط (x^2 + 2x + 1)", "simplify sin^2(x) + cos^2(x)"
        """
        if not self._validate_input(question):
            return None
        
        patterns = [
            r'(بسط|تبسيط|simplify)\s*(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, question.lower())
            if match:
                expr_str = match.group(2).strip()
                
                async def calculate_simplify():
                    expr = safe_sympify(expr_str)
                    if expr is None:
                        return None
                    
                    steps = [
                        Step("📥", "السؤال", f"تبسيط التعبير: {expr_str}"),
                        Step("🔍", "التحليل", "تطبيق قواعد التبسيط الجبرية")
                    ]
                    
                    simplified = sp.simplify(expr)
                    
                    steps.append(Step("🧮", "التبسيط", f"{expr_str} = {simplified}", sp.latex(simplified)))
                    steps.append(Step("✅", "النتيجة", str(simplified)))
                    
                    self._log_processing(question, "simplify", None)
                    return StepResult(
                        success=True,
                        result=simplified,
                        result_str=str(simplified),
                        steps=steps,
                        model="simplify",
                        extracted_data={"expression": expr_str}
                    )
                
                return await run_with_timeout(calculate_simplify())
        return None
    
    async def template_expand(self, question: str) -> Optional[StepResult]:
        """
        قالب فك الأقواس
        أمثلة: "فك (x+2)^2", "expand (x+1)(x+2)"
        """
        if not self._validate_input(question):
            return None
        
        patterns = [
            r'(فك|expand|نشر)\s*(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, question.lower())
            if match:
                expr_str = match.group(2).strip()
                
                async def calculate_expand():
                    expr = safe_sympify(expr_str)
                    if expr is None:
                        return None
                    
                    steps = [
                        Step("📥", "السؤال", f"فك الأقواس: {expr_str}"),
                        Step("🔍", "التحليل", "تطبيق خاصية التوزيع")
                    ]
                    
                    expanded = sp.expand(expr)
                    
                    steps.append(Step("🧮", "الفك", f"{expr_str} = {expanded}", sp.latex(expanded)))
                    steps.append(Step("✅", "النتيجة", str(expanded)))
                    
                    self._log_processing(question, "expand", None)
                    return StepResult(
                        success=True,
                        result=expanded,
                        result_str=str(expanded),
                        steps=steps,
                        model="expand",
                        extracted_data={"expression": expr_str}
                    )
                
                return await run_with_timeout(calculate_expand())
        return None
    
    async def template_factor(self, question: str) -> Optional[StepResult]:
        """
        قالب التحليل إلى عوامل
        أمثلة: "حلل x^2 - 5x + 6", "factor x^2 - 4"
        """
        if not self._validate_input(question):
            return None
        
        patterns = [
            r'(حلل|factor|تحليل)\s*(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, question.lower())
            if match:
                expr_str = match.group(2).strip()
                
                async def calculate_factor():
                    expr = safe_sympify(expr_str)
                    if expr is None:
                        return None
                    
                    steps = [
                        Step("📥", "السؤال", f"تحليل التعبير إلى عوامله: {expr_str}"),
                        Step("🔍", "التحليل", "إيجاد العوامل المشتركة")
                    ]
                    
                    factored = sp.factor(expr)
                    
                    steps.append(Step("🧮", "التحليل", f"{expr_str} = {factored}", sp.latex(factored)))
                    steps.append(Step("✅", "النتيجة", str(factored)))
                    
                    self._log_processing(question, "factor", None)
                    return StepResult(
                        success=True,
                        result=factored,
                        result_str=str(factored),
                        steps=steps,
                        model="factor",
                        extracted_data={"expression": expr_str}
                    )
                
                return await run_with_timeout(calculate_factor())
        return None
    
    # ========== الدالة الرئيسية ==========
    
    async def generate_code(self, question: str) -> Dict[str, Any]:
        """
        فهم السؤال وتنفيذ القالب المناسب
        مع ترتيب أولويات ذكي
        """
        normalized = question.lower().strip()
        
        # التحقق من صحة المدخلات
        if not self._validate_input(normalized):
            return {
                "success": False,
                "error": f"الإدخال طويل جداً. الحد الأقصى {MAX_INPUT_LENGTH} حرف."
            }
        
        logger.info(f"🔍 Processing: {question[:100]}...")
        
        # 1️⃣ البحث في الذاكرة
        cached = self.memory.get(normalized)
        if cached:
            return cached
        
        # 2️⃣ قائمة القوالب مرتبة حسب الأولوية
        templates_order = [
            # تحويلات متقدمة
            ("laplace", self.template_laplace),
            ("inverse_laplace", self.template_inverse_laplace),
            
            # معادلات تفاضلية
            ("differential_equation", self.template_differential_equation),
            
            # عمليات مصفوفات
            ("matrix_operations", self.template_matrix_operations),
            
            # نهايات ومجاميع
            ("limit", self.template_limit),
            ("sum", self.template_sum),
            
            # تفاضل وتكامل
            ("derivative", self.template_derivative),
            ("integral", self.template_integral),
            
            # أنظمة معادلات
            ("system_equations", self.template_system_equations),
            
            # معادلات
            ("solve_equation", self.template_solve_equation),
            ("quadratic_formula", self.template_quadratic_formula),
            
            # عمليات جبرية
            ("simplify", self.template_simplify),
            ("expand", self.template_expand),
            ("factor", self.template_factor),
            
            # العمليات الأساسية
            ("sqrt", self.template_sqrt),
            ("power", self.template_power),
            ("calculator", self.template_calculator),
        ]
        
        # تنفيذ القوالب حسب الأولوية
        for template_name, template_func in templates_order:
            try:
                result = await template_func(question)
                if result and result.success:
                    # حفظ في الذاكرة
                    self.memory.set(normalized, result.to_dict())
                    return result.to_dict()
            except Exception as e:
                logger.error(f"⚠️ Error in {template_name}: {e}")
                continue
        
        # 3️⃣ إذا ما لقينا قالب مناسب
        logger.warning(f"❌ No template matched: {question[:100]}...")
        return {
            "success": False,
            "error": "لم أتمكن من فهم السؤال. جرب صيغة أوضح.\n\n"
                    "✅ الأسئلة المدعومة حالياً:\n"
                    "• العمليات الحسابية: 2+2, sin(pi/2), sqrt(2)\n"
                    "• المعادلات: 2x+3=7, x^2-5x+6=0, 2y+3=7\n"
                    "• أنظمة معادلات: 2x+3y=5, 4x-2y=10\n"
                    "• التفاضل: اشتق x^2, derivative of sin(x)\n"
                    "• التكامل: ∫ x^2 dx, تكامل x^2 من 0 إلى 1\n"
                    "• النهايات: نهاية sin(x)/x عندما x→0\n"
                    "• المجاميع: مجموع k^2 من 1 إلى 10, ∑_{k=1}^{∞} 1/k^2\n"
                    "• المصفوفات: محدد [[1,2],[3,4]], معكوس, قيم ذاتية\n"
                    "• تحويلات لابلاس: لاپلاس sin(t), لاپلاس عكسي 1/(s^2+1)\n"
                    "• المعادلات التفاضلية: حل dy/dx = 2x, y'' - 2y' + y = 0\n"
                    "• التبسيط: بسط (x+1)^2, حلل x^2-4"
        }
    
    def get_stats(self):
        return {
            "memory": self.memory.get_stats(),
            "processing_count": self.processing_count
        }
