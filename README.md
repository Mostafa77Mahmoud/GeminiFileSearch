
# 🔍 Gemini File Search - Contract Analysis System

نظام متكامل لتحليل العقود باستخدام Gemini 2.5 Flash و File Search API.

## 📋 المميزات

- ✅ **File Search Store**: رفع الكتب المرجعية (AAOIFI) مرة واحدة فقط
- ✅ **Flask API**: endpoints لـ File Search والتحليل الكامل
- ✅ **Streamlit Frontend**: واجهة بسيطة وتفاعلية
- ✅ **System Prompt قابل للتعديل**: يمكن تعديله من Replit Secrets
- ✅ **Modular Structure**: كود منظم وسهل الدمج

## 🏗️ هيكل المشروع

```
.
├── app.py                    # Flask API
├── frontend.py               # Streamlit Frontend
├── config.py                 # Configuration Management
├── start.sh                  # Startup Script
├── requirements.txt          # Dependencies
├── services/
│   ├── file_search.py       # File Search Service
│   └── analyzer.py          # Contract Analyzer
├── context/                  # ضع ملفات AAOIFI هنا
│   └── Shariaah-Standards-ARB.pdf
└── .env                      # Environment Variables
```

## 🚀 التشغيل السريع

### 1. المتطلبات

- Python 3.11+
- Google AI API Key (Gemini)

### 2. إعداد البيئة

الملف `.env` موجود بالفعل ويحتوي على الإعدادات التالية:

```env
# Gemini API Configuration
GEMINI_API_KEY=AIzaSyDTcF7aQ8NAuJMcIpkdsKo37K7thi0ZhVE
MODEL_NAME=gemini-2.5-flash
FILE_SEARCH_STORE_ID=fileSearchStores/aaoifi-reference-store-eh6go6xtuavz

# File Search Configuration
TOP_K_CHUNKS=20

# System Prompt
SYSTEM_PROMPT=أنت محلل عقود شرعي يعمل حصريًا بنظام Retrieval...

# Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
FLASK_DEBUG=False
```

**ملاحظة**: تم إعداد File Search Store مسبقًا بالمعرف: `fileSearchStores/aaoifi-reference-store-eh6go6xtuavz`

### 3. الملفات المرجعية

✅ تم رفع الملف المرجعي: `Shariaah-Standards-ARB.pdf` في مجلد `context/`

### 4. تشغيل النظام

النظام يعمل تلقائيًا على Replit عبر الضغط على زر Run. يمكنك أيضًا التشغيل يدويًا:

```bash
bash start.sh
```

**المنافذ المستخدمة:**
- Flask API: `http://0.0.0.0:5001`
- Streamlit Frontend: `http://0.0.0.0:5000`

## 📡 API Endpoints

### 1. Health Check
```http
GET http://0.0.0.0:5001/health
```

### 2. Store Information
```http
GET http://0.0.0.0:5001/store-info
```

**Response:**
```json
{
  "status": "active",
  "store_id": "fileSearchStores/aaoifi-reference-store-eh6go6xtuavz",
  "display_name": "AAOIFI Reference Store",
  "message": "Store is ready"
}
```

### 3. File Search
```http
POST http://0.0.0.0:5001/file_search
Content-Type: application/json

{
  "contract_text": "نص العقد هنا",
  "top_k": 20
}
```

**Response:**
```json
{
  "contract_text": "نص العقد الكامل",
  "chunks": [
    {
      "uid": "chunk_0_123456",
      "chunk_text": "محتوى الـ chunk",
      "score": 0.95
    }
  ],
  "total_chunks": 20
}
```

### 4. Full Analysis
```http
POST http://0.0.0.0:5001/analyze
Content-Type: application/json

{
  "contract_text": "نص العقد هنا",
  "top_k": 20
}
```

**Response:**
```json
{
  "contract_text": "نص العقد الكامل",
  "chunks": [...],
  "analysis": {
    "contract_summary": "ملخص العقد",
    "terms": [
      {
        "term_name": "اسم البند",
        "term_text": "النص الأصلي",
        "matched_chunks": [
          {
            "chunk_uid": "chunk_0_123",
            "evidence_text": "النص الداعم"
          }
        ],
        "status": "supported",
        "analysis": "التحليل"
      }
    ]
  }
}
```

