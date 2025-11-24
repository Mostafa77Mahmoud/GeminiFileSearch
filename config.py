import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """إعدادات المشروع"""
    
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")
    
    # File Search Store Configuration
    FILE_SEARCH_STORE_ID = os.getenv("FILE_SEARCH_STORE_ID", "")
    CONTEXT_DIR = "context"
    
    # Search Configuration
    TOP_K_CHUNKS = int(os.getenv("TOP_K_CHUNKS", "20"))
    
    # File Search Prompt Template
    FILE_SEARCH_PROMPT = os.getenv(
        "FILE_SEARCH_PROMPT",
        """يجب عليك البحث في المستندات المرجعية (معايير هيئة AAOIFI الشرعية) عن معلومات متعلقة بالنص التالي.

استخدم File Search للبحث في المستندات المرفقة واستخرج جميع المقاطع (chunks) ذات الصلة.

النص المطلوب تحليله:
{contract_text}

قم بالبحث في المستندات المرجعية عن:
1. الأحكام والمعايير الشرعية المتعلقة بهذا النوع من العقود
2. الشروط والضوابط الشرعية
3. الحالات المشابهة أو الأمثلة
4. الأحكام الخاصة بالمخالفات أو الجزاءات
5. أي معلومات أخرى ذات صلة من معايير AAOIFI

يجب استخدام المستندات المرفقة في الإجابة."""
    )
    
    # Flask Configuration
    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = int(os.getenv("FLASK_PORT", "5001"))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"

    @classmethod
    def validate(cls):
        """التحقق من صحة الإعدادات الأساسية"""
        errors = []
        
        if not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY is required")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True
