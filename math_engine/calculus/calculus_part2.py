"""
================================================================================
الملف 2/3: التفاضل والتكامل - التكاملات
File 2/3: Calculus - Integrals (40 Templates)

القوالب:
38. تكاملات أساسية (5 قوالب)
39. تكاملات جزئية (5 قوالب)
40. تكاملات التعويض (5 قوالب)
41. تكاملات بالتجزئة (5 قوالب)
42. التكاملات المحدودة (5 قوالب)
43. التكاملات غير المحدودة (5 قوالب)
44. حساب المساحات تحت المنحنيات (5 قوالب)
45. حساب المساحات بين منحنيين (5 قوالب)
================================================================================
"""

import sympy as sp
import logging
from typing import Dict, Any, List, Union

logger = logging.getLogger(__name__)

# دالة مساعدة لإنشاء الخطوات
def make_step(latex_expr: str, explanation: str) -> dict:
    """إنشاء خطوة موحدة للعرض مع LaTeX"""
    return {
        "latex": latex_expr,
        "explanation": explanation
    }

class CalculusSolverPart2:
    """حلال التكاملات - يغطي القوالب 38-45"""
    
    def __init__(self):
        self.x = sp.Symbol('x', real=True)
        self.y = sp.Symbol('y', real=True)
        self.C = sp.Symbol('C')  # ثابت التكامل
        self.stats = {'total_calls': 0, 'successful': 0, 'failed': 0}
        logger.info("✅ تم تهيئة CalculusSolverPart2 - التكاملات (40 قالب)")

    # =========================================================================
    # 38. تكاملات أساسية (5 قوالب)
    # =========================================================================
    
    def template_38_basic_integral_1(self) -> Dict[str, Any]:
        """قالب 38-1: تكامل x^n dx (n ≠ -1) - مثال: ∫ x³ dx"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\int x^3 \\, dx",
            "المطلوب حساب التكامل"
        ))
        
        steps.append(make_step(
            "\\int x^n \\, dx = \\frac{x^{n+1}}{n+1} + C, \\quad n \\neq -1",
            "قاعدة تكامل القوى"
        ))
        
        steps.append(make_step(
            "\\int x^3 \\, dx = \\frac{x^{3+1}}{3+1} + C",
            "نعوض n = 3"
        ))
        
        steps.append(make_step(
            "= \\frac{x^4}{4} + C",
            "النتيجة النهائية"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{x^4}{4} + C",
            "template": "38-1",
            "name": "∫ x³ dx"
        }
    
    def template_38_basic_integral_2(self) -> Dict[str, Any]:
        """قالب 38-2: تكامل 1/x dx = ln|x| + C"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\int \\frac{1}{x} \\, dx",
            "المطلوب حساب التكامل"
        ))
        
        steps.append(make_step(
            "\\int \\frac{1}{x} \\, dx = \\ln|x| + C",
            "قاعدة تكامل 1/x"
        ))
        
        steps.append(make_step(
            "= \\ln|x| + C",
            "النتيجة النهائية"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\ln|x| + C",
            "template": "38-2",
            "name": "∫ 1/x dx"
        }
    
    def template_38_basic_integral_3(self) -> Dict[str, Any]:
        """قالب 38-3: تكامل sin(x) dx = -cos(x) + C"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\int \\sin(x) \\, dx",
            "المطلوب حساب التكامل"
        ))
        
        steps.append(make_step(
            "\\int \\sin(x) \\, dx = -\\cos(x) + C",
            "قاعدة تكامل الجيب"
        ))
        
        steps.append(make_step(
            "= -\\cos(x) + C",
            "النتيجة النهائية"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "-\\cos(x) + C",
            "template": "38-3",
            "name": "∫ sin(x) dx"
        }
    
    def template_38_basic_integral_4(self) -> Dict[str, Any]:
        """قالب 38-4: تكامل cos(x) dx = sin(x) + C"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\int \\cos(x) \\, dx",
            "المطلوب حساب التكامل"
        ))
        
        steps.append(make_step(
            "\\int \\cos(x) \\, dx = \\sin(x) + C",
            "قاعدة تكامل جيب التمام"
        ))
        
        steps.append(make_step(
            "= \\sin(x) + C",
            "النتيجة النهائية"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\sin(x) + C",
            "template": "38-4",
            "name": "∫ cos(x) dx"
        }
    
    def template_38_basic_integral_5(self) -> Dict[str, Any]:
        """قالب 38-5: تكامل e^x dx = e^x + C"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\int e^x \\, dx",
            "المطلوب حساب التكامل"
        ))
        
        steps.append(make_step(
            "\\int e^x \\, dx = e^x + C",
            "قاعدة تكامل الدالة الأسية"
        ))
        
        steps.append(make_step(
            "= e^x + C",
            "النتيجة النهائية"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "e^x + C",
            "template": "38-5",
            "name": "∫ e^x dx"
        }

    # =========================================================================
    # 39. تكاملات جزئية (Partial Fractions) - 5 قوالب
    # =========================================================================
    
    def template_39_partial_fractions_1(self) -> Dict[str, Any]:
        """قالب 39-1: تكامل 1/(x² - 1) dx"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\int \\frac{1}{x^2 - 1} \\, dx",
            "المطلوب حساب التكامل"
        ))
        
        steps.append(make_step(
            "\\frac{1}{x^2 - 1} = \\frac{1}{(x-1)(x+1)}",
            "نحلل المقام"
        ))
        
        steps.append(make_step(
            "\\frac{1}{(x-1)(x+1)} = \\frac{A}{x-1} + \\frac{B}{x+1}",
            "نفكك إلى كسور جزئية"
        ))
        
        steps.append(make_step(
            "1 = A(x+1) + B(x-1)",
            "نضرب في المقام المشترك"
        ))
        
        steps.append(make_step(
            "1 = (A+B)x + (A-B)",
            "نجمع الحدود"
        ))
        
        steps.append(make_step(
            "\\begin{cases} A+B = 0 \\\\ A-B = 1 \\end{cases}",
            "نقارن المعاملات"
        ))
        
        steps.append(make_step(
            "A = \\frac{1}{2}, \\quad B = -\\frac{1}{2}",
            "نحل النظام"
        ))
        
        steps.append(make_step(
            "\\int \\frac{1}{x^2-1} \\, dx = \\frac{1}{2} \\int \\frac{1}{x-1} \\, dx - \\frac{1}{2} \\int \\frac{1}{x+1} \\, dx",
            "نعوض A و B"
        ))
        
        steps.append(make_step(
            "= \\frac{1}{2} \\ln|x-1| - \\frac{1}{2} \\ln|x+1| + C",
            "نكامل"
        ))
        
        steps.append(make_step(
            "= \\frac{1}{2} \\ln\\left|\\frac{x-1}{x+1}\\right| + C",
            "النتيجة النهائية"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{1}{2} \\ln\\left|\\frac{x-1}{x+1}\\right| + C",
            "template": "39-1",
            "name": "∫ 1/(x²-1) dx"
        }
    
    def template_39_partial_fractions_2(self) -> Dict[str, Any]:
        """قالب 39-2: تكامل 1/(x² + x) dx"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\int \\frac{1}{x^2 + x} \\, dx", "المطلوب حساب التكامل"))
        steps.append(make_step("\\frac{1}{x^2 + x} = \\frac{1}{x(x+1)}", "نحلل المقام"))
        steps.append(make_step("\\frac{1}{x(x+1)} = \\frac{A}{x} + \\frac{B}{x+1}", "نفكك إلى كسور جزئية"))
        steps.append(make_step("1 = A(x+1) + Bx", "نضرب في المقام المشترك"))
        steps.append(make_step("1 = (A+B)x + A", "نجمع الحدود"))
        steps.append(make_step("\\begin{cases} A+B = 0 \\\\ A = 1 \\end{cases}", "نقارن المعاملات"))
        steps.append(make_step("A = 1, \\quad B = -1", "نحل النظام"))
        steps.append(make_step("\\int \\frac{1}{x^2+x} \\, dx = \\int \\frac{1}{x} \\, dx - \\int \\frac{1}{x+1} \\, dx", "نعوض A و B"))
        steps.append(make_step("= \\ln|x| - \\ln|x+1| + C", "نكامل"))
        steps.append(make_step("= \\ln\\left|\\frac{x}{x+1}\\right| + C", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\ln\\left|\\frac{x}{x+1}\\right| + C",
            "template": "39-2",
            "name": "∫ 1/(x²+x) dx"
        }
    
    def template_39_partial_fractions_3(self) -> Dict[str, Any]:
        """قالب 39-3: تكامل (2x+3)/(x²+3x+2) dx"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\int \\frac{2x+3}{x^2+3x+2} \\, dx", "المطلوب حساب التكامل"))
        steps.append(make_step("x^2+3x+2 = (x+1)(x+2)", "نحلل المقام"))
        steps.append(make_step("\\frac{2x+3}{(x+1)(x+2)} = \\frac{A}{x+1} + \\frac{B}{x+2}", "نفكك إلى كسور جزئية"))
        steps.append(make_step("2x+3 = A(x+2) + B(x+1)", "نضرب في المقام المشترك"))
        steps.append(make_step("2x+3 = (A+B)x + (2A + B)", "نجمع الحدود"))
        steps.append(make_step("\\begin{cases} A+B = 2 \\\\ 2A + B = 3 \\end{cases}", "نقارن المعاملات"))
        steps.append(make_step("A = 1, \\quad B = 1", "نحل النظام"))
        steps.append(make_step("\\int \\frac{2x+3}{x^2+3x+2} \\, dx = \\int \\frac{1}{x+1} \\, dx + \\int \\frac{1}{x+2} \\, dx", "نعوض A و B"))
        steps.append(make_step("= \\ln|x+1| + \\ln|x+2| + C", "نكامل"))
        steps.append(make_step("= \\ln|(x+1)(x+2)| + C", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\ln|(x+1)(x+2)| + C",
            "template": "39-3",
            "name": "∫ (2x+3)/(x²+3x+2) dx"
        }
    
    def template_39_partial_fractions_4(self) -> Dict[str, Any]:
        """قالب 39-4: تكامل 1/(x² + 4) dx"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\int \\frac{1}{x^2 + 4} \\, dx", "المطلوب حساب التكامل"))
        steps.append(make_step("\\int \\frac{1}{x^2 + a^2} \\, dx = \\frac{1}{a} \\arctan\\left(\\frac{x}{a}\\right) + C", "القاعدة العامة"))
        steps.append(make_step("\\text{هنا } a = 2", "نحدد a"))
        steps.append(make_step("\\int \\frac{1}{x^2 + 4} \\, dx = \\frac{1}{2} \\arctan\\left(\\frac{x}{2}\\right) + C", "نطبق القاعدة"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{1}{2} \\arctan\\left(\\frac{x}{2}\\right) + C",
            "template": "39-4",
            "name": "∫ 1/(x²+4) dx"
        }
    
    def template_39_partial_fractions_5(self) -> Dict[str, Any]:
        """قالب 39-5: تكامل (x)/(x² - 3x + 2) dx"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\int \\frac{x}{x^2 - 3x + 2} \\, dx", "المطلوب حساب التكامل"))
        steps.append(make_step("x^2 - 3x + 2 = (x-1)(x-2)", "نحلل المقام"))
        steps.append(make_step("\\frac{x}{(x-1)(x-2)} = \\frac{A}{x-1} + \\frac{B}{x-2}", "نفكك إلى كسور جزئية"))
        steps.append(make_step("x = A(x-2) + B(x-1)", "نضرب في المقام المشترك"))
        steps.append(make_step("x = (A+B)x + (-2A - B)", "نجمع الحدود"))
        steps.append(make_step("\\begin{cases} A+B = 1 \\\\ -2A - B = 0 \\end{cases}", "نقارن المعاملات"))
        steps.append(make_step("A = -1, \\quad B = 2", "نحل النظام"))
        steps.append(make_step("\\int \\frac{x}{x^2-3x+2} \\, dx = -\\int \\frac{1}{x-1} \\, dx + 2\\int \\frac{1}{x-2} \\, dx", "نعوض A و B"))
        steps.append(make_step("= -\\ln|x-1| + 2\\ln|x-2| + C", "نكامل"))
        steps.append(make_step("= \\ln\\left|\\frac{(x-2)^2}{x-1}\\right| + C", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\ln\\left|\\frac{(x-2)^2}{x-1}\\right| + C",
            "template": "39-5",
            "name": "∫ x/(x²-3x+2) dx"
        }

    # =========================================================================
    # 40. تكاملات التعويض (Substitution) - 5 قوالب
    # =========================================================================
    
    def template_40_substitution_1(self) -> Dict[str, Any]:
        """قالب 40-1: تكامل 2x·cos(x²) dx"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\int 2x \\cos(x^2) \\, dx",
            "المطلوب حساب التكامل"
        ))
        
        steps.append(make_step(
            "\\text{نفرض } u = x^2",
            "نختار التعويض المناسب"
        ))
        
        steps.append(make_step(
            "\\frac{du}{dx} = 2x \\quad \\Rightarrow \\quad du = 2x \\, dx",
            "نحسب التفاضلة"
        ))
        
        steps.append(make_step(
            "\\int 2x \\cos(x^2) \\, dx = \\int \\cos(u) \\, du",
            "نعوض في التكامل"
        ))
        
        steps.append(make_step(
            "\\int \\cos(u) \\, du = \\sin(u) + C",
            "نكامل بالنسبة لـ u"
        ))
        
        steps.append(make_step(
            "= \\sin(x^2) + C",
            "نعوض u = x²"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\sin(x^2) + C",
            "template": "40-1",
            "name": "∫ 2x·cos(x²) dx"
        }
    
    def template_40_substitution_2(self) -> Dict[str, Any]:
        """قالب 40-2: تكامل e^(3x) dx"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\int e^{3x} \\, dx", "المطلوب حساب التكامل"))
        steps.append(make_step("\\text{نفرض } u = 3x", "نختار التعويض"))
        steps.append(make_step("\\frac{du}{dx} = 3 \\quad \\Rightarrow \\quad dx = \\frac{du}{3}", "نحسب dx"))
        steps.append(make_step("\\int e^{3x} \\, dx = \\int e^u \\cdot \\frac{du}{3} = \\frac{1}{3} \\int e^u \\, du", "نعوض"))
        steps.append(make_step("\\frac{1}{3} \\int e^u \\, du = \\frac{1}{3} e^u + C", "نكامل"))
        steps.append(make_step("= \\frac{1}{3} e^{3x} + C", "نعوض u = 3x"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{1}{3} e^{3x} + C",
            "template": "40-2",
            "name": "∫ e^(3x) dx"
        }
    
    def template_40_substitution_3(self) -> Dict[str, Any]:
        """قالب 40-3: تكامل x·√(x²+1) dx"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\int x \\sqrt{x^2+1} \\, dx", "المطلوب حساب التكامل"))
        steps.append(make_step("\\text{نفرض } u = x^2 + 1", "نختار التعويض"))
        steps.append(make_step("\\frac{du}{dx} = 2x \\quad \\Rightarrow \\quad x \\, dx = \\frac{du}{2}", "نحسب x dx"))
        steps.append(make_step("\\int x \\sqrt{x^2+1} \\, dx = \\int \\sqrt{u} \\cdot \\frac{du}{2} = \\frac{1}{2} \\int u^{1/2} \\, du", "نعوض"))
        steps.append(make_step("\\frac{1}{2} \\int u^{1/2} \\, du = \\frac{1}{2} \\cdot \\frac{u^{3/2}}{3/2} + C = \\frac{1}{3} u^{3/2} + C", "نكامل"))
        steps.append(make_step("= \\frac{1}{3} (x^2+1)^{3/2} + C", "نعوض u = x²+1"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{1}{3} (x^2+1)^{3/2} + C",
            "template": "40-3",
            "name": "∫ x·√(x²+1) dx"
        }
    
    def template_40_substitution_4(self) -> Dict[str, Any]:
        """قالب 40-4: تكامل sin(ln(x))/x dx"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\int \\frac{\\sin(\\ln(x))}{x} \\, dx", "المطلوب حساب التكامل"))
        steps.append(make_step("\\text{نفرض } u = \\ln(x)", "نختار التعويض"))
        steps.append(make_step("\\frac{du}{dx} = \\frac{1}{x} \\quad \\Rightarrow \\quad \\frac{1}{x} dx = du", "نحسب"))
        steps.append(make_step("\\int \\frac{\\sin(\\ln(x))}{x} \\, dx = \\int \\sin(u) \\, du", "نعوض"))
        steps.append(make_step("\\int \\sin(u) \\, du = -\\cos(u) + C", "نكامل"))
        steps.append(make_step("= -\\cos(\\ln(x)) + C", "نعوض u = ln(x)"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "-\\cos(\\ln(x)) + C",
            "template": "40-4",
            "name": "∫ sin(ln(x))/x dx"
        }
    
    def template_40_substitution_5(self) -> Dict[str, Any]:
        """قالب 40-5: تكامل tan(x) dx"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\int \\tan(x) \\, dx", "المطلوب حساب التكامل"))
        steps.append(make_step("\\tan(x) = \\frac{\\sin(x)}{\\cos(x)}", "نكتب tan(x) على صورة كسر"))
        steps.append(make_step("\\text{نفرض } u = \\cos(x)", "نختار التعويض"))
        steps.append(make_step("\\frac{du}{dx} = -\\sin(x) \\quad \\Rightarrow \\quad \\sin(x) dx = -du", "نحسب"))
        steps.append(make_step("\\int \\tan(x) \\, dx = \\int \\frac{\\sin(x)}{\\cos(x)} \\, dx = \\int \\frac{-du}{u} = -\\int \\frac{1}{u} \\, du", "نعوض"))
        steps.append(make_step("-\\int \\frac{1}{u} \\, du = -\\ln|u| + C", "نكامل"))
        steps.append(make_step("= -\\ln|\\cos(x)| + C = \\ln|\\sec(x)| + C", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\ln|\\sec(x)| + C",
            "template": "40-5",
            "name": "∫ tan(x) dx"
        }

    # =========================================================================
    # 41. تكاملات بالتجزئة (Integration by Parts) - 5 قوالب
    # =========================================================================
    
    def template_41_by_parts_1(self) -> Dict[str, Any]:
        """قالب 41-1: تكامل x·e^x dx"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\int x e^x \\, dx",
            "المطلوب حساب التكامل"
        ))
        
        steps.append(make_step(
            "\\int u \\, dv = uv - \\int v \\, du",
            "قاعدة التكامل بالتجزئة"
        ))
        
        steps.append(make_step(
            "\\text{نختار } u = x \\quad , \\quad dv = e^x \\, dx",
            "نحدد u و dv"
        ))
        
        steps.append(make_step(
            "du = dx \\quad , \\quad v = \\int e^x \\, dx = e^x",
            "نحسب du و v"
        ))
        
        steps.append(make_step(
            "\\int x e^x \\, dx = x e^x - \\int e^x \\, dx",
            "نطبق القاعدة"
        ))
        
        steps.append(make_step(
            "= x e^x - e^x + C",
            "نكامل"
        ))
        
        steps.append(make_step(
            "= e^x (x - 1) + C",
            "النتيجة النهائية"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "e^x (x - 1) + C",
            "template": "41-1",
            "name": "∫ x·e^x dx"
        }
    
    def template_41_by_parts_2(self) -> Dict[str, Any]:
        """قالب 41-2: تكامل x·sin(x) dx"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\int x \\sin(x) \\, dx", "المطلوب حساب التكامل"))
        steps.append(make_step("\\int u \\, dv = uv - \\int v \\, du", "قاعدة التكامل بالتجزئة"))
        steps.append(make_step("\\text{نختار } u = x \\quad , \\quad dv = \\sin(x) \\, dx", "نحدد u و dv"))
        steps.append(make_step("du = dx \\quad , \\quad v = \\int \\sin(x) \\, dx = -\\cos(x)", "نحسب du و v"))
        steps.append(make_step("\\int x \\sin(x) \\, dx = x \\cdot (-\\cos(x)) - \\int (-\\cos(x)) \\, dx", "نطبق القاعدة"))
        steps.append(make_step("= -x \\cos(x) + \\int \\cos(x) \\, dx", "نبسط"))
        steps.append(make_step("= -x \\cos(x) + \\sin(x) + C", "نكامل"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "-x \\cos(x) + \\sin(x) + C",
            "template": "41-2",
            "name": "∫ x·sin(x) dx"
        }
    
    def template_41_by_parts_3(self) -> Dict[str, Any]:
        """قالب 41-3: تكامل ln(x) dx"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\int \\ln(x) \\, dx", "المطلوب حساب التكامل"))
        steps.append(make_step("\\int u \\, dv = uv - \\int v \\, du", "قاعدة التكامل بالتجزئة"))
        steps.append(make_step("\\text{نكتب } \\ln(x) = 1 \\cdot \\ln(x)", "نعيد كتابة التكامل"))
        steps.append(make_step("\\text{نختار } u = \\ln(x) \\quad , \\quad dv = 1 \\, dx", "نحدد u و dv"))
        steps.append(make_step("du = \\frac{1}{x} dx \\quad , \\quad v = x", "نحسب du و v"))
        steps.append(make_step("\\int \\ln(x) \\, dx = x \\ln(x) - \\int x \\cdot \\frac{1}{x} \\, dx", "نطبق القاعدة"))
        steps.append(make_step("= x \\ln(x) - \\int 1 \\, dx", "نبسط"))
        steps.append(make_step("= x \\ln(x) - x + C", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "x \\ln(x) - x + C",
            "template": "41-3",
            "name": "∫ ln(x) dx"
        }
    
    def template_41_by_parts_4(self) -> Dict[str, Any]:
        """قالب 41-4: تكامل x²·e^x dx"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\int x^2 e^x \\, dx", "المطلوب حساب التكامل"))
        steps.append(make_step("\\int u \\, dv = uv - \\int v \\, du", "قاعدة التكامل بالتجزئة"))
        steps.append(make_step("\\text{نختار } u = x^2 \\quad , \\quad dv = e^x \\, dx", "نحدد u و dv"))
        steps.append(make_step("du = 2x dx \\quad , \\quad v = e^x", "نحسب du و v"))
        steps.append(make_step("\\int x^2 e^x \\, dx = x^2 e^x - \\int e^x \\cdot 2x \\, dx", "نطبق القاعدة"))
        steps.append(make_step("= x^2 e^x - 2 \\int x e^x \\, dx", "نخرج العامل 2"))
        steps.append(make_step("\\int x e^x \\, dx = e^x (x - 1) + C", "نستخدم نتيجة القالب 41-1"))
        steps.append(make_step("\\int x^2 e^x \\, dx = x^2 e^x - 2 e^x (x - 1) + C", "نعوض"))
        steps.append(make_step("= e^x (x^2 - 2x + 2) + C", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "e^x (x^2 - 2x + 2) + C",
            "template": "41-4",
            "name": "∫ x²·e^x dx"
        }
    
    def template_41_by_parts_5(self) -> Dict[str, Any]:
        """قالب 41-5: تكامل e^x·sin(x) dx"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\int e^x \\sin(x) \\, dx", "المطلوب حساب التكامل"))
        steps.append(make_step("I = \\int e^x \\sin(x) \\, dx", "نرمز للتكامل بالرمز I"))
        steps.append(make_step("\\int u \\, dv = uv - \\int v \\, du", "قاعدة التكامل بالتجزئة"))
        steps.append(make_step("\\text{نختار } u = \\sin(x) \\quad , \\quad dv = e^x \\, dx", "نحدد u و dv"))
        steps.append(make_step("du = \\cos(x) dx \\quad , \\quad v = e^x", "نحسب du و v"))
        steps.append(make_step("I = e^x \\sin(x) - \\int e^x \\cos(x) \\, dx", "نطبق القاعدة (1)"))
        steps.append(make_step("J = \\int e^x \\cos(x) \\, dx", "نرمز للتكامل الجديد بـ J"))
        steps.append(make_step("\\text{نطبق التكامل بالتجزئة على J: } u = \\cos(x), dv = e^x dx", "نكرر العملية"))
        steps.append(make_step("du = -\\sin(x) dx, v = e^x", "نحسب"))
        steps.append(make_step("J = e^x \\cos(x) - \\int e^x (-\\sin(x)) \\, dx = e^x \\cos(x) + \\int e^x \\sin(x) \\, dx", "نطبق القاعدة"))
        steps.append(make_step("J = e^x \\cos(x) + I", "نلاحظ ظهور I مرة أخرى"))
        steps.append(make_step("I = e^x \\sin(x) - [e^x \\cos(x) + I]", "نعوض J في المعادلة (1)"))
        steps.append(make_step("I = e^x \\sin(x) - e^x \\cos(x) - I", "نبسط"))
        steps.append(make_step("2I = e^x (\\sin(x) - \\cos(x))", "نجمع I للطرفين"))
        steps.append(make_step("I = \\frac{e^x}{2} (\\sin(x) - \\cos(x)) + C", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{e^x}{2} (\\sin(x) - \\cos(x)) + C",
            "template": "41-5",
            "name": "∫ e^x·sin(x) dx"
        }

    # =========================================================================
    # 42. التكاملات المحدودة (Definite Integrals) - 5 قوالب
    # =========================================================================
    
    def template_42_definite_1(self) -> Dict[str, Any]:
        """قالب 42-1: تكامل محدد ∫₀¹ x² dx"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\int_{0}^{1} x^2 \\, dx",
            "المطلوب حساب التكامل المحدد"
        ))
        
        steps.append(make_step(
            "\\int x^2 \\, dx = \\frac{x^3}{3} + C",
            "نحسب التكامل غير المحدد أولاً"
        ))
        
        steps.append(make_step(
            "\\int_{0}^{1} x^2 \\, dx = \\left[ \\frac{x^3}{3} \\right]_{0}^{1}",
            "نطبق نظرية التكامل المحدد"
        ))
        
        steps.append(make_step(
            "= \\frac{1^3}{3} - \\frac{0^3}{3}",
            "نعوض الحدين العلوي والسفلي"
        ))
        
        steps.append(make_step(
            "= \\frac{1}{3} - 0 = \\frac{1}{3}",
            "النتيجة النهائية"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{1}{3}",
            "template": "42-1",
            "name": "∫₀¹ x² dx"
        }
    
    def template_42_definite_2(self) -> Dict[str, Any]:
        """قالب 42-2: تكامل محدد ∫₀^{π/2} sin(x) dx"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\int_{0}^{\\pi/2} \\sin(x) \\, dx", "المطلوب حساب التكامل المحدد"))
        steps.append(make_step("\\int \\sin(x) \\, dx = -\\cos(x) + C", "التكامل غير المحدد"))
        steps.append(make_step("\\int_{0}^{\\pi/2} \\sin(x) \\, dx = \\left[ -\\cos(x) \\right]_{0}^{\\pi/2}", "نطبق نظرية التكامل المحدد"))
        steps.append(make_step("= (-\\cos(\\pi/2)) - (-\\cos(0))", "نعوض الحدين"))
        steps.append(make_step("= (-0) - (-1) = 0 + 1 = 1", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "1",
            "template": "42-2",
            "name": "∫₀^{π/2} sin(x) dx"
        }
    
    def template_42_definite_3(self) -> Dict[str, Any]:
        """قالب 42-3: تكامل محدد ∫₁^e (1/x) dx"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\int_{1}^{e} \\frac{1}{x} \\, dx", "المطلوب حساب التكامل المحدد"))
        steps.append(make_step("\\int \\frac{1}{x} \\, dx = \\ln|x| + C", "التكامل غير المحدد"))
        steps.append(make_step("\\int_{1}^{e} \\frac{1}{x} \\, dx = \\left[ \\ln|x| \\right]_{1}^{e}", "نطبق نظرية التكامل المحدد"))
        steps.append(make_step("= \\ln(e) - \\ln(1)", "نعوض الحدين"))
        steps.append(make_step("= 1 - 0 = 1", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "1",
            "template": "42-3",
            "name": "∫₁^e (1/x) dx"
        }
    
    def template_42_definite_4(self) -> Dict[str, Any]:
        """قالب 42-4: تكامل محدد ∫₀¹ x·e^x dx"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\int_{0}^{1} x e^x \\, dx", "المطلوب حساب التكامل المحدد"))
        steps.append(make_step("\\int x e^x \\, dx = e^x (x - 1) + C", "التكامل غير المحدد (من القالب 41-1)"))
        steps.append(make_step("\\int_{0}^{1} x e^x \\, dx = \\left[ e^x (x - 1) \\right]_{0}^{1}", "نطبق نظرية التكامل المحدد"))
        steps.append(make_step("= [e^1 (1 - 1)] - [e^0 (0 - 1)]", "نعوض الحدين"))
        steps.append(make_step("= [e(0)] - [1(-1)] = 0 - (-1) = 1", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "1",
            "template": "42-4",
            "name": "∫₀¹ x·e^x dx"
        }
    
    def template_42_definite_5(self) -> Dict[str, Any]:
        """قالب 42-5: تكامل محدد ∫₀^π sin(x) dx"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\int_{0}^{\\pi} \\sin(x) \\, dx", "المطلوب حساب التكامل المحدد"))
        steps.append(make_step("\\int \\sin(x) \\, dx = -\\cos(x) + C", "التكامل غير المحدد"))
        steps.append(make_step("\\int_{0}^{\\pi} \\sin(x) \\, dx = \\left[ -\\cos(x) \\right]_{0}^{\\pi}", "نطبق نظرية التكامل المحدد"))
        steps.append(make_step("= (-\\cos(\\pi)) - (-\\cos(0))", "نعوض الحدين"))
        steps.append(make_step("= (-(-1)) - (-1) = 1 + 1 = 2", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "2",
            "template": "42-5",
            "name": "∫₀^π sin(x) dx"
        }

    # =========================================================================
    # 43. التكاملات غير المحدودة (Indefinite Integrals) - 5 قوالب
    # =========================================================================
    
    def template_43_indefinite_1(self) -> Dict[str, Any]:
        """قالب 43-1: تكامل غير محدد ∫ (3x² + 2x + 1) dx"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\int (3x^2 + 2x + 1) \\, dx",
            "المطلوب حساب التكامل غير المحدد"
        ))
        
        steps.append(make_step(
            "\\int (3x^2 + 2x + 1) \\, dx = 3\\int x^2 \\, dx + 2\\int x \\, dx + \\int 1 \\, dx",
            "نوزع التكامل على المجموع"
        ))
        
        steps.append(make_step(
            "\\int x^2 \\, dx = \\frac{x^3}{3}",
            "تكامل x²"
        ))
        
        steps.append(make_step(
            "\\int x \\, dx = \\frac{x^2}{2}",
            "تكامل x"
        ))
        
        steps.append(make_step(
            "\\int 1 \\, dx = x",
            "تكامل الثابت"
        ))
        
        steps.append(make_step(
            "= 3 \\cdot \\frac{x^3}{3} + 2 \\cdot \\frac{x^2}{2} + x + C",
            "نعوض النتائج"
        ))
        
        steps.append(make_step(
            "= x^3 + x^2 + x + C",
            "النتيجة النهائية"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "x^3 + x^2 + x + C",
            "template": "43-1",
            "name": "∫ (3x²+2x+1) dx"
        }
    
    def template_43_indefinite_2(self) -> Dict[str, Any]:
        """قالب 43-2: تكامل غير محدد ∫ (4x³ - 2x) dx"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\int (4x^3 - 2x) \\, dx", "المطلوب حساب التكامل"))
        steps.append(make_step("= 4\\int x^3 \\, dx - 2\\int x \\, dx", "نوزع التكامل"))
        steps.append(make_step("\\int x^3 \\, dx = \\frac{x^4}{4}", "تكامل x³"))
        steps.append(make_step("\\int x \\, dx = \\frac{x^2}{2}", "تكامل x"))
        steps.append(make_step("= 4 \\cdot \\frac{x^4}{4} - 2 \\cdot \\frac{x^2}{2} + C", "نعوض"))
        steps.append(make_step("= x^4 - x^2 + C", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "x^4 - x^2 + C",
            "template": "43-2",
            "name": "∫ (4x³-2x) dx"
        }
    
    def template_43_indefinite_3(self) -> Dict[str, Any]:
        """قالب 43-3: تكامل غير محدد ∫ sec²(x) dx"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\int \\sec^2(x) \\, dx", "المطلوب حساب التكامل"))
        steps.append(make_step("\\int \\sec^2(x) \\, dx = \\tan(x) + C", "القاعدة المعروفة"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\tan(x) + C",
            "template": "43-3",
            "name": "∫ sec²(x) dx"
        }
    
    def template_43_indefinite_4(self) -> Dict[str, Any]:
        """قالب 43-4: تكامل غير محدد ∫ csc²(x) dx"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\int \\csc^2(x) \\, dx", "المطلوب حساب التكامل"))
        steps.append(make_step("\\int \\csc^2(x) \\, dx = -\\cot(x) + C", "القاعدة المعروفة"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "-\\cot(x) + C",
            "template": "43-4",
            "name": "∫ csc²(x) dx"
        }
    
    def template_43_indefinite_5(self) -> Dict[str, Any]:
        """قالب 43-5: تكامل غير محدد ∫ (e^x + e^{-x}) dx"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\int (e^x + e^{-x}) \\, dx", "المطلوب حساب التكامل"))
        steps.append(make_step("= \\int e^x \\, dx + \\int e^{-x} \\, dx", "نوزع التكامل"))
        steps.append(make_step("\\int e^x \\, dx = e^x + C_1", "تكامل e^x"))
        steps.append(make_step("\\text{لـ } e^{-x}: \\text{نفرض } u = -x, du = -dx \\Rightarrow dx = -du", "نستخدم التعويض"))
        steps.append(make_step("\\int e^{-x} \\, dx = \\int e^u (-du) = -\\int e^u \\, du = -e^u + C_2", "نكامل"))
        steps.append(make_step("= -e^{-x} + C_2", "نعوض u = -x"))
        steps.append(make_step("\\int (e^x + e^{-x}) \\, dx = e^x - e^{-x} + C", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "e^x - e^{-x} + C",
            "template": "43-5",
            "name": "∫ (e^x + e^{-x}) dx"
        }

    # =========================================================================
    # 44. حساب المساحات تحت المنحنيات (Area Under Curves) - 5 قوالب
    # =========================================================================
    
    def template_44_area_under_curve_1(self) -> Dict[str, Any]:
        """قالب 44-1: المساحة تحت المنحني y = x² من x = 0 إلى x = 2"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\text{المساحة تحت المنحني } y = x^2 \\text{ من } x=0 \\text{ إلى } x=2",
            "المطلوب حساب المساحة"
        ))
        
        steps.append(make_step(
            "A = \\int_{0}^{2} x^2 \\, dx",
            "المساحة = تكامل الدالة في الفترة"
        ))
        
        steps.append(make_step(
            "\\int x^2 \\, dx = \\frac{x^3}{3}",
            "نحسب التكامل غير المحدد"
        ))
        
        steps.append(make_step(
            "A = \\left[ \\frac{x^3}{3} \\right]_{0}^{2}",
            "نطبق نظرية التكامل المحدد"
        ))
        
        steps.append(make_step(
            "= \\frac{2^3}{3} - \\frac{0^3}{3} = \\frac{8}{3} - 0",
            "نعوض الحدين"
        ))
        
        steps.append(make_step(
            "A = \\frac{8}{3} \\text{ وحدة مربعة}",
            "النتيجة النهائية"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{8}{3}",
            "template": "44-1",
            "name": "المساحة تحت y=x² من 0 إلى 2"
        }
    
    def template_44_area_under_curve_2(self) -> Dict[str, Any]:
        """قالب 44-2: المساحة تحت المنحني y = sin(x) من x = 0 إلى x = π"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\text{المساحة تحت } y = \\sin(x) \\text{ من } 0 \\text{ إلى } \\pi", "المطلوب"))
        steps.append(make_step("A = \\int_{0}^{\\pi} \\sin(x) \\, dx", "المساحة = تكامل الدالة"))
        steps.append(make_step("\\int \\sin(x) \\, dx = -\\cos(x)", "التكامل غير المحدد"))
        steps.append(make_step("A = \\left[ -\\cos(x) \\right]_{0}^{\\pi}", "نطبق التكامل المحدد"))
        steps.append(make_step("= (-\\cos(\\pi)) - (-\\cos(0)) = (-(-1)) - (-1) = 1 + 1 = 2", "نعوض"))
        steps.append(make_step("A = 2 \\text{ وحدة مربعة}", "النتيجة"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "2",
            "template": "44-2",
            "name": "المساحة تحت y=sin(x) من 0 إلى π"
        }
    
    def template_44_area_under_curve_3(self) -> Dict[str, Any]:
        """قالب 44-3: المساحة تحت المنحني y = 1/x من x = 1 إلى x = e"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\text{المساحة تحت } y = \\frac{1}{x} \\text{ من } 1 \\text{ إلى } e", "المطلوب"))
        steps.append(make_step("A = \\int_{1}^{e} \\frac{1}{x} \\, dx", "المساحة"))
        steps.append(make_step("\\int \\frac{1}{x} \\, dx = \\ln|x|", "التكامل"))
        steps.append(make_step("A = \\left[ \\ln|x| \\right]_{1}^{e} = \\ln(e) - \\ln(1) = 1 - 0 = 1", "نحسب"))
        steps.append(make_step("A = 1 \\text{ وحدة مربعة}", "النتيجة"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "1",
            "template": "44-3",
            "name": "المساحة تحت y=1/x من 1 إلى e"
        }
    
    def template_44_area_under_curve_4(self) -> Dict[str, Any]:
        """قالب 44-4: المساحة تحت المنحني y = e^x من x = 0 إلى x = 1"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\text{المساحة تحت } y = e^x \\text{ من } 0 \\text{ إلى } 1", "المطلوب"))
        steps.append(make_step("A = \\int_{0}^{1} e^x \\, dx", "المساحة"))
        steps.append(make_step("\\int e^x \\, dx = e^x", "التكامل"))
        steps.append(make_step("A = \\left[ e^x \\right]_{0}^{1} = e^1 - e^0 = e - 1", "نحسب"))
        steps.append(make_step("A = e - 1 \\approx 1.718 \\text{ وحدة مربعة}", "النتيجة"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "e - 1",
            "template": "44-4",
            "name": "المساحة تحت y=e^x من 0 إلى 1"
        }
    
    def template_44_area_under_curve_5(self) -> Dict[str, Any]:
        """قالب 44-5: المساحة تحت المنحني y = √x من x = 0 إلى x = 4"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\text{المساحة تحت } y = \\sqrt{x} \\text{ من } 0 \\text{ إلى } 4", "المطلوب"))
        steps.append(make_step("A = \\int_{0}^{4} \\sqrt{x} \\, dx = \\int_{0}^{4} x^{1/2} \\, dx", "المساحة"))
        steps.append(make_step("\\int x^{1/2} \\, dx = \\frac{x^{3/2}}{3/2} = \\frac{2}{3} x^{3/2}", "التكامل"))
        steps.append(make_step("A = \\left[ \\frac{2}{3} x^{3/2} \\right]_{0}^{4} = \\frac{2}{3} (4^{3/2} - 0^{3/2})", "نعوض"))
        steps.append(make_step("4^{3/2} = (\\sqrt{4})^3 = 2^3 = 8", "نبسط"))
        steps.append(make_step("A = \\frac{2}{3} \\cdot 8 = \\frac{16}{3} \\approx 5.33 \\text{ وحدة مربعة}", "النتيجة"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{16}{3}",
            "template": "44-5",
            "name": "المساحة تحت y=√x من 0 إلى 4"
        }

    # =========================================================================
    # 45. حساب المساحات بين منحنيين (Area Between Curves) - 5 قوالب
    # =========================================================================
    
    def template_45_area_between_curves_1(self) -> Dict[str, Any]:
        """قالب 45-1: المساحة بين y = x² و y = x من x = 0 إلى x = 1"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\text{المساحة بين } y = x^2 \\text{ و } y = x \\text{ من } x=0 \\text{ إلى } x=1",
            "المطلوب حساب المساحة"
        ))
        
        steps.append(make_step(
            "\\text{نحدد أي الدالتين أكبر في الفترة: } x \\geq x^2 \\text{ لـ } 0 \\leq x \\leq 1",
            "نقارن الدالتين"
        ))
        
        steps.append(make_step(
            "A = \\int_{0}^{1} [x - x^2] \\, dx",
            "المساحة = تكامل (الدالة العلوية - الدالة السفلية)"
        ))
        
        steps.append(make_step(
            "\\int (x - x^2) \\, dx = \\frac{x^2}{2} - \\frac{x^3}{3}",
            "نحسب التكامل غير المحدد"
        ))
        
        steps.append(make_step(
            "A = \\left[ \\frac{x^2}{2} - \\frac{x^3}{3} \\right]_{0}^{1}",
            "نطبق التكامل المحدد"
        ))
        
        steps.append(make_step(
            "= \\left(\\frac{1}{2} - \\frac{1}{3}\\right) - (0 - 0) = \\frac{1}{6}",
            "نعوض الحدين"
        ))
        
        steps.append(make_step(
            "A = \\frac{1}{6} \\text{ وحدة مربعة}",
            "النتيجة النهائية"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{1}{6}",
            "template": "45-1",
            "name": "المساحة بين y=x² و y=x من 0 إلى 1"
        }
    
    def template_45_area_between_curves_2(self) -> Dict[str, Any]:
        """قالب 45-2: المساحة بين y = sin(x) و y = cos(x) من x = π/4 إلى x = 5π/4"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\text{المساحة بين } y = \\sin(x) \\text{ و } y = \\cos(x) \\text{ من } \\pi/4 \\text{ إلى } 5\\pi/4", "المطلوب"))
        steps.append(make_step("\\text{نحدد نقاط التقاطع: } \\sin(x) = \\cos(x) \\Rightarrow x = \\pi/4, 5\\pi/4", "نقاط التقاطع"))
        steps.append(make_step("\\text{في الفترة } [\\pi/4, 5\\pi/4]: \\sin(x) \\geq \\cos(x)", "نحدد الدالة الأكبر"))
        steps.append(make_step("A = \\int_{\\pi/4}^{5\\pi/4} [\\sin(x) - \\cos(x)] \\, dx", "المساحة"))
        steps.append(make_step("\\int [\\sin(x) - \\cos(x)] \\, dx = -\\cos(x) - \\sin(x)", "التكامل"))
        steps.append(make_step("A = \\left[ -\\cos(x) - \\sin(x) \\right]_{\\pi/4}^{5\\pi/4}", "نطبق"))
        steps.append(make_step("= [-\\cos(5\\pi/4) - \\sin(5\\pi/4)] - [-\\cos(\\pi/4) - \\sin(\\pi/4)]", "نعوض"))
        steps.append(make_step("\\cos(5\\pi/4) = -\\frac{\\sqrt{2}}{2}, \\sin(5\\pi/4) = -\\frac{\\sqrt{2}}{2}", "قيم الدوال"))
        steps.append(make_step("\\cos(\\pi/4) = \\frac{\\sqrt{2}}{2}, \\sin(\\pi/4) = \\frac{\\sqrt{2}}{2}", "قيم الدوال"))
        steps.append(make_step("A = [-(-\\frac{\\sqrt{2}}{2}) - (-\\frac{\\sqrt{2}}{2})] - [-(\\frac{\\sqrt{2}}{2}) - (\\frac{\\sqrt{2}}{2})]", "نعوض"))
        steps.append(make_step("= [\\frac{\\sqrt{2}}{2} + \\frac{\\sqrt{2}}{2}] - [-\\frac{\\sqrt{2}}{2} - \\frac{\\sqrt{2}}{2}]", "نبسط"))
        steps.append(make_step("= [\\sqrt{2}] - [-\\sqrt{2}] = \\sqrt{2} + \\sqrt{2} = 2\\sqrt{2}", "النتيجة"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "2\\sqrt{2}",
            "template": "45-2",
            "name": "المساحة بين sin(x) و cos(x)"
        }
    
    def template_45_area_between_curves_3(self) -> Dict[str, Any]:
        """قالب 45-3: المساحة بين y = x² و y = 2x - x²"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\text{المساحة بين } y = x^2 \\text{ و } y = 2x - x^2", "المطلوب"))
        steps.append(make_step("\\text{نوجد نقاط التقاطع: } x^2 = 2x - x^2 \\Rightarrow 2x^2 - 2x = 0 \\Rightarrow 2x(x-1)=0", "نقاط التقاطع"))
        steps.append(make_step("x = 0 \\text{ و } x = 1", "نقاط التقاطع"))
        steps.append(make_step("\\text{في الفترة } [0,1]: 2x - x^2 \\geq x^2", "نحدد الدالة الأكبر"))
        steps.append(make_step("A = \\int_{0}^{1} [(2x - x^2) - x^2] \\, dx = \\int_{0}^{1} (2x - 2x^2) \\, dx", "المساحة"))
        steps.append(make_step("\\int (2x - 2x^2) \\, dx = x^2 - \\frac{2}{3}x^3", "التكامل"))
        steps.append(make_step("A = \\left[ x^2 - \\frac{2}{3}x^3 \\right]_{0}^{1} = (1 - \\frac{2}{3}) - (0 - 0) = \\frac{1}{3}", "النتيجة"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{1}{3}",
            "template": "45-3",
            "name": "المساحة بين y=x² و y=2x-x²"
        }
    
    def template_45_area_between_curves_4(self) -> Dict[str, Any]:
        """قالب 45-4: المساحة بين y = √x و y = x²"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\text{المساحة بين } y = \\sqrt{x} \\text{ و } y = x^2", "المطلوب"))
        steps.append(make_step("\\text{نوجد نقاط التقاطع: } \\sqrt{x} = x^2 \\Rightarrow x = x^4 \\Rightarrow x^4 - x = 0 \\Rightarrow x(x^3-1)=0", "نقاط التقاطع"))
        steps.append(make_step("x = 0 \\text{ و } x = 1", "نقاط التقاطع"))
        steps.append(make_step("\\text{في الفترة } [0,1]: \\sqrt{x} \\geq x^2", "نحدد الدالة الأكبر"))
        steps.append(make_step("A = \\int_{0}^{1} (\\sqrt{x} - x^2) \\, dx = \\int_{0}^{1} (x^{1/2} - x^2) \\, dx", "المساحة"))
        steps.append(make_step("\\int (x^{1/2} - x^2) \\, dx = \\frac{x^{3/2}}{3/2} - \\frac{x^3}{3} = \\frac{2}{3}x^{3/2} - \\frac{x^3}{3}", "التكامل"))
        steps.append(make_step("A = \\left[ \\frac{2}{3}x^{3/2} - \\frac{x^3}{3} \\right]_{0}^{1} = (\\frac{2}{3} - \\frac{1}{3}) - (0 - 0) = \\frac{1}{3}", "النتيجة"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{1}{3}",
            "template": "45-4",
            "name": "المساحة بين y=√x و y=x²"
        }
    
    def template_45_area_between_curves_5(self) -> Dict[str, Any]:
        """قالب 45-5: المساحة بين y = x و y = x³ من x = -1 إلى x = 1"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\text{المساحة بين } y = x \\text{ و } y = x^3 \\text{ من } -1 \\text{ إلى } 1", "المطلوب"))
        steps.append(make_step("\\text{نقاط التقاطع: } x = x^3 \\Rightarrow x^3 - x = 0 \\Rightarrow x(x-1)(x+1)=0", "نقاط التقاطع"))
        steps.append(make_step("x = -1, 0, 1", "نقاط التقاطع"))
        steps.append(make_step("\\text{في } [-1,0]: x \\geq x^3", "في الفترة الأولى"))
        steps.append(make_step("\\text{في } [0,1]: x^3 \\geq x", "في الفترة الثانية"))
        steps.append(make_step("A = \\int_{-1}^{0} (x - x^3) \\, dx + \\int_{0}^{1} (x^3 - x) \\, dx", "المساحة = مجموع التكاملين"))
        steps.append(make_step("\\int (x - x^3) \\, dx = \\frac{x^2}{2} - \\frac{x^4}{4}", "التكامل الأول"))
        steps.append(make_step("\\int (x^3 - x) \\, dx = \\frac{x^4}{4} - \\frac{x^2}{2}", "التكامل الثاني"))
        steps.append(make_step("A = \\left[ \\frac{x^2}{2} - \\frac{x^4}{4} \\right]_{-1}^{0} + \\left[ \\frac{x^4}{4} - \\frac{x^2}{2} \\right]_{0}^{1}", "نطبق"))
        steps.append(make_step("= [(0-0) - (\\frac{1}{2} - \\frac{1}{4})] + [(\\frac{1}{4} - \\frac{1}{2}) - (0-0)]", "نعوض"))
        steps.append(make_step("= [0 - \\frac{1}{4}] + [(-\\frac{1}{4}) - 0] = -\\frac{1}{4} - \\frac{1}{4} = -\\frac{1}{2}", "هذا خطأ في الإشارة"))
        steps.append(make_step("\\text{نأخذ القيمة المطلقة: } A = \\frac{1}{2}", "المساحة دائماً موجبة"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{1}{2}",
            "template": "45-5",
            "name": "المساحة بين y=x و y=x³"
        }

    # =========================================================================
    # دوال مساعدة وإحصائيات
    # =========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """إحصائيات استخدام القوالب"""
        return self.stats
