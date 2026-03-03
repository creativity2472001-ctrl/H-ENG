# adapters/math_adapter.py
from math_engine import MathEngine as OldMathEngine
import asyncio

class MathAdapter:
    """يربط بين main.py الجديد و math_engine.py القديم"""
    
    def __init__(self):
        self.engine = OldMathEngine()
        self.ready = True
    
    async def execute(self, code: str, use_ai_assist: bool = True):
        return await self.engine.execute(code, use_ai_assist)
    
    async def shutdown(self):
        await self.engine.shutdown()
        print("🛑 Math Engine stopped")
