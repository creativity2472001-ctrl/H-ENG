# server_enhanced.py - نسخة محسنة تستخدم القوالب بالكامل
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from pathlib import Path
import re
import math
import logging
from typing import Optional, Dict, Any, List

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# استيراد الحاسبة والقالب
from calculator import Calculator
from algebra_part1 import CompleteAlgebraSolver

# تهيئة التطبيق
app = FastAPI(title="الآلة الحاسبة المتكاملة", version="4.0.0")

# إعداد CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# إنشاء الكائنات
calc = Calculator()
solver = CompleteAlgebraSolver()

# إعداد المجلد الثابت
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

class ExpressionRequest(BaseModel):
    expression: str

def format_number(num) -> str:
    """تنسيق الأعداد للعرض"""
    try:
        if isinstance(num, float):
            if num.is_integer():
                return str(int(num))
            return f"{num:.2f}".rstrip('0').rstrip('.')
        return str(num)
    except:
        return str(num)

def detect_equation_type(equation: str) -> Dict[str, Any]:
    """تحديد نوع المعادلة واستخراج المعاملات"""
    equation = equation.replace(' ', '').replace('=', '=')
    
    if '=' not in equation:
        return {'type': 'expression'}
    
    left, right = equation.split('=')
    
    # معادلة تربيعية
    if 'x^2' in left or 'x²' in left or 'x**2' in left:
        # استخراج المعاملات
        a = b = c = 0
        try:
            # تنظيف الطرف الأيسر
            left_clean = left.replace('²', '^2').replace('x^2', 'x2')
            
            # استخراج a (معامل x²)
            import re
            a_match = re.search(r'([+-]?\d*\.?\d*)\*?x2', left_clean)
            if a_match:
                a_str = a_match.group(1)
                a = 1.0 if a_str in ['', '+'] else -1.0 if a_str == '-' else float(a_str)
            
            # استخراج b (معامل x)
            b_match = re.search(r'([+-]?\d*\.?\d*)\*?x(?!2)', left_clean)
            if b_match:
                b_str = b_match.group(1)
                b = 1.0 if b_str in ['', '+'] else -1.0 if b_str == '-' else float(b_str)
            
            # استخراج c (ثابت)
            c_val = float(right)
            
            # تعديل الإشارات حسب المعادلة
            if f"{b}x" in left_clean and '-' in left_clean.split(f"{b}x")[1][:1]:
                c = -c_val
            else:
                c = c_val
                
        except:
            pass
        
        return {
            'type': 'quadratic',
            'a': a,
            'b': b,
            'c': c,
            'equation': equation
        }
    
    # معادلة خطية
    elif 'x' in left:
        return {'type': 'linear', 'equation': equation}
    
    return {'type': 'unknown', 'equation': equation}

@app.post("/calculate")
async def calculate(data: ExpressionRequest):
    """نقطة النهاية المحسنة"""
    try:
        expr = data.expression.strip()
        logger.info(f"طلب: {expr}")
        
        # ===== 1. نظم المعادلات =====
        if expr.startswith('[') and expr.endswith(']') and ',' in expr:
            logger.info("معالجة نظام معادلات")
            # استخدام الدوال الموجودة في server.py الأصلي
            # (يمكن إضافة كود نظم المعادلات من النسخة الأصلية)
            return {"success": True, "result": "نظام المعادلات قيد التطوير"}
        
        # ===== 2. معادلات =====
        if '=' in expr:
            eq_info = detect_equation_type(expr)
            
            # معادلة تربيعية - استخدام القالب 1
            if eq_info['type'] == 'quadratic':
                a, b, c = eq_info['a'], eq_info['b'], eq_info['c']
                logger.info(f"معادلة تربيعية: a={a}, b={b}, c={c}")
                
                if a != 0:
                    result = solver.template_01_quadratic_standard(a, b, c)
                    if result and 'roots' in result:
                        roots = result['roots']['decimal']
                        if len(roots) == 2:
                            return {"success": True, "result": f"x = {format_number(roots[0])} أو x = {format_number(roots[1])}"}
                        elif len(roots) == 1:
                            return {"success": True, "result": f"x = {format_number(roots[0])}"}
            
            # معادلات أخرى - استخدام calculator
            calc_result = calc.solve_equation(expr)
            return {"success": True, "result": str(calc_result)}
        
        # ===== 3. عمليات حسابية =====
        result = calc.calculate(expr)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return {"success": True, "result": str(result)}
        
    except Exception as e:
        logger.error(f"خطأ: {e}")
        return {"success": False, "error": str(e)}

@app.get("/")
async def root():
    return FileResponse(str(static_dir / "index.html"))

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "4.0.0"}

if __name__ == "__main__":
    print("="*60)
    print("🚀 تشغيل الخادم المحسن - الإصدار 4.0.0")
    print("="*60)
    print(f"📍 http://127.0.0.1:8000")
    print("="*60)
    uvicorn.run(app, host="127.0.0.1", port=8000)
