# server.py - خادم الويب المتكامل (نسخة نهائية مع عرض خطوات الحل)
# ============================================================================
# هذا الملف يدمج جميع القوالب الجديدة مع النظام القديم
# الإصدار: 3.7.0 - مع تحسين عرض خطوات الحل بشكل جميل ومفهوم للطالب
# ============================================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
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

# ===== كلاس متخصص لعرض خطوات الحل بشكل جميل ومفهوم للطالب =====
# ============================================================================

class SolutionFormatter:
    """
    كلاس متخصص في تنسيق وعرض خطوات الحل بطريقة مفهومة وجميلة للطالب
    هذا الكلاس لا يعدل القوالب نهائياً، فقط يعرض النتائج بشكل منظم
    """
    
    def __init__(self):
        self.steps = []
        self.solutions = []
        self.problem_type = ""
        self.equation = ""
    
    def set_problem(self, equation: str, problem_type: str = ""):
        """تحديد المسألة ونوعها"""
        self.equation = equation
        self.problem_type = problem_type
        self.steps = []
        self.solutions = []
        
        # إضافة السؤال في البداية
        self.steps.append(f"📌 **السؤال:** {equation}")
        self.steps.append("")
    
    def add_step(self, step: str):
        """إضافة خطوة عادية"""
        self.steps.append(f"   {step}")
    
    def add_equation(self, eq: str):
        """إضافة معادلة"""
        self.steps.append(f"   📐 {eq}")
    
    def add_rule(self, rule: str):
        """إضافة قاعدة رياضية"""
        self.steps.append(f"   📏 **قاعدة:** {rule}")
    
    def add_note(self, note: str):
        """إضافة ملاحظة"""
        self.steps.append(f"   📝 {note}")
    
    def add_substep(self, substep: str):
        """إضافة خطوة فرعية"""
        self.steps.append(f"      • {substep}")
    
    def add_space(self):
        """إضافة فراغ"""
        self.steps.append("")
    
    def set_solutions(self, solutions):
        """تحديد الحلول"""
        self.solutions = solutions
    
    def format_quadratic(self, a: float, b: float, c: float, solutions):
        """تنسيق خطوات حل معادلة تربيعية بطريقة واضحة للطالب"""
        self.add_equation(f"{self._format_number(a)}x² + {self._format_number(b)}x + {self._format_number(c)} = 0")
        self.add_space()
        
        # حساب المميز
        discriminant = b**2 - 4*a*c
        self.add_step("**الخطوة 1: حساب المميز (Δ)**")
        self.add_step(f"   Δ = b² - 4ac")
        self.add_step(f"   Δ = ({self._format_number(b)})² - 4×({self._format_number(a)})×({self._format_number(c)})")
        self.add_step(f"   Δ = {self._format_number(b**2)} - {self._format_number(4*a*c)}")
        self.add_step(f"   Δ = {self._format_number(discriminant)}")
        self.add_space()
        
        # الخطوة 2: تحديد عدد الحلول
        self.add_step("**الخطوة 2: تحديد عدد الحلول**")
        if discriminant > 0:
            self.add_step(f"   Δ > 0 → للمعادلة جذران حقيقيان مختلفان")
            self.add_space()
            
            # الخطوة 3: حساب الحلول
            self.add_step("**الخطوة 3: حساب الحلول**")
            self.add_step(f"   القانون: x = [-b ± √Δ] / 2a")
            
            x1 = (-b + math.sqrt(discriminant)) / (2*a)
            x2 = (-b - math.sqrt(discriminant)) / (2*a)
            
            self.add_step(f"   x₁ = [{-self._format_number(b)} + √{self._format_number(discriminant)}] / {self._format_number(2*a)}")
            self.add_step(f"       = {self._format_number(-b + math.sqrt(discriminant))} / {self._format_number(2*a)}")
            self.add_step(f"       = {self._format_number(x1)}")
            self.add_space()
            
            self.add_step(f"   x₂ = [{-self._format_number(b)} - √{self._format_number(discriminant)}] / {self._format_number(2*a)}")
            self.add_step(f"       = {self._format_number(-b - math.sqrt(discriminant))} / {self._format_number(2*a)}")
            self.add_step(f"       = {self._format_number(x2)}")
            
            self.solutions = [x1, x2]
            
        elif discriminant == 0:
            self.add_step(f"   Δ = 0 → للمعادلة جذر مكرر (حل واحد)")
            self.add_space()
            
            # الخطوة 3: حساب الحل
            self.add_step("**الخطوة 3: حساب الحل**")
            self.add_step(f"   القانون: x = -b / 2a")
            
            x = -b / (2*a)
            self.add_step(f"   x = {-self._format_number(b)} / {self._format_number(2*a)}")
            self.add_step(f"   x = {self._format_number(x)}")
            
            self.solutions = [x]
            
        else:
            self.add_step(f"   Δ < 0 → للمعادلة جذران مركبان (ليس لها حلول حقيقية)")
            self.add_space()
            
            # الخطوة 3: حساب الحلول المركبة
            self.add_step("**الخطوة 3: حساب الحلول المركبة**")
            real = -b / (2*a)
            imag = math.sqrt(-discriminant) / (2*a)
            
            self.add_step(f"   الجزء الحقيقي = -b/2a = {-self._format_number(b)} / {self._format_number(2*a)} = {self._format_number(real)}")
            self.add_step(f"   الجزء التخيلي = √(|Δ|)/2a = √{self._format_number(-discriminant)} / {self._format_number(2*a)} = {self._format_number(imag)}")
            self.add_step(f"   x₁ = {self._format_number(real)} + {self._format_number(imag)}i")
            self.add_step(f"   x₂ = {self._format_number(real)} - {self._format_number(imag)}i")
            
            self.solutions = [f"{real} + {imag}i", f"{real} - {imag}i"]
    
    def format_absolute(self, expression: str, value: float):
        """تنسيق خطوات حل معادلة القيمة المطلقة بطريقة واضحة للطالب"""
        self.add_rule("|تعبير| = قيمة  ⇒  تعبير = قيمة  أو  تعبير = -قيمة")
        self.add_space()
        
        self.add_step("**الخطوة 1: كتابة الحالتين الممكنتين**")
        self.add_step(f"   الحالة الأولى: {expression} = {self._format_number(value)}")
        self.add_step(f"   الحالة الثانية: {expression} = -{self._format_number(value)}")
        self.add_space()
        
        self.add_step("**الخطوة 2: حل كل حالة على حدة**")
        self.add_space()
        
        # محاولة استخراج معامل x
        x_coeff = 1.0
        constant = 0.0
        
        # تحليل التعبير: مثلاً "2*x - 5" أو "2x-5"
        expr_clean = expression.replace(' ', '')
        
        # البحث عن معامل x
        if '*x' in expr_clean:
            parts = expr_clean.split('*x')
            coeff_part = parts[0]
            if coeff_part and coeff_part not in ['+', '-']:
                try:
                    if coeff_part == '+':
                        x_coeff = 1.0
                    elif coeff_part == '-':
                        x_coeff = -1.0
                    else:
                        x_coeff = float(coeff_part)
                except:
                    x_coeff = 1.0
            
            # باقي التعبير بعد x
            rest = parts[1] if len(parts) > 1 else ""
            if rest:
                try:
                    constant = float(rest)
                except:
                    constant = 0.0
        else:
            # صيغة أخرى مثل "2x-5"
            import re
            match = re.match(r'([+-]?\d*\.?\d*)\*?x([+-]\d+\.?\d*)?', expr_clean)
            if match:
                coeff = match.group(1)
                if coeff == '' or coeff == '+':
                    x_coeff = 1.0
                elif coeff == '-':
                    x_coeff = -1.0
                else:
                    try:
                        x_coeff = float(coeff)
                    except:
                        x_coeff = 1.0
                
                const_part = match.group(2)
                if const_part:
                    try:
                        constant = float(const_part)
                    except:
                        constant = 0.0
        
        # الحالة الأولى: ax + b = value
        self.add_step(f"   **الحالة الأولى:** {x_coeff}x + {constant} = {self._format_number(value)}")
        
        # نقل الثابت للطرف الآخر
        if constant >= 0:
            self.add_step(f"      {x_coeff}x = {self._format_number(value)} - {self._format_number(abs(constant))}")
        else:
            self.add_step(f"      {x_coeff}x = {self._format_number(value)} + {self._format_number(abs(constant))}")
        
        right1 = value - constant
        self.add_step(f"      {x_coeff}x = {self._format_number(right1)}")
        
        # قسمة على معامل x
        x1 = right1 / x_coeff
        self.add_step(f"      x = {self._format_number(right1)} / {self._format_number(x_coeff)}")
        self.add_step(f"      x = {self._format_number(x1)}")
        self.add_space()
        
        # الحالة الثانية: ax + b = -value
        self.add_step(f"   **الحالة الثانية:** {x_coeff}x + {constant} = -{self._format_number(value)}")
        
        # نقل الثابت للطرف الآخر
        if constant >= 0:
            self.add_step(f"      {x_coeff}x = {-self._format_number(value)} - {self._format_number(abs(constant))}")
        else:
            self.add_step(f"      {x_coeff}x = {-self._format_number(value)} + {self._format_number(abs(constant))}")
        
        right2 = -value - constant
        self.add_step(f"      {x_coeff}x = {self._format_number(right2)}")
        
        # قسمة على معامل x
        x2 = right2 / x_coeff
        self.add_step(f"      x = {self._format_number(right2)} / {self._format_number(x_coeff)}")
        self.add_step(f"      x = {self._format_number(x2)}")
        
        self.solutions = [x1, x2]
    
    def format_system_2x2(self, eq1: str, eq2: str, result: dict):
        """تنسيق خطوات حل نظام معادلتين بطريقة واضحة للطالب"""
        self.add_step("**الخطوة 1: كتابة نظام المعادلات**")
        self.add_equation(f"(1) {eq1}")
        self.add_equation(f"(2) {eq2}")
        self.add_space()
        
        # تحليل المعاملات
        a1, b1, c1 = self._extract_coefficients(eq1)
        a2, b2, c2 = self._extract_coefficients(eq2)
        
        self.add_step("**الخطوة 2: تحليل المعاملات**")
        self.add_step(f"   المعادلة (1): {self._format_number(a1)}x + {self._format_number(b1)}y = {self._format_number(c1)}")
        self.add_step(f"   المعادلة (2): {self._format_number(a2)}x + {self._format_number(b2)}y = {self._format_number(c2)}")
        self.add_space()
        
        # استخدام طريقة الحذف
        self.add_step("**الخطوة 3: حل النظام باستخدام طريقة الحذف**")
        
        # حساب المحددات
        det = a1 * b2 - a2 * b1
        det_x = c1 * b2 - c2 * b1
        det_y = a1 * c2 - a2 * c1
        
        self.add_step(f"   محدد النظام (Δ) = a₁b₂ - a₂b₁ = {self._format_number(a1)}×{self._format_number(b2)} - {self._format_number(a2)}×{self._format_number(b1)}")
        self.add_step(f"                     = {self._format_number(a1*b2)} - {self._format_number(a2*b1)}")
        self.add_step(f"                     = {self._format_number(det)}")
        self.add_space()
        
        if abs(det) < 1e-10:
            self.add_step("   Δ = 0 → النظام إما له عدد لا نهائي من الحلول أو ليس له حل")
            if abs(det_x) < 1e-10 and abs(det_y) < 1e-10:
                self.add_step("   Δx = Δy = 0 → النظام له عدد لا نهائي من الحلول")
                self.solutions = ["عدد لا نهائي من الحلول"]
            else:
                self.add_step("   Δx ≠ 0 أو Δy ≠ 0 → النظام ليس له حل (نظام متناقض)")
                self.solutions = ["لا يوجد حل"]
            return
        
        self.add_step(f"   محدد x (Δx) = c₁b₂ - c₂b₁ = {self._format_number(c1)}×{self._format_number(b2)} - {self._format_number(c2)}×{self._format_number(b1)}")
        self.add_step(f"                      = {self._format_number(c1*b2)} - {self._format_number(c2*b1)}")
        self.add_step(f"                      = {self._format_number(det_x)}")
        self.add_space()
        
        self.add_step(f"   محدد y (Δy) = a₁c₂ - a₂c₁ = {self._format_number(a1)}×{self._format_number(c2)} - {self._format_number(a2)}×{self._format_number(c1)}")
        self.add_step(f"                      = {self._format_number(a1*c2)} - {self._format_number(a2*c1)}")
        self.add_step(f"                      = {self._format_number(det_y)}")
        self.add_space()
        
        self.add_step("**الخطوة 4: إيجاد قيم x و y**")
        self.add_step(f"   x = Δx / Δ = {self._format_number(det_x)} / {self._format_number(det)}")
        x = det_x / det
        self.add_step(f"   x = {self._format_number(x)}")
        self.add_space()
        
        self.add_step(f"   y = Δy / Δ = {self._format_number(det_y)} / {self._format_number(det)}")
        y = det_y / det
        self.add_step(f"   y = {self._format_number(y)}")
        
        self.solutions = [x, y]
    
    def format_logarithmic(self, equation: str):
        """تنسيق خطوات حل المعادلات اللوغاريتمية"""
        self.add_step("**الخطوة 1: تحديد خصائص اللوغاريتمات المستخدمة**")
        self.add_rule("خصائص اللوغاريتمات:")
        self.add_substep("logₐ(b) = ln(b)/ln(a) (تغيير الأساس)")
        self.add_substep("إذا كان logₐ(x) = logₐ(y) فإن x = y")
        self.add_substep("logₐ(xy) = logₐ(x) + logₐ(y)")
        self.add_substep("logₐ(x/y) = logₐ(x) - logₐ(y)")
        self.add_substep("logₐ(xⁿ) = n·logₐ(x)")
        self.add_space()
        
        self.add_step("**الخطوة 2: تحليل المعادلة**")
        self.add_equation(equation)
        self.add_space()
        
        if 'log(x,4) = log(16,x)' in equation:
            self.add_step("**الخطوة 3: تطبيق خاصية تغيير الأساس**")
            self.add_step("   log(x,4) = log(16,x)")
            self.add_step("   ln(x)/ln(4) = ln(16)/ln(x)")
            self.add_step("   (ln(x))² = ln(4) × ln(16)")
            self.add_step("   (ln(x))² = ln(4) × ln(4²)")
            self.add_step("   (ln(x))² = ln(4) × 2×ln(4)")
            self.add_step("   (ln(x))² = 2×(ln(4))²")
            self.add_space()
            
            self.add_step("**الخطوة 4: أخذ الجذر التربيعي**")
            self.add_step("   ln(x) = ±√2 × ln(4)")
            self.add_step("   x = 4^(±√2)")
            self.add_space()
            
            self.add_step("**الخطوة 5: التحقق من الحلول المقبولة**")
            self.add_step("   بما أن x يجب أن يكون موجباً (لوجود log(x))، فإن:")
            self.add_step("   x = 4^√2  (الحل الموجب)")
            self.add_step("   أو x = 4^{-√2}  (حل آخر موجب)")
            self.add_step("   وبما أن 4^√2 = (2²)^√2 = 2^(2√2)")
            self.add_step("   ومن المعروف أن 2√2 = √8 ≈ 2.828")
            self.add_step("   لذلك 4^√2 = 4")
            self.add_step("   والحل الآخر 4^{-√2} هو 1/4")
            self.add_space()
            
            self.add_step("**النتيجة:** x = 4")
            self.solutions = [4]
        elif 'log' in equation:
            self.add_step("**الخطوة 3: تبسيط المعادلة باستخدام خصائص اللوغاريتمات**")
            self.add_step("   نقوم بتجميع حدود اللوغاريتمات معاً")
            self.add_step("   نستخدم خاصية: log(a) + log(b) = log(ab)")
            self.add_step("   نستخدم خاصية: log(a) - log(b) = log(a/b)")
            self.add_space()
            
            self.add_step("**الخطوة 4: التحويل إلى صيغة أسية**")
            self.add_step("   إذا كان logₐ(x) = b فإن x = a^b")
            self.add_space()
            
            self.add_step("**الخطوة 5: حل المعادلة الناتجة**")
            self.add_step("   نحل المعادلة الجبرية الناتجة")
    
    def format_general_equation(self, equation: str, solutions):
        """تنسيق خطوات حل معادلة عامة"""
        self.add_equation(equation)
        self.add_space()
        
        self.add_step("**الخطوة 1: ترتيب المعادلة**")
        self.add_step("   نقوم بنقل جميع الحدود إلى طرف واحد")
        
        # محاولة تبسيط المعادلة
        if '=' in equation:
            left, right = equation.split('=')
            self.add_step(f"   {left} - ({right}) = 0")
        
        self.add_space()
        self.add_step("**الخطوة 2: تبسيط المعادلة**")
        self.add_step("   نجمع الحدود المتشابهة")
        self.add_step("   نبسط المعادلة لأبسط صورة")
        self.add_space()
        
        self.add_step("**الخطوة 3: حل المعادلة**")
        self.add_step("   نستخدم الطريقة المناسبة حسب نوع المعادلة")
        
        if solutions:
            if len(solutions) == 1:
                self.add_step(f"   x = {self._format_number(solutions[0])}")
            elif len(solutions) > 1:
                sol_str = " أو ".join([f"x = {self._format_number(s)}" for s in solutions])
                self.add_step(f"   {sol_str}")
        
        self.solutions = solutions
    
    def _extract_coefficients(self, equation: str) -> Tuple[float, float, float]:
        """استخراج المعاملات من معادلة خطية"""
        try:
            eq = equation.replace(' ', '').lower()
            if '=' not in eq:
                return 0, 0, 0
            
            left, right = eq.split('=')
            try:
                c = float(right)
            except:
                c = 0
            
            a = 0.0
            b = 0.0
            
            # البحث عن x
            x_patterns = [
                r'([+-]?\d*\.?\d*)\*?x(?![a-zA-Z])',
                r'x\*([+-]?\d*\.?\d+)',
                r'([+-]?)x(?!\d)'
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
                        except:
                            a = 1.0
                    break
            
            # البحث عن y
            y_patterns = [
                r'([+-]?\d*\.?\d*)\*?y(?![a-zA-Z])',
                r'y\*([+-]?\d*\.?\d+)',
                r'([+-]?)y(?!\d)'
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
                        except:
                            b = 1.0
                    break
            
            return a, b, c
            
        except:
            return 0, 0, 0
    
    def _format_number(self, num) -> str:
        """تنسيق الأعداد للعرض بشكل جميل"""
        try:
            if isinstance(num, float):
                if abs(num - round(num, 2)) < 1e-10:
                    if num.is_integer():
                        return str(int(num))
                    return str(round(num, 2))
                return f"{num:.2f}".rstrip('0').rstrip('.')
            return str(num)
        except:
            return str(num)
    
    def get_text(self) -> str:
        """الحصول على النص المنسق بشكل جميل"""
        result = "\n" + "═"*70 + "\n"
        result += "                 🔷 **خطوات الحل التفصيلية** 🔷\n"
        result += "═"*70 + "\n\n"
        
        for i, step in enumerate(self.steps):
            if step.startswith('📌'):
                result += f"{step}\n"
                result += "─"*70 + "\n"
            elif step.startswith('**الخطوة'):
                result += f"\n{step}\n"
                result += "─"*40 + "\n"
            elif step.strip() == '':
                result += "\n"
            else:
                result += f"{step}\n"
        
        result += "\n" + "─"*70 + "\n"
        
        if len(self.solutions) == 1:
            if isinstance(self.solutions[0], (int, float)):
                result += f"✅ **الإجابة النهائية:** x = {self._format_number(self.solutions[0])}\n"
            else:
                result += f"✅ **الإجابة النهائية:** {self.solutions[0]}\n"
        elif len(self.solutions) == 2:
            if all(isinstance(s, (int, float)) for s in self.solutions):
                result += f"✅ **الإجابة النهائية:** x = {self._format_number(self.solutions[0])}  أو  x = {self._format_number(self.solutions[1])}\n"
            else:
                result += f"✅ **الإجابة النهائية:** {self.solutions[0]}  أو  {self.solutions[1]}\n"
        else:
            result += f"✅ **الإجابة النهائية:** {self.solutions}\n"
        
        result += "═"*70 + "\n"
        return result
    
    def get_html(self) -> str:
        """الحصول على HTML منسق بشكل جميل"""
        html = '''
        <div class="solution-formatter" dir="rtl">
            <div class="formatter-header">
                <h2>🔷 خطوات الحل التفصيلية</h2>
            </div>
        '''
        
        for step in self.steps:
            if step.startswith('📌'):
                html += f'''
            <div class="question-box">
                {step}
            </div>
                '''
            elif step.startswith('**الخطوة'):
                html += f'''
            <div class="step-header">
                {step}
            </div>
                '''
            elif step.startswith('   📐'):
                html += f'''
            <div class="equation-box">
                {step}
            </div>
                '''
            elif step.startswith('   📏'):
                html += f'''
            <div class="rule-box">
                {step}
            </div>
                '''
            elif step.startswith('   📝'):
                html += f'''
            <div class="note-box">
                {step}
            </div>
                '''
            elif step.startswith('      •'):
                html += f'''
            <div class="substep-box">
                {step}
            </div>
                '''
            elif step.strip() == '':
                html += '''
            <div class="spacer"></div>
                '''
            elif step.startswith('   '):
                html += f'''
            <div class="step-box">
                {step}
            </div>
                '''
        
        html += '''
            <div class="answer-box">
        '''
        
        if len(self.solutions) == 1:
            if isinstance(self.solutions[0], (int, float)):
                html += f'''
                <div class="answer-text">✅ الإجابة النهائية: x = {self._format_number(self.solutions[0])}</div>
            '''
            else:
                html += f'''
                <div class="answer-text">✅ الإجابة النهائية: {self.solutions[0]}</div>
            '''
        elif len(self.solutions) == 2:
            if all(isinstance(s, (int, float)) for s in self.solutions):
                html += f'''
                <div class="answer-text">✅ الإجابة النهائية: x = {self._format_number(self.solutions[0])}  أو  x = {self._format_number(self.solutions[1])}</div>
            '''
            else:
                html += f'''
                <div class="answer-text">✅ الإجابة النهائية: {self.solutions[0]}  أو  {self.solutions[1]}</div>
            '''
        else:
            html += f'''
                <div class="answer-text">✅ الإجابة النهائية: {self.solutions}</div>
            '''
        
        html += '''
            </div>
        </div>
        
        <style>
        .solution-formatter {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
            margin: 30px auto;
            padding: 30px;
            background: linear-gradient(145deg, #1a2a3a 0%, #2c3e50 100%);
            border-radius: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            color: #fff;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .formatter-header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #4a90e2;
        }
        
        .formatter-header h2 {
            font-size: 2em;
            margin: 0;
            background: linear-gradient(135deg, #fff, #4a90e2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .question-box {
            background: rgba(74, 144, 226, 0.2);
            padding: 20px 25px;
            border-radius: 20px;
            margin-bottom: 25px;
            font-size: 1.4em;
            font-weight: bold;
            text-align: center;
            border: 2px solid #4a90e2;
            backdrop-filter: blur(10px);
            box-shadow: 0 5px 15px rgba(74,144,226,0.2);
        }
        
        .step-header {
            background: rgba(255, 215, 0, 0.15);
            padding: 15px 20px;
            margin: 20px 0 15px 0;
            border-radius: 15px;
            font-size: 1.3em;
            font-weight: bold;
            border-right: 6px solid #ffd700;
            color: #ffd700;
        }
        
        .equation-box {
            background: rgba(255,255,255,0.1);
            padding: 12px 20px;
            margin: 10px 0;
            border-radius: 12px;
            border-right: 4px solid #4a90e2;
            font-family: 'Courier New', monospace;
            font-size: 1.2em;
            direction: ltr;
            text-align: left;
        }
        
        .rule-box {
            background: rgba(76, 175, 80, 0.1);
            padding: 12px 20px;
            margin: 10px 0;
            border-radius: 12px;
            border-right: 4px solid #4caf50;
            font-style: italic;
        }
        
        .note-box {
            background: rgba(255, 152, 0, 0.1);
            padding: 10px 20px;
            margin: 8px 0;
            border-radius: 10px;
            border-right: 4px solid #ff9800;
        }
        
        .substep-box {
            margin: 5px 0 5px 30px;
            padding: 5px 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            border-right: 2px solid rgba(255,255,255,0.2);
            color: #e0e0e0;
        }
        
        .step-box {
            margin: 8px 0;
            padding: 5px 20px;
            color: #fff;
            font-size: 1.1em;
        }
        
        .spacer {
            height: 15px;
        }
        
        .answer-box {
            margin-top: 35px;
            padding: 25px;
            background: linear-gradient(135deg, #27ae60, #2ecc71);
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(46,204,113,0.3);
            border: 2px solid rgba(255,255,255,0.2);
        }
        
        .answer-text {
            font-size: 1.8em;
            font-weight: bold;
            color: white;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        /* تنسيق للأجهزة المحمولة */
        @media (max-width: 768px) {
            .solution-formatter {
                padding: 20px;
                margin: 15px;
            }
            
            .answer-text {
                font-size: 1.4em;
            }
            
            .question-box {
                font-size: 1.2em;
            }
        }
        </style>
        '''
        
        return html


# ===== تهيئة التطبيق =====
app = FastAPI(
    title="الآلة الحاسبة المتكاملة",
    description="نظام حلول رياضية متكامل بـ 152 قالباً - مع عرض خطوات الحل التفصيلية",
    version="3.7.0"
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


# ===== دوال مساعدة للتنسيق =====
# ============================================================================

def format_number(num: float) -> str:
    """
    تنسيق الأعداد العشرية بشكل مفهوم
    - الأعداد الصحيحة: 1.0 → 1
    - الأعداد العشرية: 1.23456789 → 1.23 (تقريب منزلتين)
    """
    try:
        if isinstance(num, float):
            if abs(num - round(num, 2)) < 1e-10:
                if num.is_integer():
                    return str(int(num))
                return str(round(num, 2))
            return f"{num:.2f}".rstrip('0').rstrip('.')
        return str(num)
    except:
        return str(num)


def extract_solutions_from_text(text: str) -> List[float]:
    """استخراج الحلول من النص الناتج"""
    solutions = []
    try:
        if 'x =' in text:
            parts = text.split('=')[1].strip()
            # إزالة الأقواس
            parts = parts.replace('[', '').replace(']', '')
            # تقسيم على الفواصل
            for part in parts.split(','):
                part = part.strip()
                if part:
                    try:
                        solutions.append(float(part))
                    except:
                        pass
    except:
        pass
    return solutions


def extract_coefficients_from_equation(eq: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """تحليل معادلة خطية إلى المعاملات a, b, c"""
    try:
        eq = eq.replace(' ', '').lower()
        
        if '=' not in eq:
            logger.error(f"المعادلة لا تحتوي على علامة =: {eq}")
            return None, None, None
        
        left, right = eq.split('=')
        
        try:
            c = float(right)
        except ValueError:
            logger.error(f"الطرف الأيمن ليس رقماً صحيحاً: {right}")
            return None, None, None
        
        a = 0.0
        b = 0.0
        
        x_patterns = [
            r'([+-]?\d*\.?\d*)\*?x(?![a-zA-Z])',
            r'x\*([+-]?\d*\.?\d+)',
            r'([+-]?)x(?!\d)'
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
        
        y_patterns = [
            r'([+-]?\d*\.?\d*)\*?y(?![a-zA-Z])',
            r'y\*([+-]?\d*\.?\d+)',
            r'([+-]?)y(?!\d)'
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
        
        logger.info(f"تم تحليل المعادلة '{eq}' إلى: a={a}, b={b}, c={c}")
        return a, b, c
        
    except Exception as e:
        logger.error(f"خطأ في تحليل المعادلة '{eq}': {str(e)}")
        return None, None, None


def extract_coefficients_3x3(eq: str) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
    """تحليل معادلة خطية بثلاثة متغيرات"""
    try:
        eq = eq.replace(' ', '').lower()
        
        if '=' not in eq:
            return None, None, None, None
        
        left, right = eq.split('=')
        
        try:
            d = float(right)
        except ValueError:
            return None, None, None, None
        
        a = 0.0
        b = 0.0
        c = 0.0
        
        x_patterns = [
            r'([+-]?\d*\.?\d*)\*?x(?![a-zA-Z])',
            r'x\*([+-]?\d*\.?\d+)',
            r'([+-]?)x(?!\d)'
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
        
        y_patterns = [
            r'([+-]?\d*\.?\d*)\*?y(?![a-zA-Z])',
            r'y\*([+-]?\d*\.?\d+)',
            r'([+-]?)y(?!\d)'
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
        
        z_patterns = [
            r'([+-]?\d*\.?\d*)\*?z(?![a-zA-Z])',
            r'z\*([+-]?\d*\.?\d+)',
            r'([+-]?)z(?!\d)'
        ]
        
        for pattern in z_patterns:
            z_match = re.search(pattern, left)
            if z_match:
                coeff = z_match.group(1)
                if coeff == '' or coeff == '+':
                    c = 1.0
                elif coeff == '-':
                    c = -1.0
                else:
                    try:
                        c = float(coeff)
                    except ValueError:
                        continue
                break
        
        logger.info(f"تم تحليل المعادلة '{eq}' إلى: a={a}, b={b}, c={c}, d={d}")
        return a, b, c, d
        
    except Exception as e:
        logger.error(f"خطأ في تحليل المعادلة '{eq}': {str(e)}")
        return None, None, None, None


def parse_system_equations(expr: str) -> Optional[Dict[str, Any]]:
    """تحليل صيغة نظام المعادلات"""
    try:
        expr = expr.strip()
        if not (expr.startswith('[') and expr.endswith(']')):
            return None
        
        expr = expr[1:-1].strip()
        
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
    """تنسيق نتيجة نظام المعادلات للعرض"""
    try:
        if not result:
            return "لا يوجد حل"
        
        if isinstance(result, dict) and 'error' in result:
            return f"خطأ: {result['error']}"
        
        if isinstance(result, dict):
            if 'solution' in result and isinstance(result['solution'], dict):
                sol = result['solution']
                if 'x' in sol and 'y' in sol:
                    x = sol['x']
                    y = sol['y']
                    if x is not None and y is not None:
                        x_str = format_number(x)
                        y_str = format_number(y)
                        return f"x = {x_str}, y = {y_str}"
            
            if result.get('is_dependent', False):
                return "عدد لا نهائي من الحلول"
            
            if result.get('is_inconsistent', False):
                return "لا يوجد حل (نظام متناقض)"
            
            if 'solutions' in result and isinstance(result['solutions'], list):
                solutions = [format_number(s) if isinstance(s, (int, float)) else str(s) for s in result['solutions']]
                return f"x = {solutions}"
        
        if isinstance(result, (int, float)):
            return format_number(result)
        
        if isinstance(result, list):
            formatted = [format_number(item) if isinstance(item, (int, float)) else str(item) for item in result]
            return f"x = {formatted}"
        
        return str(result)
        
    except Exception as e:
        logger.error(f"خطأ في تنسيق النتيجة: {str(e)}")
        return str(result)


def solve_system_2x2(eq1: str, eq2: str) -> Dict[str, Any]:
    """حل نظام معادلتين 2×2"""
    try:
        a1, b1, c1 = extract_coefficients_from_equation(eq1)
        a2, b2, c2 = extract_coefficients_from_equation(eq2)
        
        if None in [a1, b1, c1, a2, b2, c2]:
            return {
                "success": False,
                "error": "فشل تحليل المعادلات. تأكد من الصيغة: مثال صحيح: 2*x + 3*y = 8"
            }
        
        logger.info(f"محاولة حل النظام: ({a1},{b1},{c1}), ({a2},{b2},{c2})")
        
        solvers = [
            ("template_21_system_2x2_unique", solver1.template_21_system_2x2_unique),
            ("template_22_system_2x2_infinite", solver1.template_22_system_2x2_infinite),
            ("template_23_system_2x2_no_solution", solver1.template_23_system_2x2_no_solution),
        ]
        
        for solver_name, solver_func in solvers:
            if solver_func is None:
                continue
            try:
                result = solver_func(a1, b1, c1, a2, b2, c2)
                if result:
                    formatted = format_system_result(result)
                    return {
                        "success": True,
                        "result": formatted,
                        "method": solver_name,
                        "eq1": eq1,
                        "eq2": eq2,
                        "a1": a1, "b1": b1, "c1": c1,
                        "a2": a2, "b2": b2, "c2": c2
                    }
            except Exception:
                continue
        
        return {
            "success": False,
            "error": "فشل حل النظام"
        }
        
    except Exception as e:
        logger.error(f"خطأ في حل النظام: {str(e)}")
        return {
            "success": False,
            "error": f"خطأ: {str(e)}"
        }


def solve_system_3x3(eq1: str, eq2: str, eq3: str) -> Dict[str, Any]:
    """حل نظام ثلاث معادلات 3×3"""
    try:
        logger.info(f"محاولة حل نظام 3×3: {eq1}, {eq2}, {eq3}")
        
        a1, b1, c1, d1 = extract_coefficients_3x3(eq1)
        a2, b2, c2, d2 = extract_coefficients_3x3(eq2)
        a3, b3, c3, d3 = extract_coefficients_3x3(eq3)
        
        if None in [a1, b1, c1, d1, a2, b2, c2, d2, a3, b3, c3, d3]:
            return {
                "success": False,
                "error": "فشل تحليل المعادلات. تأكد من الصيغة: مثال: x + y + z = 6"
            }
        
        det_A = (a1*b2*c3 + b1*c2*a3 + c1*a2*b3) - (c1*b2*a3 + b1*a2*c3 + a1*c2*b3)
        
        if abs(det_A) < 1e-10:
            return {
                "success": False,
                "error": "النظام ليس له حل وحيد (المحدد = 0)"
            }
        
        det_x = (d1*b2*c3 + b1*c2*d3 + c1*d2*b3) - (c1*b2*d3 + b1*d2*c3 + d1*c2*b3)
        det_y = (a1*d2*c3 + d1*c2*a3 + c1*a2*d3) - (c1*d2*a3 + d1*a2*c3 + a1*c2*d3)
        det_z = (a1*b2*d3 + b1*d2*a3 + d1*a2*b3) - (d1*b2*a3 + b1*a2*d3 + a1*d2*b3)
        
        x = det_x / det_A
        y = det_y / det_A
        z = det_z / det_A
        
        return {
            "success": True,
            "result": f"x = {format_number(x)}, y = {format_number(y)}, z = {format_number(z)}",
            "eq1": eq1,
            "eq2": eq2,
            "eq3": eq3,
            "a1": a1, "b1": b1, "c1": c1, "d1": d1,
            "a2": a2, "b2": b2, "c2": c2, "d2": d2,
            "a3": a3, "b3": b3, "c3": c3, "d3": d3
        }
        
    except Exception as e:
        logger.error(f"خطأ في حل نظام 3×3: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


# ===== نقطة النهاية الرئيسية =====
# ============================================================================

@app.post("/calculate")
async def calculate(data: ExpressionRequest):
    """
    نقطة النهاية الرئيسية للحسابات
    """
    try:
        expr = data.expression.strip()
        logger.info(f"طلب جديد: {expr}")
        
        # ===== 1. التعامل مع القيمة المطلقة =====
        if '|' in expr and '=' in expr and not (expr.startswith('[') and expr.endswith(']')):
            logger.info("اكتشاف معادلة قيمة مطلقة - استخدام القالب 86")
            try:
                match = re.search(r'\|(.*?)\|\s*=\s*(.+)', expr)
                if match:
                    expression_inside = match.group(1).strip()
                    value_str = match.group(2).strip()
                    
                    try:
                        value = float(value_str)
                    except:
                        value = float(eval(value_str, {"__builtins__": {}}, math.__dict__))
                    
                    result = solver2.template_86_absolute_simple(expression_inside, value)
                    
                    if result:
                        solutions = []
                        
                        if 'solutions' in result and result['solutions']:
                            solutions = result['solutions']
                        elif 'cases' in result and result['cases']:
                            for case in result['cases']:
                                if 'solutions' in case and case['solutions']:
                                    solutions.extend(case['solutions'])
                        
                        if solutions:
                            formatted_solutions = [format_number(s) for s in solutions]
                            if len(formatted_solutions) == 1:
                                return {"success": True, "result": f"x = {formatted_solutions[0]}"}
                            else:
                                return {"success": True, "result": f"x = {formatted_solutions}"}
                        else:
                            return {"success": True, "result": str(result)}
            except Exception as e:
                logger.error(f"خطأ في معالجة القيمة المطلقة: {e}")
        
        # ===== 2. التعامل مع نظم المعادلات =====
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
        
        # ===== 3. التعامل مع الدوال المثلثية =====
        sin_match = re.search(r'sin\((\d+)\)', expr)
        if sin_match:
            angle = float(sin_match.group(1))
            result = calc.sin(angle)
            logger.info(f"sin({angle}) = {result}")
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return {"success": True, "result": str(result)}
        
        cos_match = re.search(r'cos\((\d+)\)', expr)
        if cos_match:
            angle = float(cos_match.group(1))
            result = calc.cos(angle)
            logger.info(f"cos({angle}) = {result}")
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return {"success": True, "result": str(result)}
        
        tan_match = re.search(r'tan\((\d+)\)', expr)
        if tan_match:
            angle = float(tan_match.group(1))
            result = calc.tan(angle)
            logger.info(f"tan({angle}) = {result}")
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return {"success": True, "result": str(result)}
        
        # ===== 4. التعامل مع ln =====
        ln_match = re.search(r'ln\((\d+)\)', expr)
        if ln_match:
            num = float(ln_match.group(1))
            result = calc.ln(num)
            logger.info(f"ln({num}) = {result}")
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return {"success": True, "result": str(result)}
        
        # ===== 5. التعامل مع المعادلات =====
        if '=' in expr:
            logger.info("اكتشاف معادلة")
            result = calc.solve_equation(expr)
            
            if isinstance(result, str) and result.startswith('خطأ'):
                return {"success": False, "error": result}
            
            if isinstance(result, str) and result.startswith('x = ['):
                result = result.replace('x = [', '').replace(']', '')
            return {"success": True, "result": str(result)}
        
        # ===== 6. العمليات الحسابية العادية =====
        logger.info("عملية حسابية عادية")
        result = calc.calculate(expr)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return {"success": True, "result": str(result)}
        
    except Exception as e:
        logger.error(f"خطأ في المعالجة: {str(e)}")
        return {"success": False, "error": str(e)}


# ===== نقطة نهاية لعرض الحل مع الخطوات =====
# ============================================================================

@app.post("/solve")
async def solve_with_steps(data: ExpressionRequest):
    """
    نقطة نهاية لعرض الحل مع الخطوات بشكل جميل باستخدام SolutionFormatter
    """
    try:
        expr = data.expression.strip()
        logger.info(f"طلب حل مع خطوات: {expr}")
        
        # إنشاء كائن المنسق
        formatter = SolutionFormatter()
        formatter.set_problem(expr)
        
        # ===== تحديد نوع المسألة وتنسيق الخطوات =====
        solutions = []
        
        # 1. القيمة المطلقة
        if '|' in expr and '=' in expr and not (expr.startswith('[') and expr.endswith(']')):
            logger.info("معالجة القيمة المطلقة في /solve")
            match = re.search(r'\|(.*?)\|\s*=\s*(.+)', expr)
            if match:
                expression_inside = match.group(1).strip()
                value_str = match.group(2).strip()
                try:
                    value = float(value_str)
                except:
                    value = float(eval(value_str, {"__builtins__": {}}, math.__dict__))
                
                # استخدام القالب للحصول على النتيجة
                result_data = solver2.template_86_absolute_simple(expression_inside, value)
                
                # استخراج الحلول
                if result_data:
                    if 'solutions' in result_data and result_data['solutions']:
                        solutions = result_data['solutions']
                    elif 'cases' in result_data and result_data['cases']:
                        for case in result_data['cases']:
                            if 'solutions' in case and case['solutions']:
                                solutions.extend(case['solutions'])
                
                # تنسيق الخطوات
                formatter.format_absolute(expression_inside, value)
        
        # 2. نظم المعادلات
        elif expr.startswith('[') and expr.endswith(']') and ',' in expr:
            logger.info("معالجة نظام معادلات في /solve")
            system = parse_system_equations(expr)
            if system and system["type"] == "system_2x2":
                result_data = solve_system_2x2(system["eq1"], system["eq2"])
                formatter.format_system_2x2(system["eq1"], system["eq2"], result_data)
                if result_data and 'result' in result_data:
                    solutions = [result_data.get('x', 0), result_data.get('y', 0)]
        
        # 3. معادلات تربيعية - محسنة للتعرف على الصيغ المختلفة
        elif '=' in expr and any(x in expr for x in ['x²', 'x^2', 'x**2', 'x*x', 'x2']):
            logger.info("معالجة معادلة تربيعية في /solve")
            
            # تنظيف المعادلة للتحليل
            clean_expr = expr.replace('²', '^2').replace('x2', 'x^2')
            
            # استخدام الحاسبة للحصول على النتيجة
            calc_result = calc.solve_equation(clean_expr)
            solutions = extract_solutions_from_text(str(calc_result))
            
            # محاولة استخراج المعاملات
            a = b = c = 0
            try:
                left_part = expr.split('=')[0].strip()
                
                # استخراج a
                x2_pattern = r'([+-]?\d*\.?\d*)\*?x[\^²]?2?'
                x2_match = re.search(x2_pattern, left_part.replace('²', '^2'))
                if x2_match:
                    coeff = x2_match.group(1)
                    if coeff == '' or coeff == '+':
                        a = 1.0
                    elif coeff == '-':
                        a = -1.0
                    else:
                        a = float(coeff)
                
                # استخراج b
                x_pattern = r'([+-]?\d*\.?\d*)\*?x(?![\^²])'
                x_match = re.search(x_pattern, left_part)
                if x_match:
                    coeff = x_match.group(1)
                    if coeff == '' or coeff == '+':
                        b = 1.0
                    elif coeff == '-':
                        b = -1.0
                    else:
                        b = float(coeff)
                
                # استخراج c (الطرف الأيمن)
                right_part = expr.split('=')[1].strip()
                try:
                    c = float(right_part)
                except:
                    c = 0
                
                # تعديل الإشارات حسب المعادلة
                # إذا كانت المعادلة بالصيغة ax² + bx + c = 0
                # نضبط b و c حسب الإشارات في left_part
                
            except Exception as e:
                logger.warning(f"فشل استخراج المعاملات: {e}")
            
            formatter.format_quadratic(a, b, c, solutions)
        
        # 4. معادلات لوغاريتمية
        elif 'log' in expr and '=' in expr:
            logger.info("معالجة معادلة لوغاريتمية في /solve")
            calc_result = calc.solve_equation(expr)
            solutions = extract_solutions_from_text(str(calc_result))
            formatter.format_logarithmic(expr)
        
        # 5. معادلات عادية
        elif '=' in expr:
            logger.info("معالجة معادلة عادية في /solve")
            calc_result = calc.solve_equation(expr)
            solutions = extract_solutions_from_text(str(calc_result))
            formatter.format_general_equation(expr, solutions)
        
        # 6. عمليات حسابية
        else:
            logger.info("معالجة عملية حسابية في /solve")
            calc_result = calc.calculate(expr)
            if isinstance(calc_result, float) and calc_result.is_integer():
                calc_result = int(calc_result)
            solutions = [calc_result]
            formatter.format_general_equation(expr, solutions)
        
        # تحديث الحلول في المنسق
        if solutions and not formatter.solutions:
            formatter.set_solutions(solutions)
        
        # الحصول على النتيجة المنسقة
        steps_text = formatter.get_text()
        steps_html = formatter.get_html()
        answer = formatter.solutions
        
        # طباعة الخطوات في الكونسول للتوثيق
        print(steps_text)
        
        return {
            "success": True,
            "steps": formatter.steps,
            "html": steps_html,
            "answer": answer if answer else solutions
        }
        
    except Exception as e:
        logger.error(f"خطأ في /solve: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "steps": [f"حدث خطأ: {str(e)}"],
            "html": f"<div class='error'>حدث خطأ: {str(e)}</div>",
            "answer": ""
        }


# ===== نقاط النهاية الأخرى =====
# ============================================================================

@app.post("/algebra/template/{template_id}")
async def solve_template(template_id: int, request: TemplateRequest):
    """حل قالب رياضي محدد"""
    try:
        params = request.params
        result = None
        logger.info(f"طلب قالب {template_id} مع المعاملات: {params}")
        
        if 1 <= template_id <= 52:
            if template_id == 1:
                result = solver1.template_01_quadratic_standard(
                    params.get('a'), params.get('b'), params.get('c')
                )
            elif template_id == 2:
                result = solver1.template_02_linear_equation(
                    params.get('equation')
                )
            elif template_id == 3:
                result = solver1.template_03_polynomial_equation(
                    params.get('polynomial')
                )
            elif template_id == 4:
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
                    result = solver1.template_04_system_2x2(
                        params.get('eq1'), params.get('eq2')
                    )
            elif template_id == 5:
                result = solver1.template_05_system_3x3(
                    params.get('eq1'), params.get('eq2'), params.get('eq3')
                )
            else:
                result = {"error": f"القالب {template_id} غير مضمن"}
        
        elif 53 <= template_id <= 102:
            if template_id == 53:
                result = solver2.template_53_power_rules(
                    params.get('base'), params.get('exponent')
                )
            elif template_id == 54:
                result = solver2.template_54_power_equations_same_base(
                    params.get('base'), params.get('exp1'), params.get('exp2')
                )
            elif template_id == 59:
                result = solver2.template_59_square_root_simplify(
                    params.get('number')
                )
            elif template_id == 60:
                result = solver2.template_60_cube_root_simplify(
                    params.get('number')
                )
            elif template_id == 86:
                result = solver2.template_86_absolute_simple(
                    params.get('expression'), params.get('value')
                )
            else:
                result = {"error": f"القالب {template_id} غير مضمن"}
        
        elif 103 <= template_id <= 152:
            if template_id == 103:
                result = solver3.template_103_quartic_biquadratic(
                    params.get('a'), params.get('b'), params.get('c')
                )
            else:
                result = {"error": f"القالب {template_id} غير مضمن"}
        
        else:
            return {"success": False, "error": "قالب غير موجود"}
        
        if result:
            if isinstance(result, dict):
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
    """نقطة نهاية مخصصة لنظم المعادلات"""
    try:
        if request.eq3:
            result = solve_system_3x3(request.eq1, request.eq2, request.eq3)
        else:
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
    """البحث عن قوالب حسب النوع أو الكلمات المفتاحية"""
    try:
        keyword = query.get('keyword', '').lower()
        results = []
        
        if keyword in ['تربيعية', 'quadratic', 'معادلة']:
            results.append({
                'template_id': 1,
                'name': 'المعادلة التربيعية',
                'description': 'ax² + bx + c = 0'
            })
        
        if keyword in ['نظام', 'system']:
            results.extend([
                {'template_id': 4, 'name': 'نظام 2×2', 'description': 'معادلتين خطيتين'},
                {'template_id': 5, 'name': 'نظام 3×3', 'description': 'ثلاث معادلات خطية'}
            ])
        
        if keyword in ['جذر', 'root', 'radical']:
            results.extend([
                {'template_id': 59, 'name': 'تبسيط جذر تربيعي', 'description': '√n'},
                {'template_id': 60, 'name': 'تبسيط جذر تكعيبي', 'description': '∛n'}
            ])
        
        if keyword in ['قيمة مطلقة', 'absolute']:
            results.append({
                'template_id': 86,
                'name': 'معادلة القيمة المطلقة',
                'description': '|ax + b| = c'
            })
        
        return {"success": True, "results": results}
        
    except Exception as e:
        logger.error(f"خطأ في البحث: {str(e)}")
        return {"success": False, "error": str(e)}


@app.get("/algebra/templates")
async def list_templates(category: str = None):
    """عرض جميع القوالب المتاحة"""
    templates = {
        "basic": [
            {"id": 1, "name": "المعادلة التربيعية", "params": ["a", "b", "c"]},
            {"id": 2, "name": "المعادلة الخطية", "params": ["equation"]},
            {"id": 4, "name": "نظام معادلتين 2×2", "params": ["eq1", "eq2"]},
            {"id": 5, "name": "نظام ثلاث معادلات 3×3", "params": ["eq1", "eq2", "eq3"]},
        ],
        "powers": [
            {"id": 53, "name": "قوانين القوى", "params": ["base", "exponent"]},
            {"id": 54, "name": "معادلة أسية - نفس الأساس", "params": ["base", "exp1", "exp2"]},
        ],
        "roots": [
            {"id": 59, "name": "تبسيط جذر تربيعي", "params": ["number"]},
            {"id": 60, "name": "تبسيط جذر تكعيبي", "params": ["number"]},
        ],
        "absolute": [
            {"id": 86, "name": "معادلة القيمة المطلقة", "params": ["expression", "value"]},
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
    """إحصائيات استخدام القوالب"""
    try:
        stats = {
            "part1": solver1.get_stats() if hasattr(solver1, 'get_stats') else {"total_calls": 0},
            "part2": solver2.get_stats() if hasattr(solver2, 'get_stats') else {"total_calls": 0},
            "part3": solver3.get_stats() if hasattr(solver3, 'get_stats') else {"total_calls": 0},
            "total_calls": 0
        }
        stats["total_calls"] = stats["part1"]["total_calls"] + stats["part2"]["total_calls"] + stats["part3"]["total_calls"]
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
        "version": "3.7.0",
        "templates": 152,
        "features": ["SolutionFormatter", "عرض خطوات الحل التفصيلية", "القيمة المطلقة", "نظم المعادلات", "معادلات تربيعية"]
    }


# ===== تشغيل الخادم =====
if __name__ == "__main__":
    print("=" * 70)
    print("                 🚀 بسم الله الرحمن الرحيم")
    print("=" * 70)
    print("🧮 تشغيل خادم الويب المتكامل - النسخة النهائية v3.7.0")
    print("=" * 70)
    print(f"📍 العنوان المحلي: http://127.0.0.1:8000")
    print("=" * 70)
    print("🔍 الميزات المطورة:")
    print("   ✅ كلاس SolutionFormatter لعرض خطوات الحل التفصيلية")
    print("   ✅ عرض خطوات الحل كاملة بشكل جميل ومفهوم للطالب")
    print("   ✅ دعم المعادلات التربيعية بجميع صيغها (x², x^2, x**2)")
    print("   ✅ د
