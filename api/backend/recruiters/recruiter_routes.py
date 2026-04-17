from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

recruiters = Blueprint("recruiters", __name__)


# GET /rec/candidates
# List all candidates with optional filters: ?name=, ?university=, ?stage=, ?cycle=
@recruiters.route("/candidates", methods=["GET"])
def get_candidates():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("GET /rec/candidates")

        name = request.args.get("name")
        university = request.args.get("university")
        stage = request.args.get("stage")
        cycle = request.args.get("cycle")

        query = """
            SELECT
                s.StudentID,
                CONCAT(u.FirstName, ' ', u.LastName) AS full_name,
                u.Email,
                i.InstitutionName AS university,
                p.Title AS role,
                a.Cycle AS cycle,
                a.Status AS stage,
                a.ApplicationID,
                COALESCE(a.LastUpdated, a.Application_Date) AS last_updated,
                s.DegreeLevel AS degree_level
            FROM Student s
            JOIN `User` u ON s.UserID = u.UserID
            JOIN Institution i ON u.InstitutionID = i.InstitutionID
            JOIN Job_Application a ON a.StudentID = s.StudentID
            JOIN `Position` p ON a.PositionID = p.PositionID
            WHERE a.IsArchived = FALSE
        """
        params = []

        if name:
            query += " AND CONCAT(u.FirstName, ' ', u.LastName) LIKE %s"
            params.append(f"%{name}%")
        if university:
            query += " AND i.InstitutionName = %s"
            params.append(university)
        if stage:
            query += " AND a.Status = %s"
            params.append(stage)
        if cycle:
            query += " AND a.Cycle = %s"
            params.append(cycle)

        query += " ORDER BY last_updated DESC"

        cursor.execute(query, params)
        candidates = cursor.fetchall()
        return jsonify(candidates), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_candidates: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# GET /rec/candidates/<student_id>
# Full candidate profile: personal info + all applications
@recruiters.route("/candidates/<int:student_id>", methods=["GET"])
def get_candidate_profile(student_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /rec/candidates/{student_id}")

        cursor.execute("""
            SELECT
                s.StudentID,
                u.FirstName,
                u.LastName,
                u.Email,
                i.InstitutionName AS university,
                s.DegreeLevel AS degree_level,
                s.GPA,
                s.Year
            FROM Student s
            JOIN `User` u ON s.UserID = u.UserID
            JOIN Institution i ON u.InstitutionID = i.InstitutionID
            WHERE s.StudentID = %s
        """, (student_id,))
        candidate = cursor.fetchone()

        if not candidate:
            return jsonify({"error": "Candidate not found"}), 404

        cursor.execute("""
            SELECT
                a.ApplicationID,
                a.Status AS stage,
                a.Cycle AS cycle,
                a.Application_Date,
                COALESCE(a.LastUpdated, a.Application_Date) AS last_updated,
                p.Title AS role,
                e.Name AS employer
            FROM Job_Application a
            JOIN `Position` p ON a.PositionID = p.PositionID
            JOIN Employer e ON p.EmployerID = e.EmployerID
            WHERE a.StudentID = %s AND a.IsArchived = FALSE
            ORDER BY a.Application_Date DESC
        """, (student_id,))
        candidate["applications"] = cursor.fetchall()

        return jsonify(candidate), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_candidate_profile: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# PUT /rec/applications/<app_id>/stage
# Update the hiring stage (Status) of an application
# Body: { "stage": "Offer Sent" }
@recruiters.route("/applications/<int:app_id>/stage", methods=["PUT"])
def update_stage(app_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"PUT /rec/applications/{app_id}/stage")

        data = request.get_json()
        if not data or "stage" not in data:
            return jsonify({"error": "Missing required field: stage"}), 400

        cursor.execute("SELECT ApplicationID FROM Job_Application WHERE ApplicationID = %s", (app_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Application not found"}), 404

        cursor.execute(
            "UPDATE Job_Application SET Status = %s WHERE ApplicationID = %s",
            (data["stage"], app_id)
        )
        get_db().commit()
        return jsonify({"message": "Stage updated successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in update_stage: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# POST /rec/applications/<app_id>/notes
# Add a recruiter note to an application
# Body: { "note_text": "...", "recruiter_id": 1 }
@recruiters.route("/applications/<int:app_id>/notes", methods=["POST"])
def add_note(app_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"POST /rec/applications/{app_id}/notes")

        data = request.get_json()
        if not data or "note_text" not in data:
            return jsonify({"error": "Missing required field: note_text"}), 400

        cursor.execute("SELECT ApplicationID FROM Job_Application WHERE ApplicationID = %s", (app_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Application not found"}), 404

        recruiter_id = data.get("recruiter_id")

        cursor.execute("""
            INSERT INTO Note (ApplicationID, Note_Text, Created_At, RecruiterID)
            VALUES (%s, %s, NOW(), %s)
        """, (app_id, data["note_text"], recruiter_id))
        get_db().commit()

        return jsonify({"message": "Note added successfully", "note_id": cursor.lastrowid}), 201
    except Error as e:
        current_app.logger.error(f"Database error in add_note: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# GET /rec/applications/<app_id>/notes
# List all notes for an application, newest first
@recruiters.route("/applications/<int:app_id>/notes", methods=["GET"])
def get_notes(app_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /rec/applications/{app_id}/notes")

        cursor.execute("SELECT ApplicationID FROM Job_Application WHERE ApplicationID = %s", (app_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Application not found"}), 404

        cursor.execute("""
            SELECT
                n.NoteID,
                n.Note_Text,
                n.Created_At,
                n.RecruiterID,
                CONCAT(u.FirstName, ' ', u.LastName) AS recruiter_name
            FROM Note n
            LEFT JOIN Recruiter r ON n.RecruiterID = r.RecruiterID
            LEFT JOIN `User` u ON r.UserID = u.UserID
            WHERE n.ApplicationID = %s
            ORDER BY n.Created_At DESC
        """, (app_id,))
        notes = cursor.fetchall()
        return jsonify(notes), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_notes: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# DELETE /rec/notes/<note_id>
# Delete a specific note
@recruiters.route("/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"DELETE /rec/notes/{note_id}")

        cursor.execute("SELECT NoteID FROM Note WHERE NoteID = %s", (note_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Note not found"}), 404

        cursor.execute("DELETE FROM Note WHERE NoteID = %s", (note_id,))
        get_db().commit()
        return jsonify({"message": "Note deleted successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in delete_note: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# GET /rec/pipeline/stats
# Aggregate candidate counts grouped by hiring stage
@recruiters.route("/pipeline/stats", methods=["GET"])
def get_pipeline_stats():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("GET /rec/pipeline/stats")

        cursor.execute("""
            SELECT Status AS stage, COUNT(*) AS count
            FROM Job_Application
            WHERE IsArchived = FALSE
            GROUP BY Status
            ORDER BY count DESC
        """)
        stats = cursor.fetchall()
        return jsonify(stats), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_pipeline_stats: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# GET /rec/recruiters
# List all recruiters for the Home.py persona selector
@recruiters.route("/recruiters", methods=["GET"])
def get_recruiters():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("GET /rec/recruiters")

        cursor.execute("""
            SELECT r.RecruiterID, u.FirstName, u.LastName, u.Email,
                   CONCAT(u.FirstName, ' ', u.LastName) AS full_name
            FROM Recruiter r
            JOIN `User` u ON r.UserID = u.UserID
            ORDER BY u.FirstName
        """)
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_recruiters: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
