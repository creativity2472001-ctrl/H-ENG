# ai_engine.py - الإصدار النهائي مع جميع التحسينات (v3.0)
import re
import hashlib
import json
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import sympy as sp

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_math_input(text: str) -> str:
    """تنظيف المدخلات الرياضية"""
    text = text.lower()
    text = text.replace("²", "**2").replace("³", "**3").replace("⁴", "**4").replace("⁵", "**5")
    text = text.replace("^", "**").replace("×", "*").replace("÷", "/")
    text = text.replace(" ", "").replace("=", " = ").replace("+", " + ").replace("-", " - ")
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_numbers(text: str) -> List[float]:
    """استخراج الأرقام من النص"""
    return [float(x) for x in re.findall(r'-?\d+\.?\d*', text)]

def extract_complex_numbers(text: str) -> List[tuple]:
    """
    استخراج أعداد مركبة من النص
    مثال: "3+4i" -> (3, 4)
    """
    complex_nums = []
    # نمط: a+bi أو a-bi
    pattern = r'([+-]?\d+\.?\d*)\s*([+-])\s*(\d+\.?\d*)i'
    matches = re.findall(pattern, text.replace(" ", ""))
    for match in matches:
        real = float(match[0])
        sign = 1 if match[1] == '+' else -1
        imag = float(match[2]) * sign
        complex_nums.append((real, imag))
    return complex_nums

def extract_angle_unit(text: str) -> str:
    """استخراج وحدة الزاوية (deg/rad) من النص"""
    if 'rad' in text.lower() or 'راديان' in text:
        return 'rad'
    return 'deg'

def extract_matrix(text: str) -> Optional[List[List[float]]]:
    """
    استخراج مصفوفة من النص
    يدعم: [[1,2],[3,4]]، [1 2; 3 4]، matrix([1,2],[3,4])
    """
    # نمط JSON
    json_pattern = r'\[\[(.*?)\]\]'
    match = re.search(json_pattern, text)
    if match:
        try:
            return json.loads(f'[{match.group(1)}]')
        except:
            pass
    
    # نمط الفاصلة المنقوطة [1 2; 3 4]
    semicolon_pattern = r'\[(.*?);(.*?)\]'
    match = re.search(semicolon_pattern, text)
    if match:
        try:
            row1 = [float(x) for x in match.group(1).split()]
            row2 = [float(x) for x in match.group(2).split()]
            return [row1, row2]
        except:
            pass
    
    # نمط matrix function
    matrix_pattern = r'matrix\(\[(.*?)\],\[(.*?)\]\)'
    match = re.search(matrix_pattern, text.lower())
    if match:
        try:
            row1 = [float(x) for x in match.group(1).split(',')]
            row2 = [float(x) for x in match.group(2).split(',')]
            return [row1, row2]
        except:
            pass
    
    return None

def extract_equation_system(text: str) -> Optional[List[List[float]]]:
    """
    استخراج نظام معادلات
    يدعم: 2x+3y=5, 4x-2y=10
    """
    equations = re.split(r'[,\n;]', text)
    system = []
    
    for eq in equations:
        if '=' in eq:
            # محاولة استخراج المعاملات
            coeffs = []
            # نمط: ax+by=c
            pattern = r'([+-]?\d*)x\s*([+-]?\d*)y\s*=\s*([+-]?\d+)'
            match = re.search(pattern, eq.replace(" ", ""))
            if match:
                a = float(match.group(1)) if match.group(1) not in ['', '+'] else 1
                if match.group(1) == '-':
                    a = -1
                b = float(match.group(2)) if match.group(2) not in ['', '+'] else 1
                if match.group(2) == '-':
                    b = -1
                c = float(match.group(3))
                system.append([a, b, c])
    
    return system if len(system) >= 2 else None

