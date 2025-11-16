# Overview

This is a **Simple File Search System** powered by Google's Gemini 2.5 Flash and File Search API. The system searches for relevant content from reference materials (AAOIFI standards) stored in a File Search vector store.

The application provides a Flask REST API backend and a Streamlit web frontend for searching contracts against reference documents.

# User Preferences

Preferred communication style: Simple, everyday language (Arabic and English).

# System Architecture

## Application Structure

**Multi-Service Architecture**: The system uses a dual-service approach:
- **Flask API** (`app.py`) - Backend REST service handling File Search operations
- **Streamlit Frontend** (`frontend.py`) - User interface for contract upload and results visualization

## Core Components

### 1. Configuration Management (`config.py`)

**Environment-based Configuration**: All sensitive data and configurable parameters are stored in environment variables:
- API keys (`GEMINI_API_KEY`)
- Model selection (`MODEL_NAME`)
- File Search Store ID (`FILE_SEARCH_STORE_ID` - persisted across sessions)
- Search prompt template (`SEARCH_PROMPT` - customizable)
- Search parameters (`TOP_K_CHUNKS`)
- Server configuration (host, port, debug)

### 2. File Search Service (`services/file_search.py`)

**Vector Store Pattern**: Uses Google's File Search API to create a persistent vector store for reference documents:
- One-time upload of AAOIFI reference materials to `context/` directory
- Store ID persists via environment variable to avoid re-uploading
- Automatic store creation if ID not provided
- Chunk retrieval with configurable top-k parameter
- Clean error handling and type safety

**Key Methods**:
- `initialize_store()`: Create or connect to existing File Search store
- `search_chunks(query, top_k)`: Search for relevant chunks in the store using customizable prompt
- `get_store_info()`: Get metadata about the current store
- `_upload_context_files()`: Upload files from context/ directory
- `_extract_grounding_chunks()`: Extract chunks from Gemini response

### 3. API Endpoints

**RESTful Design**:
- `GET /health` - Service health check
- `GET /store-info` - File Search store metadata
- `POST /file_search` - Retrieve relevant chunks for contract text

## Data Flow

1. **Initialization**: Reference documents uploaded once to File Search store
2. **Search Request**: User submits contract text via Streamlit
3. **Retrieval**: Flask API queries File Search using `SEARCH_PROMPT + contract text`
4. **Response**: Returns chunks with UID, text, and relevance score

## Design Patterns

**Service Layer Pattern**: Business logic isolated in `services/` directory separating concerns from API routes.

**Configuration Object Pattern**: Centralized config validation and environment variable management.

**Type Safety**: Full type hints throughout the codebase for better IDE support and error catching.

# External Dependencies

## Google AI Platform

**Gemini 2.5 Flash API**: Primary LLM for File Search
- Model: `gemini-2.5-flash` (configurable)
- Purpose: Semantic search and chunk retrieval
- SDK: `google-genai` (new unified SDK)

**File Search API**: Vector storage and semantic retrieval
- Purpose: Store and search AAOIFI reference documents
- Persistence: Store ID saved in environment variables
- Chunk Retrieval: Configurable top-k parameter (default: 20)

## Web Frameworks

**Flask 3.1.2**: Backend REST API server
- CORS enabled for frontend communication
- Custom error handling and service initialization

**Streamlit 1.51.0**: Frontend web interface
- Real-time file search UI
- Store information dashboard
- Request/response visualization
- Type-safe request handlers

## Supporting Libraries

- `python-dotenv`: Environment variable management
- `requests`: HTTP client for frontend-backend communication
- `flask-cors`: Cross-origin resource sharing for API

## File System Dependencies

**Context Directory** (`context/`): 
- Stores AAOIFI reference PDF/documents
- Auto-created if missing
- Files uploaded to File Search store on initialization

## Environment Requirements

- Python 3.11+
- Required Secrets/Environment Variables:
  - `GEMINI_API_KEY` - Google AI API authentication
  - `FILE_SEARCH_STORE_ID` - Persistent vector store identifier (auto-generated on first run)
  - `SEARCH_PROMPT` - Customizable search prompt template (optional, has default value)
  - `TOP_K_CHUNKS` - Number of chunks to retrieve (optional, default: 20)

