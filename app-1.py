from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@127.0.0.1/school'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Students(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    student_number = db.Column(db.String(20), nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    middle_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    gender = db.Column(db.Integer, nullable=False)
    birthday = db.Column(db.Date, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "student_number": self.student_number,
            "first_name": self.first_name,
            "middle_name": self.middle_name,
            "last_name": self.last_name,
            "gender": self.gender,
            "birthday": self.birthday.strftime("%Y-%m-%d")
        }

@app.route("/students", methods=["GET"])
def get_students():
    students = Students.query.limit(100)
    return jsonify(
        {
            "success": True,
            "data": [student.to_dict() for student in students]
        }
    ), 200

@app.route("/students/<int:id>", methods=['GET'])
def get_student(id):
    student = db.session.get(Students, id)
    if not student:
        return jsonify(
            {
                "success": False,
                "error": "Student not found"
            }
        ), 404
    return jsonify(
        {
            "success": True,
            "data": student.to_dict()
        }
    ), 200

@app.route("/students", methods=['POST'])
def add_student():
    if not request.is_json:
        return jsonify(
            {
                "success": False,
                "error": "Content-type must be application/json"
            }
        ), 400
    data = request.get_json()
    required_fields = ["student_number", "first_name", "middle_name", "last_name", "gender", "birthday"]

    for field in required_fields:
        if field not in data:
            return jsonify(
                {
                    "success": False,
                    "error": f"Missing field: {field}"
                }
            ), 400

    try:
        new_student = Students(
            student_number=data["student_number"],
            first_name=data["first_name"],
            middle_name=data["middle_name"],
            last_name=data["last_name"],
            gender=data["gender"],
            birthday=datetime.strptime(data["birthday"], "%Y-%m-%d")
        )
        db.session.add(new_student)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "success": False,
                "error": str(e)
            }
        ), 500

    return jsonify(
        {
            "success": True,
            "data": new_student.to_dict()
        }
    ), 201

@app.route("/students/<int:id>", methods=["PUT"])
def update_student(id):
    student = db.session.get(Students, id)
    if not student:
        return jsonify(
            {
                "success": False,
                "error": "Student not found"
            }
        ), 404

    data = request.get_json()
    updatable_fields = ["student_number", "first_name", "middle_name", "last_name", "gender", "birthday"]

    for field in updatable_fields:
        if field in data:
            if field == "birthday":
                try:
                    setattr(student, field, datetime.strptime(data[field], "%Y-%m-%d"))
                except ValueError:
                    return jsonify(
                        {
                            "success": False,
                            "error": "Invalid format, use YYYY-MM-DD"
                        }
                    ), 400
            else:
                setattr(student, field, data[field])

    db.session.commit()
    return jsonify(
        {
            "success": True,
            "data": student.to_dict()
        }
    ), 200

@app.route("/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    student = db.session.get(Students, id)
    if not student:
        return jsonify(
            {
                "success": False,
                "error": "Student not found"
            }
        ), 404
    db.session.delete(student)
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "message": "Student successfully deleted" 
        }
    ), 204

if __name__ == '__main__':
    app.run(debug=True)
