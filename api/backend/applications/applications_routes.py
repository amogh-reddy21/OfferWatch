from flask import Blueprint, jsonify, request
from backend.db_connection import get_db

applications = Blueprint('applications', __name__)


@applications.route('/applications', methods=['GET'])
def get_applications():
    try:
        query = """
            SELECT *
            FROM Job_Application
            ORDER BY Application_Date DESC
            LIMIT 100;
        """

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query)

        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        cursor.close()

        results = [dict(zip(columns, row)) for row in rows]
        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@applications.route('/positions', methods=['GET'])
def get_positions():
    try:
        query = """
            SELECT
                p.PositionID,
                p.Title,
                e.Name AS EmployerName
            FROM Position p
            JOIN Employer e
                ON p.EmployerID = e.EmployerID
            ORDER BY p.PositionID;
        """

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query)

        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        cursor.close()

        results = [dict(zip(columns, row)) for row in rows]
        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@applications.route('/applications', methods=['POST'])
def create_application():
    try:
        data = request.get_json()

        student_id = data.get("StudentID")
        position_id = data.get("PositionID")
        notes = data.get("Notes", "").strip()

        if not student_id or not position_id:
            return jsonify({
                "error": "StudentID and PositionID are required."
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # Validate that the position exists
        cursor.execute(
            """
            SELECT PositionID
            FROM Position
            WHERE PositionID = %s
            """,
            (position_id,)
        )
        position_row = cursor.fetchone()

        if not position_row:
            cursor.close()
            return jsonify({
                "error": f"PositionID {position_id} does not exist."
            }), 400

        # Get the student's latest resume, if one exists
        cursor.execute(
            """
            SELECT ResumeID
            FROM Resume
            WHERE StudentID = %s
            ORDER BY Version DESC, DateSubmitted DESC
            LIMIT 1
            """,
            (student_id,)
        )
        resume_row = cursor.fetchone()
        resume_id = resume_row[0] if resume_row else None

        query = """
            INSERT INTO Job_Application (
                StudentID,
                PositionID,
                ResumeID,
                Application_Date,
                Status,
                Notes,
                IsArchived
            )
            VALUES (%s, %s, %s, NOW(), %s, %s, FALSE)
        """

        cursor.execute(
            query,
            (
                student_id,
                position_id,
                resume_id,
                "Applied",
                notes if notes else None
            )
        )

        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()

        return jsonify({
            "message": "Application created successfully",
            "ApplicationID": new_id,
            "ResumeID": resume_id,
            "Status": "Applied"
        }), 201

    except Exception as e:
        print("ERROR creating application:", e)
        return jsonify({"error": str(e)}), 500