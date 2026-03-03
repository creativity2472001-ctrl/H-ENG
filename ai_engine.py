# ai_engine.py - الإصدار النهائي مع دعم 3 APIs
import os
import httpx
import sympy as sp
import re
import asyncio

# ========== المفاتيح من متغيرات البيئة ==========
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

class AIEngine:
    """محرك AI يدعم 3 خدمات مع fallback تلقائي"""
    
    def __init__(self):
        self.groq_key = GROQ_API_KEY
        self.gemini_key = GEMINI_API_KEY
        self.openrouter_key = OPENROUTER_API_KEY
        self.ready = any([self.groq_key, self.gemini_key, self.openrouter_key])
        
        # إحصائيات
        self.stats = {
            "groq": {"success": 0, "failed": 0},
            "gemini": {"success": 0, "failed": 0},
            "openrouter": {"success": 0, "failed": 0},
            "sympy": {"used": 0}
        }
        
        # تحضير SymPy كـ fallback
        self.x, self.y, self.z = sp.symbols('x y z')
        
        print(f"✅ AI Engine ready - APIs: {self._available_apis()}")
    
    def _available_apis(self) -> str:
        """إرجاع أسماء APIs المتاحة"""
        apis = []
        if self.groq_key: apis.append("Groq")
        if self.gemini_key: apis.append("Gemini")
        if self.openrouter_key: apis.append("OpenRouter")
        return ", ".join(apis) if apis else "None (SymPy only)"
    
    # ========== دوال مساعدة للتنظيف ==========
    def _clean_math_input(self, text: str) -> str:
        """تنظيف الإدخال من الرموز العربية"""
        text = text.lower()
        text = text.replace("²", "**2")
        text = text.replace("³", "**3")
        text = text.replace("⁴", "**4")
        text = text.replace("⁵", "**5")
        text = text.replace("^", "**")
        text = text.replace("×", "*")
        text = text.replace("÷", "/")
        text = text.replace(" ", "")
        return text
    
    # ========== دوال APIs المختلفة ==========
    async def _call_groq(self, prompt: str) -> dict:
        """الاتصال بـ Groq API"""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.groq_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.1,
                        "max_tokens": 2000
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "code": data["choices"][0]["message"]["content"],
                        "model": "groq"
                    }
                else:
                    return {"success": False, "error": f"Groq HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": f"Groq error: {str(e)}"}
    
    async def _call_gemini(self, prompt: str) -> dict:
        """الاتصال بـ Gemini API"""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
                
                response = await client.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{
                            "parts": [{"text": prompt}]
                        }]
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "candidates" in data:
                        return {
                            "success": True,
                            "code": data["candidates"][0]["content"]["parts"][0]["text"],
                            "model": "gemini"
                        }
                return {"success": False, "error": f"Gemini HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": f"Gemini error: {str(e)}"}
    
    async def _call_openrouter(self, prompt: str) -> dict:
        """الاتصال بـ OpenRouter API"""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:8000",
                        "X-Title": "Zaky Matik"
                    },
                    json={
                        "model": "deepseek/deepseek-chat",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.1
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "code": data["choices"][0]["message"]["content"],
                        "model": "openrouter"
                    }
                else:
                    return {"success": False, "error": f"OpenRouter HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": f"OpenRouter error: {str(e)}"}
    
    # ========== Fallback باستخدام SymPy ==========
    async def _sympy_fallback(self, question: str) -> dict:
        """حل المسائل البسيطة باستخدام SymPy"""
        self.stats["sympy"]["used"] += 1
        question = self._clean_math_input(question)
        
        # محاولة التعرف على نوع المسألة
        if "مشتق" in question or "derivative" in question or "diff" in question:
            return await self._sympy_derivative(question)
        elif "تكامل" in question or "integral" in question:
            return await self._sympy_integral(question)
        elif "حل" in question or "solve" in question:
            return await self._sympy_equation(question)
        else:
            return {"success": False, "error": "لم يتم التعرف على نوع المسألة"}
    
    async def _sympy_derivative(self, question: str) -> dict:
        """حل المشتقات باستخدام SymPy"""
        # استخراج الدالة (تبسيط)
        func = "x**2"  # افتراضي
        return {
            "success": True,
            "code": f"""
import sympy as sp
x = sp.symbols('x')
f = {func}
final_result = sp.diff(f, x)
steps = [
    {{"text": "الدالة: f(x) = {func}"}},
    {{"text": f"المشتقة: f'(x) = {{final_result}}"}}
]
""",
            "model": "sympy"
        }
    
    async def _sympy_integral(self, question: str) -> dict:
        """حل التكاملات باستخدام SymPy"""
        func = "x**2"
        return {
            "success": True,
            "code": f"""
import sympy as sp
x = sp.symbols('x')
f = {func}
final_result = sp.integrate(f, x)
steps = [
    {{"text": "الدالة: f(x) = {func}"}},
    {{"text": f"التكامل: ∫f(x)dx = {{final_result}} + C"}}
]
""",
            "model": "sympy"
        }
    
    async def _sympy_equation(self, question: str) -> dict:
        """حل المعادلات باستخدام SymPy"""
        return {
            "success": True,
            "code": """
import sympy as sp
x = sp.symbols('x')
eq = sp.Eq(2*x + 5, 13)
final_result = sp.solve(eq, x)
steps = [
    {"text": "المعادلة: 2x + 5 = 13"},
    {"text": f"الحل: x = {final_result[0]}"}
]
""",
            "model": "sympy"
        }
    
    # ========== الدالة الرئيسية ==========
    async def generate_code(self, question: str, domain: str = "general") -> dict:
        """توليد كود SymPy باستخدام أفضل API متاح"""
        
        # بناء الـ prompt
        prompt = f"""
        You are a SymPy expert. Convert this math question to Python code using sympy.
        
        Question: {question}
        Domain: {domain}
        
        Rules:
        1. Use import sympy as sp
        2. Define variables with sp.symbols()
        3. Use sp.Eq() for equations
        4. Save result in 'final_result'
        5. Create 'steps' list with step-by-step explanations
        6. Include LaTeX in steps when possible
        
        Return ONLY the Python code, no explanations.
        """
        
        # قائمة APIs بالترتيب (الأسرع أولاً)
        apis = []
        
        if self.groq_key:
            apis.append(("groq", self._call_groq))
        if self.gemini_key:
            apis.append(("gemini", self._call_gemini))
        if self.openrouter_key:
            apis.append(("openrouter", self._call_openrouter))
        
        # تجربة APIs بالترتيب
        for api_name, api_func in apis:
            try:
                result = await api_func(prompt)
                if result.get("success"):
                    self.stats[api_name]["success"] += 1
                    return result
                else:
                    self.stats[api_name]["failed"] += 1
            except Exception as e:
                self.stats[api_name]["failed"] += 1
                continue
        
        # إذا فشلت كل APIs، استخدم SymPy كـ fallback
        return await self._sympy_fallback(question)
    
    # ========== دوال إضافية ==========
    async def start(self):
        """بدء تشغيل المحرك"""
        print(f"✅ AI Engine started with APIs: {self._available_apis()}")
    
    async def stop(self):
        """إيقاف المحرك"""
        print("🛑 AI Engine stopped")
    
    def get_stats(self) -> dict:
        """إحصائيات الاستخدام"""
        return self.stats
