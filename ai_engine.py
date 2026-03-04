# ai_engine.py - إصدار الإطلاق السريع
import sympy as sp
import re
import hashlib
from typing import Dict, Any, Optional, Tuple, List

def clean_math_input(text: str) -> str:
    text = text.lower()
    text = text.replace("²", "**2").replace("³", "**3")
    text = text.replace("^", "**").replace("×", "*").replace("÷", "/")
    text = text.replace(" ", "")
    return text

class Memory:
    def __init__(self):
        self.cache = {}
    
    def _make_key(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()
    
    def get(self, text: str) -> Optional[Dict]:
        key = self._make_key(text)
        return self.cache.get(key)
    
    def set(self, text: str, value: Dict):
        key = self._make_key(text)
        self.cache[key] = value

class AIEngine:
    def __init__(self):
        self.math = sp
        self.memory = Memory()
        self.x, self.y, self.z = sp.symbols('x y z')
        print("✅ AI Engine ready - إصدار الإطلاق")
    
    async def generate_code(self, question: str) -> Dict[str, Any]:
        normalized = clean_math_input(question)
        
        # 1️⃣ بحث في الذاكرة
        cached = self.memory.get(normalized)
        if cached:
            return cached
        
        try:
            # 2️⃣ آلة حاسبة
            if all(c in "0123456789+-*/()." for c in normalized):
                result = sp.sympify(normalized).evalf()
                response = {
                    "success": True,
                    "result": str(result),
                    "steps": [("🔢", f"{normalized} = {result}")],
                    "model": "calculator"
                }
                self.memory.set(normalized, response)
                return response
            
            # 3️⃣ معادلة
            if "=" in normalized:
                left, right = normalized.split("=")
                expr = sp.sympify(left) - sp.sympify(right)
                var = list(expr.free_symbols)[0] if expr.free_symbols else self.x
                solutions = sp.solve(expr, var)
                sol_str = ' أو '.join([f"{var} = {s}" for s in solutions])
                response = {
                    "success": True,
                    "result": sol_str,
                    "steps": [("⚖️", f"{question} → {sol_str}")],
                    "model": "equation"
                }
                self.memory.set(normalized, response)
                return response
            
            # 4️⃣ مشتقة
            if "مشتق" in question:
                expr = normalized.replace("مشتقة", "").replace("مشتق", "")
                f = sp.sympify(expr)
                var = list(f.free_symbols)[0] if f.free_symbols else self.x
                result = sp.diff(f, var)
                response = {
                    "success": True,
                    "result": str(result),
                    "steps": [("📐", f"d/d{var}({expr}) = {result}")],
                    "model": "derivative"
                }
                self.memory.set(normalized, response)
                return response
            
            # 5️⃣ تكامل
            if "تكامل" in question:
                expr = normalized.replace("تكامل", "")
                f = sp.sympify(expr)
                var = list(f.free_symbols)[0] if f.free_symbols else self.x
                result = sp.integrate(f, var)
                response = {
                    "success": True,
                    "result": str(result) + " + C",
                    "steps": [("∫", f"∫{expr} d{var} = {result} + C")],
                    "model": "integral"
                }
                self.memory.set(normalized, response)
                return response
            
            return {"success": False, "error": "لم أفهم السؤال"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
