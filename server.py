# server.py - طبقة API فقط (مقسم من الملف الأصلي)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from pathlib import Path
import logging

# استيراد المتحكم
from solver.solver_controller import (
    solve_calculate,
    solve_template,
    solve_system,
    search_templates,
    list_templates,
    get_stats
)

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="الآلة الحاسبة المتكاملة",
    description="نظام حلول رياضية متكامل بـ 152 قالباً",
    version="4.0.0"
)

# إعداد CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# إعداد المجلد الثابت
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

# ===== نماذج البيانات =====
class ExpressionRequest(BaseModel):
    expression: str

class TemplateRequest(BaseModel):
    template_id: int
    params: dict

class SystemRequest(BaseModel):
    eq1: str
    eq2: str
    eq3: str | None = None

class SearchQuery(BaseModel):
    keyword: str

# ===== نقاط النهاية =====
@app.post("/calculate")
async def calculate(data: ExpressionRequest):
    """نقطة النهاية الرئيسية"""
    return solve_calculate(data.expression)

@app.post("/algebra/template/{template_id}")
async def template(template_id: int, request: TemplateRequest):
    """حل قالب محدد"""
    return solve_template(template_id, request.params)

@app.post("/algebra/system")
async def system(request: SystemRequest):
    """حل نظم معادلات"""
    return solve_system(request.eq1, request.eq2, request.eq3)

@app.post("/algebra/search")
async def search(query: SearchQuery):
    """بحث عن قوالب"""
    return search_templates(query.keyword)

@app.get("/algebra/templates")
async def templates(category: str = None):
    """عرض القوالب"""
    return list_templates(category)

@app.get("/algebra/stats")
async def stats():
    """إحصائيات"""
    return get_stats()

@app.get("/")
async def root():
    return FileResponse(str(static_dir / "index.html"))

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "4.0.0",
        "templates": 152
    }

if __name__ == "__main__":
    print("="*70)
    print("🚀 تشغيل الخادم - الإصدار 4.0.0")
    print("="*70)
    uvicorn.run(app, host="127.0.0.1", port=8000)
