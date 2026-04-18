from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

alex = Blueprint("alex", __name__)


# grabs all students so the home page dropdown can list them
@alex.route("/students", methods=["GET"])
def get_students():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("GET /alex/students")

        cursor.execute("""
            SELECT s.StudentID, u.FirstName, u.LastName, u.Email,
                   CONCAT(u.FirstName, ' ', u.LastName) AS full_name,
                   m.MajorName AS major, s.Year, s.GPA
            FROM Student s
            JOIN `User` u ON s.UserID = u.UserID
            LEFT JOIN Major m ON s.MajorID = m.MajorID
            ORDER BY u.FirstName
        """)
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_students: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# list of the student's applications, can filter by status in the URL
@alex.route("/students/<int:student_id>/applications", methods=["GET"])
def get_applications(student_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /alex/students/{student_id}/applications")

        status = request.args.get("status")

        query = """
            SELECT
                a.ApplicationID,
                a.Application_Date,
                a.Status,
                a.Notes,
                p.PositionID,
                p.Title AS position_title,
                e.EmployerID,
                e.Name AS employer_name,
                e.Location
            FROM Job_Application a
            JOIN `Position` p ON a.PositionID = p.PositionID
            JOIN Employer e ON p.EmployerID = e.EmployerID
            WHERE a.StudentID = %s
              AND a.IsArchived = FALSE
        """
        params = [student_id]

        if status:
            query += " AND a.Status = %s"
            params.append(status)

        query += " ORDER BY a.Application_Date DESC"

        cursor.execute(query, params)
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_applications: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# logs a new application for the student
@alex.route("/students/<int:student_id>/applications", methods=["POST"])
def create_application(student_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"POST /alex/students/{student_id}/applications")

        data = request.get_json()
        if not data or "position_id" not in data or "application_date" not in data:
            return jsonify({
                "error": "Missing required fields: position_id, application_date"
            }), 400

        cursor.execute("""
            INSERT INTO Job_Application
                (StudentID, PositionID, ResumeID, Application_Date,
                 Status, Notes, IsArchived)
            VALUES (%s, %s, %s, %s, %s, %s, FALSE)
        """, (
            student_id,
            data["position_id"],
            data.get("resume_id"),
            data["application_date"],
            data.get("status", "Applied"),
            data.get("notes"),
        ))
        new_id = cursor.lastrowid

        # bump the student's app counter + activity date so it stays accurate
        cursor.execute("""
            UPDATE Student
               SET NumApplications = NumApplications + 1,
                   LastActivityDate = NOW()
             WHERE StudentID = %s
        """, (student_id,))

        get_db().commit()
        return jsonify({
            "message": "Application created successfully",
            "application_id": new_id
        }), 201
    except Error as e:
        current_app.logger.error(f"Database error in create_application: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# full detail for one application
@alex.route("/applications/<int:app_id>", methods=["GET"])
def get_application(app_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /alex/applications/{app_id}")

        cursor.execute("""
            SELECT
                a.ApplicationID,
                a.StudentID,
                a.Application_Date,
                a.Status,
                a.Notes,
                a.IsArchived,
                p.Title AS position_title,
                e.Name AS employer_name,
                e.Location
            FROM Job_Application a
            JOIN `Position` p ON a.PositionID = p.PositionID
            JOIN Employer e ON p.EmployerID = e.EmployerID
            WHERE a.ApplicationID = %s
        """, (app_id,))
        application = cursor.fetchone()

        if not application:
            return jsonify({"error": "Application not found"}), 404

        return jsonify(application), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_application: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# update the status or the notes on an app (or both)
@alex.route("/applications/<int:app_id>", methods=["PUT"])
def update_application(app_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"PUT /alex/applications/{app_id}")

        data = request.get_json()
        if not data or ("status" not in data and "notes" not in data):
            return jsonify({
                "error": "Provide at least one field: status or notes"
            }), 400

        # make sure the app exists before trying to update it
        cursor.execute(
            "SELECT ApplicationID FROM Job_Application WHERE ApplicationID = %s",
            (app_id,)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Application not found"}), 404

        # only update whichever fields they sent
        fields, params = [], []
        if "status" in data:
            fields.append("Status = %s")
            params.append(data["status"])
        if "notes" in data:
            fields.append("Notes = %s")
            params.append(data["notes"])
        params.append(app_id)

        cursor.execute(
            f"UPDATE Job_Application SET {', '.join(fields)} WHERE ApplicationID = %s",
            params
        )
        get_db().commit()
        return jsonify({"message": "Application updated successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in update_application: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# soft delete — just flip IsArchived to TRUE so we don't lose the history
@alex.route("/applications/<int:app_id>", methods=["DELETE"])
def archive_application(app_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"DELETE /alex/applications/{app_id}")

        cursor.execute(
            "SELECT ApplicationID FROM Job_Application WHERE ApplicationID = %s",
            (app_id,)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Application not found"}), 404

        cursor.execute(
            "UPDATE Job_Application SET IsArchived = TRUE WHERE ApplicationID = %s",
            (app_id,)
        )
        get_db().commit()
        return jsonify({"message": "Application archived successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in archive_application: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        

# personal funnel metrics for one student - apps, interviews, offers, conversion rates
@alex.route("/students/<int:student_id>/funnel", methods=["GET"])
def get_personal_funnel(student_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f"GET /alex/students/{student_id}/funnel")

        cursor.execute("""
            SELECT
                COUNT(DISTINCT a.ApplicationID) AS total_applications,
                COUNT(DISTINCT i.InterviewID)   AS total_interviews,
                COUNT(DISTINCT jo.OfferID)      AS total_offers,
                ROUND(
                    COUNT(DISTINCT i.InterviewID) * 100.0
                    / NULLIF(COUNT(DISTINCT a.ApplicationID), 0),
                    2
                ) AS application_to_interview_rate,
                ROUND(
                    COUNT(DISTINCT jo.OfferID) * 100.0
                    / NULLIF(COUNT(DISTINCT i.InterviewID), 0),
                    2
                ) AS interview_to_offer_rate
            FROM Job_Application a
            LEFT JOIN Interview i  ON a.ApplicationID = i.ApplicationID
            LEFT JOIN Job_Offer jo ON a.ApplicationID = jo.ApplicationID
            WHERE a.StudentID = %s
              AND a.IsArchived = FALSE
        """, (student_id,))
        row = cursor.fetchone()
        row["student_id"] = student_id
        return jsonify(row), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_personal_funnel: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()