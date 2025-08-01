#!/bin/bash

echo "🚀 Starting Trust Hire Application..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip3 install -r requirements.txt

# Start the Flask server in the background
echo "🌐 Starting Flask backend server on http://localhost:5000..."
python3 app.py &
FLASK_PID=$!

# Wait a moment for the server to start
sleep 3

# Go back to root directory
cd ..

echo "✅ Backend server started successfully!"
echo "🌟 Frontend is available at: frontend/index.html"
echo ""
echo "📋 Demo Credentials:"
echo "   Admin: admin@trusthire.com / admin123"
echo "   User:  user@trusthire.com / user123"
echo ""
echo "To stop the server, run: kill $FLASK_PID"
echo "Or press Ctrl+C to stop"

# Keep the script running
wait $FLASK_PID