# Change pls
# FINAL CODE - Updated Advisor Routes - V2

from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

advisor_routes = Blueprint('advisor_routes', __name__, url_prefix='/advisor')


# GET  /advisor/<advisor_id>/dashboard
# US1 — Cohort-wide Applied → Interview → Offer conversion rates
@advisor_routes.route('/<int:advisor_id>/dashboard', methods=['GET'])
def get_cohort_dashboard(advisor_id):
    try:
        conn   = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                COUNT(DISTINCT ja.ApplicationID)  AS TotalApplications,
                COUNT(DISTINCT i.InterviewID)      AS TotalInterviews,
                COUNT(DISTINCT jo.OfferID)         AS TotalOffers,
                ROUND(
                    COUNT(DISTINCT i.InterviewID) * 100.0
                    / NULLIF(COUNT(DISTINCT ja.ApplicationID), 0), 2
                ) AS AppliedToInterviewRate,
                ROUND(
                    COUNT(DISTINCT jo.OfferID) * 100.0
                    / NULLIF(COUNT(DISTINCT i.InterviewID), 0), 2
                ) AS InterviewToOfferRate
            FROM Student s
            JOIN Job_Application ja ON s.StudentID     = ja.StudentID
            LEFT JOIN Interview   i  ON ja.ApplicationID = i.ApplicationID
            LEFT JOIN Job_Offer   jo ON ja.ApplicationID = jo.ApplicationID
            WHERE s.AdvisorID = %s
              AND ja.IsArchived = FALSE
        """, (advisor_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "No data found for this advisor."}), 404
        return jsonify(row), 200
    except Error as e:
        current_app.logger.error(f"get_cohort_dashboard error: {e}")
        return jsonify({"error": "Database error."}), 500


# GET  /advisor/<advisor_id>/students/flagged
# US2 — Students inactive for 14+ days or with zero applications
@advisor_routes.route('/<int:advisor_id>/students/flagged', methods=['GET'])
def get_flagged_students(advisor_id):
    try:
        conn   = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                s.StudentID,
                CONCAT(u.FirstName, ' ', u.LastName) AS StudentName,
                s.LastActivityDate,
                COUNT(ja.ApplicationID) AS ApplicationVolume
            FROM Student s
            JOIN `User` u ON s.UserID = u.UserID
            LEFT JOIN Job_Application ja ON s.StudentID = ja.StudentID
            WHERE s.AdvisorID = %s
            GROUP BY s.StudentID, u.FirstName, u.LastName, s.LastActivityDate
            HAVING s.LastActivityDate < DATE_SUB(CURDATE(), INTERVAL 14 DAY)
               OR COUNT(ja.ApplicationID) = 0
        """, (advisor_id,))
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"get_flagged_students error: {e}")
        return jsonify({"error": "Database error."}), 500


# GET  /advisor/<advisor_id>/resumes/success-rates
# US3 — Resume version × industry interview conversion rates
@advisor_routes.route('/<int:advisor_id>/resumes/success-rates', methods=['GET'])
def get_resume_success_rates(advisor_id):
    try:
        conn   = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                r.Version,
                ind.Title                         AS Industry,
                COUNT(DISTINCT ja.ApplicationID)  AS Applications,
                COUNT(DISTINCT i.InterviewID)     AS Interviews,
                ROUND(
                    LEAST(COUNT(DISTINCT i.InterviewID) * 100.0
                    / NULLIF(COUNT(DISTINCT ja.ApplicationID), 0),100), 2
                ) AS InterviewRate
            FROM Resume r
            JOIN Student s          ON r.StudentID       = s.StudentID
            JOIN Job_Application ja ON r.ResumeID        = ja.ResumeID
            JOIN `Position` p       ON ja.PositionID     = p.PositionID
            JOIN Employer   e       ON p.EmployerID      = e.EmployerID
            JOIN Industry   ind     ON e.IndustryID      = ind.IndustryID
            LEFT JOIN Interview i   ON ja.ApplicationID  = i.ApplicationID
            WHERE s.AdvisorID = %s
            GROUP BY r.Version, ind.Title
            ORDER BY r.Version, ind.Title
        """, (advisor_id,))
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"get_resume_success_rates error: {e}")
        return jsonify({"error": "Database error."}), 500


# GET  /advisor/<advisor_id>/employers/top-offers
# US4 — Companies and industries ranked by offers extended to cohort
@advisor_routes.route('/<int:advisor_id>/employers/top-offers', methods=['GET'])
def get_top_offer_employers(advisor_id):
    try:
        conn   = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                ind.Title  AS Industry,
                e.Name     AS EmployerName,
                e.Location,
                COUNT(DISTINCT jo.OfferID) AS OffersExtended
            FROM Job_Offer jo
            JOIN Job_Application ja ON jo.ApplicationID = ja.ApplicationID
            JOIN `Position`     p   ON ja.PositionID    = p.PositionID
            JOIN Employer       e   ON p.EmployerID     = e.EmployerID
            JOIN Industry       ind ON e.IndustryID     = ind.IndustryID
            JOIN Student        s   ON ja.StudentID     = s.StudentID
            WHERE s.AdvisorID = %s
            GROUP BY ind.Title, e.Name, e.Location
            ORDER BY OffersExtended DESC, Industry, EmployerName
        """, (advisor_id,))
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"get_top_offer_employers error: {e}")
        return jsonify({"error": "Database error."}), 500


