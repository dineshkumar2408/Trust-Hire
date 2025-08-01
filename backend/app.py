from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app, supports_credentials=True)

# In-memory user storage (in production, use a proper database)
users_db = {
    "admin@trusthire.com": {
        "password": generate_password_hash("admin123"),
        "name": "Admin User",
        "role": "admin",
        "created_at": datetime.now().isoformat()
    },
    "user@trusthire.com": {
        "password": generate_password_hash("user123"),
        "name": "John Doe",
        "role": "user",
        "created_at": datetime.now().isoformat()
    }
}

@app.route('/')
def home():
    return 'Trust Hire API'

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = users_db.get(email)
        if user and check_password_hash(user['password'], password):
            session['user_email'] = email
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            
            return jsonify({
                'success': True,
                'user': {
                    'email': email,
                    'name': user['name'],
                    'role': user['role']
                }
            })
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
            
    except Exception as e:
        return jsonify({'error': 'Server error'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/profile', methods=['GET'])
def get_profile():
    if 'user_email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    email = session['user_email']
    user = users_db.get(email)
    
    if user:
        return jsonify({
            'email': email,
            'name': user['name'],
            'role': user['role'],
            'created_at': user['created_at']
        })
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/api/dashboard-stats', methods=['GET'])
def get_dashboard_stats():
    if 'user_email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Mock dashboard statistics
    stats = {
        'total_applications': 24,
        'pending_reviews': 8,
        'scheduled_interviews': 5,
        'hired_candidates': 3,
        'recent_activities': [
            {'type': 'application', 'message': 'New application from Sarah Johnson', 'time': '2 hours ago'},
            {'type': 'interview', 'message': 'Interview scheduled with Mike Chen', 'time': '4 hours ago'},
            {'type': 'hire', 'message': 'Candidate Emma Wilson hired', 'time': '1 day ago'},
            {'type': 'review', 'message': 'Application review completed', 'time': '2 days ago'}
        ]
    }
    
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True, port=5000)