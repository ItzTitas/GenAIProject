import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from datetime import datetime, timedelta
import random
from werkzeug.exceptions import HTTPException

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes
# Configuration
app.config['JSON_SORT_KEYS'] = False  # Maintain JSON key order
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyAfUs3f9DlR9C4aqdRl2pCdbPTUaXy-Hrs')  # Use environment variable

if not GEMINI_API_KEY:
    raise ValueError("Missing Gemini API key. Please set GEMINI_API_KEY environment variable.")

genai.configure(api_key=GEMINI_API_KEY)

# Global constants
POSITIONS = ['Software Engineer', 'Data Analyst', 'Product Manager', 'UX Designer']
STAGES = ['Applied', 'Screening', 'Interview', 'Offer', 'Hired']

# Error handler
@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return jsonify(error=str(e)), code

# Mock data generation with more realistic data
def generate_dashboard_data():
    return {
        'metrics': {
            'open_positions': random.randint(5, 15),
            'candidates_in_pipeline': random.randint(50, 200),
            'avg_time_to_hire': random.randint(10, 30),
            'offer_acceptance_rate': random.randint(70, 95),
        },
        'positions': [{'title': title, 'count': random.randint(1, 5)} for title in POSITIONS],
        'pipeline': [{'stage': stage, 'count': random.randint(5, 25)} for stage in STAGES],
        'recent_activity': [
            {
                'action': f"Candidate moved to {random.choice(STAGES)}",
                'position': random.choice(POSITIONS),
                'time': (datetime.now() - timedelta(hours=random.randint(1, 24))).strftime('%I:%M %p'),
                'candidate': f"Candidate #{random.randint(1000, 9999)}"
            } for _ in range(5)
        ]
    }

# Candidate data with more fields
candidates_db = [
    {
        "id": 1,
        "name": "John Doe",
        "status": "New",
        "skills": ["Python", "Flask", "Docker"],
        "applied_date": "2025-03-25",
        "experience": "5 years",
        "education": "MS Computer Science",
        "source": "LinkedIn"
    },
    {
        "id": 2,
        "name": "Jane Smith",
        "status": "Interview Scheduled",
        "skills": ["React", "Node.js", "TypeScript"],
        "applied_date": "2025-03-20",
        "experience": "3 years",
        "education": "BS Software Engineering",
        "source": "Company Website"
    },
    {
        "id": 3,
        "name": "Alex Johnson",
        "status": "Screening",
        "skills": ["Java", "Spring", "AWS"],
        "applied_date": "2025-03-22",
        "experience": "7 years",
        "education": "BS Computer Engineering",
        "source": "Referral"
    }
]

@app.route("/api/dashboard", methods=["GET"])
def get_dashboard_data():
    try:
        return jsonify(generate_dashboard_data())
    except Exception as e:
        app.logger.error(f"Dashboard error: {str(e)}")
        return jsonify({"error": "Failed to generate dashboard data"}), 500

@app.route("/api/candidates", methods=["GET"])
def get_candidates():
    try:
        # Add simple filtering capability
        status_filter = request.args.get('status')
        if status_filter:
            filtered = [c for c in candidates_db if c['status'].lower() == status_filter.lower()]
            return jsonify({"candidates": filtered})
        return jsonify({"candidates": candidates_db})
    except Exception as e:
        app.logger.error(f"Candidates error: {str(e)}")
        return jsonify({"error": "Failed to retrieve candidates"}), 500

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Invalid request format"}), 400
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        
        # Enhanced prompt with context
        prompt = f"""You are an AI Talent Acquisition Assistant helping HR professionals.
        Current time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        Available candidate statuses: {', '.join(STAGES)}
        Available positions: {', '.join(POSITIONS)}
        
        HR Query: {user_message}
        
        Provide a concise, professional response:"""
        
        response = model.generate_content(prompt)
        return jsonify({
            "response": response.text,
            "status": "success",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        app.logger.error(f"Chat error: {str(e)}")
        return jsonify({
            "error": "Failed to process your message",
            "details": str(e)
        }), 500

# **FIXED: Interviews Route (removed incorrect indentation)**
@app.route("/api/interviews", methods=["GET"])
def get_interviews():
    try:
        # Get date range parameters from FullCalendar
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        
        # Mock data - in a real app you'd query your database
        interviews = [
            {
                "id": 1,
                "title": "John Doe - Technical Interview",
                "start": "2025-03-28T10:00:00",
                "end": "2025-03-28T11:00:00",
                "extendedProps": {
                    "candidate_id": 1,
                    "status": "scheduled",
                    "interviewers": "Jane Smith, Mike Johnson"
                }
            },
            {
                "id": 2,
                "title": "Alice Brown - HR Interview",
                "start": "2025-03-29T14:00:00",
                "end": "2025-03-29T15:00:00",
                "extendedProps": {
                    "candidate_id": 2,
                    "status": "confirmed",
                    "interviewers": "Sarah Wilson"
                }
            }
        ]
        
        # Filter by date range if provided
        if start_date and end_date:
            interviews = [i for i in interviews if i['start'] >= start_date and i['end'] <= end_date]
            
        return jsonify(interviews)
        
    except Exception as e:
        app.logger.error(f"Error getting interviews: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/interviews/upcoming", methods=["GET"])
def upcoming_interviews():
    try:
        # Get interviews for next 7 days
        today = datetime.now()
        next_week = today + timedelta(days=7)
        
        upcoming = [
            {
                "id": 1,
                "candidate_name": "John Doe",
                "position": "Software Engineer",
                "time": "Mar 28, 10:00 AM - 11:00 AM",
                "status": "Scheduled",
                "interview_type": "Technical"
            },
            {
                "id": 2,
                "candidate_name": "Alice Brown",
                "position": "Product Manager",
                "time": "Mar 29, 2:00 PM - 3:00 PM",
                "status": "Confirmed",
                "interview_type": "HR"
            }
        ]
        
        return jsonify(upcoming)
        
    except Exception as e:
        app.logger.error(f"Error getting upcoming interviews: {str(e)}")
        return jsonify({"error": str(e)}), 500

# **FIXED: Removed extra `.` at the end**
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
