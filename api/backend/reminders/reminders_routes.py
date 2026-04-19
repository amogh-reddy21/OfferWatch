from flask import Blueprint, jsonify
from backend.db_connection import get_db

reminders = Blueprint("reminders", __name__)


@reminders.route("/reminders", methods=["GET"])
def get_reminders():
    try:
        query = """
            SELECT
                r.ReminderID,
                r.ApplicationID,
                ja.StudentID,
                e.Name AS EmployerName,
                p.Title AS PositionTitle,
                r.Description,
                r.DueDate
            FROM Reminder r
            JOIN Job_Application ja
                ON r.ApplicationID = ja.ApplicationID
            JOIN Position p
                ON ja.PositionID = p.PositionID
            JOIN Employer e
                ON p.EmployerID = e.EmployerID
            ORDER BY r.DueDate ASC;
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