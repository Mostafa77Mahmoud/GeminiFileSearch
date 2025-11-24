import streamlit as st
import requests
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from config import Config

st.set_page_config(
    page_title="تحليل العقود - Gemini File Search",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Use 127.0.0.1 for internal connection
API_BASE_URL = "http://127.0.0.1:{}".format(Config.FLASK_PORT)
RESULTS_DIR = "results"

# إنشاء مجلد النتائج إذا لم يكن موجوداً
os.makedirs(RESULTS_DIR, exist_ok=True)

def check_api_health() -> bool:
    """التحقق من حالة Flask API"""
    try:
        response = requests.get("{}/health".format(API_BASE_URL), timeout=2)
        return response.status_code == 200
    except:
        return False

def get_store_info() -> Optional[Dict[str, Any]]:
    """الحصول على معلومات File Search Store"""
    try:
        response = requests.get("{}/store-info".format(API_BASE_URL), timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def file_search_request(contract_text: str, top_k: int = 10) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """إرسال طلب البحث للـ API"""
    try:
        response = requests.post(
            "{}/file_search".format(API_BASE_URL),
            json={"contract_text": contract_text, "top_k": top_k},
            timeout=300  # زيادة timeout إلى 5 دقائق
        )
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, response.json().get("error", "خطأ غير معروف")
    except Exception as e:
        return None, str(e)

def save_results_to_file(result: Dict[str, Any], contract_text: str) -> str:
    """حفظ نتائج البحث في ملف JSON"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = "analysis_{}.json".format(timestamp)
    filepath = os.path.join(RESULTS_DIR, filename)
    
    # تجهيز البيانات
    output_data = {
        "timestamp": timestamp,
        "contract_length": len(contract_text),
        "total_chunks": result.get("total_chunks", 0),
        "extracted_terms": result.get("extracted_terms", []),
        "chunks": result.get("chunks", [])
    }
    
    # حفظ الملف
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    return filepath

# ============= الواجهة الرئيسية =============
st.title("⚖️ نظام تحليل العقود - Gemini File Search")
st.markdown("### نظام متقدم لتحليل العقود الإسلامية وفق معايير AAOIFI")

# Sidebar
with st.sidebar:
    st.header("📋 معلومات النظام")
    
    if check_api_health():
        st.success("✅ الـ API يعمل")
    else:
        st.error("❌ الـ API غير متاح")
        st.stop()
    
    store_info = get_store_info()
    if store_info:
        st.subheader("📊 File Search Store")
        st.metric("الحالة", store_info.get('status', 'unknown'))
        st.metric("عدد الملفات", "1 (AAOIFI Reference)")
    
    st.divider()
    
    # معلومات مجلد النتائج
    results_count = len([f for f in os.listdir(RESULTS_DIR) if f.endswith('.json')]) if os.path.exists(RESULTS_DIR) else 0
    st.metric("عدد نتائج البحث المحفوظة", results_count)
    
    st.info("💾 جميع النتائج يتم حفظها تلقائياً في مجلد `results/`")

# المحتوى الرئيسي
st.markdown("---")

# قسم الإدخال
st.header("🔍 أداة تحليل العقد")
st.markdown("أدخل نص العقد واتركنا نحلله وفق معايير الشريعة الإسلامية")

# شريط الإدخال
contract_input = st.text_area(
    "📄 أدخل نص العقد:",
    height=250,
    placeholder="أدخل نص العقد الكامل هنا...",
    label_visibility="visible"
)

# أزرار التحكم
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    run_search = st.button("🔍 بدء التحليل", type="primary", use_container_width=True)
with col2:
    top_k = st.number_input("عدد النتائج", min_value=5, max_value=50, value=10)
with col3:
    st.empty()

# معلومات مهمة
st.info("ℹ️ **ملاحظة:** العملية تستغرق 2-4 دقائق حسب حجم النص. يتم البحث على مرحلتين:\n"
        "1️⃣ استخراج البنود المهمة\n"
        "2️⃣ البحث الهجين (عام + معمّق للبنود الحساسة)")

st.markdown("---")

# معالجة الطلب
if run_search:
    if not contract_input.strip():
        st.error("❌ يرجى إدخال نص العقد أولاً")
    else:
        # شريط التقدم
        progress_bar = st.progress(0)
        status_container = st.container()
        
        with status_container:
            with st.spinner("⏳ جاري التحليل... (هذا قد يستغرق 2-4 دقائق)"):
                result, error = file_search_request(contract_input, int(top_k))
                progress_bar.progress(100)
        
        if error:
            st.error("❌ حدث خطأ: {}".format(error))
        elif result:
            # حفظ النتائج
            result_path = save_results_to_file(result, contract_input)
            
            # عرض النتائج
            st.success("✅ تم التحليل بنجاح!")
            
            # ملخص النتائج
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📝 عدد البنود المستخرجة", len(result.get("extracted_terms", [])))
            with col2:
                st.metric("📊 عدد الـ Chunks", result.get("total_chunks", 0))
            with col3:
                st.metric("💾 تم الحفظ", os.path.basename(result_path))
            
            st.markdown("---")
            
            # قسم البنود المستخرجة
            if result.get("extracted_terms"):
                st.subheader("🔎 البنود المستخرجة من العقد")
                
                with st.expander("عرض البنود المستخرجة", expanded=False):
                    for idx, term in enumerate(result.get("extracted_terms", []), 1):
                        with st.container():
                            col1, col2 = st.columns([1, 4])
                            with col1:
                                st.write(f"**البند #{idx}**")
                            with col2:
                                st.write(f"**{term.get('term_id', 'N/A')}**")
                            
                            st.write(f"📌 **النص:** {term.get('term_text', '')[:200]}...")
                            
                            issues = term.get('potential_issues', [])
                            if issues:
                                st.write(f"⚠️ **المشاكل المحتملة:** {', '.join(issues)}")
                            
                            st.write(f"💡 **السبب:** {term.get('relevance_reason', '')}")
                            st.divider()
            
            # قسم الـ Chunks
            st.subheader("📦 المقاطع المستخرجة من معايير AAOIFI")
            
            if result.get('chunks'):
                # شريط البحث داخل الـ chunks
                search_query = st.text_input("🔍 ابحث في النتائج:", placeholder="ابحث عن كلمة...")
                
                # تصفية النتائج
                chunks = result.get('chunks', [])
                if search_query:
                    chunks = [c for c in chunks if search_query.lower() in c.get('chunk_text', '').lower()]
                
                st.write(f"عدد النتائج: **{len(chunks)}** من **{result.get('total_chunks', 0)}**")
                
                # عرض الـ chunks
                for idx, chunk in enumerate(chunks, 1):
                    with st.container():
                        # رأس الـ chunk
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.write(f"**📋 Chunk #{idx}**")
                        with col2:
                            score = chunk.get('score', 0)
                            st.metric("الصلة", f"{score:.2%}")
                        with col3:
                            st.write(f"**{len(chunk.get('chunk_text', ''))} حرف**")
                        
                        # محتوى الـ chunk
                        chunk_text = chunk.get('chunk_text', '')
                        # عرض أول 300 حرف مع إمكانية التوسع
                        if len(chunk_text) > 300:
                            with st.expander("عرض النص الكامل"):
                                st.write(chunk_text)
                            st.write(chunk_text[:300] + "...")
                        else:
                            st.write(chunk_text)
                        
                        # معلومات المصدر
                        if chunk.get('uri'):
                            st.caption(f"📂 المصدر: {chunk.get('uri', 'N/A')}")
                        
                        st.divider()
                
                # أزرار التحميل
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    # تحميل JSON
                    json_data = json.dumps(result, ensure_ascii=False, indent=2)
                    st.download_button(
                        label="⬇️ تحميل النتائج (JSON)",
                        data=json_data,
                        file_name="analysis_{}.json".format(datetime.now().strftime("%Y%m%d_%H%M%S")),
                        mime="application/json",
                        use_container_width=True
                    )
                
                with col2:
                    # تحميل نص عادي
                    text_output = "=== نتائج تحليل العقد ===\n\n"
                    text_output += f"التاريخ: {datetime.now()}\n"
                    text_output += f"عدد البنود: {len(result.get('extracted_terms', []))}\n"
                    text_output += f"عدد الـ Chunks: {result.get('total_chunks', 0)}\n\n"
                    
                    text_output += "--- البنود المستخرجة ---\n"
                    for term in result.get('extracted_terms', []):
                        text_output += f"\n{term.get('term_id')}: {term.get('term_text')}\n"
                    
                    st.download_button(
                        label="📄 تحميل النتائج (Text)",
                        data=text_output,
                        file_name="analysis_{}.txt".format(datetime.now().strftime("%Y%m%d_%H%M%S")),
                        mime="text/plain",
                        use_container_width=True
                    )
            else:
                st.warning("لم يتم العثور على نتائج")

# قسم السجل
st.markdown("---")
st.header("📜 السجل")

if os.path.exists(RESULTS_DIR):
    result_files = sorted([f for f in os.listdir(RESULTS_DIR) if f.endswith('.json')], reverse=True)
    
    if result_files:
        st.subheader("آخر التحليلات")
        
        with st.expander("عرض السجل", expanded=False):
            for filename in result_files[:10]:  # عرض آخر 10 نتائج
                st.write(f"📁 {filename}")
                filepath = os.path.join(RESULTS_DIR, filename)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.caption(f"التاريخ: {data.get('timestamp', 'N/A')}")
                    with col2:
                        st.caption(f"البنود: {len(data.get('extracted_terms', []))}")
                    with col3:
                        st.caption(f"Chunks: {data.get('total_chunks', 0)}")
    else:
        st.info("لا توجد نتائج مسبقة")
