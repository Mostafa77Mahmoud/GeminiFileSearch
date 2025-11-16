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
    SEARCH_PROMPT = os.getenv(
        "SEARCH_PROMPT",
        "ابحث عن جميع المعلومات والمعايير الشرعية المرتبطة بالنص التالي من المستندات المرجعية"
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
