"""
================================================================================
الملف 3/3: التفاضل والتكامل - الحدود والمعادلات التفاضلية
File 3/3: Calculus - Limits and Differential Equations (50 Templates)

القوالب:
46. حدود أساسية (5 قوالب)
47. حدود متقدمة (L'Hôpital) (5 قوالب)
48. التفاضل الجزئي (5 قوالب)
49. التفاضل الكلي (5 قوالب)
50. معادلات تفاضلية بسيطة (dy/dx) (5 قوالب)
51. معادلات تفاضلية خطية من الرتبة الأولى (5 قوالب)
52. معادلات تفاضلية قابلة للفصل (5 قوالب)
53. معادلات تفاضلية باستخدام التكامل (5 قوالب)
54. مشتقات التكاملات (نظرية الأساس) (5 قوالب)
55. اشتقاقات الدوال متعددة المتغيرات (5 قوالب)
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

class CalculusSolverPart3:
    """حلال الحدود والمعادلات التفاضلية - يغطي القوالب 46-55"""
    
    def __init__(self):
        self.x = sp.Symbol('x', real=True)
        self.y = sp.Symbol('y', real=True)
        self.t = sp.Symbol('t', real=True)
        self.C = sp.Symbol('C')  # ثابت التكامل
        self.stats = {'total_calls': 0, 'successful': 0, 'failed': 0}
        logger.info("✅ تم تهيئة CalculusSolverPart3 - الحدود والمعادلات التفاضلية (50 قالب)")

    # =========================================================================
    # 46. حدود أساسية (Basic Limits) - 5 قوالب
    # =========================================================================
    
    def template_46_basic_limit_1(self) -> Dict[str, Any]:
        """قالب 46-1: نهاية x² عندما x → 2"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\lim_{x \\to 2} x^2",
            "المطلوب حساب النهاية"
        ))
        
        steps.append(make_step(
            "\\text{الدالة متصلة، نعوض } x = 2",
            "نطبق خاصية التعويض المباشر"
        ))
        
        steps.append(make_step(
            "\\lim_{x \\to 2} x^2 = 2^2 = 4",
            "النتيجة"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "4",
            "template": "46-1",
            "name": "lim x² when x→2"
        }
    
    def template_46_basic_limit_2(self) -> Dict[str, Any]:
        """قالب 46-2: نهاية (x²-4)/(x-2) عندما x → 2"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\lim_{x \\to 2} \\frac{x^2 - 4}{x - 2}",
            "المطلوب حساب النهاية"
        ))
        
        steps.append(make_step(
            "\\text{بالتعويض المباشر: } \\frac{4-4}{2-2} = \\frac{0}{0}",
            "نحصل على كمية غير معينة"
        ))
        
        steps.append(make_step(
            "x^2 - 4 = (x-2)(x+2)",
            "نحلل البسط"
        ))
        
        steps.append(make_step(
            "\\lim_{x \\to 2} \\frac{(x-2)(x+2)}{x-2} = \\lim_{x \\to 2} (x+2)",
            "نختصر (x-2)"
        ))
        
        steps.append(make_step(
            "= 2 + 2 = 4",
            "نعوض x = 2"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "4",
            "template": "46-2",
            "name": "lim (x²-4)/(x-2) when x→2"
        }
    
    def template_46_basic_limit_3(self) -> Dict[str, Any]:
        """قالب 46-3: نهاية sin(x)/x عندما x → 0"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\lim_{x \\to 0} \\frac{\\sin(x)}{x}",
            "المطلوب حساب النهاية"
        ))
        
        steps.append(make_step(
            "\\text{هذه نهاية أساسية معروفة}",
            "نهاية مشهورة"
        ))
        
        steps.append(make_step(
            "\\lim_{x \\to 0} \\frac{\\sin(x)}{x} = 1",
            "النتيجة"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "1",
            "template": "46-3",
            "name": "lim sin(x)/x when x→0"
        }
    
    def template_46_basic_limit_4(self) -> Dict[str, Any]:
        """قالب 46-4: نهاية (1 - cos(x))/x² عندما x → 0"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\lim_{x \\to 0} \\frac{1 - \\cos(x)}{x^2}",
            "المطلوب حساب النهاية"
        ))
        
        steps.append(make_step(
            "\\text{نستخدم المتطابقة: } 1 - \\cos(x) = 2\\sin^2\\left(\\frac{x}{2}\\right)",
            "نحول البسط"
        ))
        
        steps.append(make_step(
            "\\lim_{x \\to 0} \\frac{2\\sin^2(x/2)}{x^2} = 2 \\lim_{x \\to 0} \\frac{\\sin^2(x/2)}{x^2}",
            "نخرج العامل 2"
        ))
        
        steps.append(make_step(
            "= 2 \\lim_{x \\to 0} \\left( \\frac{\\sin(x/2)}{x/2} \\right)^2 \\cdot \\frac{1}{4}",
            "نضرب ونقسم على (1/2)²"
        ))
        
        steps.append(make_step(
            "= 2 \\cdot \\frac{1}{4} \\cdot \\left( \\lim_{x \\to 0} \\frac{\\sin(x/2)}{x/2} \\right)^2",
            "نبسط"
        ))
        
        steps.append(make_step(
            "= \\frac{1}{2} \\cdot 1^2 = \\frac{1}{2}",
            "نهاية sin(u)/u = 1"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{1}{2}",
            "template": "46-4",
            "name": "lim (1-cos(x))/x² when x→0"
        }
    
    def template_46_basic_limit_5(self) -> Dict[str, Any]:
        """قالب 46-5: نهاية (1 + 1/x)^x عندما x → ∞"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\lim_{x \\to \\infty} \\left(1 + \\frac{1}{x}\\right)^x",
            "المطلوب حساب النهاية"
        ))
        
        steps.append(make_step(
            "\\text{هذه نهاية أساسية تعطي العدد e}",
            "نهاية مشهورة"
        ))
        
        steps.append(make_step(
            "\\lim_{x \\to \\infty} \\left(1 + \\frac{1}{x}\\right)^x = e",
            "النتيجة"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "e",
            "template": "46-5",
            "name": "lim (1+1/x)^x when x→∞"
        }

    # =========================================================================
    # 47. حدود متقدمة (L'Hôpital's Rule) - 5 قوالب
    # =========================================================================
    
    def template_47_lhopital_1(self) -> Dict[str, Any]:
        """قالب 47-1: نهاية (e^x - 1)/x عندما x → 0 باستخدام لوبيتال"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\lim_{x \\to 0} \\frac{e^x - 1}{x}",
            "المطلوب حساب النهاية"
        ))
        
        steps.append(make_step(
            "\\text{بالتعويض: } \\frac{e^0 - 1}{0} = \\frac{0}{0}",
            "نحصل على كمية غير معينة"
        ))
        
        steps.append(make_step(
            "\\text{نطبق قاعدة لوبيتال: } \\lim \\frac{f(x)}{g(x)} = \\lim \\frac{f'(x)}{g'(x)}",
            "قاعدة لوبيتال"
        ))
        
        steps.append(make_step(
            "f'(x) = \\frac{d}{dx}(e^x - 1) = e^x",
            "مشتقة البسط"
        ))
        
        steps.append(make_step(
            "g'(x) = \\frac{d}{dx}(x) = 1",
            "مشتقة المقام"
        ))
        
        steps.append(make_step(
            "\\lim_{x \\to 0} \\frac{e^x}{1} = e^0 = 1",
            "النتيجة"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "1",
            "template": "47-1",
            "name": "lim (e^x-1)/x using L'Hôpital"
        }
    
    def template_47_lhopital_2(self) -> Dict[str, Any]:
        """قالب 47-2: نهاية (ln(x))/(x-1) عندما x → 1"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\lim_{x \\to 1} \\frac{\\ln(x)}{x-1}",
            "المطلوب حساب النهاية"
        ))
        
        steps.append(make_step(
            "\\text{بالتعويض: } \\frac{\\ln(1)}{0} = \\frac{0}{0}",
            "نحصل على كمية غير معينة"
        ))
        
        steps.append(make_step(
            "\\text{نطبق قاعدة لوبيتال}",
            "نستخدم القاعدة"
        ))
        
        steps.append(make_step(
            "f'(x) = \\frac{d}{dx}\\ln(x) = \\frac{1}{x}",
            "مشتقة البسط"
        ))
        
        steps.append(make_step(
            "g'(x) = \\frac{d}{dx}(x-1) = 1",
            "مشتقة المقام"
        ))
        
        steps.append(make_step(
            "\\lim_{x \\to 1} \\frac{1/x}{1} = 1",
            "النتيجة"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "1",
            "template": "47-2",
            "name": "lim ln(x)/(x-1) when x→1"
        }
    
    def template_47_lhopital_3(self) -> Dict[str, Any]:
        """قالب 47-3: نهاية (sin(x) - x)/x³ عندما x → 0"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\lim_{x \\to 0} \\frac{\\sin(x) - x}{x^3}",
            "المطلوب حساب النهاية"
        ))
        
        steps.append(make_step(
            "\\text{بالتعويض: } \\frac{0 - 0}{0} = \\frac{0}{0}",
            "كمية غير معينة"
        ))
        
        steps.append(make_step(
            "\\text{نطبق قاعدة لوبيتال (مرة أولى)}",
            "الخطوة الأولى"
        ))
        
        steps.append(make_step(
            "f'(x) = \\cos(x) - 1, \\quad g'(x) = 3x^2",
            "مشتقات المرة الأولى"
        ))
        
        steps.append(make_step(
            "\\lim_{x \\to 0} \\frac{\\cos(x) - 1}{3x^2} \\Rightarrow \\frac{0}{0}",
            "لا زالت غير معينة"
        ))
        
        steps.append(make_step(
            "\\text{نطبق لوبيتال مرة ثانية}",
            "الخطوة الثانية"
        ))
        
        steps.append(make_step(
            "f''(x) = -\\sin(x), \\quad g''(x) = 6x",
            "مشتقات المرة الثانية"
        ))
        
        steps.append(make_step(
            "\\lim_{x \\to 0} \\frac{-\\sin(x)}{6x} \\Rightarrow \\frac{0}{0}",
            "لا زالت غير معينة"
        ))
        
        steps.append(make_step(
            "\\text{نطبق لوبيتال مرة ثالثة}",
            "الخطوة الثالثة"
        ))
        
        steps.append(make_step(
            "f'''(x) = -\\cos(x), \\quad g'''(x) = 6",
            "مشتقات المرة الثالثة"
        ))
        
        steps.append(make_step(
            "\\lim_{x \\to 0} \\frac{-\\cos(x)}{6} = -\\frac{1}{6}",
            "النتيجة النهائية"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "-\\frac{1}{6}",
            "template": "47-3",
            "name": "lim (sin(x)-x)/x³ using L'Hôpital"
        }
    
    def template_47_lhopital_4(self) -> Dict[str, Any]:
        """قالب 47-4: نهاية x ln(x) عندما x → 0⁺"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\lim_{x \\to 0^+} x \\ln(x)",
            "المطلوب حساب النهاية"
        ))
        
        steps.append(make_step(
            "\\text{هذه نهاية على صورة } 0 \\cdot (-\\infty)",
            "كمية غير معينة"
        ))
        
        steps.append(make_step(
            "\\text{نعيد كتابتها: } x \\ln(x) = \\frac{\\ln(x)}{1/x}",
            "نحول إلى صورة كسر"
        ))
        
        steps.append(make_step(
            "\\lim_{x \\to 0^+} \\frac{\\ln(x)}{1/x} \\Rightarrow \\frac{-\\infty}{\\infty}",
            "صورة غير معينة"
        ))
        
        steps.append(make_step(
            "\\text{نطبق قاعدة لوبيتال}",
            "نستخدم القاعدة"
        ))
        
        steps.append(make_step(
            "f'(x) = \\frac{d}{dx}\\ln(x) = \\frac{1}{x}",
            "مشتقة البسط"
        ))
        
        steps.append(make_step(
            "g'(x) = \\frac{d}{dx}(1/x) = -\\frac{1}{x^2}",
            "مشتقة المقام"
        ))
        
        steps.append(make_step(
            "\\lim_{x \\to 0^+} \\frac{1/x}{-1/x^2} = \\lim_{x \\to 0^+} (-x) = 0",
            "النتيجة"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "0",
            "template": "47-4",
            "name": "lim x ln(x) when x→0⁺"
        }
    
    def template_47_lhopital_5(self) -> Dict[str, Any]:
        """قالب 47-5: نهاية (1 - cos(x))/(x sin(x)) عندما x → 0"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\lim_{x \\to 0} \\frac{1 - \\cos(x)}{x \\sin(x)}",
            "المطلوب حساب النهاية"
        ))
        
        steps.append(make_step(
            "\\text{بالتعويض: } \\frac{0}{0}",
            "كمية غير معينة"
        ))
        
        steps.append(make_step(
            "\\text{نطبق قاعدة لوبيتال}",
            "الخطوة الأولى"
        ))
        
        steps.append(make_step(
            "f'(x) = \\sin(x), \\quad g'(x) = \\sin(x) + x\\cos(x)",
            "مشتقات المرة الأولى (قاعدة الضرب)"
        ))
        
        steps.append(make_step(
            "\\lim_{x \\to 0} \\frac{\\sin(x)}{\\sin(x) + x\\cos(x)} \\Rightarrow \\frac{0}{0}",
            "لا زالت غير معينة"
        ))
        
        steps.append(make_step(
            "\\text{نطبق لوبيتال مرة ثانية}",
            "الخطوة الثانية"
        ))
        
        steps.append(make_step(
            "f''(x) = \\cos(x), \\quad g''(x) = \\cos(x) + \\cos(x) - x\\sin(x) = 2\\cos(x) - x\\sin(x)",
            "مشتقات المرة الثانية"
        ))
        
        steps.append(make_step(
            "\\lim_{x \\to 0} \\frac{\\cos(x)}{2\\cos(x) - x\\sin(x)} = \\frac{1}{2 - 0} = \\frac{1}{2}",
            "النتيجة"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{1}{2}",
            "template": "47-5",
            "name": "lim (1-cos(x))/(x sin(x))"
        }

    # =========================================================================
    # 48. التفاضل الجزئي (Partial Derivatives) - 5 قوالب
    # =========================================================================
    
    def template_48_partial_derivative_1(self) -> Dict[str, Any]:
        """قالب 48-1: مشتقة جزئية ∂/∂x لـ x²y + xy²"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "f(x, y) = x^2 y + x y^2",
            "الدالة بمتغيرين"
        ))
        
        steps.append(make_step(
            "\\frac{\\partial}{\\partial x} (x^2 y + x y^2)",
            "نشتق بالنسبة لـ x (y ثابت)"
        ))
        
        steps.append(make_step(
            "\\frac{\\partial}{\\partial x} (x^2 y) = 2x y",
            "مشتقة x²y"
        ))
        
        steps.append(make_step(
            "\\frac{\\partial}{\\partial x} (x y^2) = y^2",
            "مشتقة xy²"
        ))
        
        steps.append(make_step(
            "\\frac{\\partial f}{\\partial x} = 2xy + y^2",
            "النتيجة النهائية"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "2xy + y^2",
            "template": "48-1",
            "name": "∂/∂x of x²y + xy²"
        }
    
    def template_48_partial_derivative_2(self) -> Dict[str, Any]:
        """قالب 48-2: مشتقة جزئية ∂/∂y لـ x²y + xy²"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x, y) = x^2 y + x y^2", "الدالة بمتغيرين"))
        steps.append(make_step("\\frac{\\partial}{\\partial y} (x^2 y + x y^2)", "نشتق بالنسبة لـ y (x ثابت)"))
        steps.append(make_step("\\frac{\\partial}{\\partial y} (x^2 y) = x^2", "مشتقة x²y"))
        steps.append(make_step("\\frac{\\partial}{\\partial y} (x y^2) = 2x y", "مشتقة xy²"))
        steps.append(make_step("\\frac{\\partial f}{\\partial y} = x^2 + 2xy", "النتيجة"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "x^2 + 2xy",
            "template": "48-2",
            "name": "∂/∂y of x²y + xy²"
        }
    
    def template_48_partial_derivative_3(self) -> Dict[str, Any]:
        """قالب 48-3: مشتقة جزئية ∂/∂x لـ sin(xy)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x, y) = \\sin(xy)", "الدالة بمتغيرين"))
        steps.append(make_step("\\frac{\\partial}{\\partial x} \\sin(xy)", "نشتق بالنسبة لـ x"))
        steps.append(make_step("\\text{نستخدم قاعدة السلسلة: } u = xy", "الدالة الداخلية"))
        steps.append(make_step("\\frac{\\partial u}{\\partial x} = y", "مشتقة u بالنسبة لـ x"))
        steps.append(make_step("\\frac{d}{du}\\sin(u) = \\cos(u)", "مشتقة الدالة الخارجية"))
        steps.append(make_step("\\frac{\\partial f}{\\partial x} = \\cos(xy) \\cdot y", "تطبيق قاعدة السلسلة"))
        steps.append(make_step("= y \\cos(xy)", "النتيجة"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "y \\cos(xy)",
            "template": "48-3",
            "name": "∂/∂x of sin(xy)"
        }
    
    def template_48_partial_derivative_4(self) -> Dict[str, Any]:
        """قالب 48-4: مشتقة جزئية ∂/∂y لـ e^(x²y)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x, y) = e^{x^2 y}", "الدالة بمتغيرين"))
        steps.append(make_step("\\frac{\\partial}{\\partial y} e^{x^2 y}", "نشتق بالنسبة لـ y"))
        steps.append(make_step("u = x^2 y", "الدالة الداخلية"))
        steps.append(make_step("\\frac{\\partial u}{\\partial y} = x^2", "مشتقة u بالنسبة لـ y"))
        steps.append(make_step("\\frac{d}{du} e^u = e^u", "مشتقة الدالة الخارجية"))
        steps.append(make_step("\\frac{\\partial f}{\\partial y} = e^{x^2 y} \\cdot x^2", "النتيجة"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "x^2 e^{x^2 y}",
            "template": "48-4",
            "name": "∂/∂y of e^(x²y)"
        }
    
    def template_48_partial_derivative_5(self) -> Dict[str, Any]:
        """قالب 48-5: مشتقة جزئية ثانية ∂²/∂x² لـ x³y²"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x, y) = x^3 y^2", "الدالة بمتغيرين"))
        steps.append(make_step("\\frac{\\partial f}{\\partial x} = 3x^2 y^2", "المشتقة الأولى"))
        steps.append(make_step("\\frac{\\partial^2 f}{\\partial x^2} = 6x y^2", "المشتقة الثانية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "6x y^2",
            "template": "48-5",
            "name": "∂²/∂x² of x³y²"
        }

    # =========================================================================
    # 49. التفاضل الكلي (Total Derivatives) - 5 قوالب
    # =========================================================================
    
    def template_49_total_derivative_1(self) -> Dict[str, Any]:
        """قالب 49-1: التفاضل الكلي لـ f(x,y) = x² + y²"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "f(x, y) = x^2 + y^2",
            "الدالة بمتغيرين"
        ))
        
        steps.append(make_step(
            "df = \\frac{\\partial f}{\\partial x} dx + \\frac{\\partial f}{\\partial y} dy",
            "صيغة التفاضل الكلي"
        ))
        
        steps.append(make_step(
            "\\frac{\\partial f}{\\partial x} = 2x",
            "المشتقة الجزئية بالنسبة لـ x"
        ))
        
        steps.append(make_step(
            "\\frac{\\partial f}{\\partial y} = 2y",
            "المشتقة الجزئية بالنسبة لـ y"
        ))
        
        steps.append(make_step(
            "df = 2x \\, dx + 2y \\, dy",
            "التفاضل الكلي"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "2x \\, dx + 2y \\, dy",
            "template": "49-1",
            "name": "Total differential of x²+y²"
        }
    
    def template_49_total_derivative_2(self) -> Dict[str, Any]:
        """قالب 49-2: التفاضل الكلي لـ f(x,y) = e^(xy)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x, y) = e^{xy}", "الدالة بمتغيرين"))
        steps.append(make_step("df = \\frac{\\partial f}{\\partial x} dx + \\frac{\\partial f}{\\partial y} dy", "صيغة التفاضل الكلي"))
        steps.append(make_step("\\frac{\\partial f}{\\partial x} = y e^{xy}", "المشتقة بالنسبة لـ x"))
        steps.append(make_step("\\frac{\\partial f}{\\partial y} = x e^{xy}", "المشتقة بالنسبة لـ y"))
        steps.append(make_step("df = y e^{xy} \\, dx + x e^{xy} \\, dy", "التفاضل الكلي"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "y e^{xy} \\, dx + x e^{xy} \\, dy",
            "template": "49-2",
            "name": "Total differential of e^(xy)"
        }
    
    def template_49_total_derivative_3(self) -> Dict[str, Any]:
        """قالب 49-3: التفاضل الكلي لـ f(x,y) = ln(x² + y²)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x, y) = \\ln(x^2 + y^2)", "الدالة بمتغيرين"))
        steps.append(make_step("df = \\frac{\\partial f}{\\partial x} dx + \\frac{\\partial f}{\\partial y} dy", "صيغة التفاضل الكلي"))
        steps.append(make_step("\\frac{\\partial f}{\\partial x} = \\frac{2x}{x^2 + y^2}", "المشتقة بالنسبة لـ x"))
        steps.append(make_step("\\frac{\\partial f}{\\partial y} = \\frac{2y}{x^2 + y^2}", "المشتقة بالنسبة لـ y"))
        steps.append(make_step("df = \\frac{2x}{x^2+y^2} \\, dx + \\frac{2y}{x^2+y^2} \\, dy", "التفاضل الكلي"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{2x}{x^2+y^2} \\, dx + \\frac{2y}{x^2+y^2} \\, dy",
            "template": "49-3",
            "name": "Total differential of ln(x²+y²)"
        }
    
    def template_49_total_derivative_4(self) -> Dict[str, Any]:
        """قالب 49-4: التفاضل الكلي لـ f(x,y) = sin(x) cos(y)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x, y) = \\sin(x) \\cos(y)", "الدالة بمتغيرين"))
        steps.append(make_step("df = \\frac{\\partial f}{\\partial x} dx + \\frac{\\partial f}{\\partial y} dy", "صيغة التفاضل الكلي"))
        steps.append(make_step("\\frac{\\partial f}{\\partial x} = \\cos(x) \\cos(y)", "المشتقة بالنسبة لـ x"))
        steps.append(make_step("\\frac{\\partial f}{\\partial y} = -\\sin(x) \\sin(y)", "المشتقة بالنسبة لـ y"))
        steps.append(make_step("df = \\cos(x)\\cos(y) \\, dx - \\sin(x)\\sin(y) \\, dy", "التفاضل الكلي"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\cos(x)\\cos(y) \\, dx - \\sin(x)\\sin(y) \\, dy",
            "template": "49-4",
            "name": "Total differential of sin(x)cos(y)"
        }
    
    def template_49_total_derivative_5(self) -> Dict[str, Any]:
        """قالب 49-5: التفاضل الكلي لـ f(x,y,z) = x² + y² + z²"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x, y, z) = x^2 + y^2 + z^2", "الدالة بثلاثة متغيرات"))
        steps.append(make_step("df = \\frac{\\partial f}{\\partial x} dx + \\frac{\\partial f}{\\partial y} dy + \\frac{\\partial f}{\\partial z} dz", "صيغة التفاضل الكلي"))
        steps.append(make_step("\\frac{\\partial f}{\\partial x} = 2x", "المشتقة بالنسبة لـ x"))
        steps.append(make_step("\\frac{\\partial f}{\\partial y} = 2y", "المشتقة بالنسبة لـ y"))
        steps.append(make_step("\\frac{\\partial f}{\\partial z} = 2z", "المشتقة بالنسبة لـ z"))
        steps.append(make_step("df = 2x \\, dx + 2y \\, dy + 2z \\, dz", "التفاضل الكلي"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "2x \\, dx + 2y \\, dy + 2z \\, dz",
            "template": "49-5",
            "name": "Total differential of x²+y²+z²"
        }

    # =========================================================================
    # 50. معادلات تفاضلية بسيطة (Simple Differential Equations) - 5 قوالب
    # =========================================================================
    
    def template_50_simple_de_1(self) -> Dict[str, Any]:
        """قالب 50-1: حل المعادلة dy/dx = 2x"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\frac{dy}{dx} = 2x",
            "المعادلة التفاضلية"
        ))
        
        steps.append(make_step(
            "dy = 2x \\, dx",
            "نفصل المتغيرات"
        ))
        
        steps.append(make_step(
            "\\int dy = \\int 2x \\, dx",
            "نكامل الطرفين"
        ))
        
        steps.append(make_step(
            "y = x^2 + C",
            "النتيجة"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "y = x^2 + C",
            "template": "50-1",
            "name": "dy/dx = 2x"
        }
    
    def template_50_simple_de_2(self) -> Dict[str, Any]:
        """قالب 50-2: حل المعادلة dy/dx = x² + 1"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\frac{dy}{dx} = x^2 + 1", "المعادلة التفاضلية"))
        steps.append(make_step("dy = (x^2 + 1) \\, dx", "نفصل المتغيرات"))
        steps.append(make_step("\\int dy = \\int (x^2 + 1) \\, dx", "نكامل الطرفين"))
        steps.append(make_step("y = \\frac{x^3}{3} + x + C", "النتيجة"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "y = \\frac{x^3}{3} + x + C",
            "template": "50-2",
            "name": "dy/dx = x²+1"
        }
    
    def template_50_simple_de_3(self) -> Dict[str, Any]:
        """قالب 50-3: حل المعادلة dy/dx = e^x مع الشرط y(0)=2"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\frac{dy}{dx} = e^x", "المعادلة التفاضلية"))
        steps.append(make_step("dy = e^x \\, dx", "نفصل المتغيرات"))
        steps.append(make_step("\\int dy = \\int e^x \\, dx", "نكامل الطرفين"))
        steps.append(make_step("y = e^x + C", "الحل العام"))
        steps.append(make_step("\\text{نستخدم الشرط } y(0) = 2 \\Rightarrow 2 = e^0 + C", "نعوض الشرط"))
        steps.append(make_step("2 = 1 + C \\Rightarrow C = 1", "نوجد C"))
        steps.append(make_step("y = e^x + 1", "الحل الخاص"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "y = e^x + 1",
            "template": "50-3",
            "name": "dy/dx = e^x, y(0)=2"
        }
    
    def template_50_simple_de_4(self) -> Dict[str, Any]:
        """قالب 50-4: حل المعادلة dy/dx = sin(x) مع الشرط y(π)=0"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\frac{dy}{dx} = \\sin(x)", "المعادلة التفاضلية"))
        steps.append(make_step("dy = \\sin(x) \\, dx", "نفصل المتغيرات"))
        steps.append(make_step("\\int dy = \\int \\sin(x) \\, dx", "نكامل الطرفين"))
        steps.append(make_step("y = -\\cos(x) + C", "الحل العام"))
        steps.append(make_step("\\text{نستخدم الشرط } y(\\pi) = 0 \\Rightarrow 0 = -\\cos(\\pi) + C", "نعوض الشرط"))
        steps.append(make_step("0 = -(-1) + C = 1 + C \\Rightarrow C = -1", "نوجد C"))
        steps.append(make_step("y = -\\cos(x) - 1", "الحل الخاص"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "y = -\\cos(x) - 1",
            "template": "50-4",
            "name": "dy/dx = sin(x), y(π)=0"
        }
    
    def template_50_simple_de_5(self) -> Dict[str, Any]:
        """قالب 50-5: حل المعادلة dy/dx = 1/x مع الشرط y(e)=1"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\frac{dy}{dx} = \\frac{1}{x}", "المعادلة التفاضلية"))
        steps.append(make_step("dy = \\frac{1}{x} \\, dx", "نفصل المتغيرات"))
        steps.append(make_step("\\int dy = \\int \\frac{1}{x} \\, dx", "نكامل الطرفين"))
        steps.append(make_step("y = \\ln|x| + C", "الحل العام"))
        steps.append(make_step("\\text{نستخدم الشرط } y(e) = 1 \\Rightarrow 1 = \\ln(e) + C", "نعوض الشرط"))
        steps.append(make_step("1 = 1 + C \\Rightarrow C = 0", "نوجد C"))
        steps.append(make_step("y = \\ln|x|", "الحل الخاص"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "y = \\ln|x|",
            "template": "50-5",
            "name": "dy/dx = 1/x, y(e)=1"
        }

    # =========================================================================
    # 51. معادلات تفاضلية خطية من الرتبة الأولى (First Order Linear) - 5 قوالب
    # =========================================================================
    
    def template_51_linear_de_1(self) -> Dict[str, Any]:
        """قالب 51-1: حل المعادلة dy/dx + y = 0"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\frac{dy}{dx} + y = 0",
            "المعادلة التفاضلية الخطية"
        ))
        
        steps.append(make_step(
            "\\frac{dy}{dx} = -y",
            "نعيد الترتيب"
        ))
        
        steps.append(make_step(
            "\\frac{1}{y} \\, dy = -dx",
            "نفصل المتغيرات"
        ))
        
        steps.append(make_step(
            "\\int \\frac{1}{y} \\, dy = -\\int dx",
            "نكامل الطرفين"
        ))
        
        steps.append(make_step(
            "\\ln|y| = -x + C",
            "النتيجة"
        ))
        
        steps.append(make_step(
            "|y| = e^{-x + C} = e^C e^{-x}",
            "نستخدم الأس"
        ))
        
        steps.append(make_step(
            "y = A e^{-x} \\text{ حيث } A = \\pm e^C",
            "الحل العام"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "y = A e^{-x}",
            "template": "51-1",
            "name": "dy/dx + y = 0"
        }
    
    def template_51_linear_de_2(self) -> Dict[str, Any]:
        """قالب 51-2: حل المعادلة dy/dx + 2y = 0"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\frac{dy}{dx} + 2y = 0", "المعادلة التفاضلية"))
        steps.append(make_step("\\frac{dy}{dx} = -2y", "نعيد الترتيب"))
        steps.append(make_step("\\frac{1}{y} \\, dy = -2 \\, dx", "نفصل المتغيرات"))
        steps.append(make_step("\\int \\frac{1}{y} \\, dy = -2 \\int dx", "نكامل الطرفين"))
        steps.append(make_step("\\ln|y| = -2x + C", "النتيجة"))
        steps.append(make_step("y = A e^{-2x}", "الحل العام"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "y = A e^{-2x}",
            "template": "51-2",
            "name": "dy/dx + 2y = 0"
        }
    
    def template_51_linear_de_3(self) -> Dict[str, Any]:
        """قالب 51-3: حل المعادلة dy/dx + y = e^x باستخدام عامل التكامل"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\frac{dy}{dx} + y = e^x",
            "المعادلة التفاضلية"
        ))
        
        steps.append(make_step(
            "\\text{عامل التكامل } \\mu(x) = e^{\\int 1 \\, dx} = e^x",
            "نحسب عامل التكامل"
        ))
        
        steps.append(make_step(
            "e^x \\frac{dy}{dx} + e^x y = e^x \\cdot e^x = e^{2x}",
            "نضرب المعادلة في عامل التكامل"
        ))
        
        steps.append(make_step(
            "\\frac{d}{dx}(e^x y) = e^{2x}",
            "الطرف الأيسر مشتقة حاصل ضرب"
        ))
        
        steps.append(make_step(
            "e^x y = \\int e^{2x} \\, dx = \\frac{1}{2} e^{2x} + C",
            "نكامل الطرفين"
        ))
        
        steps.append(make_step(
            "y = \\frac{1}{2} e^{x} + C e^{-x}",
            "نقسم على e^x"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "y = \\frac{1}{2} e^{x} + C e^{-x}",
            "template": "51-3",
            "name": "dy/dx + y = e^x"
        }
    
    def template_51_linear_de_4(self) -> Dict[str, Any]:
        """قالب 51-4: حل المعادلة dy/dx + 2y = e^x"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\frac{dy}{dx} + 2y = e^x", "المعادلة التفاضلية"))
        steps.append(make_step("\\text{عامل التكامل } \\mu(x) = e^{\\int 2 \\, dx} = e^{2x}", "نحسب عامل التكامل"))
        steps.append(make_step("e^{2x} \\frac{dy}{dx} + 2e^{2x} y = e^{2x} e^x = e^{3x}", "نضرب المعادلة"))
        steps.append(make_step("\\frac{d}{dx}(e^{2x} y) = e^{3x}", "الطرف الأيسر مشتقة"))
        steps.append(make_step("e^{2x} y = \\int e^{3x} \\, dx = \\frac{1}{3} e^{3x} + C", "نكامل"))
        steps.append(make_step("y = \\frac{1}{3} e^{x} + C e^{-2x}", "نقسم على e^{2x}"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "y = \\frac{1}{3} e^{x} + C e^{-2x}",
            "template": "51-4",
            "name": "dy/dx + 2y = e^x"
        }
    
    def template_51_linear_de_5(self) -> Dict[str, Any]:
        """قالب 51-5: حل المعادلة dy/dx + y/x = x²"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\frac{dy}{dx} + \\frac{y}{x} = x^2", "المعادلة التفاضلية"))
        steps.append(make_step("\\text{عامل التكامل } \\mu(x) = e^{\\int \\frac{1}{x} \\, dx} = e^{\\ln|x|} = |x|", "نحسب عامل التكامل"))
        steps.append(make_step("\\text{نأخذ } \\mu(x) = x", "نبسط"))
        steps.append(make_step("x \\frac{dy}{dx} + y = x^3", "نضرب المعادلة في x"))
        steps.append(make_step("\\frac{d}{dx}(x y) = x^3", "الطرف الأيسر مشتقة"))
        steps.append(make_step("x y = \\int x^3 \\, dx = \\frac{x^4}{4} + C", "نكامل"))
        steps.append(make_step("y = \\frac{x^3}{4} + \\frac{C}{x}", "نقسم على x"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "y = \\frac{x^3}{4} + \\frac{C}{x}",
            "template": "51-5",
            "name": "dy/dx + y/x = x²"
        }

    # =========================================================================
    # 52. معادلات تفاضلية قابلة للفصل (Separable) - 5 قوالب
    # =========================================================================
    
    def template_52_separable_de_1(self) -> Dict[str, Any]:
        """قالب 52-1: حل المعادلة dy/dx = x/y"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\frac{dy}{dx} = \\frac{x}{y}",
            "المعادلة التفاضلية"
        ))
        
        steps.append(make_step(
            "y \\, dy = x \\, dx",
            "نفصل المتغيرات"
        ))
        
        steps.append(make_step(
            "\\int y \\, dy = \\int x \\, dx",
            "نكامل الطرفين"
        ))
        
        steps.append(make_step(
            "\\frac{y^2}{2} = \\frac{x^2}{2} + C",
            "النتيجة"
        ))
        
        steps.append(make_step(
            "y^2 = x^2 + 2C",
            "نضرب في 2"
        ))
        
        steps.append(make_step(
            "y^2 - x^2 = K \\text{ حيث } K = 2C",
            "الحل العام"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "y^2 - x^2 = K",
            "template": "52-1",
            "name": "dy/dx = x/y"
        }
    
    def template_52_separable_de_2(self) -> Dict[str, Any]:
        """قالب 52-2: حل المعادلة dy/dx = xy"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\frac{dy}{dx} = xy", "المعادلة التفاضلية"))
        steps.append(make_step("\\frac{1}{y} \\, dy = x \\, dx", "نفصل المتغيرات"))
        steps.append(make_step("\\int \\frac{1}{y} \\, dy = \\int x \\, dx", "نكامل"))
        steps.append(make_step("\\ln|y| = \\frac{x^2}{2} + C", "النتيجة"))
        steps.append(make_step("|y| = e^{x^2/2 + C} = e^C e^{x^2/2}", "نستخدم الأس"))
        steps.append(make_step("y = A e^{x^2/2}", "الحل العام"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "y = A e^{x^2/2}",
            "template": "52-2",
            "name": "dy/dx = xy"
        }
    
    def template_52_separable_de_3(self) -> Dict[str, Any]:
        """قالب 52-3: حل المعادلة dy/dx = y² مع الشرط y(0)=1"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\frac{dy}{dx} = y^2", "المعادلة التفاضلية"))
        steps.append(make_step("\\frac{1}{y^2} \\, dy = dx", "نفصل المتغيرات"))
        steps.append(make_step("\\int y^{-2} \\, dy = \\int dx", "نكامل"))
        steps.append(make_step("-y^{-1} = x + C", "النتيجة"))
        steps.append(make_step("-\\frac{1}{y} = x + C", "نكتب بشكل آخر"))
        steps.append(make_step("\\frac{1}{y} = -x - C", "نضرب في -1"))
        steps.append(make_step("y = \\frac{1}{-x - C}", "الحل العام"))
        steps.append(make_step("\\text{نستخدم الشرط } y(0) = 1 \\Rightarrow 1 = \\frac{1}{-0 - C} = -\\frac{1}{C}", "نعوض"))
        steps.append(make_step("C = -1", "نوجد C"))
        steps.append(make_step("y = \\frac{1}{-x + 1} = \\frac{1}{1 - x}", "الحل الخاص"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "y = \\frac{1}{1 - x}",
            "template": "52-3",
            "name": "dy/dx = y², y(0)=1"
        }
    
    def template_52_separable_de_4(self) -> Dict[str, Any]:
        """قالب 52-4: حل المعادلة dy/dx = e^(x-y)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\frac{dy}{dx} = e^{x-y}", "المعادلة التفاضلية"))
        steps.append(make_step("\\frac{dy}{dx} = e^x e^{-y}", "نفك الأس"))
        steps.append(make_step("e^y \\, dy = e^x \\, dx", "نفصل المتغيرات"))
        steps.append(make_step("\\int e^y \\, dy = \\int e^x \\, dx", "نكامل"))
        steps.append(make_step("e^y = e^x + C", "النتيجة"))
        steps.append(make_step("y = \\ln(e^x + C)", "الحل العام"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "y = \\ln(e^x + C)",
            "template": "52-4",
            "name": "dy/dx = e^(x-y)"
        }
    
    def template_52_separable_de_5(self) -> Dict[str, Any]:
        """قالب 52-5: حل المعادلة dy/dx = (y² + 1)/(x² + 1)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\frac{dy}{dx} = \\frac{y^2 + 1}{x^2 + 1}", "المعادلة التفاضلية"))
        steps.append(make_step("\\frac{1}{y^2 + 1} \\, dy = \\frac{1}{x^2 + 1} \\, dx", "نفصل المتغيرات"))
        steps.append(make_step("\\int \\frac{1}{y^2 + 1} \\, dy = \\int \\frac{1}{x^2 + 1} \\, dx", "نكامل"))
        steps.append(make_step("\\arctan(y) = \\arctan(x) + C", "النتيجة"))
        steps.append(make_step("y = \\tan(\\arctan(x) + C)", "نأخذ tan للطرفين"))
        steps.append(make_step("\\text{باستخدام قانون جمع الزوايا: } \\tan(A+B) = \\frac{\\tan A + \\tan B}{1 - \\tan A \\tan B}", "نطبق القانون"))
        steps.append(make_step("y = \\frac{x + \\tan(C)}{1 - x \\tan(C)}", "الحل العام"))
        steps.append(make_step("y = \\frac{x + K}{1 - Kx} \\text{ حيث } K = \\tan(C)", "نكتب بصورة أبسط"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "y = \\frac{x + K}{1 - Kx}",
            "template": "52-5",
            "name": "dy/dx = (y²+1)/(x²+1)"
        }

    # =========================================================================
    # 53. معادلات تفاضلية باستخدام التكامل (Integration Method) - 5 قوالب
    # =========================================================================
    
    def template_53_integration_de_1(self) -> Dict[str, Any]:
        """قالب 53-1: حل المعادلة d²y/dx² = 6x"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\frac{d^2y}{dx^2} = 6x",
            "المعادلة التفاضلية من الرتبة الثانية"
        ))
        
        steps.append(make_step(
            "\\frac{dy}{dx} = \\int 6x \\, dx = 3x^2 + C_1",
            "نكامل مرة أولى"
        ))
        
        steps.append(make_step(
            "y = \\int (3x^2 + C_1) \\, dx = x^3 + C_1 x + C_2",
            "نكامل مرة ثانية"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "y = x^3 + C_1 x + C_2",
            "template": "53-1",
            "name": "d²y/dx² = 6x"
        }
    
    def template_53_integration_de_2(self) -> Dict[str, Any]:
        """قالب 53-2: حل المعادلة d²y/dx² = sin(x)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\frac{d^2y}{dx^2} = \\sin(x)", "المعادلة التفاضلية"))
        steps.append(make_step("\\frac{dy}{dx} = \\int \\sin(x) \\, dx = -\\cos(x) + C_1", "نكامل مرة أولى"))
        steps.append(make_step("y = \\int (-\\cos(x) + C_1) \\, dx = -\\sin(x) + C_1 x + C_2", "نكامل مرة ثانية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "y = -\\sin(x) + C_1 x + C_2",
            "template": "53-2",
            "name": "d²y/dx² = sin(x)"
        }
    
    def template_53_integration_de_3(self) -> Dict[str, Any]:
        """قالب 53-3: حل المعادلة d²y/dx² = e^x مع الشروط y(0)=1, y'(0)=0"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\frac{d^2y}{dx^2} = e^x", "المعادلة التفاضلية"))
        steps.append(make_step("\\frac{dy}{dx} = \\int e^x \\, dx = e^x + C_1", "نكامل مرة أولى"))
        steps.append(make_step("\\text{نستخدم الشرط } y'(0) = 0 \\Rightarrow 0 = e^0 + C_1 = 1 + C_1 \\Rightarrow C_1 = -1", "نوجد C₁"))
        steps.append(make_step("\\frac{dy}{dx} = e^x - 1", "المشتقة الأولى"))
        steps.append(make_step("y = \\int (e^x - 1) \\, dx = e^x - x + C_2", "نكامل مرة ثانية"))
        steps.append(make_step("\\text{نستخدم الشرط } y(0) = 1 \\Rightarrow 1 = e^0 - 0 + C_2 = 1 + C_2 \\Rightarrow C_2 = 0", "نوجد C₂"))
        steps.append(make_step("y = e^x - x", "الحل الخاص"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "y = e^x - x",
            "template": "53-3",
            "name": "d²y/dx² = e^x, y(0)=1, y'(0)=0"
        }
    
    def template_53_integration_de_4(self) -> Dict[str, Any]:
        """قالب 53-4: حل المعادلة d³y/dx³ = 6"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\frac{d^3y}{dx^3} = 6", "المعادلة التفاضلية من الرتبة الثالثة"))
        steps.append(make_step("\\frac{d^2y}{dx^2} = \\int 6 \\, dx = 6x + C_1", "نكامل مرة أولى"))
        steps.append(make_step("\\frac{dy}{dx} = \\int (6x + C_1) \\, dx = 3x^2 + C_1 x + C_2", "نكامل مرة ثانية"))
        steps.append(make_step("y = \\int (3x^2 + C_1 x + C_2) \\, dx = x^3 + \\frac{C_1}{2} x^2 + C_2 x + C_3", "نكامل مرة ثالثة"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "y = x^3 + \\frac{C_1}{2} x^2 + C_2 x + C_3",
            "template": "53-4",
            "name": "d³y/dx³ = 6"
        }
    
    def template_53_integration_de_5(self) -> Dict[str, Any]:
        """قالب 53-5: حل المعادلة d²y/dx² = cos(2x)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("\\frac{d^2y}{dx^2} = \\cos(2x)", "المعادلة التفاضلية"))
        steps.append(make_step("\\frac{dy}{dx} = \\int \\cos(2x) \\, dx = \\frac{1}{2} \\sin(2x) + C_1", "نكامل مرة أولى"))
        steps.append(make_step("y = \\int \\left(\\frac{1}{2} \\sin(2x) + C_1\\right) \\, dx = -\\frac{1}{4} \\cos(2x) + C_1 x + C_2", "نكامل مرة ثانية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "y = -\\frac{1}{4} \\cos(2x) + C_1 x + C_2",
            "template": "53-5",
            "name": "d²y/dx² = cos(2x)"
        }

    # =========================================================================
    # 54. مشتقات التكاملات (نظرية الأساس) - 5 قوالب
    # =========================================================================
    
    def template_54_fundamental_theorem_1(self) -> Dict[str, Any]:
        """قالب 54-1: مشتقة F(x) = ∫₀ˣ t² dt"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "F(x) = \\int_{0}^{x} t^2 \\, dt",
            "الدالة المعرفة بتكامل"
        ))
        
        steps.append(make_step(
            "\\text{نظرية الأساس في التفاضل والتكامل: } \\frac{d}{dx} \\int_{a}^{x} f(t) \\, dt = f(x)",
            "نطبق النظرية"
        ))
        
        steps.append(make_step(
            "F'(x) = x^2",
            "النتيجة"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "x^2",
            "template": "54-1",
            "name": "d/dx ∫₀ˣ t² dt"
        }
    
    def template_54_fundamental_theorem_2(self) -> Dict[str, Any]:
        """قالب 54-2: مشتقة F(x) = ∫₀ˣ sin(t) dt"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("F(x) = \\int_{0}^{x} \\sin(t) \\, dt", "الدالة"))
        steps.append(make_step("F'(x) = \\sin(x)", "بتطبيق نظرية الأساس"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\sin(x)",
            "template": "54-2",
            "name": "d/dx ∫₀ˣ sin(t) dt"
        }
    
    def template_54_fundamental_theorem_3(self) -> Dict[str, Any]:
        """قالب 54-3: مشتقة F(x) = ∫₀^{x²} cos(t) dt"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "F(x) = \\int_{0}^{x^2} \\cos(t) \\, dt",
            "الدالة مع حد علوي مركب"
        ))
        
        steps.append(make_step(
            "\\text{نظرية الأساس مع قاعدة السلسلة: } \\frac{d}{dx} \\int_{a}^{u(x)} f(t) \\, dt = f(u(x)) \\cdot u'(x)",
            "نطبق الصيغة العامة"
        ))
        
        steps.append(make_step(
            "u(x) = x^2, \\quad u'(x) = 2x",
            "نحدد u ومشتقتها"
        ))
        
        steps.append(make_step(
            "f(u) = \\cos(u) = \\cos(x^2)",
            "نعوض f(u)"
        ))
        
        steps.append(make_step(
            "F'(x) = \\cos(x^2) \\cdot 2x = 2x \\cos(x^2)",
            "النتيجة"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "2x \\cos(x^2)",
            "template": "54-3",
            "name": "d/dx ∫₀^{x²} cos(t) dt"
        }
    
    def template_54_fundamental_theorem_4(self) -> Dict[str, Any]:
        """قالب 54-4: مشتقة F(x) = ∫_{x}^{0} e^t dt"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("F(x) = \\int_{x}^{0} e^t \\, dt", "الدالة مع حد سفلي متغير"))
        steps.append(make_step("\\int_{x}^{0} e^t \\, dt = -\\int_{0}^{x} e^t \\, dt", "نعكس الحدود"))
        steps.append(make_step("F'(x) = -\\frac{d}{dx} \\int_{0}^{x} e^t \\, dt = -e^x", "نطبق نظرية الأساس"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "-e^x",
            "template": "54-4",
            "name": "d/dx ∫_{x}⁰ e^t dt"
        }
    
    def template_54_fundamental_theorem_5(self) -> Dict[str, Any]:
        """قالب 54-5: مشتقة F(x) = ∫_{x}^{x²} ln(t) dt"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "F(x) = \\int_{x}^{x^2} \\ln(t) \\, dt",
            "الدالة مع حدين متغيرين"
        ))
        
        steps.append(make_step(
            "\\int_{x}^{x^2} \\ln(t) \\, dt = \\int_{0}^{x^2} \\ln(t) \\, dt - \\int_{0}^{x} \\ln(t) \\, dt",
            "نفصل التكامل"
        ))
        
        steps.append(make_step(
            "F'(x) = \\frac{d}{dx} \\int_{0}^{x^2} \\ln(t) \\, dt - \\frac{d}{dx} \\int_{0}^{x} \\ln(t) \\, dt",
            "نشتق"
        ))
        
        steps.append(make_step(
            "= \\ln(x^2) \\cdot 2x - \\ln(x)",
            "نطبق نظرية الأساس مع قاعدة السلسلة"
        ))
        
        steps.append(make_step(
            "= 2x \\ln(x^2) - \\ln(x)",
            "النتيجة"
        ))
        
        steps.append(make_step(
            "= 2x \\cdot 2\\ln(x) - \\ln(x) = (4x - 1)\\ln(x)",
            "نبسط باستخدام خصائص اللوغاريتم"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "(4x - 1)\\ln(x)",
            "template": "54-5",
            "name": "d/dx ∫_{x}^{x²} ln(t) dt"
        }

    # =========================================================================
    # 55. اشتقاقات الدوال متعددة المتغيرات (Advanced Multivariable) - 5 قوالب
    # =========================================================================
    
    def template_55_advanced_multivariable_1(self) -> Dict[str, Any]:
        """قالب 55-1: المشتقة الاتجاهية لـ f(x,y)=x²+y² في اتجاه v=(1,1)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "f(x, y) = x^2 + y^2",
            "الدالة"
        ))
        
        steps.append(make_step(
            "\\vec{v} = (1, 1)",
            "الاتجاه المعطى"
        ))
        
        steps.append(make_step(
            "\\nabla f = \\left( \\frac{\\partial f}{\\partial x}, \\frac{\\partial f}{\\partial y} \\right) = (2x, 2y)",
            "نحسب التدرج (Gradient)"
        ))
        
        steps.append(make_step(
            "\\text{عند النقطة } (x,y) = (1,0) \\text{ (مثلاً)}",
            "نختار نقطة"
        ))
        
        steps.append(make_step(
            "\\nabla f(1,0) = (2, 0)",
            "التدرج عند النقطة"
        ))
        
        steps.append(make_step(
            "\\|\\vec{v}\\| = \\sqrt{1^2 + 1^2} = \\sqrt{2}",
            "طول متجه الاتجاه"
        ))
        
        steps.append(make_step(
            "\\vec{u} = \\frac{\\vec{v}}{\\|\\vec{v}\\|} = \\left(\\frac{1}{\\sqrt{2}}, \\frac{1}{\\sqrt{2}}\\right)",
            "متجه الوحدة في اتجاه v"
        ))
        
        steps.append(make_step(
            "D_{\\vec{u}} f(1,0) = \\nabla f(1,0) \\cdot \\vec{u} = (2,0) \\cdot \\left(\\frac{1}{\\sqrt{2}}, \\frac{1}{\\sqrt{2}}\\right) = \\frac{2}{\\sqrt{2}} = \\sqrt{2}",
            "المشتقة الاتجاهية = حاصل الضرب النقطي"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\sqrt{2}",
            "template": "55-1",
            "name": "Directional derivative of x²+y²"
        }
    
    def template_55_advanced_multivariable_2(self) -> Dict[str, Any]:
        """قالب 55-2: نقطة حرجة للدالة f(x,y)=x²+y²-2x-4y+5"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "f(x, y) = x^2 + y^2 - 2x - 4y + 5",
            "الدالة"
        ))
        
        steps.append(make_step(
            "\\frac{\\partial f}{\\partial x} = 2x - 2",
            "المشتقة الجزئية بالنسبة لـ x"
        ))
        
        steps.append(make_step(
            "\\frac{\\partial f}{\\partial y} = 2y - 4",
            "المشتقة الجزئية بالنسبة لـ y"
        ))
        
        steps.append(make_step(
            "\\text{عند النقطة الحرجة: } \\frac{\\partial f}{\\partial x} = 0 \\text{ و } \\frac{\\partial f}{\\partial y} = 0",
            "نضع المشتقات = 0"
        ))
        
        steps.append(make_step(
            "2x - 2 = 0 \\Rightarrow x = 1",
            "نحل المعادلة الأولى"
        ))
        
        steps.append(make_step(
            "2y - 4 = 0 \\Rightarrow y = 2",
            "نحل المعادلة الثانية"
        ))
        
        steps.append(make_step(
            "\\text{النقطة الحرجة: } (1, 2)",
            "النتيجة"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "(1, 2)",
            "template": "55-2",
            "name": "Critical point of x²+y²-2x-4y+5"
        }
    
    def template_55_advanced_multivariable_3(self) -> Dict[str, Any]:
        """قالب 55-3: تصنيف النقطة الحرجة (قيم عظمى/صغرى) للدالة f(x,y)=x²+y²-2x-4y+5"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "f(x, y) = x^2 + y^2 - 2x - 4y + 5",
            "الدالة"
        ))
        
        steps.append(make_step(
            "\\text{النقطة الحرجة: } (1, 2) \\text{ (من القالب السابق)}",
            "نقطة حرجة"
        ))
        
        steps.append(make_step(
            "f_{xx} = \\frac{\\partial^2 f}{\\partial x^2} = 2",
            "المشتقة الثانية بالنسبة لـ x"
        ))
        
        steps.append(make_step(
            "f_{yy} = \\frac{\\partial^2 f}{\\partial y^2} = 2",
            "المشتقة الثانية بالنسبة لـ y"
        ))
        
        steps.append(make_step(
            "f_{xy} = \\frac{\\partial^2 f}{\\partial x \\partial y} = 0",
            "المشتقة المختلطة"
        ))
        
        steps.append(make_step(
            "D = f_{xx} f_{yy} - (f_{xy})^2 = 2 \\cdot 2 - 0^2 = 4",
            "مميز الاختبار"
        ))
        
        steps.append(make_step(
            "D > 0 \\text{ و } f_{xx} > 0 \\Rightarrow \\text{نقطة صغرى محلية}",
            "تفسير النتيجة"
        ))
        
        steps.append(make_step(
            "f(1,2) = 1^2 + 2^2 - 2(1) - 4(2) + 5 = 1 + 4 - 2 - 8 + 5 = 0",
            "قيمة الدالة عند النقطة"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\text{نقطة صغرى محلية بقيمة } 0",
            "template": "55-3",
            "name": "Classify critical point"
        }
    
    def template_55_advanced_multivariable_4(self) -> Dict[str, Any]:
        """قالب 55-4: قاعدة السلسلة لدالة متعددة المتغيرات"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\text{إذا كانت } z = f(x,y) = x^2 + y^2 \\text{ و } x = t^2, y = e^t",
            "دالة مركبة"
        ))
        
        steps.append(make_step(
            "\\frac{dz}{dt} = \\frac{\\partial f}{\\partial x} \\frac{dx}{dt} + \\frac{\\partial f}{\\partial y} \\frac{dy}{dt}",
            "قاعدة السلسلة"
        ))
        
        steps.append(make_step(
            "\\frac{\\partial f}{\\partial x} = 2x, \\quad \\frac{\\partial f}{\\partial y} = 2y",
            "المشتقات الجزئية لـ f"
        ))
        
        steps.append(make_step(
            "\\frac{dx}{dt} = 2t, \\quad \\frac{dy}{dt} = e^t",
            "مشتقات x و y"
        ))
        
        steps.append(make_step(
            "\\frac{dz}{dt} = 2x \\cdot 2t + 2y \\cdot e^t = 4xt + 2y e^t",
            "نعوض"
        ))
        
        steps.append(make_step(
            "= 4(t^2)(t) + 2(e^t)(e^t) = 4t^3 + 2e^{2t}",
            "نعوض x = t², y = e^t"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "4t^3 + 2e^{2t}",
            "template": "55-4",
            "name": "Chain rule for multivariable"
        }
    
    def template_55_advanced_multivariable_5(self) -> Dict[str, Any]:
        """قالب 55-5: تفاضل ضمني (Implicit Differentiation)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "\\text{إذا كانت } x^2 + y^2 = 25",
            "معادلة ضمنية"
        ))
        
        steps.append(make_step(
            "\\frac{d}{dx}(x^2) + \\frac{d}{dx}(y^2) = \\frac{d}{dx}(25)",
            "نشتق الطرفين بالنسبة لـ x"
        ))
        
        steps.append(make_step(
            "2x + 2y \\frac{dy}{dx} = 0",
            "نطبق قاعدة السلسلة على y²"
        ))
        
        steps.append(make_step(
            "2y \\frac{dy}{dx} = -2x",
            "ننقل 2x للطرف الآخر"
        ))
        
        steps.append(make_step(
            "\\frac{dy}{dx} = -\\frac{x}{y}",
            "نقسم على 2y"
        ))
        
        steps.append(make_step(
            "\\text{عند النقطة } (3,4): \\frac{dy}{dx} = -\\frac{3}{4}",
            "مثال بقيم محددة"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "-\\frac{x}{y}",
            "template": "55-5",
            "name": "Implicit differentiation"
        }

    # =========================================================================
    # دوال مساعدة وإحصائيات
    # =========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """إحصائيات استخدام القوالب"""
        return self.stats
