"""
================================================================================
الملف 1/3: التفاضل والتكامل - المشتقات
File 1/3: Calculus - Derivatives (35 Templates)

القوالب:
31. مشتقات أساسية (5 قوالب)
32. مشتقات مركبة (5 قوالب)
33. مشتقات الضرب والقسمة (5 قوالب)
34. مشتقات الدوال المثلثية المعكوسة (5 قوالب)
35. مشتقات اللوغاريتمية (5 قوالب)
36. مشتقات الدوال الأسية (5 قوالب)
37. مشتقات متقدمة متعددة المتغيرات (5 قوالب)
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

class CalculusSolverPart1:
    """حلال المشتقات - يغطي القوالب 31-37"""
    
    def __init__(self):
        self.x = sp.Symbol('x', real=True)
        self.y = sp.Symbol('y', real=True)
        self.z = sp.Symbol('z', real=True)
        self.stats = {'total_calls': 0, 'successful': 0, 'failed': 0}
        logger.info("✅ تم تهيئة CalculusSolverPart1 - المشتقات (35 قالب)")

    # =========================================================================
    # 31. مشتقات أساسية (5 قوالب)
    # =========================================================================
    
    def template_31_derivative_basic_1(self) -> Dict[str, Any]:
        """قالب 31-1: مشتقة x^n (n عدد صحيح) - مثال: f(x) = x^3"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "f(x) = x^3",
            "الدالة الأصلية"
        ))
        
        steps.append(make_step(
            "\\frac{d}{dx}[x^n] = n \\cdot x^{n-1}",
            "قاعدة المشتقة: مشتقة x^n هي n·x^(n-1)"
        ))
        
        steps.append(make_step(
            "f'(x) = 3 \\cdot x^{3-1} = 3x^2",
            "نعوض n = 3"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "3x^2",
            "template": "31-1",
            "name": "مشتقة x^3"
        }
    
    def template_31_derivative_basic_2(self) -> Dict[str, Any]:
        """قالب 31-2: مشتقة x^n (n كسري) - مثال: f(x) = x^(1/2) = √x"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "f(x) = \\sqrt{x} = x^{\\frac{1}{2}}",
            "الدالة الأصلية (نكتبها على صورة أسية)"
        ))
        
        steps.append(make_step(
            "\\frac{d}{dx}[x^n] = n \\cdot x^{n-1}",
            "نطبق قاعدة المشتقة"
        ))
        
        steps.append(make_step(
            "f'(x) = \\frac{1}{2} \\cdot x^{\\frac{1}{2}-1} = \\frac{1}{2} x^{-\\frac{1}{2}}",
            "نعوض n = 1/2"
        ))
        
        steps.append(make_step(
            "f'(x) = \\frac{1}{2\\sqrt{x}}",
            "نبسط النتيجة"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{1}{2\\sqrt{x}}",
            "template": "31-2",
            "name": "مشتقة √x"
        }
    
    def template_31_derivative_basic_3(self) -> Dict[str, Any]:
        """قالب 31-3: مشتقة sin(x)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "f(x) = \\sin(x)",
            "الدالة الأصلية"
        ))
        
        steps.append(make_step(
            "\\frac{d}{dx}[\\sin(x)] = \\cos(x)",
            "قاعدة مشتقة الجيب"
        ))
        
        steps.append(make_step(
            "f'(x) = \\cos(x)",
            "النتيجة"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\cos(x)",
            "template": "31-3",
            "name": "مشتقة sin(x)"
        }
    
    def template_31_derivative_basic_4(self) -> Dict[str, Any]:
        """قالب 31-4: مشتقة cos(x)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "f(x) = \\cos(x)",
            "الدالة الأصلية"
        ))
        
        steps.append(make_step(
            "\\frac{d}{dx}[\\cos(x)] = -\\sin(x)",
            "قاعدة مشتقة جيب التمام"
        ))
        
        steps.append(make_step(
            "f'(x) = -\\sin(x)",
            "النتيجة"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "-\\sin(x)",
            "template": "31-4",
            "name": "مشتقة cos(x)"
        }
    
    def template_31_derivative_basic_5(self) -> Dict[str, Any]:
        """قالب 31-5: مشتقة tan(x)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "f(x) = \\tan(x) = \\frac{\\sin(x)}{\\cos(x)}",
            "الدالة الأصلية"
        ))
        
        steps.append(make_step(
            "\\frac{d}{dx}[\\tan(x)] = \\sec^2(x)",
            "قاعدة مشتقة الظل"
        ))
        
        steps.append(make_step(
            "f'(x) = \\sec^2(x) = \\frac{1}{\\cos^2(x)}",
            "النتيجة"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\sec^2(x)",
            "template": "31-5",
            "name": "مشتقة tan(x)"
        }

    # =========================================================================
    # 32. مشتقات مركبة (Chain Rule) - 5 قوالب
    # =========================================================================
    
    def template_32_chain_rule_1(self) -> Dict[str, Any]:
        """قالب 32-1: مشتقة sin(2x)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "f(x) = \\sin(2x)",
            "الدالة الأصلية (دالة مركبة)"
        ))
        
        steps.append(make_step(
            "\\text{نفرض } u = 2x \\text{ ، } f(u) = \\sin(u)",
            "نحدد الدالة الداخلية والخارجية"
        ))
        
        steps.append(make_step(
            "\\frac{du}{dx} = 2",
            "مشتقة الدالة الداخلية"
        ))
        
        steps.append(make_step(
            "\\frac{df}{du} = \\cos(u)",
            "مشتقة الدالة الخارجية"
        ))
        
        steps.append(make_step(
            "\\frac{df}{dx} = \\frac{df}{du} \\cdot \\frac{du}{dx} = \\cos(u) \\cdot 2",
            "نطبق قاعدة السلسلة"
        ))
        
        steps.append(make_step(
            "f'(x) = 2\\cos(2x)",
            "نعوض u = 2x"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "2\\cos(2x)",
            "template": "32-1",
            "name": "مشتقة sin(2x)"
        }
    
    def template_32_chain_rule_2(self) -> Dict[str, Any]:
        """قالب 32-2: مشتقة cos(3x)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x) = \\cos(3x)", "الدالة الأصلية"))
        steps.append(make_step("u = 3x", "الدالة الداخلية"))
        steps.append(make_step("\\frac{du}{dx} = 3", "مشتقة u"))
        steps.append(make_step("\\frac{d}{du}[\\cos(u)] = -\\sin(u)", "مشتقة الدالة الخارجية"))
        steps.append(make_step("f'(x) = -\\sin(3x) \\cdot 3", "تطبيق قاعدة السلسلة"))
        steps.append(make_step("f'(x) = -3\\sin(3x)", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "-3\\sin(3x)",
            "template": "32-2",
            "name": "مشتقة cos(3x)"
        }
    
    def template_32_chain_rule_3(self) -> Dict[str, Any]:
        """قالب 32-3: مشتقة e^(x²)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x) = e^{x^2}", "الدالة الأصلية"))
        steps.append(make_step("u = x^2", "الدالة الداخلية"))
        steps.append(make_step("\\frac{du}{dx} = 2x", "مشتقة u"))
        steps.append(make_step("\\frac{d}{du}[e^u] = e^u", "مشتقة الدالة الخارجية"))
        steps.append(make_step("f'(x) = e^{x^2} \\cdot 2x", "تطبيق قاعدة السلسلة"))
        steps.append(make_step("f'(x) = 2x e^{x^2}", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "2x e^{x^2}",
            "template": "32-3",
            "name": "مشتقة e^(x²)"
        }
    
    def template_32_chain_rule_4(self) -> Dict[str, Any]:
        """قالب 32-4: مشتقة ln(x²+1)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x) = \\ln(x^2 + 1)", "الدالة الأصلية"))
        steps.append(make_step("u = x^2 + 1", "الدالة الداخلية"))
        steps.append(make_step("\\frac{du}{dx} = 2x", "مشتقة u"))
        steps.append(make_step("\\frac{d}{du}[\\ln(u)] = \\frac{1}{u}", "مشتقة الدالة الخارجية"))
        steps.append(make_step("f'(x) = \\frac{1}{x^2+1} \\cdot 2x", "تطبيق قاعدة السلسلة"))
        steps.append(make_step("f'(x) = \\frac{2x}{x^2+1}", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{2x}{x^2+1}",
            "template": "32-4",
            "name": "مشتقة ln(x²+1)"
        }
    
    def template_32_chain_rule_5(self) -> Dict[str, Any]:
        """قالب 32-5: مشتقة sin(cos(x))"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x) = \\sin(\\cos(x))", "الدالة الأصلية"))
        steps.append(make_step("u = \\cos(x)", "الدالة الداخلية الأولى"))
        steps.append(make_step("\\frac{du}{dx} = -\\sin(x)", "مشتقة u"))
        steps.append(make_step("\\frac{d}{du}[\\sin(u)] = \\cos(u)", "مشتقة الدالة الخارجية"))
        steps.append(make_step("f'(x) = \\cos(\\cos(x)) \\cdot (-\\sin(x))", "تطبيق قاعدة السلسلة"))
        steps.append(make_step("f'(x) = -\\sin(x) \\cdot \\cos(\\cos(x))", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "-\\sin(x) \\cdot \\cos(\\cos(x))",
            "template": "32-5",
            "name": "مشتقة sin(cos(x))"
        }

    # =========================================================================
    # 33. مشتقات الضرب والقسمة (5 قوالب)
    # =========================================================================
    
    def template_33_product_quotient_1(self) -> Dict[str, Any]:
        """قالب 33-1: مشتقة x·sin(x) (قاعدة الضرب)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "f(x) = x \\cdot \\sin(x)",
            "الدالة الأصلية (حاصل ضرب دالتين)"
        ))
        
        steps.append(make_step(
            "\\text{نفرض } u = x \\text{، } v = \\sin(x)",
            "نحدد الدالتين"
        ))
        
        steps.append(make_step(
            "u' = 1, \\quad v' = \\cos(x)",
            "مشتقة كل دالة"
        ))
        
        steps.append(make_step(
            "\\frac{d}{dx}[u \\cdot v] = u' \\cdot v + u \\cdot v'",
            "قاعدة مشتقة الضرب"
        ))
        
        steps.append(make_step(
            "f'(x) = 1 \\cdot \\sin(x) + x \\cdot \\cos(x)",
            "نعوض"
        ))
        
        steps.append(make_step(
            "f'(x) = \\sin(x) + x\\cos(x)",
            "النتيجة النهائية"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\sin(x) + x\\cos(x)",
            "template": "33-1",
            "name": "مشتقة x·sin(x)"
        }
    
    def template_33_product_quotient_2(self) -> Dict[str, Any]:
        """قالب 33-2: مشتقة x²·cos(x)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x) = x^2 \\cdot \\cos(x)", "الدالة الأصلية"))
        steps.append(make_step("u = x^2, \\; v = \\cos(x)", "نحدد الدالتين"))
        steps.append(make_step("u' = 2x, \\; v' = -\\sin(x)", "مشتقة كل دالة"))
        steps.append(make_step("f'(x) = u'v + uv' = 2x \\cdot \\cos(x) + x^2 \\cdot (-\\sin(x))", "تطبيق قاعدة الضرب"))
        steps.append(make_step("f'(x) = 2x\\cos(x) - x^2\\sin(x)", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "2x\\cos(x) - x^2\\sin(x)",
            "template": "33-2",
            "name": "مشتقة x²·cos(x)"
        }
    
    def template_33_product_quotient_3(self) -> Dict[str, Any]:
        """قالب 33-3: مشتقة sin(x)/x (قاعدة القسمة)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x) = \\frac{\\sin(x)}{x}", "الدالة الأصلية (ناتج قسمة)"))
        steps.append(make_step("u = \\sin(x), \\; v = x", "نحدد البسط والمقام"))
        steps.append(make_step("u' = \\cos(x), \\; v' = 1", "مشتقة البسط والمقام"))
        steps.append(make_step("\\frac{d}{dx}\\left[\\frac{u}{v}\\right] = \\frac{u'v - uv'}{v^2}", "قاعدة مشتقة القسمة"))
        steps.append(make_step("f'(x) = \\frac{\\cos(x) \\cdot x - \\sin(x) \\cdot 1}{x^2}", "نعوض"))
        steps.append(make_step("f'(x) = \\frac{x\\cos(x) - \\sin(x)}{x^2}", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{x\\cos(x) - \\sin(x)}{x^2}",
            "template": "33-3",
            "name": "مشتقة sin(x)/x"
        }
    
    def template_33_product_quotient_4(self) -> Dict[str, Any]:
        """قالب 33-4: مشتقة tan(x) باستخدام قاعدة القسمة"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x) = \\tan(x) = \\frac{\\sin(x)}{\\cos(x)}", "نكتب tan(x) على صورة كسر"))
        steps.append(make_step("u = \\sin(x), \\; v = \\cos(x)", "نحدد البسط والمقام"))
        steps.append(make_step("u' = \\cos(x), \\; v' = -\\sin(x)", "مشتقة البسط والمقام"))
        steps.append(make_step("f'(x) = \\frac{u'v - uv'}{v^2} = \\frac{\\cos(x)\\cos(x) - \\sin(x)(-\\sin(x))}{\\cos^2(x)}", "تطبيق قاعدة القسمة"))
        steps.append(make_step("f'(x) = \\frac{\\cos^2(x) + \\sin^2(x)}{\\cos^2(x)}", "نبسط"))
        steps.append(make_step("f'(x) = \\frac{1}{\\cos^2(x)} = \\sec^2(x)", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\sec^2(x)",
            "template": "33-4",
            "name": "مشتقة tan(x) (طريقة القسمة)"
        }
    
    def template_33_product_quotient_5(self) -> Dict[str, Any]:
        """قالب 33-5: مشتقة (x²+1)/(x-1)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x) = \\frac{x^2+1}{x-1}", "الدالة الأصلية"))
        steps.append(make_step("u = x^2+1, \\; v = x-1", "نحدد البسط والمقام"))
        steps.append(make_step("u' = 2x, \\; v' = 1", "مشتقة البسط والمقام"))
        steps.append(make_step("f'(x) = \\frac{(2x)(x-1) - (x^2+1)(1)}{(x-1)^2}", "تطبيق قاعدة القسمة"))
        steps.append(make_step("f'(x) = \\frac{2x^2 - 2x - x^2 - 1}{(x-1)^2}", "نبسط البسط"))
        steps.append(make_step("f'(x) = \\frac{x^2 - 2x - 1}{(x-1)^2}", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{x^2 - 2x - 1}{(x-1)^2}",
            "template": "33-5",
            "name": "مشتقة (x²+1)/(x-1)"
        }

    # =========================================================================
    # 34. مشتقات الدوال المثلثية المعكوسة (5 قوالب)
    # =========================================================================
    
    def template_34_inverse_trig_1(self) -> Dict[str, Any]:
        """قالب 34-1: مشتقة arcsin(x)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "f(x) = \\arcsin(x)",
            "الدالة الأصلية (قوس الجيب)"
        ))
        
        steps.append(make_step(
            "\\frac{d}{dx}[\\arcsin(x)] = \\frac{1}{\\sqrt{1-x^2}}",
            "قاعدة مشتقة arcsin(x)"
        ))
        
        steps.append(make_step(
            "f'(x) = \\frac{1}{\\sqrt{1-x^2}}",
            "النتيجة"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{1}{\\sqrt{1-x^2}}",
            "template": "34-1",
            "name": "مشتقة arcsin(x)"
        }
    
    def template_34_inverse_trig_2(self) -> Dict[str, Any]:
        """قالب 34-2: مشتقة arccos(x)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x) = \\arccos(x)", "الدالة الأصلية"))
        steps.append(make_step("\\frac{d}{dx}[\\arccos(x)] = -\\frac{1}{\\sqrt{1-x^2}}", "قاعدة مشتقة arccos(x)"))
        steps.append(make_step("f'(x) = -\\frac{1}{\\sqrt{1-x^2}}", "النتيجة"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "-\\frac{1}{\\sqrt{1-x^2}}",
            "template": "34-2",
            "name": "مشتقة arccos(x)"
        }
    
    def template_34_inverse_trig_3(self) -> Dict[str, Any]:
        """قالب 34-3: مشتقة arctan(x)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x) = \\arctan(x)", "الدالة الأصلية"))
        steps.append(make_step("\\frac{d}{dx}[\\arctan(x)] = \\frac{1}{1+x^2}", "قاعدة مشتقة arctan(x)"))
        steps.append(make_step("f'(x) = \\frac{1}{1+x^2}", "النتيجة"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{1}{1+x^2}",
            "template": "34-3",
            "name": "مشتقة arctan(x)"
        }
    
    def template_34_inverse_trig_4(self) -> Dict[str, Any]:
        """قالب 34-4: مشتقة arcsec(x)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x) = \\arcsec(x)", "الدالة الأصلية"))
        steps.append(make_step("\\frac{d}{dx}[\\arcsec(x)] = \\frac{1}{|x|\\sqrt{x^2-1}}", "قاعدة مشتقة arcsec(x)"))
        steps.append(make_step("f'(x) = \\frac{1}{x\\sqrt{x^2-1}} \\text{ for } x>1", "النتيجة"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{1}{x\\sqrt{x^2-1}}",
            "template": "34-4",
            "name": "مشتقة arcsec(x)"
        }
    
    def template_34_inverse_trig_5(self) -> Dict[str, Any]:
        """قالب 34-5: مشتقة arccot(x)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x) = \\arccot(x)", "الدالة الأصلية"))
        steps.append(make_step("\\frac{d}{dx}[\\arccot(x)] = -\\frac{1}{1+x^2}", "قاعدة مشتقة arccot(x)"))
        steps.append(make_step("f'(x) = -\\frac{1}{1+x^2}", "النتيجة"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "-\\frac{1}{1+x^2}",
            "template": "34-5",
            "name": "مشتقة arccot(x)"
        }

    # =========================================================================
    # 35. مشتقات اللوغاريتمية (5 قوالب)
    # =========================================================================
    
    def template_35_log_derivative_1(self) -> Dict[str, Any]:
        """قالب 35-1: مشتقة ln(x)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "f(x) = \\ln(x)",
            "الدالة الأصلية (اللوغاريتم الطبيعي)"
        ))
        
        steps.append(make_step(
            "\\frac{d}{dx}[\\ln(x)] = \\frac{1}{x}",
            "قاعدة مشتقة اللوغاريتم الطبيعي"
        ))
        
        steps.append(make_step(
            "f'(x) = \\frac{1}{x}",
            "النتيجة"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{1}{x}",
            "template": "35-1",
            "name": "مشتقة ln(x)"
        }
    
    def template_35_log_derivative_2(self) -> Dict[str, Any]:
        """قالب 35-2: مشتقة log_a(x) (أساس a)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x) = \\log_a(x)", "الدالة الأصلية (لوغاريتم للأساس a)"))
        steps.append(make_step("\\log_a(x) = \\frac{\\ln(x)}{\\ln(a)}", "نغير الأساس للوغاريتم الطبيعي"))
        steps.append(make_step("\\frac{d}{dx}[\\ln(x)] = \\frac{1}{x}", "مشتقة ln(x)"))
        steps.append(make_step("f'(x) = \\frac{1}{\\ln(a)} \\cdot \\frac{1}{x}", "نطبق المشتقة"))
        steps.append(make_step("f'(x) = \\frac{1}{x\\ln(a)}", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{1}{x\\ln(a)}",
            "template": "35-2",
            "name": "مشتقة log_a(x)"
        }
    
    def template_35_log_derivative_3(self) -> Dict[str, Any]:
        """قالب 35-3: مشتقة ln(x²+1)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x) = \\ln(x^2+1)", "الدالة الأصلية"))
        steps.append(make_step("u = x^2+1", "نستخدم قاعدة السلسلة"))
        steps.append(make_step("\\frac{du}{dx} = 2x", "مشتقة الدالة الداخلية"))
        steps.append(make_step("\\frac{d}{du}[\\ln(u)] = \\frac{1}{u}", "مشتقة الدالة الخارجية"))
        steps.append(make_step("f'(x) = \\frac{1}{x^2+1} \\cdot 2x", "تطبيق قاعدة السلسلة"))
        steps.append(make_step("f'(x) = \\frac{2x}{x^2+1}", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{2x}{x^2+1}",
            "template": "35-3",
            "name": "مشتقة ln(x²+1)"
        }
    
    def template_35_log_derivative_4(self) -> Dict[str, Any]:
        """قالب 35-4: مشتقة ln(sin(x))"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x) = \\ln(\\sin(x))", "الدالة الأصلية"))
        steps.append(make_step("u = \\sin(x)", "الدالة الداخلية"))
        steps.append(make_step("\\frac{du}{dx} = \\cos(x)", "مشتقة u"))
        steps.append(make_step("\\frac{d}{du}[\\ln(u)] = \\frac{1}{u}", "مشتقة الدالة الخارجية"))
        steps.append(make_step("f'(x) = \\frac{1}{\\sin(x)} \\cdot \\cos(x)", "تطبيق قاعدة السلسلة"))
        steps.append(make_step("f'(x) = \\cot(x)", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\cot(x)",
            "template": "35-4",
            "name": "مشتقة ln(sin(x))"
        }
    
    def template_35_log_derivative_5(self) -> Dict[str, Any]:
        """قالب 35-5: مشتقة ln(√(x²+1))"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x) = \\ln(\\sqrt{x^2+1})", "الدالة الأصلية"))
        steps.append(make_step("\\ln(\\sqrt{x^2+1}) = \\frac{1}{2}\\ln(x^2+1)", "نبسط باستخدام خصائص اللوغاريتمات"))
        steps.append(make_step("f(x) = \\frac{1}{2}\\ln(x^2+1)", "بعد التبسيط"))
        steps.append(make_step("f'(x) = \\frac{1}{2} \\cdot \\frac{2x}{x^2+1}", "مشتقة ln(x²+1) كما في القالب السابق"))
        steps.append(make_step("f'(x) = \\frac{x}{x^2+1}", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "\\frac{x}{x^2+1}",
            "template": "35-5",
            "name": "مشتقة ln(√(x²+1))"
        }

    # =========================================================================
    # 36. مشتقات الدوال الأسية (5 قوالب)
    # =========================================================================
    
    def template_36_exp_derivative_1(self) -> Dict[str, Any]:
        """قالب 36-1: مشتقة e^x"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "f(x) = e^x",
            "الدالة الأصلية"
        ))
        
        steps.append(make_step(
            "\\frac{d}{dx}[e^x] = e^x",
            "قاعدة مشتقة الدالة الأسية"
        ))
        
        steps.append(make_step(
            "f'(x) = e^x",
            "النتيجة"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "e^x",
            "template": "36-1",
            "name": "مشتقة e^x"
        }
    
    def template_36_exp_derivative_2(self) -> Dict[str, Any]:
        """قالب 36-2: مشتقة a^x"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x) = a^x", "الدالة الأصلية"))
        steps.append(make_step("\\frac{d}{dx}[a^x] = a^x \\ln(a)", "قاعدة مشتقة الدالة الأسية للأساس a"))
        steps.append(make_step("f'(x) = a^x \\ln(a)", "النتيجة"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "a^x \\ln(a)",
            "template": "36-2",
            "name": "مشتقة a^x"
        }
    
    def template_36_exp_derivative_3(self) -> Dict[str, Any]:
        """قالب 36-3: مشتقة e^(2x)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x) = e^{2x}", "الدالة الأصلية"))
        steps.append(make_step("u = 2x", "نستخدم قاعدة السلسلة"))
        steps.append(make_step("\\frac{du}{dx} = 2", "مشتقة الدالة الداخلية"))
        steps.append(make_step("\\frac{d}{du}[e^u] = e^u", "مشتقة الدالة الخارجية"))
        steps.append(make_step("f'(x) = e^{2x} \\cdot 2", "تطبيق قاعدة السلسلة"))
        steps.append(make_step("f'(x) = 2e^{2x}", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "2e^{2x}",
            "template": "36-3",
            "name": "مشتقة e^(2x)"
        }
    
    def template_36_exp_derivative_4(self) -> Dict[str, Any]:
        """قالب 36-4: مشتقة e^(sin(x))"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x) = e^{\\sin(x)}", "الدالة الأصلية"))
        steps.append(make_step("u = \\sin(x)", "الدالة الداخلية"))
        steps.append(make_step("\\frac{du}{dx} = \\cos(x)", "مشتقة u"))
        steps.append(make_step("\\frac{d}{du}[e^u] = e^u", "مشتقة الدالة الخارجية"))
        steps.append(make_step("f'(x) = e^{\\sin(x)} \\cdot \\cos(x)", "تطبيق قاعدة السلسلة"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "e^{\\sin(x)} \\cos(x)",
            "template": "36-4",
            "name": "مشتقة e^(sin(x))"
        }
    
    def template_36_exp_derivative_5(self) -> Dict[str, Any]:
        """قالب 36-5: مشتقة 2^(3x)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x) = 2^{3x}", "الدالة الأصلية"))
        steps.append(make_step("2^{3x} = e^{3x\\ln(2)}", "نحول للأساس e"))
        steps.append(make_step("u = 3x\\ln(2)", "نستخدم قاعدة السلسلة"))
        steps.append(make_step("\\frac{du}{dx} = 3\\ln(2)", "مشتقة u"))
        steps.append(make_step("\\frac{d}{du}[e^u] = e^u", "مشتقة الدالة الخارجية"))
        steps.append(make_step("f'(x) = e^{3x\\ln(2)} \\cdot 3\\ln(2)", "تطبيق قاعدة السلسلة"))
        steps.append(make_step("f'(x) = 2^{3x} \\cdot 3\\ln(2)", "النتيجة النهائية"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "2^{3x} \\cdot 3\\ln(2)",
            "template": "36-5",
            "name": "مشتقة 2^(3x)"
        }

    # =========================================================================
    # 37. مشتقات متقدمة متعددة المتغيرات (5 قوالب)
    # =========================================================================
    
    def template_37_multivariable_1(self) -> Dict[str, Any]:
        """قالب 37-1: مشتقة جزئية ∂/∂x لـ x² + y²"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step(
            "f(x, y) = x^2 + y^2",
            "الدالة بمتغيرين"
        ))
        
        steps.append(make_step(
            "\\frac{\\partial}{\\partial x}[x^2 + y^2]",
            "نشتق بالنسبة لـ x (نعتبر y ثابت)"
        ))
        
        steps.append(make_step(
            "\\frac{\\partial}{\\partial x}[x^2] = 2x",
            "مشتقة x²"
        ))
        
        steps.append(make_step(
            "\\frac{\\partial}{\\partial x}[y^2] = 0",
            "مشتقة y² (y ثابت)"
        ))
        
        steps.append(make_step(
            "\\frac{\\partial f}{\\partial x} = 2x",
            "النتيجة النهائية"
        ))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "2x",
            "template": "37-1",
            "name": "∂/∂x لـ x²+y²"
        }
    
    def template_37_multivariable_2(self) -> Dict[str, Any]:
        """قالب 37-2: مشتقة جزئية ∂/∂y لـ x² + y²"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x, y) = x^2 + y^2", "الدالة بمتغيرين"))
        steps.append(make_step("\\frac{\\partial}{\\partial y}[x^2 + y^2]", "نشتق بالنسبة لـ y"))
        steps.append(make_step("\\frac{\\partial}{\\partial y}[x^2] = 0", "x ثابت"))
        steps.append(make_step("\\frac{\\partial}{\\partial y}[y^2] = 2y", "مشتقة y²"))
        steps.append(make_step("\\frac{\\partial f}{\\partial y} = 2y", "النتيجة"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "2y",
            "template": "37-2",
            "name": "∂/∂y لـ x²+y²"
        }
    
    def template_37_multivariable_3(self) -> Dict[str, Any]:
        """قالب 37-3: مشتقة جزئية ∂/∂x لـ sin(xy)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x, y) = \\sin(xy)", "الدالة بمتغيرين"))
        steps.append(make_step("\\frac{\\partial}{\\partial x}[\\sin(xy)]", "نشتق بالنسبة لـ x"))
        steps.append(make_step("u = xy", "نستخدم قاعدة السلسلة"))
        steps.append(make_step("\\frac{du}{dx} = y", "مشتقة u بالنسبة لـ x"))
        steps.append(make_step("\\frac{d}{du}[\\sin(u)] = \\cos(u)", "مشتقة الدالة الخارجية"))
        steps.append(make_step("\\frac{\\partial f}{\\partial x} = \\cos(xy) \\cdot y", "تطبيق قاعدة السلسلة"))
        steps.append(make_step("\\frac{\\partial f}{\\partial x} = y\\cos(xy)", "النتيجة"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "y\\cos(xy)",
            "template": "37-3",
            "name": "∂/∂x لـ sin(xy)"
        }
    
    def template_37_multivariable_4(self) -> Dict[str, Any]:
        """قالب 37-4: مشتقة جزئية ∂/∂y لـ sin(xy)"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x, y) = \\sin(xy)", "الدالة بمتغيرين"))
        steps.append(make_step("\\frac{\\partial}{\\partial y}[\\sin(xy)]", "نشتق بالنسبة لـ y"))
        steps.append(make_step("u = xy", "نستخدم قاعدة السلسلة"))
        steps.append(make_step("\\frac{du}{dy} = x", "مشتقة u بالنسبة لـ y"))
        steps.append(make_step("\\frac{d}{du}[\\sin(u)] = \\cos(u)", "مشتقة الدالة الخارجية"))
        steps.append(make_step("\\frac{\\partial f}{\\partial y} = \\cos(xy) \\cdot x", "تطبيق قاعدة السلسلة"))
        steps.append(make_step("\\frac{\\partial f}{\\partial y} = x\\cos(xy)", "النتيجة"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "x\\cos(xy)",
            "template": "37-4",
            "name": "∂/∂y لـ sin(xy)"
        }
    
    def template_37_multivariable_5(self) -> Dict[str, Any]:
        """قالب 37-5: مشتقة جزئية ثانية ∂²/∂x² لـ x²y + y³"""
        self.stats['total_calls'] += 1
        steps = []
        
        steps.append(make_step("f(x, y) = x^2 y + y^3", "الدالة بمتغيرين"))
        steps.append(make_step("\\frac{\\partial f}{\\partial x} = 2xy", "المشتقة الأولى بالنسبة لـ x"))
        steps.append(make_step("\\frac{\\partial^2 f}{\\partial x^2} = 2y", "المشتقة الثانية بالنسبة لـ x"))
        
        self.stats['successful'] += 1
        return {
            "steps": steps,
            "answer": "2y",
            "template": "37-5",
            "name": "∂²/∂x² لـ x²y + y³"
        }

    # =========================================================================
    # دوال مساعدة وإحصائيات
    # =========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """إحصائيات استخدام القوالب"""
        return self.stats
