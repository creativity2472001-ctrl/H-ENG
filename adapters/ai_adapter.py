# adapters/ai_adapter.py
from ai_engine import AIEngine as OldAIEngine
import asyncio

class AIAdapter:
    """يربط بين main.py الجديد و ai_engine.py القديم"""
    
    def __init__(self):
        self.engine = OldAIEngine()
        self.ready = False
    
    async def start(self):
        await self.engine.start()
        self.ready = True
        print("✅ AI Engine ready (via adapter)")
    
    async def stop(self):
        await self.engine.stop()
        self.ready = False
        print("🛑 AI Engine stopped")
    
    async def generate_code(self, question: str, domain: str = "general"):
        if not self.ready:
            return {"success": False, "error": "AI Engine not ready"}
        
        return await self.engine.generate_code(question, domain)