# GET  /advisor/<advisor_id>/analytics/placement
# US5 — Year-over-year placements and average time-to-offer
@advisor_routes.route('/<int:advisor_id>/analytics/placement', methods=['GET'])
def get_yoy_placement(advisor_id):
    try:
        conn   = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                YEAR(ja.Application_Date) AS ApplicationYear,
                COUNT(DISTINCT
                    CASE WHEN jo.OfferAccepted = TRUE
                         THEN ja.StudentID END) AS StudentsPlaced,
                ROUND(AVG(TIMESTAMPDIFF(WEEK, ja.Application_Date, jo.DateExtended)), 2)
                    AS AvgWeeksToOffer
            FROM Job_Application ja
            LEFT JOIN Job_Offer jo ON ja.ApplicationID = jo.ApplicationID
            JOIN Student s         ON ja.StudentID     = s.StudentID
            WHERE s.AdvisorID = %s
            GROUP BY YEAR(ja.Application_Date)
            ORDER BY ApplicationYear
        """, (advisor_id,))
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"get_yoy_placement error: {e}")
        return jsonify({"error": "Database error."}), 500


# GET  /advisor/<advisor_id>/students/<student_id>/applications
# US6 — Full application log for one student with interviews + offers
@advisor_routes.route('/<int:advisor_id>/students/<int:student_id>/applications',
                      methods=['GET'])
def get_student_application_log(advisor_id, student_id):
    try:
        conn   = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT StudentID FROM Student WHERE StudentID = %s AND AdvisorID = %s",
            (student_id, advisor_id)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Student not found under this advisor."}), 404

        cursor.execute("""
            SELECT
                ja.ApplicationID,
                ja.Application_Date,
                ja.Status,
                p.Title  AS PositionTitle,
                e.Name   AS EmployerName,
                i.Date_Time         AS InterviewDate,
                i.Type              AS InterviewType,
                i.RecruiterFeedback,
                jo.Salary,
                jo.DateExtended,
                jo.Deadline,
                jo.OfferAccepted
            FROM Job_Application ja
            JOIN `Position` p ON ja.PositionID     = p.PositionID
            JOIN Employer   e ON p.EmployerID      = e.EmployerID
            LEFT JOIN Interview  i  ON ja.ApplicationID = i.ApplicationID
            LEFT JOIN Job_Offer  jo ON ja.ApplicationID = jo.ApplicationID
            WHERE ja.StudentID = %s
            ORDER BY ja.Application_Date DESC, i.Date_Time DESC
        """, (student_id,))
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"get_student_application_log error: {e}")
        return jsonify({"error": "Database error."}), 500


# GET  /advisor/<advisor_id>/students/<student_id>/applications/<app_id>/notes
# US6 — Return all coaching notes on a specific application
@advisor_routes.route(
    '/<int:advisor_id>/students/<int:student_id>/applications/<int:app_id>/notes',
    methods=['GET']
)
def get_application_notes(advisor_id, student_id, app_id):
    try:
        conn   = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT n.NoteID, n.Note_Text, n.Created_At
            FROM Note n
            JOIN Job_Application ja ON n.ApplicationID = ja.ApplicationID
            JOIN Student s          ON ja.StudentID    = s.StudentID
            WHERE n.ApplicationID = %s
              AND ja.StudentID    = %s
              AND s.AdvisorID     = %s
            ORDER BY n.Created_At DESC
        """, (app_id, student_id, advisor_id))
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f"get_application_notes error: {e}")
        return jsonify({"error": "Database error."}), 500


