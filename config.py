# config.py
import os

# مفاتيح API - تأتي من متغيرات البيئة فقط!
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# تحذير إذا كانت المفاتيح فارغة
if not GROQ_API_KEY:
    print("⚠️ تحذير: GROQ_API_KEY غير موجودة")

if not GEMINI_API_KEY:
    print("⚠️ تحذير: GEMINI_API_KEY غير موجودة")

if not OPENROUTER_API_KEY:
    print("⚠️ تحذير: OPENROUTER_API_KEY غير موجودة")

# باقي الإعدادات
MAX_CODE_LENGTH = 5000
CACHE_TTL = 3600
DEBUG_MODE = False
HOST = "127.0.0.1"
PORT = 8000