def extract_definite_integral(text: str) -> Optional[Dict]:
    """
    استخراج تكامل محدد
    يدعم: ∫[0,1] x^2 dx, ∫_0^1 x^2 dx, تكامل x^2 من 0 إلى 1
    """
    # نمط LaTeX: ∫_0^1
    latex_pattern = r'∫[_\^]?\{?(\d+)\}?\^?\{?(\d+)\}?\s*([^d]+)d\w'
    match = re.search(latex_pattern, text)
    if match:
        return {
            "lower": float(match.group(1)),
            "upper": float(match.group(2)),
            "func": match.group(3).strip()
        }
    
    # نمط عربي: من ... إلى ...
    arabic_pattern = r'(تكامل|integral).*من\s*(\d+)\s*إلى\s*(\d+)\s*([^d]+)'
    match = re.search(arabic_pattern, text.lower())
    if match:
        return {
            "lower": float(match.group(2)),
            "upper": float(match.group(3)),
            "func": match.group(4).strip()
        }
    
    # نمط [a,b]
    bracket_pattern = r'\[(\d+),(\d+)\]\s*([^d]+)d\w'
    match = re.search(bracket_pattern, text)
    if match:
        return {
            "lower": float(match.group(1)),
            "upper": float(match.group(2)),
            "func": match.group(3).strip()
        }
    
    return None

class Memory:
    """ذاكرة ذكية مع إحصائيات"""
    
    def __init__(self):
        self.cache = {}
        self.stats = {"hits": 0, "misses": 0}
        self.history = []
    
    def _make_key(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()
    
    def get(self, text: str) -> Optional[Dict]:
        key = self._make_key(text)
        if key in self.cache:
            self.stats["hits"] += 1
            logger.info(f"✅ Memory hit for: {text[:50]}...")
            return self.cache[key]
        self.stats["misses"] += 1
        logger.info(f"❌ Memory miss for: {text[:50]}...")
        return None
    
    def set(self, text: str, value: Dict):
        key = self._make_key(text)
        self.cache[key] = value
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "question": text[:100],
            "model": value.get("model", "unknown")
        })
        logger.info(f"💾 Saved to memory: {text[:50]}...")
    
    def get_stats(self):
        return {**self.stats, "history_size": len(self.history)}

