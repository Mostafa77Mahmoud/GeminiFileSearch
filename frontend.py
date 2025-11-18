import streamlit as st
import requests
import json
from typing import Optional, Dict, Any, Tuple
from config import Config

st.set_page_config(
    page_title="Gemini File Search - Contract Analysis",
    page_icon="🔍",
    layout="wide"
)

# Use 127.0.0.1 for internal connection instead of 0.0.0.0
API_BASE_URL = "http://127.0.0.1:{}".format(Config.FLASK_PORT)

def check_api_health() -> bool:
    """Check if Flask API is running"""
    try:
        response = requests.get("{}/health".format(API_BASE_URL), timeout=2)
        return response.status_code == 200
    except:
        return False

def get_store_info() -> Optional[Dict[str, Any]]:
    """Get File Search Store information"""
    try:
        response = requests.get("{}/store-info".format(API_BASE_URL), timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def file_search_request(contract_text: str, top_k: int = 20) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Send file search request to API"""
    try:
        response = requests.post(
            "{}/file_search".format(API_BASE_URL),
            json={"contract_text": contract_text, "top_k": top_k},
            timeout=180
        )
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, response.json().get("error", "Unknown error")
    except Exception as e:
        return None, str(e)

st.title("🔍 Gemini File Search - Contract Analysis System")
st.markdown("### تحليل العقود باستخدام Gemini 2.5 Flash و File Search API")

if not check_api_health():
    st.error("⚠️ Flask API is not running. Please start the Flask server first.")
    st.info("Run: `python app.py`")
    st.stop()

st.success("✅ Connected to Flask API")

store_info = get_store_info()
if store_info:
    with st.expander("📊 File Search Store Information"):
        st.json(store_info)

st.markdown("---")

st.header("File Search")
st.markdown("استخرج الـ chunks المرتبطة بنص العقد من الكتاب المرجعي (AAOIFI)")

contract_input = st.text_area(
    "أدخل نص العقد:",
    height=200,
    placeholder="أدخل نص العقد هنا للبحث في الكتاب المرجعي..."
)

col1, col2 = st.columns([3, 1])
with col1:
    run_search_btn = st.button("🔍 Run File Search", type="primary", use_container_width=True)
with col2:
    top_k_search = st.number_input("Top-K", min_value=1, max_value=100, value=10)

st.info("ℹ️ ملاحظة: عملية البحث قد تستغرق 30-90 ثانية حسب حجم النص وعدد الـ chunks المطلوبة")

if run_search_btn:
    if not contract_input.strip():
        st.error("يرجى إدخال نص العقد")
    else:
        with st.spinner("جاري البحث في File Search Store... (قد يستغرق دقيقة أو أكثر)"):
            result, error = file_search_request(contract_input, int(top_k_search))
        
        if error:
            st.error("خطأ: {}".format(error))
        elif result:
            st.success("✅ تم استرجاع {} chunks".format(result['total_chunks']))
            
            st.markdown("### 📄 نص العقد الكامل:")
            with st.expander("عرض نص العقد", expanded=False):
                st.text_area("نص العقد", value=result['contract_text'], height=150, disabled=True, key="contract_display", label_visibility="hidden")
            
            st.markdown("### 📦 الـ Chunks المسترجعة:")
            
            if result['chunks']:
                # زر تحميل النتائج
                download_data = {
                    "contract_text": result['contract_text'],
                    "total_chunks": result['total_chunks'],
                    "top_k": result['top_k'],
                    "chunks": result['chunks']
                }
                
                json_str = json.dumps(download_data, ensure_ascii=False, indent=2)
                
                st.download_button(
                    label="⬇️ تحميل النتائج (JSON)",
                    data=json_str,
                    file_name="file_search_results.json",
                    mime="application/json",
                    use_container_width=True,
                    type="primary"
                )
                
                st.markdown("---")
                
                for idx, chunk in enumerate(result['chunks'], 1):
                    with st.container():
                        st.markdown("#### Chunk {}".format(idx))
                        col_a, col_b = st.columns([1, 3])
                        with col_a:
                            st.metric("UID", chunk['uid'])
                            st.metric("Score", "{:.4f}".format(chunk['score']))
                        with col_b:
                            st.text_area(
                                "محتوى الـ Chunk",
                                value=chunk['chunk_text'],
                                height=120,
                                disabled=True,
                                key="chunk_text_{}".format(idx),
                                label_visibility="visible"
                            )
                        st.markdown("---")
            else:
                st.warning("لم يتم العثور على chunks مرتبطة")
        else:
            st.error("حدث خطأ غير متوقع")

st.markdown("---")
st.caption("Powered by Gemini 2.5 Flash & File Search API")
