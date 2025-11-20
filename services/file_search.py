import time
from google import genai
from google.genai import types
from pathlib import Path
from typing import List, Dict, Optional
from config import Config


class FileSearchService:
    """
    خدمة البحث في الملفات باستخدام Google Gemini File Search API
    تركز على استرجاع chunks من مستندات AAOIFI المرجعية
    """

    def __init__(self):
        """تهيئة الخدمة بالاتصال بـ Gemini API"""
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model_name = Config.MODEL_NAME
        self.store_id: Optional[str] = Config.FILE_SEARCH_STORE_ID
        self.context_dir = Config.CONTEXT_DIR
        self.search_prompt_template = Config.SEARCH_PROMPT

        print("[INFO] FileSearchService initialized")
        print("[INFO] Model: {}".format(self.model_name))
        print("[INFO] Context Directory: {}".format(self.context_dir))

    def initialize_store(self) -> str:
        """
        تهيئة أو الاتصال بـ File Search Store الموجود

        Returns:
            str: معرّف الـ Store (store_id)
        """
        print("\n" + "="*60)
        print("FILE SEARCH STORE INITIALIZATION")
        print("="*60)

        # التحقق من وجود Store ID موجود
        if self.store_id:
            print("[INFO] Checking existing Store ID: {}".format(self.store_id))
            try:
                store = self.client.file_search_stores.get(name=self.store_id)
                print("[SUCCESS] Connected to existing store: '{}'".format(store.display_name))
                print("[INFO] Store is active and ready")
                return self.store_id
            except Exception as e:
                print("[WARNING] Could not access store {}".format(self.store_id))
                print("[WARNING] Error: {}".format(e))
                print("[INFO] Will create a new store...")

        # إنشاء Store جديد
        print("[INFO] Creating new File Search Store...")
        try:
            store = self.client.file_search_stores.create(
                config={'display_name': 'AAOIFI Reference Store'}
            )
            self.store_id = store.name
            print("[SUCCESS] New store created: {}".format(self.store_id))
            print("[IMPORTANT] Save this Store ID to .env file:")
            print("[IMPORTANT] FILE_SEARCH_STORE_ID={}".format(self.store_id))

            # رفع الملفات من مجلد context/
            self._upload_context_files()

            # Ensure we return a string, not None
            if self.store_id is None:
                raise ValueError("Store ID was not set after creation")

            return self.store_id

        except Exception as e:
            print("[ERROR] Failed to create File Search Store: {}".format(e))
            raise

    def _upload_context_files(self):
        """رفع جميع الملفات من مجلد context/ إلى File Search Store"""

        if not self.store_id:
            print("[ERROR] Store ID is not set. Cannot upload files.")
            return

        context_path = Path(self.context_dir)

        # التحقق من وجود المجلد
        if not context_path.exists():
            print("[WARNING] Context directory '{}' not found".format(self.context_dir))
            context_path.mkdir(parents=True, exist_ok=True)
            print("[INFO] Created directory: {}".format(self.context_dir))
            print("[INFO] Please add your AAOIFI reference files to '{}/' folder".format(self.context_dir))
            return

        # البحث عن الملفات
        files = list(context_path.glob("*"))
        files = [f for f in files if f.is_file() and not f.name.startswith('.')]

        if not files:
            print("[WARNING] No files found in '{}/' directory".format(self.context_dir))
            print("[INFO] Please add your AAOIFI reference files (PDF, TXT, etc.)")
            return

        print("\n[INFO] Found {} file(s) to upload:".format(len(files)))
        for f in files:
            print("  - {}".format(f.name))

        # رفع كل ملف
        uploaded_count = 0
        for file_path in files:
            print("\n[UPLOAD] Uploading: {}".format(file_path.name))
            try:
                operation = self.client.file_search_stores.upload_to_file_search_store(
                    file=str(file_path),
                    file_search_store_name=self.store_id,
                    config={'display_name': file_path.name}
                )

                print("[INDEXING] Waiting for {} to be indexed...".format(file_path.name))
                while not operation.done:
                    time.sleep(2)
                    operation = self.client.operations.get(operation)

                uploaded_count += 1
                print("[SUCCESS] {} uploaded and indexed".format(file_path.name))

            except Exception as e:
                print("[ERROR] Failed to upload {}: {}".format(file_path.name, e))

        print("\n[SUMMARY] Successfully uploaded {}/{} files".format(uploaded_count, len(files)))
        print("="*60 + "\n")

    def search_chunks(self, contract_text: str, top_k: Optional[int] = None) -> List[Dict]:
        """
        البحث عن chunks ذات صلة بنص العقد

        Args:
            contract_text: نص العقد للبحث عنه
            top_k: عدد الـ chunks المطلوبة (اختياري)

        Returns:
            List[Dict]: قائمة بالـ chunks المسترجعة، كل chunk يحتوي على:
                - uid: معرّف فريد للـ chunk
                - chunk_text: نص الـ chunk
                - score: درجة الصلة
                - uri: مصدر الـ chunk (إن وجد)
        """

        if not self.store_id:
            raise ValueError("File Search Store not initialized. Run initialize_store() first.")

        if top_k is None:
            top_k = Config.TOP_K_CHUNKS

        print("\n[SEARCH] Starting search (top_k={})...".format(top_k))
        print("[SEARCH] Contract text length: {} characters".format(len(contract_text)))

        try:
            # بناء prompt محسّن لإجبار Gemini على استخدام File Search
            # يجب أن يكون الـ prompt واضحاً جداً أننا نريد البحث في المستندات المرفقة
            full_prompt = """يجب عليك البحث في المستندات المرجعية (معايير هيئة AAOIFI الشرعية) عن معلومات متعلقة بالنص التالي.

استخدم File Search للبحث في المستندات المرفقة واستخرج جميع المقاطع (chunks) ذات الصلة.

النص المطلوب تحليله:
{}

قم بالبحث في المستندات المرجعية عن:
1. الأحكام والمعايير الشرعية المتعلقة بهذا النوع من العقود
2. الشروط والضوابط الشرعية
3. الحالات المشابهة أو الأمثلة
4. الأحكام الخاصة بالمخالفات أو الجزاءات
5. أي معلومات أخرى ذات صلة من معايير AAOIFI

يجب استخدام المستندات المرفقة في الإجابة.""".format(contract_text)

            print("[SEARCH] Querying Gemini File Search...")
            print("[SEARCH] Using store: {}".format(self.store_id))
            print("[SEARCH] Top K: {}".format(top_k))

            # استدعاء Gemini مع File Search tool والـ store_id
            # topK parameter في FileSearch يتحكم في عدد الـ chunks
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[self.store_id],
                            top_k=top_k
                        )
                    )],
                    response_modalities=["TEXT"]
                )
            )

            print("[DEBUG] Response received from Gemini")
            print("[DEBUG] Response type: {}".format(type(response)))
            
            # طباعة diagnostic information
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                print("[DEBUG] Candidate finish_reason: {}".format(getattr(candidate, 'finish_reason', 'N/A')))
                print("[DEBUG] Has grounding_metadata: {}".format(hasattr(candidate, 'grounding_metadata')))
                if hasattr(candidate, 'grounding_metadata'):
                    gm = candidate.grounding_metadata
                    print("[DEBUG] grounding_metadata is None: {}".format(gm is None))
                    if gm:
                        print("[DEBUG] Has grounding_chunks: {}".format(hasattr(gm, 'grounding_chunks')))
                        if hasattr(gm, 'grounding_chunks'):
                            print("[DEBUG] Number of grounding_chunks: {}".format(len(gm.grounding_chunks) if gm.grounding_chunks else 0))
                
                # طباعة النص المُولّد من Gemini
                if hasattr(candidate, 'content') and candidate.content:
                    if hasattr(candidate.content, 'parts') and candidate.content.parts:
                        generated_text = candidate.content.parts[0].text if hasattr(candidate.content.parts[0], 'text') else 'N/A'
                        print("[DEBUG] Generated text preview: {}...".format(generated_text[:200]))

            # استخراج الـ chunks من الـ grounding metadata
            chunks = self._extract_grounding_chunks(response, top_k)

            print("[SUCCESS] Retrieved {} chunks\n".format(len(chunks)))
            return chunks

        except Exception as e:
            print("[ERROR] Search failed: {}".format(e))
            import traceback
            traceback.print_exc()
            raise

    def _extract_grounding_chunks(self, response, top_k: int) -> List[Dict]:
        """
        استخراج الـ chunks من الـ grounding metadata
        
        يستخرج المقاطع الأصلية من ملف PDF المُخزّن في File Search Store

        Args:
            response: استجابة Gemini
            top_k: الحد الأقصى لعدد الـ chunks

        Returns:
            List[Dict]: قائمة بالـ chunks، كل chunk يحتوي على:
                - uid: معرّف فريد
                - chunk_text: النص الأصلي من PDF
                - score: درجة الصلة
                - uri: مصدر الملف
                - title: عنوان الملف
        """

        chunks = []

        # التحقق من وجود candidates
        if not hasattr(response, 'candidates') or not response.candidates:
            print("[WARNING] No candidates in response")
            return chunks

        candidate = response.candidates[0]

        # التحقق من وجود grounding_metadata
        if not hasattr(candidate, 'grounding_metadata'):
            print("[WARNING] No grounding_metadata attribute in candidate")
            return chunks

        grounding = candidate.grounding_metadata
        
        # التحقق من أن grounding_metadata ليس None
        if grounding is None:
            print("[WARNING] grounding_metadata is None")
            return chunks
        
        # ===== PRIORITY 1: استخراج من grounding_chunks (المقاطع الأصلية من PDF) =====
        if hasattr(grounding, 'grounding_chunks') and grounding.grounding_chunks:
            total_chunks = len(grounding.grounding_chunks)
            print("[INFO] Found {} grounding_chunks from File Search".format(total_chunks))

            for idx, chunk in enumerate(grounding.grounding_chunks):
                if idx >= top_k:
                    break

                chunk_data = {
                    "uid": "chunk_{}".format(idx + 1),
                    "chunk_text": "",
                    "score": 0.0,
                    "uri": None,
                    "title": None
                }

                # استخراج النص الأصلي من retrieved_context
                if hasattr(chunk, 'retrieved_context') and chunk.retrieved_context:
                    retrieved = chunk.retrieved_context

                    # النص الأصلي من PDF
                    if hasattr(retrieved, 'text'):
                        chunk_data["chunk_text"] = retrieved.text
                    
                    # URI للملف
                    if hasattr(retrieved, 'uri'):
                        chunk_data["uri"] = retrieved.uri
                    
                    # عنوان الملف أو القسم
                    if hasattr(retrieved, 'title'):
                        chunk_data["title"] = retrieved.title

                # استخراج درجة الصلة (relevance score)
                # ملاحظة: الـ File Search API الحالي لا يوفر scores للـ chunks
                # الـ chunks مرتبة حسب الصلة تلقائياً من Gemini
                # لذلك، نستخدم ترتيب الـ chunk كمؤشر على الصلة
                chunk_data["score"] = 1.0 - (idx * 0.05)  # تقليل الـ score تدريجياً حسب الترتيب

                # إضافة الـ chunk إذا كان يحتوي على نص
                if chunk_data["chunk_text"]:
                    chunks.append(chunk_data)
                    print("[SUCCESS] Chunk {} - {} chars - score: {:.4f}".format(
                        idx + 1, 
                        len(chunk_data["chunk_text"]), 
                        chunk_data["score"]
                    ))

            if chunks:
                print("[INFO] Successfully extracted {} original chunks from PDF".format(len(chunks)))
                return chunks
            else:
                print("[WARNING] grounding_chunks exist but contain no text")

        # ===== FALLBACK: استخراج من grounding_supports (نص Gemini المُولّد) =====
        if hasattr(grounding, 'grounding_supports') and grounding.grounding_supports:
            print("[INFO] Falling back to grounding_supports (Gemini generated text)")
            print("[WARNING] This is NOT the original PDF content!")
            
            for idx, support in enumerate(grounding.grounding_supports):
                if idx >= top_k:
                    break

                chunk_data = {
                    "uid": "support_{}".format(idx + 1),
                    "chunk_text": "",
                    "score": 0.0,
                    "uri": None,
                    "title": "Generated Summary"
                }

                # استخراج من segment (نص Gemini)
                if hasattr(support, 'segment') and support.segment:
                    if hasattr(support.segment, 'text'):
                        chunk_data["chunk_text"] = support.segment.text

                # استخراج confidence scores
                if hasattr(support, 'confidence_scores') and support.confidence_scores:
                    chunk_data["score"] = float(support.confidence_scores[0])

                if chunk_data["chunk_text"]:
                    chunks.append(chunk_data)

            if chunks:
                print("[INFO] Extracted {} chunks from grounding_supports (fallback)".format(len(chunks)))
                return chunks

        # لم يتم العثور على أي chunks
        print("[ERROR] No chunks found in grounding_chunks or grounding_supports")
        return chunks

    def get_store_info(self) -> Dict:
        """
        الحصول على معلومات عن File Search Store الحالي

        Returns:
            Dict: معلومات عن الـ Store
        """

        if not self.store_id:
            return {
                "status": "not_initialized",
                "store_id": None,
                "message": "Store not initialized"
            }

        try:
            store = self.client.file_search_stores.get(name=self.store_id)

            return {
                "status": "active",
                "store_id": self.store_id,
                "display_name": store.display_name if hasattr(store, 'display_name') else "Unknown",
                "message": "Store is ready"
            }

        except Exception as e:
            return {
                "status": "error",
                "store_id": self.store_id,
                "error": str(e),
                "message": "Failed to access store"
            }