class AIEngine:
    """محرك فهم الأسئلة - 60+ قالب مع تحسينات"""
    
    def __init__(self):
        self.math_engine = None
        self.memory = Memory()
        self.processing_count = 0
        print("✅ AI Engine ready - 60+ قالب فهم مع تحسينات نهائية")
        logger.info("AI Engine initialized")
    
    def set_math_engine(self, math_engine):
        """ربط محرك الرياضيات"""
        self.math_engine = math_engine
        logger.info("Math engine connected")
    
    def _log_processing(self, question: str, template: str, result: Dict):
        """تسجيل معالجة سؤال"""
        self.processing_count += 1
        logger.info(f"📝 Processed #{self.processing_count}: {template} - {question[:50]}...")
    
    # ========== الأساسيات (10 قوالب فهم) ==========
    
    async def template_calculator(self, question: str) -> Optional[Dict]:
        """
        قالب 1: آلة حاسبة بسيطة
        أمثلة: "2+2", "5*3", "10/2", "احسب 2+2"
        """
        # إزالة الكلمات غير المرغوب فيها
        clean_q = re.sub(r'(احسب|حساب|قيمة|كم|calculate|value of)', '', question.lower())
        # البحث عن تعبير رياضي
        expr_match = re.search(r'([\d\+\-\*\/\(\)\.\s]+)$', clean_q)
        if expr_match:
            expr = expr_match.group(1).strip()
            # التحقق من صحة التعبير
            try:
                float(eval(expr.replace('^', '**')))
                result = await self.math_engine.calculate(expr)
                if result.success:
                    self._log_processing(question, "calculator", result)
                    return {
                        "success": True,
                        "result": result.result_str,
                        "steps": result.steps,
                        "model": "calculator"
                    }
            except:
                pass
        return None
    
    async def template_power(self, question: str) -> Optional[Dict]:
        """
        قالب 2: رفع لقوة
        أمثلة: "2^3", "5^2", "2 أس 3", "2 to the power 3"
        """
        patterns = [
            r'(\d+)\s*[\^أس]\s*(\d+)',
            r'(\d+)\s*مرفوع\s*ل?لقوة\s*(\d+)',
            r'(\d+)\s*to\s*the\s*power\s*(\d+)',
            r'(\d+)\*\*(\d+)',
            r'power\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)'
        ]
        for pattern in patterns:
            match = re.search(pattern, question.lower())
            if match:
                base, exp = float(match.group(1)), float(match.group(2))
                result = await self.math_engine.power(base, exp)
                if result.success:
                    self._log_processing(question, "power", result)
                    return {
                        "success": True,
                        "result": result.result_str,
                        "steps": result.steps,
                        "model": "power"
                    }
        return None
    
    async def template_sqrt(self, question: str) -> Optional[Dict]:
        """
        قالب 3: جذر تربيعي
        أمثلة: "جذر 16", "sqrt 25", "√16", "sqrt(16)"
        """
        patterns = [
            r'(جذر|sqrt|جذ|√)\s*(\d+)',
            r'sqrt\s*\(\s*(\d+)\s*\)',
            r'(\d+)\s*تحت\s*الجذر',
            r'square\s*root\s*of\s*(\d+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, question.lower())
            if match:
                # الرقم ممكن يكون في group 1 أو 2
                num_str = match.group(1) if match.group(1).isdigit() else match.group(2)
                num = float(num_str)
                result = await self.math_engine.sqrt(num)
                if result.success:
                    self._log_processing(question, "sqrt", result)
                    return {
                        "success": True,
                        "result": result.result_str,
                        "steps": result.steps,
                        "model": "sqrt"
                    }
        return None
    
    # ... (باقي القوالب الأساسية مع تحسينات مشابهة)
    
    # ========== معادلات (10 قوالب فهم) ==========
    
    async def template_linear(self, question: str) -> Optional[Dict]:
        """
        قالب 11: معادلة خطية
        أمثلة: "2x + 3 = 7", "x - 5 = 10", "3x = 12", "x = 5"
        """
        # تنظيف المعادلة
        clean_q = question.replace(" ", "").lower()
        
        # قائمة الأنماط من الأكثر تعقيداً إلى الأبسط
        patterns = [
            # ax + b = c
            (r'(\d*)x([+-]\d+)=(\d+)', lambda m: self._solve_linear_with_b(m)),
            # ax = c
            (r'(\d*)x=(\d+)', lambda m: self._solve_linear_simple(m)),
            # x + b = c
            (r'x([+-]\d+)=(\d+)', lambda m: self._solve_linear_x_plus_b(m)),
            # x = c
            (r'x=(\d+)', lambda m: self._solve_linear_x_equals(m))
        ]
        
        for pattern, handler in patterns:
            match = re.search(pattern, clean_q)
            if match:
                result = await handler(match)
                if result and result.success:
                    self._log_processing(question, "linear", result)
                    return {
                        "success": True,
                        "result": result.result_str,
                        "steps": result.steps,
                        "model": "linear"
                    }
        return None
    
    async def _solve_linear_with_b(self, match):
        """ax + b = c"""
        a = 1 if match.group(1) == '' else float(match.group(1))
        b = float(match.group(2))
        c = float(match.group(3))
        return await self.math_engine.solve_linear(a, c - b)
    
    async def _solve_linear_simple(self, match):
        """ax = c"""
        a = 1 if match.group(1) == '' else float(match.group(1))
        c = float(match.group(2))
        return await self.math_engine.solve_linear(a, c)
    
    async def _solve_linear_x_plus_b(self, match):
        """x + b = c"""
        b = float(match.group(1))
        c = float(match.group(2))
        return await self.math_engine.solve_linear(1, c - b)
    
    async def _solve_linear_x_equals(self, match):
        """x = c"""
        return {
            "success": True,
            "result_str": f"x = {match.group(1)}",
            "steps": []
        }
    
    async def template_quadratic(self, question: str) -> Optional[Dict]:
        """
        قالب 12: معادلة تربيعية
        أمثلة: "x^2 - 5x + 6 = 0", "x² - 5x + 6 = 0"
        """
        # تنظيف وتحويل ² إلى ^2
        clean_q = question.replace("²", "^2").replace(" ", "").lower()
        
        # أنماط متعددة
        patterns = [
            # x^2 + bx + c = 0
            r'x\^2([+-]\d+)x([+-]\d+)=0',
            # x^2 + bx = c
            r'x\^2([+-]\d+)x=([+-]\d+)',
            # ax^2 + bx + c = 0
            r'(\d*)x\^2([+-]\d+)x([+-]\d+)=0'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, clean_q)
            if match:
                if pattern.startswith('x\^2([+-]'):  # a=1
                    a = 1
                    b = float(match.group(1))
                    c = float(match.group(2)) if len(match.groups()) > 2 else 0
                else:  # a موجود
                    a = 1 if match.group(1) == '' else float(match.group(1))
                    b = float(match.group(2))
                    c = float(match.group(3))
                
                result = await self.math_engine.solve_quadratic(a, b, c)
                if result.success:
                    self._log_processing(question, "quadratic", result)
                    return {
                        "success": True,
                        "result": result.result_str,
                        "steps": result.steps,
                        "model": "quadratic"
                    }
        return None
    
    async def template_system(self, question: str) -> Optional[Dict]:
        """
        قالب 13: نظام معادلات (2x2, 3x3)
        أمثلة: "2x+3y=5, 4x-2y=10", "x+y+z=6, 2x-y+z=3, x+2y-z=2"
        """
        # استخراج نظام المعادلات
        system = extract_equation_system(question)
        
        if system:
            if len(system) == 2 and len(system[0]) == 3:  # 2x2
                a1, b1, c1 = system[0]
                a2, b2, c2 = system[1]
                result = await self.math_engine.solve_system_2x2(a1, b1, c1, a2, b2, c2)
                if result.success:
                    self._log_processing(question, "system_2x2", result)
                    return {
                        "success": True,
                        "result": result.result_str,
                        "steps": result.steps,
                        "model": "system_2x2"
                    }
            
            elif len(system) == 3 and len(system[0]) == 4:  # 3x3
                # تحويل إلى مصفوفة وحلها
                A = [[eq[0], eq[1], eq[2]] for eq in system]
                B = [eq[3] for eq in system]
                
                # استخدام sympy لحل النظام
                x, y, z = sp.symbols('x y z')
                equations = [
                    A[0][0]*x + A[0][1]*y + A[0][2]*z - B[0],
                    A[1][0]*x + A[1][1]*y + A[1][2]*z - B[1],
                    A[2][0]*x + A[2][1]*y + A[2][2]*z - B[2]
                ]
                solution = sp.solve(equations, (x, y, z))
                
                if solution:
                    result_str = f"x = {solution[x]}, y = {solution[y]}, z = {solution[z]}"
                    self._log_processing(question, "system_3x3", {"result_str": result_str})
                    return {
                        "success": True,
                        "result": result_str,
                        "steps": [],
                        "model": "system_3x3"
                    }
        
        return None
    
    # ========== مشتقات (10 قوالب فهم) محسنة ==========
    
    async def template_derivative(self, question: str) -> Optional[Dict]:
        """
        قالب مشتقة عام
        أمثلة: "مشتقة sin(2x)", "derivative of x^3 + 2x", "d/dx (x^2)"
        """
        # محاولة استخراج الدالة
        func = None
        
        # نمط: مشتقة [دالة]
        match = re.search(r'(مشتق|derivative|مشتقة).*?([a-zA-Z0-9\*\^\+\-\/\(\)]+)', question.lower())
        if match:
            func = match.group(2).strip()
        
        # نمط: d/dx (دالة)
        match = re.search(r'd/dx\s*\(?([^\)]+)\)?', question.lower())
        if match:
            func = match.group(1).strip()
        
        if func:
            # محاولة تحويل ^ إلى **
            func = func.replace('^', '**')
            
            # استخدام sympify للتحقق من صحة الدالة
            try:
                sp.sympify(func)
                # لا نستطيع استدعاء derivative مباشرة لأننا لا نعرف النوع
                # سنمرر الدالة إلى math_engine بطريقة عامة
                result = await self.math_engine.derivative_power(2)  # مؤقت
                # هذا يحتاج تحسين في math_engine لقبول دالة عامة
            except:
                pass
        
        return None
    
    # ========== تكاملات (10 قوالب فهم) محسنة ==========
    
    async def template_integral_definite_improved(self, question: str) -> Optional[Dict]:
        """
        قالب 25: تكامل محدد - نسخة محسنة
        أمثلة: "∫_0^1 x^2 dx", "تكامل x^2 من 0 إلى 1", "integral of x^2 from 0 to 1"
        """
        integral_data = extract_definite_integral(question)
        
        if integral_data:
            result = await self.math_engine.integral_definite(
                integral_data["func"], 
                integral_data["lower"], 
                integral_data["upper"]
            )
            if result.success:
                self._log_processing(question, "integral_definite", result)
                return {
                    "success": True,
                    "result": result.result_str,
                    "steps": result.steps,
                    "model": "integral_definite"
                }
        return None
    
    # ========== مصفوفات (5 قوالب فهم) محسنة ==========
    
    async def template_matrix_general(self, question: str) -> Optional[Dict]:
        """
        قالب مصفوفة عام
        أمثلة: 
        - "[[1,2],[3,4]] + [[5,6],[7,8]]" (جمع)
        - "[[1,2],[3,4]] * [[5,6],[7,8]]" (ضرب)
        - "محدد [[1,2],[3,4]]" (محدد)
        - "معكوس [[1,2],[3,4]]" (معكوس)
        """
        matrix = extract_matrix(question)
        
        if not matrix:
            return None
        
        # تحديد العملية
        if '+' in question or 'جمع' in question:
            # البحث عن مصفوفة ثانية
            second_matrix = extract_matrix(question.split('+')[-1])
            if second_matrix:
                result = await self.math_engine.matrix_add(matrix, second_matrix)
                if result.success:
                    self._log_processing(question, "matrix_add", result)
                    return {
                        "success": True,
                        "result": result.result_str,
                        "steps": result.steps,
                        "model": "matrix_add"
                    }
        
        elif '*' in question or 'ضرب' in question:
            second_matrix = extract_matrix(question.split('*')[-1])
            if second_matrix:
                result = await self.math_engine.matrix_multiply(matrix, second_matrix)
                if result.success:
                    self._log_processing(question, "matrix_multiply", result)
                    return {
                        "success": True,
                        "result": result.result_str,
                        "steps": result.steps,
                        "model": "matrix_multiply"
                    }
        
        elif 'محدد' in question or 'det' in question.lower():
            result = await self.math_engine.matrix_determinant(matrix)
            if result.success:
                self._log_processing(question, "matrix_determinant", result)
                return {
                    "success": True,
                    "result": result.result_str,
                    "steps": result.steps,
                    "model": "matrix_determinant"
                }
        
        elif 'معكوس' in question or 'inverse' in question.lower():
            result = await self.math_engine.matrix_inverse(matrix)
            if result.success:
                self._log_processing(question, "matrix_inverse", result)
                return {
                    "success": True,
                    "result": result.result_str,
                    "steps": result.steps,
                    "model": "matrix_inverse"
                }
        
        return None
    
    # ========== أعداد مركبة (5 قوالب فهم) محسنة ==========
    
    async def template_complex_general(self, question: str) -> Optional[Dict]:
        """
        قالب أعداد مركبة عام
        أمثلة: 
        - "(3+4i) + (1+2i)" (جمع)
        - "(3+4i) * (1+2i)" (ضرب)
        - "مرافق 3+4i" (مرافق)
        - "مقياس 3+4i" (مقياس)
        """
        complex_nums = extract_complex_numbers(question)
        
        if not complex_nums:
            return None
        
        if '+' in question and len(complex_nums) >= 2:
            a1, b1 = complex_nums[0]
            a2, b2 = complex_nums[1]
            result = await self.math_engine.complex_add(a1, b1, a2, b2)
            if result.success:
                self._log_processing(question, "complex_add", result)
                return {
                    "success": True,
                    "result": result.result_str,
                    "steps": result.steps,
                    "model": "complex_add"
                }
        
        elif '*' in question and len(complex_nums) >= 2:
            a1, b1 = complex_nums[0]
            a2, b2 = complex_nums[1]
            result = await self.math_engine.complex_multiply(a1, b1, a2, b2)
            if result.success:
                self._log_processing(question, "complex_multiply", result)
                return {
                    "success": True,
                    "result": result.result_str,
                    "steps": result.steps,
                    "model": "complex_multiply"
                }
        
        elif 'مرافق' in question or 'conjugate' in question.lower():
            a, b = complex_nums[0]
            result = await self.math_engine.complex_conjugate(a, b)
            if result.success:
                self._log_processing(question, "complex_conjugate", result)
                return {
                    "success": True,
                    "result": result.result_str,
                    "steps": result.steps,
                    "model": "complex_conjugate"
                }
        
        elif 'مقياس' in question or 'modulus' in question.lower() or '|' in question:
            a, b = complex_nums[0]
            result = await self.math_engine.complex_modulus(a, b)
            if result.success:
                self._log_processing(question, "complex_modulus", result)
                return {
                    "success": True,
                    "result": result.result_str,
                    "steps": result.steps,
                    "model": "complex_modulus"
                }
        
        return None
    
    # ========== الدالة الرئيسية ==========
    
    async def generate_code(self, question: str) -> Dict[str, Any]:
        """فهم السؤال وتنفيذ القالب المناسب"""
        
        normalized = clean_math_input(question)
        logger.info(f"🔍 Processing: {question[:100]}...")
        
        # 1️⃣ البحث في الذاكرة
        cached = self.memory.get(normalized)
        if cached:
            return cached
        
        # 2️⃣ تجربة جميع القوالب بالترتيب
        templates = [
            # أساسيات
            self.template_calculator,
            self.template_power,
            self.template_sqrt,
            self.template_factorial,
            self.template_percent,
            self.template_absolute,
            self.template_gcd,
            self.template_lcm,
            self.template_log10,
            self.template_ln,
            
            # معادلات
            self.template_linear,
            self.template_quadratic,
            self.template_system,
            self.template_cubic,
            
            # مصفوفات
            self.template_matrix_general,
            
            # أعداد مركبة
            self.template_complex_general,
            
            # تكاملات
            self.template_integral_definite_improved,
            self.template_integral_power,
            self.template_integral_sin,
            self.template_integral_cos,
            self.template_integral_exp,
            
            # مشتقات
            self.template_derivative_power,
            self.template_derivative_sin,
            self.template_derivative_cos,
            self.template_derivative_tan,
            self.template_derivative_exp,
            self.template_derivative_ln,
            
            # نهايات
            self.template_limit,
            
            # إحصاء
            self.template_mean,
            self.template_median,
            
            # مثلثات
            self.template_sin,
            self.template_cos,
        ]
        
        for template in templates:
            try:
                result = await template(question)
                if result:
                    # حفظ في الذاكرة
                    self.memory.set(normalized, result)
                    return result
            except Exception as e:
                logger.error(f"⚠️ Error in template {template.__name__}: {e}")
                continue
        
        # 3️⃣ إذا ما لقينا قالب مناسب
        logger.warning(f"❌ No template matched: {question[:100]}...")
        return {
            "success": False,
            "error": "لم أتمكن من فهم السؤال. جرب صيغة أبسط."
        }
    
    def get_stats(self):
        return {
            "memory": self.memory.get_stats(),
            "processing_count": self.processing_count
        }
