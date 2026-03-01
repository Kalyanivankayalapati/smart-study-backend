from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# -----------------------------
# Database Configuration
# -----------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -----------------------------
# User Table
# -----------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

# -----------------------------
# Subject Table
# -----------------------------
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# -----------------------------
# Study Session Table
# -----------------------------
class StudySession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    duration = db.Column(db.Float)  # hours
    date = db.Column(db.Date)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# -----------------------------
# Home
# -----------------------------
@app.route("/")
def home():
    return "Backend with Full Analytics is running!"

# -----------------------------
# Register
# -----------------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json

    if User.query.filter_by(email=data.get("email")).first():
        return jsonify({"message": "User already exists!"}), 400

    new_user = User(
        name=data.get("name"),
        email=data.get("email"),
        password=data.get("password")
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully!"})

# -----------------------------
# Login
# -----------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json

    user = User.query.filter_by(email=data.get("email")).first()

    if user and user.password == data.get("password"):
        return jsonify({
            "message": "Login successful!",
            "user_id": user.id
        })
    else:
        return jsonify({"message": "Invalid email or password"}), 401

# -----------------------------
# Add Subject
# -----------------------------
@app.route("/add-subject", methods=["POST"])
def add_subject():
    data = request.json

    new_subject = Subject(
        name=data.get("name"),
        user_id=data.get("user_id")
    )

    db.session.add(new_subject)
    db.session.commit()

    return jsonify({"message": "Subject added successfully!"})

# -----------------------------
# Get Subjects
# -----------------------------
@app.route("/get-subjects/<int:user_id>", methods=["GET"])
def get_subjects(user_id):
    subjects = Subject.query.filter_by(user_id=user_id).all()

    return jsonify([
        {"id": s.id, "name": s.name}
        for s in subjects
    ])

# -----------------------------
# Add Study Session
# -----------------------------
@app.route("/add-session", methods=["POST"])
def add_session():
    data = request.json

    new_session = StudySession(
        duration=data.get("duration"),
        subject_id=data.get("subject_id"),
        user_id=data.get("user_id"),
        date=datetime.strptime(data.get("date"), "%Y-%m-%d")
    )

    db.session.add(new_session)
    db.session.commit()

    return jsonify({"message": "Study session added successfully!"})

# -----------------------------
# Get All Sessions for User
# -----------------------------
@app.route("/get-sessions/<int:user_id>", methods=["GET"])
def get_sessions(user_id):
    sessions = StudySession.query.filter_by(user_id=user_id).all()

    return jsonify([
        {
            "duration": s.duration,
            "date": s.date.strftime("%Y-%m-%d"),
            "subject_id": s.subject_id
        }
        for s in sessions
    ])

# -----------------------------
# Analytics Route (Improved)
# -----------------------------
@app.route("/analytics/<int:user_id>", methods=["GET"])
def analytics(user_id):
    sessions = StudySession.query.filter_by(user_id=user_id).all()

    total_hours = sum(s.duration for s in sessions)
    total_sessions = len(sessions)

    productivity_score = (total_hours * 2) + (total_sessions * 1.5)

    # Find Most Productive Day
    most_productive_day = None
    if sessions:
        best_session = max(sessions, key=lambda s: s.duration)
        most_productive_day = best_session.date.strftime("%Y-%m-%d")

    return jsonify({
        "total_hours": total_hours,
        "total_sessions": total_sessions,
        "productivity_score": round(productivity_score, 2),
        "most_productive_day": most_productive_day
    })

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)