# Recent Changes (November 16, 2025)

## Latest Updates - Fixed Chunk Extraction Logic
- **Critical Fix**: Corrected chunk extraction priority in `_extract_grounding_chunks()` to retrieve **original PDF content** first
- **Extraction Order**: Now correctly extracts from `grounding_chunks.retrieved_context` (original PDF text) before falling back to `grounding_supports` (Gemini-generated summaries)
- **Metadata Extraction**: Added proper extraction of `title`, `uri`, and `score` fields from retrieved_context
- **Score Accuracy**: Fixed relevance score extraction from `chunk.score` or `chunk.relevance_score` instead of confidence_scores
- **Improved Logging**: Added clear debug messages to distinguish between original chunks and fallback summaries
- **Verified by Architect**: Code review confirmed correct implementation according to Gemini File Search API documentation

## Previous Updates - Replit Environment Setup
- **Fixed API Parameter**: Updated `file_search_stores` to `file_search_store_names` for compatibility with latest google-genai SDK
- **Configured for Replit**: Successfully imported GitHub project and configured for Replit environment
- **Secrets Management**: Moved API keys (GEMINI_API_KEY, FILE_SEARCH_STORE_ID) to Replit Secrets for security
- **Streamlit Configuration**: Added `.streamlit/config.toml` with CORS and XSRF disabled for Replit proxy compatibility
- **Workflow Setup**: Configured workflow to run both Flask (port 5001) and Streamlit (port 5000) via `start.sh`
- **Deployment Ready**: Configured for autoscale deployment on Replit
- **Added .gitignore**: Created Python-specific .gitignore to exclude cache and environment files
- **Dependencies Installed**: All required packages installed via pip (flask, streamlit, google-genai, etc.)
- **Services Running**: Both Flask API and Streamlit frontend successfully running and responding

## Previous Updates
- **Removed SYSTEM_PROMPT**: Deleted the multi-line SYSTEM_PROMPT that was causing python-dotenv parsing errors
- **Added SEARCH_PROMPT**: Simple, single-line search prompt for File Search queries
- **Fixed LSP Errors**: Resolved all type safety issues in `services/file_search.py` and `frontend.py`
- **Simplified Project Focus**: Removed contract analysis features to focus exclusively on File Search functionality
- **Deleted Components**: Removed `services/analyzer.py` and `/analyze` endpoint
- **Simplified Frontend**: Removed "Full Analysis" tab, kept only "File Search" functionality

# How to Use on Replit

1. **Setup Secrets**: Configure the following in Replit Secrets (already done):
   - `GEMINI_API_KEY`: Your Google AI API key from https://aistudio.google.com/apikey
   - `FILE_SEARCH_STORE_ID`: Your File Search store ID (optional, created automatically if not provided)

2. **Add Documents**: Place AAOIFI reference files in `context/` directory (already contains `Shariaah-Standards-ARB.pdf`)

3. **Run**: Click the "Run" button or the workflow will start automatically
   - Flask API runs on port 5001 (backend)
   - Streamlit frontend runs on port 5000 (accessible via Replit webview)

4. **Search**: Enter contract text in the Streamlit interface and get relevant chunks from the reference documents

# Configuration

The system uses environment variables from Replit Secrets and the `.env` file:

**Required (Replit Secrets)**:
- `GEMINI_API_KEY`: Google AI API key
- `FILE_SEARCH_STORE_ID`: File Search store identifier (auto-generated if not set)

**Optional (.env file)**:
- `MODEL_NAME`: Gemini model to use (default: `gemini-2.5-flash`)
- `TOP_K_CHUNKS`: Number of chunks to retrieve (default: `20`)
- `SEARCH_PROMPT`: Arabic search prompt template
- `FLASK_HOST`: Flask server host (default: `0.0.0.0`)
- `FLASK_PORT`: Flask server port (default: `5001`)
- `FLASK_DEBUG`: Debug mode (default: `False`)

**Note**: Sensitive credentials are stored in Replit Secrets, not in `.env` file for security.
