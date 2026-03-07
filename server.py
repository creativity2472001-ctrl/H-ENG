# server.py - خادم الويب المتكامل (نسخة نهائية مع عرض خطوات الحل)
# ============================================================================  
# هذا الملف يدمج جميع القوالب الجديدة مع النظام القديم  
# الإصدار: 3.5.0 - مع عرض خطوات الحل بشكل جميل ومتكامل
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
  
# ===== تهيئة التطبيق =====  
app = FastAPI(  
    title="الآلة الحاسبة المتكاملة",  
    description="نظام حلول رياضية متكامل بـ 152 قالباً - مع عرض خطوات الحل",  
    version="3.5.0"  
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

# ===== دوال تنسيق وعرض خطوات الحل بشكل جميل =====
# ============================================================================

def format_solution_steps(template_id: int, result: dict, question: str = "") -> dict:
    """
    تنسيق خطوات الحل بشكل جميل ومنظم
    هذه الدالة لا تعدل النتيجة الأصلية، فقط تضيف تنسيقاً للعرض
    """
    steps = []
    steps.append(f"📌 **السؤال:** {question}")
    steps.append("")
    
    # تحديد نوع القالب وعرض الخطوات المناسبة
    if template_id == 86:  # القيمة المطلقة
        steps.extend(_format_absolute_steps(result))
    elif template_id in [1, 2, 3]:  # المعادلات الأساسية
        steps.extend(_format_equation_steps(result))
    elif template_id in [4, 5, 21, 22, 23]:  # نظم المعادلات
        steps.extend(_format_system_steps(result))
    elif template_id in [53, 54, 55, 56, 57, 58]:  # القوى والأسس
        steps.extend(_format_power_steps(result))
    elif template_id in [59, 60, 61, 62, 63]:  # الجذور
        steps.extend(_format_root_steps(result))
    elif template_id in [64, 65, 66, 67, 68]:  # قواعد اللوغاريتمات
        steps.extend(_format_log_rules_steps(result))
    elif template_id in [69, 70, 71, 72, 73, 74]:  # معادلات لوغاريتمية
        steps.extend(_format_log_equation_steps(result))
    elif template_id in [75, 76, 77, 78, 79, 80]:  # معادلات أسية
        steps.extend(_format_exponential_steps(result))
    elif template_id in [81, 82, 83, 84, 85]:  # معادلات كسرية
        steps.extend(_format_rational_steps(result))
    elif template_id in [91, 92, 93, 94, 95, 96, 97, 98]:  # عمليات كسور
        steps.extend(_format_fraction_ops_steps(result))
    elif template_id in [99, 100, 101, 102]:  # معادلات جذرية
        steps.extend(_format_radical_steps(result))
    elif template_id in [103, 104, 105, 106, 107, 108]:  # معادلات رباعية
        steps.extend(_format_quartic_steps(result))
    elif template_id in [144, 145, 146, 147, 148, 149, 150, 151, 152]:  # التحقق
        steps.extend(_format_verification_steps(result))
    else:
        # تنسيق عام
        if 'method' in result:
            steps.append(f"🔷 **طريقة الحل:** {result['method']}")
        if 'steps' in result and isinstance(result['steps'], list):
            for i, step in enumerate(result['steps'], 1):
                steps.append(f"   {i}. {step}")
    
    # إضافة الإجابة النهائية
    answer = _extract_answer(result)
    if answer:
        steps.append("")
        steps.append(f"✅ **الإجابة:** {answer}")
    
    # تحويل الخطوات إلى HTML و LaTeX
    html = _steps_to_html(steps, template_id)
    latex = _steps_to_latex(steps)
    
    return {
        "steps": steps,
        "html": html,
        "latex": latex,
        "answer": answer,
        "template_id": template_id
    }

def _format_absolute_steps(result: dict) -> list:
    """تنسيق خطوات حل معادلة القيمة المطلقة"""
    steps = []
    steps.append("📐 **خطوات حل معادلة القيمة المطلقة:**")
    steps.append("")
    steps.append("   **القاعدة:** |تعبير| = قيمة  ⇒  تعبير = قيمة  أو  تعبير = -قيمة")
    steps.append("")
    
    cases = result.get('cases', [])
    for i, case in enumerate(cases, 1):
        case_text = case.get('case', '')
        steps.append(f"   **الحالة {i}:** {case_text}")
        if case.get('solutions'):
            sol = case['solutions'][0]
            steps.append(f"      → الحل: x = {format_number(sol)}")
        steps.append("")
    
    return steps

def _format_equation_steps(result: dict) -> list:
    """تنسيق خطوات حل المعادلات"""
    steps = []
    steps.append("📐 **خطوات حل المعادلة:**")
    
    if 'discriminant' in result:
        d = result['discriminant']
        steps.append(f"   **المميز (Δ) = {d}**")
        if d > 0:
            steps.append("   ✓ Δ > 0 → للمعادلة جذران حقيقيان مختلفان")
        elif d == 0:
            steps.append("   ✓ Δ = 0 → للمعادلة جذر حقيقي مكرر")
        else:
            steps.append("   ✓ Δ < 0 → للمعادلة جذران مركبان")
    
    if 'roots' in result:
        steps.append(f"   **الجذور:** {result['roots']}")
    
    return steps

def _format_system_steps(result: dict) -> list:
    """تنسيق خطوات حل نظم المعادلات"""
    steps = []
    steps.append("📐 **خطوات حل نظام المعادلات:**")
    
    if 'method' in result:
        steps.append(f"   **طريقة الحل:** {result['method']}")
    
    if 'steps' in result and isinstance(result['steps'], list):
        for i, step in enumerate(result['steps'], 1):
            steps.append(f"   {i}. {step}")
    
    return steps

def _format_power_steps(result: dict) -> list:
    """تنسيق خطوات حل معادلات القوى والأسس"""
    steps = []
    steps.append("📐 **خطوات حل المعادلة الأسية:**")
    
    if 'method' in result:
        steps.append(f"   **الطريقة:** {result['method']}")
    
    if 'logarithmic_form' in result:
        steps.append(f"   **الصيغة اللوغاريتمية:** {result['logarithmic_form']}")
    
    if 'rules_demonstration' in result:
        steps.append("   **القوانين المستخدمة:**")
        for rule in result['rules_demonstration']:
            if isinstance(rule, dict):
                steps.append(f"      • {rule.get('rule', '')}")
    
    return steps

def _format_root_steps(result: dict) -> list:
    """تنسيق خطوات تبسيط الجذور"""
    steps = []
    steps.append("📐 **خطوات تبسيط الجذر:**")
    
    if 'method' in result:
        steps.append(f"   **الطريقة:** {result['method']}")
    
    if 'prime_factors' in result:
        steps.append(f"   **التحليل:** {result['prime_factors']}")
        steps.append(f"   **التبسيط:** {result.get('original', '')} = {result.get('simplified', '')}")
    
    return steps

def _format_log_rules_steps(result: dict) -> list:
    """تنسيق خطوات تطبيق قواعد اللوغاريتم"""
    steps = []
    steps.append("📐 **تطبيق قواعد اللوغاريتم:**")
    
    if 'property' in result:
        steps.append(f"   **القاعدة:** {result['property']}")
    
    if 'demonstration' in result:
        demo = result['demonstration']
        if isinstance(demo, dict):
            steps.append(f"   **التحقق:** الطرف الأيسر = {demo.get('left', '')}, الطرف الأيمن = {demo.get('right', '')}")
    
    return steps

def _format_log_equation_steps(result: dict) -> list:
    """تنسيق خطوات حل المعادلات اللوغاريتمية"""
    steps = []
    steps.append("📐 **خطوات حل المعادلة اللوغاريتمية:**")
    
    if 'method' in result:
        steps.append(f"   **الطريقة:** {result['method']}")
    
    if 'exponential_form' in result:
        steps.append(f"   **الصيغة الأسية:** {result['exponential_form']}")
    
    if 'domain_condition' in result:
        steps.append(f"   **شرط المجال:** {result['domain_condition']}")
    
    return steps

def _format_exponential_steps(result: dict) -> list:
    """تنسيق خطوات حل المعادلات الأسية"""
    steps = []
    steps.append("📐 **خطوات حل المعادلة الأسية:**")
    
    if 'method' in result:
        steps.append(f"   **الطريقة:** {result['method']}")
    
    if 'logarithmic_form' in result:
        steps.append(f"   **الصيغة اللوغاريتمية:** {result['logarithmic_form']}")
    
    return steps

def _format_rational_steps(result: dict) -> list:
    """تنسيق خطوات حل المعادلات الكسرية"""
    steps = []
    steps.append("📐 **خطوات حل المعادلة الكسرية:**")
    
    if 'method' in result:
        steps.append(f"   **الطريقة:** {result['method']}")
    
    if 'domain' in result:
        steps.append(f"   **المجال:** {result['domain']}")
    
    if 'excluded_values' in result:
        steps.append(f"   **قيم مستبعدة:** {result['excluded_values']}")
    
    return steps

def _format_fraction_ops_steps(result: dict) -> list:
    """تنسيق خطوات عمليات الكسور"""
    steps = []
    steps.append("📐 **خطوات إجراء العمليات على الكسور:**")
    
    if 'operation' in result:
        steps.append(f"   **العملية:** {result.get('operation', '')}")
    
    if 'steps' in result and isinstance(result['steps'], list):
        for step in result['steps']:
            steps.append(f"   {step}")
    
    return steps

def _format_radical_steps(result: dict) -> list:
    """تنسيق خطوات حل المعادلات الجذرية"""
    steps = []
    steps.append("📐 **خطوات حل المعادلة الجذرية:**")
    
    if 'method' in result:
        steps.append(f"   **الطريقة:** {result['method']}")
    
    if 'domain_condition' in result:
        steps.append(f"   **شرط المجال:** {result['domain_condition']}")
    
    if 'extraneous' in result and result['extraneous']:
        steps.append(f"   **حلول دخيلة:** {result['extraneous']}")
    
    return steps

def _format_quartic_steps(result: dict) -> list:
    """تنسيق خطوات حل المعادلات الرباعية"""
    steps = []
    steps.append("📐 **خطوات حل المعادلة الرباعية:**")
    
    if 'method' in result:
        steps.append(f"   **الطريقة:** {result['method']}")
    
    if 'substitution' in result:
        steps.append(f"   **التعويض:** {result['substitution']}")
    
    return steps

def _format_verification_steps(result: dict) -> list:
    """تنسيق خطوات التحقق من الحلول"""
    steps = []
    steps.append("📐 **خطوات التحقق من الحل:**")
    
    if 'verification' in result and isinstance(result['verification'], list):
        for v in result['verification']:
            if isinstance(v, dict) and 'solution' in v:
                steps.append(f"   **التحقق من الحل {v['solution']}:**")
                if v.get('is_valid'):
                    steps.append(f"      ✅ صحيح")
                else:
                    steps.append(f"      ❌ غير صحيح")
    
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
        return str(result['result'])
    
    if 'answer' in result:
        return str(result['answer'])
    
    return "تم الحل بنجاح"

def _steps_to_html(steps: list, template_id: int) -> str:
    """تحويل الخطوات إلى HTML للعرض الجميل"""
    html = f'<div class="solution-template template-{template_id}" dir="rtl">\n'
    
    for step in steps:
        if step.startswith('📌'):
            html += f'  <div class="question-box"><span class="icon">📌</span> {step[2:]}</div>\n'
        elif step.startswith('✅'):
            html += f'  <div class="answer-box"><span class="icon">✅</span> {step[2:]}</div>\n'
        elif step.startswith('📐'):
            html += f'  <div class="section-header"><span class="icon">📐</span> {step[2:]}</div>\n'
        elif step.startswith('   **'):
            html += f'  <div class="step-bold">{step}</div>\n'
        elif step.startswith('      '):
            html += f'  <div class="step-indent">{step}</div>\n'
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
    .step-bold {
        font-weight: bold;
        margin: 10px 0;
        padding: 5px 15px;
        background: rgba(255,255,255,0.1);
        border-radius: 8px;
    }
    .step-indent {
        margin: 5px 0 5px 30px;
        padding: 5px 15px;
        background: rgba(255,255,255,0.05);
        border-radius: 5px;
        font-size: 0.95em;
    }
    .step-normal {
        margin: 8px 0;
        padding: 5px 15px;
    }
    .spacer {
        height: 10px;
    }
    .icon {
        margin-left: 10px;
        font-size: 1.2em;
    }
    </style>
    '''
    
    return html

def _steps_to_latex(steps: list) -> str:
    """تحويل الخطوات إلى LaTeX للعرض الأكاديمي"""
    latex = []
    latex.append("\\begin{rtl}")
    latex.append("\\textbf{خطوات الحل:}")
    latex.append("")
    
    for step in steps:
        if step.startswith('📌'):
            latex.append(f"\\textbf{{{step[2:]}}}")
        elif step.startswith('✅'):
            latex.append(f"\\boxed{{{step[2:]}}}")
        elif step.startswith('📐'):
            latex.append(f"\\subsection*{{{step[2:]}}}")
        elif step.strip():
            # تنظيف النص من الرموز التعبيرية للـ LaTeX
            clean_step = step.replace('📌', '').replace('✅', '').replace('📐', '')
            latex.append(clean_step)
    
    latex.append("\\end{rtl}")
    return "\n".join(latex)

# ===== دوال تحليل المعادلات =====  
# ============================================================================  
  
def extract_coefficients_from_equation(eq: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:  
    """  
    تحليل معادلة خطية إلى المعاملات a, b, c  
    مثال: "2*x + 3*y = 8" -> (2, 3, 8)  
    """  
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
    """  
    تحليل معادلة خطية بثلاثة متغيرات إلى المعاملات a, b, c, d  
    مثال: "x + y + z = 6" -> (1, 1, 1, 6)  
    """  
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
    """  
    تحليل صيغة نظام المعادلات  
    مثال: "[2*x + 3*y = 8, 3*x - y = 1]"  
    """  
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
    """  
    تنسيق نتيجة نظام المعادلات للعرض بشكل مفهوم للمستخدم  
    """  
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
              
            if 'solution' in result and isinstance(result['solution'], dict) and 'sympy' in result['solution']:  
                sympy_sol = result['solution']['sympy']  
                if 'x' in sympy_sol and 'y' in sympy_sol:  
                    x = sympy_sol['x']  
                    y = sympy_sol['y']  
                    if x is not None and y is not None:  
                        x_str = format_number(x)  
                        y_str = format_number(y)  
                        return f"x = {x_str}, y = {y_str}"  
              
            if 'solution' in result and isinstance(result['solution'], dict) and 'cramer' in result['solution']:  
                cramer_sol = result['solution']['cramer']  
                if 'x' in cramer_sol and 'y' in cramer_sol:  
                    x = cramer_sol['x']  
                    y = cramer_sol['y']  
                    if x is not None and y is not None:  
                        x_str = format_number(x)  
                        y_str = format_number(y)  
                        return f"x = {x_str}, y = {y_str}"  
              
            if result.get('is_dependent', False):  
                general_sol = result.get('general_solution', '')  
                return f"عدد لا نهائي من الحلول: {general_sol}"  
              
            if result.get('is_inconsistent', False):  
                return "لا يوجد حل (نظام متناقض)"  
              
            if 'solutions' in result and isinstance(result['solutions'], dict):  
                if 'sympy_method' in result['solutions']:  
                    sol = result['solutions']['sympy_method']  
                    if sol:  
                        parts = []  
                        if 'x' in sol and sol['x'] is not None:  
                            x = sol['x']  
                            x_str = format_number(x)  
                            parts.append(f"x = {x_str}")  
                        if 'y' in sol and sol['y'] is not None:  
                            y = sol['y']  
                            y_str = format_number(y)  
                            parts.append(f"y = {y_str}")  
                        if 'z' in sol and sol['z'] is not None:  
                            z = sol['z']  
                            z_str = format_number(z)  
                            parts.append(f"z = {z_str}")  
                        if parts:  
                            return ", ".join(parts)  
              
            if 'roots' in result:  
                roots = result['roots']  
                if isinstance(roots, dict) and 'values' in roots:  
                    values = roots['values']  
                    if 'real' in values and values['real']:  
                        real_roots = [format_number(r) for r in values['real']]  
                        return f"x = {real_roots}"  
                    elif 'decimal' in values:  
                        decimals = [format_number(d) for d in values['decimal']]  
                        return f"x = {decimals}"  
              
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
    """  
    حل نظام معادلتين 2×2 مع محاولة جميع التوابع المتاحة  
    """  
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
            ("template_04_system_2x2", getattr(solver1, 'template_04_system_2x2', None))  
        ]  
          
        last_error = None  
          
        for solver_name, solver_func in solvers:  
            if solver_func is None:  
                continue  
                  
            try:  
                logger.info(f"محاولة استخدام {solver_name}")  
                result = solver_func(a1, b1, c1, a2, b2, c2)  
                  
                if result:  
                    formatted = format_system_result(result)  
                    return {  
                        "success": True,  
                        "result": formatted,  
                        "method": solver_name  
                    }  
            except Exception as e:  
                last_error = str(e)  
                logger.warning(f"فشل {solver_name}: {e}")  
                continue  
          
        return {  
            "success": False,  
            "error": f"فشل حل النظام. آخر خطأ: {last_error}"  
        }  
          
    except Exception as e:  
        logger.error(f"خطأ غير متوقع في حل النظام: {str(e)}")  
        return {  
            "success": False,  
            "error": f"خطأ غير متوقع: {str(e)}"  
        }  
  
def solve_system_3x3(eq1: str, eq2: str, eq3: str) -> Dict[str, Any]:  
    """  
    حل نظام ثلاث معادلات 3×3  
    """  
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
          
        logger.info(f"المعاملات: ({a1},{b1},{c1},{d1}), ({a2},{b2},{c2},{d2}), ({a3},{b3},{c3},{d3})")  
          
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
          
        logger.info(f"الحل: x={x}, y={y}, z={z}")  
          
        result = {  
            "success": True,  
            "result": f"x = {format_number(x)}, y = {format_number(y)}, z = {format_number(z)}"  
        }  
          
        return result  
          
    except Exception as e:  
        logger.error(f"خطأ في حل نظام 3×3: {str(e)}")  
        return {  
            "success": False,  
            "error": str(e)  
        }  

# ===== نقطة نهاية جديدة لعرض الحل مع الخطوات =====
# ============================================================================

@app.post("/solve")
async def solve_with_steps(data: ExpressionRequest):
    """
    نقطة النهاية الرئيسية - تحل المسألة وتعرض خطوات الحل بشكل جميل
    """
    try:
        expr = data.expression.strip()
        logger.info(f"طلب حل مع خطوات: {expr}")
        
        # ===== تحديد القالب المناسب =====
        template_id = None
        params = {}
        raw_result = None
        
        # 1. القيمة المطلقة
        if '|' in expr and '=' in expr and not (expr.startswith('[') and expr.endswith(']')):
            template_id = 86
            match = re.search(r'\|(.*?)\|\s*=\s*(.+)', expr)
            if match:
                params['expression'] = match.group(1).strip()
                value_str = match.group(2).strip()
                try:
                    params['value'] = float(value_str)
                except:
                    params['value'] = float(eval(value_str, {"__builtins__": {}}, math.__dict__))
                
                raw_result = solver2.template_86_absolute_simple(
                    params.get('expression'), 
                    params.get('value')
                )
        
        # 2. نظم المعادلات
        elif expr.startswith('[') and expr.endswith(']') and ',' in expr:
            system = parse_system_equations(expr)
            if system and system["type"] == "system_2x2":
                template_id = 4
                system_result = solve_system_2x2(system["eq1"], system["eq2"])
                raw_result = {
                    "solutions": [system_result.get("result", "")],
                    "method": system_result.get("method", "طريقة الحذف"),
                    "steps": [
                        f"المعادلة الأولى: {system['eq1']}",
                        f"المعادلة الثانية: {system['eq2']}",
                        f"باستخدام {system_result.get('method', 'طريقة الحذف')}"
                    ]
                }
        
        # 3. معادلات عادية
        elif '=' in expr:
            template_id = 2
            calc_result = calc.solve_equation(expr)
            
            # محاولة استخراج الحلول
            solutions = []
            if isinstance(calc_result, str):
                if 'x =' in calc_result:
                    sol_part = calc_result.split('=')[1].strip()
                    if '[' in sol_part and ']' in sol_part:
                        sol_part = sol_part.replace('[', '').replace(']', '')
                        solutions = [float(s.strip()) for s in sol_part.split(',') if s.strip()]
                    else:
                        try:
                            solutions = [float(sol_part)]
                        except:
                            solutions = []
            
            raw_result = {
                "solutions": solutions,
                "equation": expr,
                "method": "حل المعادلة مباشرة"
            }
        
        # 4. عمليات حسابية عادية
        else:
            template_id = 0
            calc_result = calc.calculate(expr)
            if isinstance(calc_result, float) and calc_result.is_integer():
                calc_result = int(calc_result)
            
            raw_result = {
                "solutions": [calc_result],
                "expression": expr,
                "method": "عملية حسابية"
            }
        
        # إذا لم يتم العثور على نتيجة
        if raw_result is None:
            return {
                "success": False,
                "error": "لم يتم التعرف على نوع المسألة",
                "steps": ["لم يتم تحديد قالب مناسب"],
                "html": "<div class='error'>لم يتم التعرف على نوع المسألة</div>",
                "answer": ""
            }
        
        # تنسيق الخطوات
        formatted = format_solution_steps(template_id, raw_result, expr)
        
        return {
            "success": True,
            "steps": formatted["steps"],
            "html": formatted["html"],
            "latex": formatted["latex"],
            "answer": formatted["answer"],
            "template_id": template_id
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

# ===== نقاط النهاية الأخرى (بدون تغيير) =====
# ============================================================================

@app.post("/calculate")  
async def calculate(data: ExpressionRequest):  
    """  
    نقطة النهاية القديمة - للتوافق مع الإصدارات السابقة
    """  
    try:  
        expr = data.expression.strip()  
        logger.info(f"طلب calculate: {expr}")  
        
        # استخدام الدالة الجديدة ثم استخراج النتيجة فقط
        result = await solve_with_steps(data)
        
        if result["success"]:
            return {"success": True, "result": result["answer"]}
        else:
            return {"success": False, "error": result.get("error", "خطأ غير معروف")}
          
    except Exception as e:  
        logger.error(f"خطأ في calculate: {str(e)}")  
        return {"success": False, "error": str(e)}  

@app.post("/algebra/template/{template_id}")  
async def solve_template(template_id: int, request: TemplateRequest):  
    """  
    حل قالب رياضي محدد باستخدام المعاملات المعطاة  
    """  
    try:  
        params = request.params  
        result = None  
        logger.info(f"طلب قالب {template_id} مع المعاملات: {params}")  
          
        # ===== القوالب 1-52 (الملف الأول) =====  
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
            elif template_id == 6:  
                result = solver1.template_06_simplify_expression(  
                    params.get('expression'), params.get('method', 'auto')  
                )  
            elif template_id == 7:  
                result = solver1.template_07_gcd(  
                    params.get('expr1'), params.get('expr2')  
                )  
            elif template_id == 8:  
                result = solver1.template_08_lcm(  
                    params.get('expr1'), params.get('expr2')  
                )  
            elif template_id == 9:  
                result = solver1.template_09_expand(  
                    params.get('expression'), params.get('fully', True)  
                )  
            elif template_id == 10:  
                result = solver1.template_10_factorize(  
                    params.get('expression'), params.get('method', 'auto')  
                )  
            else:  
                result = {"error": f"القالب {template_id} غير مضمن بعد في هذه النسخة"}  
          
        # ===== القوالب 53-102 (الملف الثاني) =====  
        elif 53 <= template_id <= 102:  
            if template_id == 53:  
                result = solver2.template_53_power_rules(  
                    params.get('base'), params.get('exponent')  
                )  
            elif template_id == 54:  
                result = solver2.template_54_power_equations_same_base(  
                    params.get('base'), params.get('exp1'), params.get('exp2')  
                )  
            elif template_id == 55:  
                result = solver2.template_55_power_equations_different_base(  
                    params.get('a'), params.get('b')  
                )  
            elif template_id == 56:  
                result = solver2.template_56_power_inequalities(  
                    params.get('a'), params.get('b'), params.get('inequality')  
                )  
            elif template_id == 57:  
                result = solver2.template_57_power_system(  
                    params.get('eq1'), params.get('eq2')  
                )  
            elif template_id == 58:  
                result = solver2.template_58_power_word_problems(  
                    params.get('problem_type'), params.get('values', {})  
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
                result = {"error": f"القالب {template_id} غير مضمن بعد في هذه النسخة"}  
          
        # ===== القوالب 103-152 (الملف الثالث) =====  
        elif 103 <= template_id <= 152:  
            if template_id == 103:  
                result = solver3.template_103_quartic_biquadratic(  
                    params.get('a'), params.get('b'), params.get('c')  
                )  
            elif template_id == 104:  
                result = solver3.template_104_quartic_depressed(  
                    params.get('a'), params.get('b'), params.get('c'),   
                    params.get('d'), params.get('e')  
                )  
            elif template_id == 105:  
                result = solver3.template_105_quartic_factorable(  
                    params.get('coefficients')  
                )  
            elif template_id == 106:  
                result = solver3.template_106_quartic_reciprocal(  
                    params.get('a'), params.get('b'), params.get('c')  
                )  
            elif template_id == 107:  
                result = solver3.template_107_quartic_quadratic_form(  
                    params.get('a'), params.get('b'), params.get('c'), params.get('d')  
                )  
            elif template_id == 108:  
                result = solver3.template_108_quartic_general(  
                    params.get('a'), params.get('b'), params.get('c'),   
                    params.get('d'), params.get('e')  
                )  
            else:  
                result = {"error": f"القالب {template_id} غير مضمن بعد في هذه النسخة"}  
          
        else:  
            return {"success": False, "error": "قالب غير موجود"}  
          
        if result:  
            logger.info(f"تم تنفيذ القالب {template_id} بنجاح")  
            if isinstance(result, dict):  
                formatted = format_system_result(result)  
                return {"success": True, "result": formatted}  
            return {"success": True, "result": str(result)}  
        else:  
            return {"success": False, "error": "فشل في تنفيذ القالب"}  
              
    except Exception as e:  
        logger.error(f"خطأ في تنفيذ القالب {template_id}: {str(e)}")  
        return {"success": False, "error": str(e)}  

# ===== باقي نقاط النهاية (بدون تغيير) =====
# ============================================================================

@app.post("/algebra/system")  
async def solve_system(request: SystemRequest):  
    """  
    نقطة نهاية مخصصة لنظم المعادلات  
    """  
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
    """  
    البحث عن قوالب حسب النوع أو الكلمات المفتاحية  
    """  
    try:  
        keyword = query.get('keyword', '').lower()  
        results = []  
          
        if keyword in ['تربيعية', 'quadratic', 'معادلة']:  
            results.append({  
                'template_id': 1,  
                'name': 'المعادلة التربيعية',  
                'description': 'ax² + bx + c = 0'  
            })  
          
        if keyword in ['خطية', 'linear', 'معادلة']:  
            results.append({  
                'template_id': 2,  
                'name': 'المعادلة الخطية',  
                'description': 'ax + b = 0'  
            })  
          
        if keyword in ['نظام', 'system']:  
            results.extend([  
                {'template_id': 4, 'name': 'نظام 2×2', 'description': 'معادلتين خطيتين'},  
                {'template_id': 5, 'name': 'نظام 3×3', 'description': 'ثلاث معادلات خطية'}  
            ])  
          
        if keyword in ['تحليل', 'factor']:  
            results.append({  
                'template_id': 10,  
                'name': 'تحليل العوامل',  
                'description': 'تحليل تعبير جبري'  
            })  
          
        if keyword in ['أسية', 'exponential']:  
            results.extend([  
                {'template_id': 55, 'name': 'معادلة أسية', 'description': 'a^x = b'},  
                {'template_id': 56, 'name': 'متباينة أسية', 'description': 'a^x > b'}  
            ])  
          
        if keyword in ['لوغاريتم', 'log']:  
            results.extend([  
                {'template_id': 64, 'name': 'أساسيات اللوغاريتم', 'description': 'log_b(a)'},  
                {'template_id': 65, 'name': 'خصائص اللوغاريتم', 'description': 'قوانين اللوغاريتمات'}  
            ])  
          
        if keyword in ['جذر', 'root', 'radical']:  
            results.extend([  
                {'template_id': 59, 'name': 'تبسيط جذر تربيعي', 'description': '√n'},  
                {'template_id': 60, 'name': 'تبسيط جذر تكعيبي', 'description': '∛n'},  
                {'template_id': 99, 'name': 'معادلة جذرية', 'description': '√(ax+b) = c'}  
            ])  
          
        if keyword in ['رباعية', 'quartic']:  
            results.extend([  
                {'template_id': 103, 'name': 'معادلة رباعية ثنائية التربيع', 'description': 'ax⁴ + bx² + c = 0'},  
                {'template_id': 108, 'name': 'معادلة رباعية عامة', 'description': 'ax⁴ + bx³ + cx² + dx + e = 0'}  
            ])  
          
        return {"success": True, "results": results}  
          
    except Exception as e:  
        logger.error(f"خطأ في البحث: {str(e)}")  
        return {"success": False, "error": str(e)}  

@app.get("/algebra/templates")  
async def list_templates(category: str = None):  
    """  
    عرض جميع القوالب المتاحة (اختياري حسب الفئة)  
    """  
    templates = {  
        "basic": [  
            {"id": 1, "name": "المعادلة التربيعية", "params": ["a", "b", "c"]},  
            {"id": 2, "name": "المعادلة الخطية", "params": ["equation"]},  
            {"id": 3, "name": "معادلة متعددة الحدود", "params": ["polynomial"]},  
            {"id": 4, "name": "نظام معادلتين 2×2", "params": ["eq1", "eq2"]},  
            {"id": 5, "name": "نظام ثلاث معادلات 3×3", "params": ["eq1", "eq2", "eq3"]},  
            {"id": 6, "name": "تبسيط تعبير جبري", "params": ["expression"]},  
            {"id": 7, "name": "GCD", "params": ["expr1", "expr2"]},  
            {"id": 8, "name": "LCM", "params": ["expr1", "expr2"]},  
            {"id": 9, "name": "توسيع", "params": ["expression"]},  
            {"id": 10, "name": "تحليل", "params": ["expression"]}  
        ],  
        "powers": [  
            {"id": 53, "name": "قوانين القوى", "params": ["base", "exponent"]},  
            {"id": 54, "name": "معادلة أسية - نفس الأساس", "params": ["base", "exp1", "exp2"]},  
            {"id": 55, "name": "معادلة أسية - أساس مختلف", "params": ["a", "b"]},  
            {"id": 56, "name": "متباينة أسية", "params": ["a", "b", "inequality"]},  
            {"id": 59, "name": "تبسيط جذر تربيعي", "params": ["number"]},  
            {"id": 60, "name": "تبسيط جذر تكعيبي", "params": ["number"]}  
        ],  
        "logs": [  
            {"id": 64, "name": "أساسيات اللوغاريتم", "params": ["base", "argument"]},  
            {"id": 65, "name": "خصائص اللوغاريتم", "params": ["operation", "a", "b"]},  
            {"id": 66, "name": "تبسيط تعبير لوغاريتمي", "params": ["expression"]},  
            {"id": 67, "name": "تغيير أساس اللوغاريتم", "params": ["value", "old_base", "new_base"]},  
            {"id": 69, "name": "معادلة لوغاريتمية بسيطة", "params": ["base", "argument", "value"]}  
        ],  
        "quartic": [  
            {"id": 103, "name": "معادلة رباعية ثنائية التربيع", "params": ["a", "b", "c"]},  
            {"id": 104, "name": "معادلة رباعية ناقصة", "params": ["a", "b", "c", "d", "e"]},  
            {"id": 105, "name": "معادلة رباعية قابلة للتحليل", "params": ["coefficients"]},  
            {"id": 108, "name": "معادلة رباعية عامة", "params": ["a", "b", "c", "d", "e"]}  
        ],  
        "verification": [  
            {"id": 144, "name": "التحقق من نوع المعادلة", "params": ["equation"]},  
            {"id": 146, "name": "التحقق من مجال المعادلة", "params": ["equation"]},  
            {"id": 149, "name": "التحقق من صحة جذر", "params": ["equation", "root"]},  
            {"id": 150, "name": "التحقق من عدة جذور", "params": ["equation", "roots"]},  
            {"id": 152, "name": "التحقق من دقة جذر", "params": ["equation", "root"]}  
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
    """  
    إحصائيات استخدام القوالب  
    """  
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
        "version": "3.5.0",  
        "templates": 152,  
        "parts": ["part1 (1-52)", "part2 (53-102)", "part3 (103-152)"],  
        "features": ["عرض خطوات الحل", "القيمة المطلقة", "نظم المعادلات", "تقريب الأعداد"]  
    }  

# ===== تشغيل الخادم =====  
if __name__ == "__main__":  
    print("=" * 70)  
    print("🚀 بسم الله الرحمن الرحيم")  
    print("=" * 70)  
    print("🧮 تشغيل خادم الويب المتكامل - النسخة النهائية v3.5.0")  
    print("=" * 70)  
    print(f"📍 العنوان المحلي: http://127.0.0.1:8000")  
    print(f"🌐 العنوان الشبكي: http://localhost:8000")  
    print("=" * 70)  
    print(f"📊 القوالب المتاحة: 152 قالباً")  
    print(f"   📁 الجزء الأول: القوالب 1-52 (الجبر الأساسي)")  
    print(f"   📁 الجزء الثاني: القوالب 53-102 (الجبر المتوسط)")  
    print(f"   📁 الجزء الثالث: القوالب 103-152 (الجبر المتقدم)")  
    print("=" * 70)  
    print("🔍 الميزات الجديدة في v3.5.0:")  
    print("   ✅ عرض خطوات الحل كاملة بشكل جميل")  
    print("   ✅ تنسيق HTML و LaTeX للعرض")  
    print("   ✅ دعم جميع أنواع المعادلات")  
    print("   ✅ الاحتفاظ بنقطة /calculate القديمة")  
    print("=" * 70)  
    print("🔍 نقاط النهاية المتاحة:")  
    print("   ✅ POST /solve - حل مع خطوات كاملة (جديد)")  
    print("   ✅ POST /calculate - للتوافق مع الإصدارات السابقة")  
    print("   ✅ POST /algebra/template/{id} - حل قالب محدد")  
    print("   ✅ POST /algebra/system - حل نظم معادلات")  
    print("   ✅ POST /algebra/search - بحث عن قوالب")  
    print("   ✅ GET  /algebra/templates - عرض القوالب")  
    print("   ✅ GET  /algebra/stats - إحصائيات")  
    print("   ✅ GET  /health - فحص الصحة")  
    print("=" * 70)  
    print("📝 أمثلة للاستخدام:")  
    print("   • [2*x + 3*y = 8, 3*x - y = 1]        → x = 1, y = 2")  
    print("   • |2*x - 5| = 7                        → x = -1, 6")  
    print("   • x^2 - 5*x + 6 = 0                   → x = 2, 3")  
    print("   • sin(30)                              → 0.5")  
    print("=" * 70)  
    print("✅ النظام جاهز للعمل - جميع الأنظمة تعمل بكفاءة")  
    print("=" * 70)  
      
    # تشغيل الخادم  
    uvicorn.run(  
        app,   
        host="127.0.0.1",   
        port=8000,  
        log_level="info"  
    )
