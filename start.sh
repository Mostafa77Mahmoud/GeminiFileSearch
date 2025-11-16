
#!/bin/bash

echo "Starting Gemini File Search System..."
echo "======================================"

# Start Flask API in the background
echo "Starting Flask API on port 5001..."
python app.py &
FLASK_PID=$!

# Wait for Flask to be ready
echo "Waiting for Flask API to be ready..."
sleep 5

# Start Streamlit
echo "Starting Streamlit Frontend on port 5000..."
streamlit run frontend.py --server.port=5000 --server.address=0.0.0.0 --server.headless=true

# If Streamlit exits, kill Flask
kill $FLASK_PID 2>/dev/null || true
