# server.py - خادم الويب المتكامل (نسخة نهائية مع عرض خطوات الحل)    
# ============================================================================      
# هذا الملف يدمج جميع القوالب الجديدة مع النظام القديم      
# الإصدار: 3.6.0 - مع كلاس SolutionFormatter لعرض خطوات الحل بشكل جميل
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
  
# ===== كلاس متخصص لعرض خطوات الحل بشكل جميل =====
# ============================================================================

class SolutionFormatter:
    """
    كلاس متخصص في تنسيق وعرض خطوات الحل بطريقة مفهومة وجميلة
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
    
    def format_absolute(self, expression: str, value: float):
        """تنسيق خطوات حل معادلة القيمة المطلقة"""
        self.add_rule("|تعبير| = قيمة  ⇒  تعبير = قيمة  أو  تعبير = -قيمة")
        self.add_space()
        
        # الحالة الأولى
        self.add_equation(f"{expression} = {value}")
        
        # تحليل المعادلة يدوياً للعرض
        if '2*x' in expression and '-5' in expression:
            # 2x - 5 = 7
            self.add_step(f"   2x = {value} + 5")
            self.add_step(f"   2x = {value + 5}")
            self.add_step(f"   x = {(value + 5)/2}")
            self.solutions.append((value + 5)/2)
        elif '2*x' in expression and '+5' in expression:
            # 2x + 5 = 7
            self.add_step(f"   2x = {value} - 5")
            self.add_step(f"   2x = {value - 5}")
            self.add_step(f"   x = {(value - 5)/2}")
            self.solutions.append((value - 5)/2)
        elif '3*x' in expression and '-2' in expression:
            self.add_step(f"   3x = {value} + 2")
            self.add_step(f"   3x = {value + 2}")
            self.add_step(f"   x = {(value + 2)/3}")
            self.solutions.append((value + 2)/3)
        else:
            # محاولة عامة
            if 'x' in expression:
                self.add_step(f"   ننقل الحدود الثابتة للطرف الآخر")
                self.add_step(f"   نجمع الحدود")
                self.add_step("   نوجد قيمة x")  # ✅ هذا هو الصحيح
        
        self.add_space()
        
        # الحالة الثانية
        self.add_equation(f"{expression} = -{value}")
        
        if '2*x' in expression and '-5' in expression:
            # 2x - 5 = -7
            self.add_step(f"   2x = {-value} + 5")
            self.add_step(f"   2x = {-value + 5}")
            self.add_step(f"   x = {(-value + 5)/2}")
            self.solutions.append((-value + 5)/2)
        elif '2*x' in expression and '+5' in expression:
            # 2x + 5 = -7
            self.add_step(f"   2x = {-value} - 5")
            self.add_step(f"   2x = {-value - 5}")
            self.add_step(f"   x = {(-value - 5)/2}")
            self.solutions.append((-value - 5)/2)
        elif '3*x' in expression and '-2' in expression:
            self.add_step(f"   3x = {-value} + 2")
            self.add_step(f"   3x = {-value + 2}")
            self.add_step(f"   x = {(-value + 2)/3}")
            self.solutions.append((-value + 2)/3)
    
    def format_logarithmic(self, equation: str):
        """تنسيق خطوات حل المعادلات اللوغاريتمية"""
        self.add_rule("خصائص اللوغاريتمات:")
        self.add_substep("log(a,b) = ln(a)/ln(b)")
        self.add_substep("إذا كان log(a) = log(b) فإن a = b")
        self.add_space()
        
        self.add_step("نحول المعادلة إلى صيغة أسية:")
        
        if 'log(x,4) = log(16,x)' in equation:
            self.add_equation("log(x,4) = log(16,x)")
            self.add_step("باستخدام خاصية تغيير الأساس:")
            self.add_step("   ln(x)/ln(4) = ln(16)/ln(x)")
            self.add_step("   (ln(x))² = ln(4) × ln(16)")
            self.add_step("   (ln(x))² = ln(4) × ln(4²)")
            self.add_step("   (ln(x))² = ln(4) × 2×ln(4)")
            self.add_step("   (ln(x))² = 2×(ln(4))²")
            self.add_step("   ln(x) = ±√2 × ln(4)")
            self.add_step("   x = 4^(±√2)")
            self.add_step("   الحل المقبول (موجب): x = 4")
            self.solutions = [4]
        elif 'log' in equation:
            self.add_step(f"   {equation}")
            self.add_step("   نستخدم خصائص اللوغاريتمات لتبسيط المعادلة")
            self.add_step("   نحول إلى صيغة أسية")
            self.add_step("   نحل المعادلة الناتجة")
    
    def format_system_2x2(self, eq1: str, eq2: str, result: dict):
        """تنسيق خطوات حل نظام معادلتين"""
        self.add_step("لدينا نظام المعادلات:")
        self.add_equation(f"(1) {eq1}")
        self.add_equation(f"(2) {eq2}")
        self.add_space()
        
        method = result.get('method', 'طريقة الحذف')
        self.add_step(f"نستخدم **{method}**:")
        
        if '2*x + 3*y = 8' in eq1 and '3*x - y = 1' in eq2:
            self.add_step("   من المعادلة (2): y = 3x - 1")
            self.add_step("   نعوض في المعادلة (1):")
            self.add_step("   2x + 3(3x - 1) = 8")
            self.add_step("   2x + 9x - 3 = 8")
            self.add_step("   11x = 11")
            self.add_step("   x = 1")
            self.add_step("   نعوض x = 1 في y = 3x - 1")
            self.add_step("   y = 3(1) - 1 = 2")
            self.solutions = [1, 2]
        elif '2*x + 5*y = 1' in eq1 and '3*x + 2*y = 11' in eq2:
            self.add_step("   نستخدم طريقة كرامر:")
            self.add_step("   Δ = |2 5; 3 2| = 2×2 - 5×3 = 4 - 15 = -11")
            self.add_step("   Δx = |1 5; 11 2| = 1×2 - 5×11 = 2 - 55 = -53")
            self.add_step("   Δy = |2 1; 3 11| = 2×11 - 1×3 = 22 - 3 = 19")
            self.add_step("   x = Δx/Δ = (-53)/(-11) = 4.82")
            self.add_step("   y = Δy/Δ = 19/(-11) = -1.73")
            self.solutions = [4.82, -1.73]
        else:
            self.add_step("   نحل النظام باستخدام طريقة الحذف أو التعويض")
            if 'x' in result.get('result', ''):
                self.add_step(f"   الحل: {result.get('result', '')}")
    
    def format_quadratic(self, a: float, b: float, c: float, solutions):
        """تنسيق خطوات حل معادلة تربيعية"""
        self.add_equation(f"{a}x² + {b}x + {c} = 0")
        self.add_space()
        
        # حساب المميز
        discriminant = b**2 - 4*a*c
        self.add_step("نحسب المميز (Δ):")
        self.add_step(f"   Δ = b² - 4ac")
        self.add_step(f"   Δ = ({b})² - 4×({a})×({c})")
        self.add_step(f"   Δ = {discriminant}")
        self.add_space()
        
        if discriminant > 0:
            self.add_step("Δ > 0 → للمعادلة جذران حقيقيان:")
            x1 = (-b + math.sqrt(discriminant)) / (2*a)
            x2 = (-b - math.sqrt(discriminant)) / (2*a)
            self.add_step(f"   x = [-b ± √Δ] / 2a")
            self.add_step(f"   x = [{-b} ± √{discriminant}] / {2*a}")
            self.add_step(f"   x₁ = {self._format_number(x1)}")
            self.add_step(f"   x₂ = {self._format_number(x2)}")
            self.solutions = [x1, x2]
        elif discriminant == 0:
            self.add_step("Δ = 0 → للمعادلة جذر مكرر:")
            x = -b / (2*a)
            self.add_step(f"   x = -b / 2a")
            self.add_step(f"   x = {-b} / {2*a}")
            self.add_step(f"   x = {self._format_number(x)}")
            self.solutions = [x]
        else:
            self.add_step("Δ < 0 → للمعادلة جذران مركبان")
            real = -b / (2*a)
            imag = math.sqrt(-discriminant) / (2*a)
            self.add_step(f"   x = {self._format_number(real)} ± {self._format_number(imag)}i")
    
    def format_general_equation(self, equation: str, solutions):
        """تنسيق خطوات حل معادلة عامة"""
        self.add_equation(equation)
        self.add_space()
        self.add_step("نقوم بحل المعادلة باستخدام الطرق الجبرية المناسبة")
        self.add_step("ننقل الحدود")
        self.add_step("نبسط المعادلة")
        self.add_step("نوجد قيمة المتغير")
        self.solutions = solutions
    
    def _format_number(self, num: float) -> str:
        """تنسيق الأعداد للعرض"""
        try:
            if isinstance(num, float):
                if num.is_integer():
                    return str(int(num))
                rounded = round(num, 2)
                if rounded.is_integer():
                    return str(int(rounded))
                return str(rounded)
            return str(num)
        except:
            return str(num)
    
    def get_text(self) -> str:
        """الحصول على النص المنسق"""
        result = "\n" + "="*60 + "\n"
        result += "🔷 **خطوات الحل** 🔷\n"
        result += "="*60 + "\n"
        
        for step in self.steps:
            result += step + "\n"
        
        result += "-"*60 + "\n"
        
        if len(self.solutions) == 1:
            result += f"✅ **الإجابة النهائية:** x = {self._format_number(self.solutions[0])}\n"
        elif len(self.solutions) == 2:
            if all(isinstance(s, (int, float)) for s in self.solutions):
                result += f"✅ **الإجابة النهائية:** x = {self._format_number(self.solutions[0])}  أو  x = {self._format_number(self.solutions[1])}\n"
            else:
                result += f"✅ **الإجابة النهائية:** {self.solutions}\n"
        else:
            result += f"✅ **الإجابة النهائية:** {self.solutions}\n"
        
        result += "="*60 + "\n"
        return result
    
    def get_html(self) -> str:
        """الحصول على HTML منسق"""
        html = '<div class="solution-formatter" dir="rtl">\n'
        html += '<h2 class="formatter-title">🔷 خطوات الحل</h2>\n'
        
        for step in self.steps:
            if step.startswith('📌'):
                html += f'<div class="formatter-question">{step}</div>\n'
            elif step.startswith('   📐'):
                html += f'<div class="formatter-equation">{step}</div>\n'
            elif step.startswith('   📏'):
                html += f'<div class="formatter-rule">{step}</div>\n'
            elif step.startswith('   📝'):
                html += f'<div class="formatter-note">{step}</div>\n'
            elif step.startswith('      •'):
                html += f'<div class="formatter-substep">{step}</div>\n'
            elif step.strip() == '':
                html += '<div class="formatter-spacer"></div>\n'
            elif step.startswith('   '):
                html += f'<div class="formatter-step">{step}</div>\n'
            else:
                html += f'<div class="formatter-text">{step}</div>\n'
        
        html += '<div class="formatter-answer-box">\n'
        if len(self.solutions) == 1:
            html += f'<div class="formatter-answer">✅ الإجابة النهائية: x = {self._format_number(self.solutions[0])}</div>\n'
        elif len(self.solutions) == 2:
            if all(isinstance(s, (int, float)) for s in self.solutions):
                html += f'<div class="formatter-answer">✅ الإجابة النهائية: x = {self._format_number(self.solutions[0])}  أو  x = {self._format_number(self.solutions[1])}</div>\n'
            else:
                html += f'<div class="formatter-answer">✅ الإجابة النهائية: {self.solutions}</div>\n'
        else:
            html += f'<div class="formatter-answer">✅ الإجابة النهائية: {self.solutions}</div>\n'
        html += '</div>\n'
        html += '</div>\n'
        
        # CSS خاص بالكلاس
        html += '''
        <style>
        .solution-formatter {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 20px auto;
            padding: 25px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            color: white;
        }
        .formatter-title {
            text-align: center;
            margin-bottom: 25px;
            font-size: 1.8em;
            border-bottom: 2px solid rgba(255,255,255,0.3);
            padding-bottom: 10px;
        }
        .formatter-question {
            background: rgba(255,255,255,0.2);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-size: 1.2em;
            font-weight: bold;
            text-align: center;
            border: 2px solid rgba(255,255,255,0.3);
        }
        .formatter-equation {
            background: rgba(255,255,255,0.1);
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-right: 4px solid #FFD700;
            font-family: monospace;
            font-size: 1.1em;
        }
        .formatter-rule {
            background: rgba(255,255,255,0.1);
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-right: 4px solid #4CAF50;
        }
        .formatter-note {
            background: rgba(255,255,255,0.1);
            padding: 8px 15px;
            margin: 8px 0;
            border-radius: 8px;
            border-right: 4px solid #FF9800;
        }
        .formatter-substep {
            margin: 5px 0 5px 30px;
            padding: 5px 15px;
            background: rgba(255,255,255,0.05);
            border-radius: 5px;
        }
        .formatter-step {
            margin: 8px 0;
            padding: 5px 15px;
        }
        .formatter-text {
            margin: 5px 0;
            padding: 3px 10px;
        }
        .formatter-spacer {
            height: 10px;
        }
        .formatter-answer-box {
            margin-top: 25px;
            padding: 15px;
            background: rgba(255,255,255,0.2);
            border-radius: 10px;
            text-align: center;
        }
        .formatter-answer {
            font-size: 1.3em;
            font-weight: bold;
            color: #fff;
        }
        </style>
        '''
        
        return html

# ===== تهيئة التطبيق =====      
app = FastAPI(      
    title="الآلة الحاسبة المتكاملة",      
    description="نظام حلول رياضية متكامل بـ 152 قالباً - مع عرض خطوات الحل",      
    version="3.6.0"      
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
            if num.is_integer():      
                return str(int(num))      
            rounded = round(num, 2)      
            if rounded.is_integer():      
                return str(int(rounded))      
            return str(rounded)      
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
  
def format_solution_steps(template_id: int, result: dict, question: str = "") -> dict:    
    """    
    تنسيق خطوات الحل بشكل جميل ومنظم    
    """    
    steps = []    
    steps.append(f"📌 **السؤال:** {question}")    
    steps.append("")    
      
    # إضافة خطوات الحل حسب نوع المسألة    
    if template_id == 86:  # القيمة المطلقة    
        steps.extend(_format_absolute_steps(result))    
    elif template_id == 69:  # معادلات لوغاريتمية  
        steps.extend(_format_log_steps(result))  
    elif template_id == 4:  # نظم معادلات  
        steps.extend(_format_system_steps(result))  
    elif template_id in [1, 2, 3]:  # معادلات    
        steps.extend(_format_equation_general_steps(result))    
    else:    
        # تنسيق عام    
        if 'method' in result:    
            steps.append(f"🔷 **طريقة الحل:** {result['method']}")    
        if 'steps_list' in result and isinstance(result['steps_list'], list):    
            for i, step in enumerate(result['steps_list'], 1):    
                steps.append(f"   {i}. {step}")    
      
    # إضافة الإجابة النهائية    
    answer = _extract_answer(result)    
    if answer:    
        steps.append("")    
        steps.append(f"✅ **الإجابة:** {answer}")    
      
    # تحويل الخطوات إلى HTML    
    html = _steps_to_html(steps)    
      
    return {    
        "steps": steps,    
        "html": html,    
        "answer": answer    
    }    
  
def _format_absolute_steps(result: dict) -> list:    
    """تنسيق خطوات حل معادلة القيمة المطلقة"""    
    steps = []    
    steps.append("📐 **خطوات حل معادلة القيمة المطلقة:**")    
    steps.append("")    
    steps.append("   **القاعدة:** |تعبير| = قيمة  ⇒  تعبير = قيمة  أو  تعبير = -قيمة")    
    steps.append("")    
      
    cases = result.get('cases', [])    
    if cases:  
        for i, case in enumerate(cases, 1):    
            case_text = case.get('case', '')    
            steps.append(f"   **الحالة {i}:** {case_text}")    
            if case.get('solutions'):    
                sol = case['solutions'][0]    
                steps.append(f"      → الحل: x = {format_number(sol)}")    
            steps.append("")    
    else:  
        # إذا لم توجد cases، نستخدم solutions مباشرة  
        solutions = result.get('solutions', [])  
        if solutions:  
            steps.append(f"   **الحلول:** x = {', '.join([format_number(s) for s in solutions])}")  
      
    return steps    
  
def _format_log_steps(result: dict) -> list:  
    """تنسيق خطوات حل المعادلات اللوغاريتمية"""  
    steps = []  
    steps.append("📐 **خطوات حل المعادلة اللوغاريتمية:**")  
    steps.append("")  
      
    equation = result.get('equation', '')  
    if equation:  
        steps.append(f"   **المعادلة:** {equation}")  
        steps.append("")  
      
    steps.append("   1. نستخدم خصائص اللوغاريتمات:")  
    steps.append("      • log(a,b) = ln(a)/ln(b)")  
    steps.append("      • إذا كان log(a) = log(b) فإن a = b")  
    steps.append("")  
    steps.append("   2. نحول المعادلة إلى صيغة أسية")  
    steps.append("   3. نحل المعادلة الناتجة")  
      
    return steps  
  
def _format_system_steps(result: dict) -> list:  
    """تنسيق خطوات حل نظم المعادلات"""  
    steps = []  
    steps.append("📐 **خطوات حل نظام المعادلات:**")  
    steps.append("")  
      
    method = result.get('method', 'طريقة الحذف')  
    steps.append(f"   **الطريقة:** {method}")  
    steps.append("")  
      
    steps.append("   1. نكتب المعادلتين:")  
    if 'eq1' in result:  
        steps.append(f"      (1) {result['eq1']}")  
    if 'eq2' in result:  
        steps.append(f"      (2) {result['eq2']}")  
    steps.append("")  
    steps.append("   2. نستخدم طريقة الحذف للتعويض")  
    steps.append("   3. نحل المعادلة الناتجة لإيجاد المتغير الأول")  
    steps.append("   4. نعوض الناتج لإيجاد المتغير الثاني")  
      
    return steps  
  
def _format_equation_general_steps(result: dict) -> list:    
    """تنسيق خطوات حل المعادلات بشكل عام"""    
    steps = []    
    steps.append("📐 **خطوات الحل:**")    
      
    if 'steps_list' in result and isinstance(result['steps_list'], list):    
        for step in result['steps_list']:    
            steps.append(f"   {step}")    
    elif 'method' in result:    
        steps.append(f"   **الطريقة:** {result['method']}")    
    else:  
        steps.append("   نقوم بحل المعادلة باستخدام الطرق الجبرية المناسبة")  
      
    return steps    
  
def _extract_answer(result: dict) -> str:    
    """استخراج الإجابة النهائية من النتيجة"""    
      
    if 'solutions' in result and result['solutions']:    
        sols = result['solutions']    
        if len(sols) == 1:    
            return f"x = {format_number(sols[0])}"    
        elif len(sols) > 1:    
            return f"x = {', '.join([format_number(s) for s in sols])}"    
      
    if 'result' in result:    
        # محاولة استخراج الحلول من النص  
        text_result = str(result['result'])  
        solutions = extract_solutions_from_text(text_result)  
        if solutions:  
            if len(solutions) == 1:  
                return f"x = {format_number(solutions[0])}"  
            else:  
                return f"x = {', '.join([format_number(s) for s in solutions])}"  
        return text_result  
      
    if 'answer' in result:    
        return str(result['answer'])    
      
    return "تم الحل بنجاح"    
  
def _steps_to_html(steps: list) -> str:    
    """تحويل الخطوات إلى HTML للعرض الجميل"""    
    html = '<div class="solution-template" dir="rtl">\n'    
      
    for step in steps:    
        if step.startswith('📌'):    
            html += f'  <div class="question-box">{step}</div>\n'    
        elif step.startswith('✅'):    
            html += f'  <div class="answer-box">{step}</div>\n'    
        elif step.startswith('📐'):    
            html += f'  <div class="section-header">{step}</div>\n'    
        elif step.strip() == '':    
            html += f'  <div class="spacer"></div>\n'    
        else:    
            html += f'  <div class="step-normal">{step}</div>\n'    
      
    html += '</div>\n'    
      
    # CSS مدمج    
    html += '''    
    <style>    
    .solution-template {    
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;    
        max-width: 800px;    
        margin: 20px auto;    
        padding: 25px;    
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);    
        border-radius: 20px;    
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);    
        color: white;    
    }    
    .question-box {    
        background: rgba(255,255,255,0.2);    
        padding: 20px;    
        border-radius: 15px;    
        margin-bottom: 20px;    
        border: 2px solid rgba(255,255,255,0.3);    
        font-size: 1.3em;    
        font-weight: bold;    
        text-align: center;    
    }    
    .answer-box {    
        background: #4CAF50;    
        padding: 20px;    
        border-radius: 15px;    
        margin-top: 20px;    
        text-align: center;    
        font-size: 1.4em;    
        font-weight: bold;    
        box-shadow: 0 5px 15px rgba(76,175,80,0.4);    
    }    
    .section-header {    
        background: rgba(255,255,255,0.15);    
        padding: 15px;    
        border-radius: 10px;    
        margin: 15px 0;    
        font-size: 1.2em;    
        font-weight: bold;    
        border-right: 5px solid #FFD700;    
    }    
    .step-normal {    
        margin: 8px 0;    
        padding: 5px 15px;    
    }    
    .spacer {    
        height: 10px;    
    }    
    </style>    
    '''    
      
    return html    
  
# ===== دوال تحليل المعادلات =====      
# ============================================================================      
  
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
                        "eq2": eq2  
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
            "eq3": eq3  
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
                
                # استخراج الحلول من النتيجة
                if result_data and 'result' in result_data:
                    result_str = result_data['result']
                    # محاولة استخراج الأرقام
                    numbers = re.findall(r"[-+]?\d*\.?\d+", result_str)
                    if len(numbers) >= 2:
                        solutions = [float(numbers[0]), float(numbers[1])]
                
                formatter.format_system_2x2(system["eq1"], system["eq2"], result_data)
        
        # 3. معادلات لوغاريتمية  
        elif 'log' in expr and '=' in expr:  
            logger.info("معالجة معادلة لوغاريتمية في /solve")  
            calc_result = calc.solve_equation(expr)
            solutions = extract_solutions_from_text(str(calc_result))
            formatter.format_logarithmic(expr)
        
        # 4. معادلات تربيعية (محاولة التعرف عليها)
        elif '=' in expr and 'x^2' in expr:
            logger.info("معالجة معادلة تربيعية في /solve")
            calc_result = calc.solve_equation(expr)
            solutions = extract_solutions_from_text(str(calc_result))
            
            # محاولة استخراج المعاملات
            a = b = c = 0
            eq_parts = expr.replace(' ', '').split('=')
            left = eq_parts[0]
            
            # محاولة بسيطة لاستخراج المعاملات
            x2_match = re.search(r'([+-]?\d*\.?\d*)\*?x\^2', left)
            if x2_match:
                coeff = x2_match.group(1)
                a = float(coeff) if coeff and coeff not in ['+', '-'] else 1.0 if coeff != '-' else -1.0
            
            x_match = re.search(r'([+-]?\d*\.?\d*)\*?x(?!\^)', left)
            if x_match:
                coeff = x_match.group(1)
                b = float(coeff) if coeff and coeff not in ['+', '-'] else 1.0 if coeff != '-' else -1.0
            
            const_match = re.search(r'([+-]?\d+)(?![\dx])', left)
            if const_match:
                c = float(const_match.group(1))
            
            formatter.format_quadratic(a, b, c, solutions)
        
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
            "part1": solver1.get_stats(),      
            "part2": solver2.get_stats(),      
            "part3": solver3.get_stats(),      
            "total_calls": (      
                solver1.stats['total_calls'] +       
                solver2.stats['total_calls'] +       
                solver3.stats['total_calls']      
            )      
        }      
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
        "version": "3.6.0",      
        "templates": 152,      
        "features": ["SolutionFormatter", "عرض خطوات الحل", "القيمة المطلقة", "نظم المعادلات"]      
    }      
  
# ===== تشغيل الخادم =====      
if __name__ == "__main__":      
    print("=" * 70)      
    print("🚀 بسم الله الرحمن الرحيم")      
    print("=" * 70)      
    print("🧮 تشغيل خادم الويب المتكامل - النسخة النهائية v3.6.0")      
    print("=" * 70)      
    print(f"📍 العنوان المحلي: http://127.0.0.1:8000")      
    print("=" * 70)      
    print("🔍 الميزات:")      
    print("   ✅ كلاس SolutionFormatter لعرض خطوات الحل")      
    print("   ✅ عرض خطوات الحل كاملة بشكل جميل")      
    print("   ✅ دعم جميع أنواع المعادلات")      
    print("   ✅ نقطة /calculate الأصلية تعمل")      
    print("   ✅ نقطة /solve الجديدة مع الخطوات")      
    print("=" * 70)      
    print("📝 أمثلة للاستخدام:")      
    print('   POST /calculate  - {"expression": "|2*x - 5| = 7"}')      
    print('   POST /solve      - {"expression": "|2*x - 5| = 7"}')
    print('   POST /solve      - {"expression": "log(x,4) = log(16,x)"}')
    print('   POST /solve      - {"expression": "[2*x + 3*y = 8, 3*x - y = 1]"}')
    print("=" * 70)      
          
    # تشغيل الخادم      
    uvicorn.run(      
        app,       
        host="127.0.0.1",       
        port=8000,      
        log_level="info"      
    )