# POST /advisor/<advisor_id>/students/<student_id>/applications/<app_id>/notes
# US6 — Advisor adds a coaching note to an application
# Body: { "note_text": "..." }
@advisor_routes.route(
    '/<int:advisor_id>/students/<int:student_id>/applications/<int:app_id>/notes',
    methods=['POST']
)
def add_application_note(advisor_id, student_id, app_id):
    try:
        body      = request.get_json(force=True)
        note_text = (body.get('note_text') or '').strip()
        if not note_text:
            return jsonify({"error": "note_text is required."}), 400

        conn   = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT ja.ApplicationID FROM Job_Application ja
            JOIN Student s ON ja.StudentID = s.StudentID
            WHERE ja.ApplicationID = %s AND ja.StudentID = %s AND s.AdvisorID = %s
        """, (app_id, student_id, advisor_id))
        if not cursor.fetchone():
            return jsonify({"error": "Application not found."}), 404

        cursor.execute(
            "INSERT INTO Note (ApplicationID, Note_Text, Created_At) VALUES (%s, %s, NOW())",
            (app_id, note_text)
        )
        conn.commit()
        return jsonify({"message": "Note added.", "NoteID": cursor.lastrowid}), 201
    except Error as e:
        current_app.logger.error(f"add_application_note error: {e}")
        return jsonify({"error": "Database error."}), 500


# PUT  /advisor/<advisor_id>/students/<student_id>/applications/<app_id>/status
# US6 — Advisor corrects an application's status or notes field
# Body: { "status": "...", "notes": "..." }  (at least one required)
@advisor_routes.route(
    '/<int:advisor_id>/students/<int:student_id>/applications/<int:app_id>/status',
    methods=['PUT']
)
def update_application_status(advisor_id, student_id, app_id):
    try:
        body   = request.get_json(force=True)
        status = body.get('status')
        notes  = body.get('notes')

        if not status and notes is None:
            return jsonify({"error": "Provide at least one of: status, notes."}), 400

        conn   = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT ja.ApplicationID FROM Job_Application ja
            JOIN Student s ON ja.StudentID = s.StudentID
            WHERE ja.ApplicationID = %s AND ja.StudentID = %s AND s.AdvisorID = %s
        """, (app_id, student_id, advisor_id))
        if not cursor.fetchone():
            return jsonify({"error": "Application not found."}), 404

        updates, params = [], []
        if status:
            updates.append("Status = %s")
            params.append(status)
        if notes is not None:
            updates.append("Notes = %s")
            params.append(notes)

        params.append(app_id)
        cursor.execute(
            f"UPDATE Job_Application SET {', '.join(updates)} WHERE ApplicationID = %s",
            params
        )
        conn.commit()
        return jsonify({"message": "Application updated."}), 200
    except Error as e:
        current_app.logger.error(f"update_application_status error: {e}")
        return jsonify({"error": "Database error."}), 500


# PUT  /advisor/<advisor_id>/notes/<note_id>
# US6 — Advisor edits the text of an existing coaching note
# Body: { "note_text": "..." }
@advisor_routes.route('/<int:advisor_id>/notes/<int:note_id>', methods=['PUT'])
def update_note(advisor_id, note_id):
    try:
        body      = request.get_json(force=True)
        note_text = (body.get('note_text') or '').strip()
        if not note_text:
            return jsonify({"error": "note_text is required."}), 400

        conn   = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT n.NoteID FROM Note n
            JOIN Job_Application ja ON n.ApplicationID = ja.ApplicationID
            JOIN Student s          ON ja.StudentID    = s.StudentID
            WHERE n.NoteID = %s AND s.AdvisorID = %s
        """, (note_id, advisor_id))
        if not cursor.fetchone():
            return jsonify({"error": "Note not found."}), 404

        cursor.execute(
            "UPDATE Note SET Note_Text = %s WHERE NoteID = %s",
            (note_text, note_id)
        )
        conn.commit()
        return jsonify({"message": "Note updated."}), 200
    except Error as e:
        current_app.logger.error(f"update_note error: {e}")
        return jsonify({"error": "Database error."}), 500


# DELETE /advisor/<advisor_id>/notes/<note_id>
# US6 — Advisor removes a coaching note (verifies ownership first)
@advisor_routes.route('/<int:advisor_id>/notes/<int:note_id>', methods=['DELETE'])
def delete_note(advisor_id, note_id):
    try:
        conn   = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT n.NoteID FROM Note n
            JOIN Job_Application ja ON n.ApplicationID = ja.ApplicationID
            JOIN Student s          ON ja.StudentID    = s.StudentID
            WHERE n.NoteID = %s AND s.AdvisorID = %s
        """, (note_id, advisor_id))
        if not cursor.fetchone():
            return jsonify({"error": "Note not found."}), 404

        cursor.execute("DELETE FROM Note WHERE NoteID = %s", (note_id,))
        conn.commit()
        return jsonify({"message": "Note deleted."}), 200
    except Error as e:
        current_app.logger.error(f"delete_note error: {e}")
        return jsonify({"error": "Database error."}), 500
