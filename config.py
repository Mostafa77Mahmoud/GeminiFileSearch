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
    
    # المرحلة الأولى: Prompt لاستخراج البنود المهمة من العقد
    # ملاحظة: Keywords باللغة العربية لتطابق embeddings AAOIFI (المستند عربي)
    EXTRACT_KEY_TERMS_PROMPT = os.getenv(
        "EXTRACT_KEY_TERMS_PROMPT",
        """أنت خبير شرعي في تحليل العقود وفق معايير AAOIFI الشرعية. لديك نص عقد مقاولة (استصناع) كامل، ومهمتك استخراج البنود الرئيسية التي قد تكون ذات صلة شرعية، مثل تلك المتعلقة بالشروط، الجزاءات، الرفض، الدفعات، التحكيم، أو أي بند يحتمل مخالفة شرعية (مثل الغرر، الربا، الظلم، عدم الوضوح).

الخطوات:
1. اقرأ العقد كاملاً وحدد البنود المهمة فقط (تجنب البنود الروتينية مثل الأطراف أو التعريفات إلا إذا كانت ذات صلة شرعية).
2. لكل بند مهم، حدد:
   - term_id: معرف فريد مثل "clause_9" أو "penalty_section".
   - term_text: النص الكامل للبند.
   - potential_issues: قائمة بكلمات مفتاحية شرعية **باللغة العربية** (مثل "الغرر" للجهالة، "الربا" للفائدة، "التعويض" للتعويض، "الظلم" للظلم، "الاستصناع" للاستصناع، "الجهالة" للغموض، "الشروط" للشروط، "التحكيم" للتحكيم، "الإكراه" للإجبار، "الضرر" للضرر). اختر مصطلحات عربية دقيقة من معايير AAOIFI لتحسين الصلة الدلالية مع المستندات المرجعية العربية.
   - relevance_reason: شرح مختصر لماذا هذا البند مهم شرعياً (مثل "قد يحتوي على غرر بسبب عدم إبداء أسباب الرفض").

ركز على 5-15 بنداً رئيسياً فقط لتجنب الإفراط. أخرج النتيجة كقائمة JSON فقط، بدون مقدمة أو شرح إضافي، بهذا الهيكل:
[
  {{
    "term_id": "clause_example",
    "term_text": "نص البند هنا",
    "potential_issues": ["الغرر", "الربا", "التعويض"],
    "relevance_reason": "شرح مختصر"
  }}
]

نص العقد:
{contract_text}"""
    )
    
    # المرحلة الثانية: Prompt محسّن لـ File Search باستخدام البنود المستخرجة
    # ملاحظة: Keywords بالعربية لتطابق أفضل مع Embeddings AAOIFI
    FILE_SEARCH_PROMPT = os.getenv(
        "FILE_SEARCH_PROMPT",
        """يجب عليك استخدام File Search للبحث في المستندات المرجعية (معايير هيئة AAOIFI الشرعية، المخزنة في الـ store) عن chunks ذات صلة دلالية عالية جداً بالبنود الرئيسية المستخرجة من العقد التالي. ركز على الصلة الدلالية مع المصطلحات الشرعية العربية مثل الغرر، الربا، التعويض، الاستصناع، الظلم، الجهالة، الشروط، التحكيم، الإكراه، الضرر.

البنود المستخرجة من العقد (استخدم كل بند كاستعلام فرعي لاسترجاع chunks محددة ودقيقة):
{extracted_clauses}

قم بالبحث عن:
1. الأحكام والمعايير الشرعية المتعلقة بكل بند (مثل معيار 11 للاستصناع، معيار 9 للربا).
2. الشروط والضوابط الشرعية الدقيقة، مع أمثلة على المخالفات (مثل الغرر في الرفض غير المبرر أو الجهالة في الأسعار).
3. الحالات المشابهة أو الأمثلة من AAOIFI على مشاكل مشابهة.
4. الأحكام الخاصة بالجزاءات أو التعويضات (مثل التعويض عن ضرر فعلي فقط، مع استثناء قوة القاهرة).
5. أي معلومات أخرى ذات صلة، مثل تحريم الربا في التحكيم أو الشروط الجائرة.

يجب أن تكون الإجابة مبنية على المستندات المرفقة في الـ store، مع اقتباس chunks دقيقة وكاملة للتحليل الشرعي الموثوق."""
    )
    
    # Chunk Schema Configuration (هيكل البيانات المُرجعة من File Search)
    CHUNK_SCHEMA = {
        "description": "قائمة بالـ chunks المسترجعة من File Search",
        "fields": {
            "uid": "معرّف فريد للـ chunk",
            "chunk_text": "نص الـ chunk الأصلي من المستند",
            "score": "درجة الصلة (0.0 - 1.0)",
            "uri": "مصدر الملف (URI)",
            "title": "عنوان الملف أو القسم"
        }
    }
    
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
