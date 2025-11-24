from flask import Flask, request, jsonify
from flask_cors import CORS
from services.file_search import FileSearchService
from config import Config

app = Flask(__name__)
CORS(app)

file_search_service = None

def initialize_services():
    """Initialize File Search service on app startup"""
    global file_search_service
    
    try:
        Config.validate()
        print("[INFO] Configuration validated successfully")
    except ValueError as e:
        print(f"[ERROR] {e}")
        print("[INFO] Please check your .env file and ensure all required variables are set")
        return False
    
    try:
        file_search_service = FileSearchService()
        
        print("[INFO] Initializing File Search Store...")
        store_id = file_search_service.initialize_store()
        print(f"[SUCCESS] File Search Store initialized: {store_id}")
        
        store_info = file_search_service.get_store_info()
        print(f"[INFO] Store Info: {store_info}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to initialize services: {e}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "File Search API is running"
    })

@app.route('/store-info', methods=['GET'])
def store_info():
    """Get File Search Store information"""
    if not file_search_service:
        return jsonify({
            "error": "Service not initialized"
        }), 500
    
    info = file_search_service.get_store_info()
    return jsonify(info)

@app.route('/extract_terms', methods=['POST'])
def extract_terms():
    """Extract key terms endpoint - extracts important clauses from contract"""
    
    if not file_search_service:
        return jsonify({
            "error": "File Search Service not initialized"
        }), 500
    
    try:
        data = request.get_json()
        
        if not data or 'contract_text' not in data:
            return jsonify({
                "error": "Missing 'contract_text' in request body"
            }), 400
        
        contract_text = data['contract_text']
        
        if not contract_text.strip():
            return jsonify({
                "error": "Contract text cannot be empty"
            }), 400
        
        print(f"[INFO] Processing term extraction request")
        extracted_terms = file_search_service.extract_key_terms(contract_text)
        
        response = {
            "contract_text": contract_text,
            "extracted_terms": extracted_terms,
            "total_terms": len(extracted_terms)
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"[ERROR] Term extraction failed: {e}")
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/file_search', methods=['POST'])
def file_search():
    """
    File Search endpoint - two-step process:
    1. Extracts key terms from contract
    2. Searches for relevant chunks using extracted terms
    """
    
    if not file_search_service:
        return jsonify({
            "error": "File Search Service not initialized"
        }), 500
    
    try:
        data = request.get_json()
        
        if not data or 'contract_text' not in data:
            return jsonify({
                "error": "Missing 'contract_text' in request body"
            }), 400
        
        contract_text = data['contract_text']
        top_k = data.get('top_k', Config.TOP_K_CHUNKS)
        
        if not contract_text.strip():
            return jsonify({
                "error": "Contract text cannot be empty"
            }), 400
        
        print(f"[INFO] Processing two-step file search request with top_k={top_k}")
        
        # ملاحظة: search_chunks الآن يرجع (chunks, extracted_terms)
        chunks, extracted_terms = file_search_service.search_chunks(contract_text, top_k)
        
        response = {
            "contract_text": contract_text,
            "extracted_terms": extracted_terms,
            "chunks": chunks,
            "total_chunks": len(chunks),
            "top_k": top_k,
            "message": "Two-step process: extracted key terms then searched File Search"
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"[ERROR] File search failed: {e}")
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("GEMINI FILE SEARCH API - Starting Up")
    print("=" * 60)
    
    if initialize_services():
        print("\n" + "=" * 60)
        print("API READY - Endpoints Available:")
        print(f"  - GET  /health")
        print(f"  - GET  /store-info")
        print(f"  - POST /extract_terms  (Step 1: Extract key terms)")
        print(f"  - POST /file_search    (Two-step: Extract + Search)")
        print("=" * 60 + "\n")
        
        app.run(
            host=Config.FLASK_HOST,
            port=Config.FLASK_PORT,
            debug=Config.FLASK_DEBUG
        )
    else:
        print("\n[ERROR] Failed to initialize services. Please check your configuration.")
        print("[INFO] Make sure you have:")
        print("  1. Created a .env file based on .env.example")
        print("  2. Set your GEMINI_API_KEY in the .env file")
        print("  3. Added your AAOIFI reference book to the 'context/' folder")
