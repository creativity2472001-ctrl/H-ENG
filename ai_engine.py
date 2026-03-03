# ai/engine.py
from config import GROQ_API_KEY, GEMINI_API_KEY, OPENROUTER_API_KEY

class AIEngine:
    def __init__(self):
        self.groq_key = GROQ_API_KEY
        self.gemini_key = GEMINI_API_KEY
        self.openrouter_key = OPENROUTER_API_KEY
        
        if not self.groq_key:
            print("⚠️ Groq API key غير موجودة - لن تعمل خدمة Groq")
        if not self.gemini_key:
            print("⚠️ Gemini API key غير موجودة - لن تعمل خدمة Gemini")
        if not self.openrouter_key:
            print("⚠️ OpenRouter API key غير موجودة - لن تعمل خدمة OpenRouter")
