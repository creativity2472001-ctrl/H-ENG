# server.py - خادم الويب (معدل مع دعم القوالب الجديدة)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from pathlib import Path
import re
import math
import json

from calculator import Calculator

# ===== استيراد القوالب الجديدة =====
from algebra_part1 import CompleteAlgebraSolver
from algebra_part2 import IntermediateAlgebraSolver
from algebra_part3 import AdvancedAlgebraSolver

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

calc = Calculator()

# ===== إنشاء كائنات الحلولين الجدد =====
solver1 = CompleteAlgebraSolver()  # القوالب 1-52
solver2 = IntermediateAlgebraSolver()  # القوالب 53-102
solver3 = AdvancedAlgebraSolver()  # القوالب 103-152

static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

class ExpressionRequest(BaseModel):
    expression: str

class TemplateRequest(BaseModel):
    template_id: int
    params: dict

@app.post("/calculate")
async def calculate(data: ExpressionRequest):
    try:
        expr = data.expression.lower().strip()
        
        # ===== 1. التعامل مع الدوال المثلثية =====
        # sin(30)
        if 'sin' in expr and '(' in expr and ')' in expr:
            match = re.search(r'sin\((\d+)\)', expr)
            if match:
                angle = float(match.group(1))
                result = calc.sin(angle)
                return {"success": True, "result": str(result)}
        
        # cos(60)
        if 'cos' in expr and '(' in expr and ')' in expr:
            match = re.search(r'cos\((\d+)\)', expr)
            if match:
                angle = float(match.group(1))
                result = calc.cos(angle)
                return {"success": True, "result": str(result)}
        
        # tan(45)
        if 'tan' in expr and '(' in expr and ')' in expr:
            match = re.search(r'tan\((\d+)\)', expr)
            if match:
                angle = float(match.group(1))
                result = calc.tan(angle)
                return {"success": True, "result": str(result)}
        
        # ===== 2. التعامل مع ln =====
        if 'ln' in expr and '(' in expr and ')' in expr:
            match = re.search(r'ln\((\d+)\)', expr)
            if match:
                num = float(match.group(1))
                result = calc.ln(num)
                return {"success": True, "result": str(result)}
        
        # ===== 3. التعامل مع المعادلات البسيطة (تحتوي على =) =====
        if '=' in expr:
            result = calc.solve_equation(expr)
            return {"success": True, "result": str(result)}
        
        # ===== 4. العمليات الحسابية العادية =====
        result = calc.calculate(expr)
        return {"success": True, "result": str(result)}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== نقاط نهاية API جديدة للقوالب المتقدمة =====

@app.post("/algebra/template/{template_id}")
async def solve_template(template_id: int, request: TemplateRequest):
    """
    حل قالب رياضي محدد باستخدام المعاملات المعطاة
    """
    try:
        params = request.params
        result = None
        
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
            # ... يمكن إضافة باقي القوالب 11-52 بنفس النمط
        
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
            # ... يمكن إضافة باقي القوالب حتى 102
        
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
            # ... يمكن إضافة باقي القوالب حتى 152
        
        else:
            return {"success": False, "error": "قالب غير موجود"}
        
        if result:
            return {"success": True, "result": result}
        else:
            return {"success": False, "error": "فشل في تنفيذ القالب"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/algebra/search")
async def search_templates(query: dict):
    """
    البحث عن قوالب حسب النوع أو الكلمات المفتاحية
    """
    try:
        keyword = query.get('keyword', '').lower()
        results = []
        
        # البحث في القوالب 1-52
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
        return {"success": False, "error": str(e)}

@app.get("/")
async def root():
    return FileResponse(str(static_dir / "index.html"))

if __name__ == "__main__":
    print("="*60)
    print("🚀 تشغيل خادم الويب - النسخة المتكاملة")
    print("="*60)
    print(f"📍 http://127.0.0.1:8000")
    print(f"📊 القوالب المتاحة: 152 قالباً")
    print(f"📁 الأجزاء: part1 (1-52), part2 (53-102), part3 (103-152)")
    print("="*60)
    print("🔍 نقاط النهاية الجديدة:")
    print("   POST /algebra/template/{id} - حل قالب محدد")
    print("   POST /algebra/search - بحث عن قوالب")
    print("   GET  /algebra/templates - عرض القوالب")
    print("   GET  /algebra/stats - إحصائيات")
    print("="*60)
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
