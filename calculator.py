# calculator.py - آلة حاسبة علمية أساسية (النسخة الأولى)
import sympy as sp
import math

class Calculator:
    """آلة حاسبة علمية أساسية - العمليات البسيطة أولاً"""
    
    def __init__(self):
        self.x = sp.Symbol('x')
        self.last_result = None
    
    # ========== العمليات الحسابية الأساسية ==========
    
    def calculate(self, expression: str):
        """
        حساب أي تعبير رياضي بسيط
        يدعم: +, -, *, /, ^, جذر, دوال مثلثية, لوغاريتمات
        """
        try:
            # استبدال ^ بـ ** (لأن sympy يفهم **)
            expr_str = expression.replace('^', '**')
            
            # تحويل النص إلى تعبير رياضي
            expr = sp.sympify(expr_str)
            
            # تقييم التعبير
            result = expr.evalf()
            
            # تحويل إلى float إذا كان عدداً
            if result.is_number:
                self.last_result = float(result)
                return self.last_result
            else:
                return str(result)
                
        except Exception as e:
            return f"خطأ: {e}"
    
    # ========== دعم النتيجة الأخيرة ==========
    
    def get_last_result(self):
        """إرجاع النتيجة الأخيرة"""
        return self.last_result
    
    # ========== العمليات الإضافية (للتوسع لاحقاً) ==========
    # سنضيفها واحدة تلو الأخرى بعد التأكد من الأساسيات