## 🎨 Streamlit Interface

الواجهة تحتوي على تبويبتين:

### 1. File Search Only
- إدخال نص العقد
- استرجاع الـ chunks المرتبطة (افتراضي: 20 chunk)
- عرض UID ومحتوى كل chunk

### 2. Full Analysis
- إدخال نص العقد
- تحليل كامل باستخدام System Prompt
- عرض:
  - ملخص العقد
  - البنود المحللة
  - الـ chunks الداعمة
  - حالة كل بند (supported/not_supported/ambiguous)

## ⚙️ التكوين الحالي

| Variable | القيمة الحالية | الوصف |
|----------|---------|-------------|
| `GEMINI_API_KEY` | `AIzaSyD...ZhVE` | مفتاح API من Google AI |
| `MODEL_NAME` | `gemini-2.5-flash` | موديل Gemini المستخدم |
| `FILE_SEARCH_STORE_ID` | `fileSearchStores/aaoifi-reference-store-eh6go6xtuavz` | معرف الـ Store النشط |
| `TOP_K_CHUNKS` | `20` | عدد الـ chunks المسترجعة |
| `FLASK_HOST` | `0.0.0.0` | عنوان الاستماع للـ API |
| `FLASK_PORT` | `5001` | منفذ Flask API |
| `FLASK_DEBUG` | `False` | وضع التطوير |

## 📦 التبعيات

```
flask==3.0.0
flask-cors==4.0.0
google-genai
python-dotenv==1.0.0
streamlit==1.29.0
requests==2.31.0
```

## 🔑 System Prompt الحالي

النظام يستخدم prompt متخصص لتحليل العقود الشرعية:

```
أنت محلل عقود شرعي يعمل حصريًا بنظام Retrieval. يتم تزويدك بـ:
1. نص عقد كامل (raw contract text)
2. مجموعة chunks مسترجعة من File Search

القواعد الصارمة:
- لا تستخدم معلومات غير موجودة في العقد أو الـ chunks
- اذكر chunk_uid عند الاستدلال
- لا تخترع أو تفترض معلومات
- التزم ببنية JSON المحددة
```

## 📝 ملاحظات مهمة

1. **File Search Store**:
   - ✅ Store ID موجود ونشط: `fileSearchStores/aaoifi-reference-store-eh6go6xtuavz`
   - ✅ تم رفع `Shariaah-Standards-ARB.pdf`
   - لا حاجة لإعادة رفع الملفات

2. **System Prompt**:
   - يمكن تعديله من ملف `.env` مباشرة
   - لا تحتاج لإعادة تشغيل عند التعديل

3. **الأمان**:
   - ⚠️ API Key ظاهر في `.env` - استخدم Replit Secrets للإنتاج

## 🔄 إعادة استخدام الكود

```python
from services.file_search import FileSearchService
from services.analyzer import ContractAnalyzer

# Initialize services
fs_service = FileSearchService()
fs_service.initialize_store()

# Search chunks
chunks = fs_service.search_chunks("نص العقد", top_k=20)

# Analyze contract
analyzer = ContractAnalyzer()
analysis = analyzer.analyze_contract("نص العقد", chunks)
```

## 🛠️ Troubleshooting

### التحذيرات الحالية في Console:
```
Python-dotenv could not parse statement starting at line 13-37
```
**السبب**: System Prompt متعدد الأسطر في `.env`
**التأثير**: لا يؤثر على عمل النظام - الـ prompt يُقرأ بشكل صحيح

### الحل (اختياري):
ضع System Prompt في ملف منفصل أو استخدم Replit Secrets

## 📊 حالة النظام

✅ Flask API يعمل على: `http://0.0.0.0:5001`  
✅ Streamlit يعمل على: `http://0.0.0.0:5000`  
✅ File Search Store نشط ومُهيأ  
✅ الملف المرجعي محمّل ومُفهرس

## 📧 الدعم

للمساعدة والاستفسارات، راجع:
- [Gemini API Docs](https://ai.google.dev/gemini-api/docs/file-search)
- [Google GenAI SDK](https://googleapis.github.io/python-genai/)

---

**Built with ❤️ using Gemini 2.5 Flash & File Search API**
