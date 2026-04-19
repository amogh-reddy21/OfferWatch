from flask import Blueprint, jsonify
from backend.db_connection import get_db

recruiter = Blueprint("recruiter", __name__)


@recruiter.route("/recruiter/candidates", methods=["GET"])
def get_candidates():
    try:
        query = """
            SELECT
                ja.ApplicationID,
                s.StudentID,
                CONCAT(u.FirstName, ' ', u.LastName) AS CandidateName,
                inst.InstitutionName,
                m.MajorName,
                p.Title AS PositionTitle,
                e.Name AS EmployerName,
                ja.Status,
                ja.Application_Date
            FROM Job_Application ja
            JOIN Student s
                ON ja.StudentID = s.StudentID
            JOIN User u
                ON s.UserID = u.UserID
            JOIN Institution inst
                ON u.InstitutionID = inst.InstitutionID
            LEFT JOIN Major m
                ON s.MajorID = m.MajorID
            JOIN Position p
                ON ja.PositionID = p.PositionID
            JOIN Employer e
                ON p.EmployerID = e.EmployerID
            ORDER BY ja.Application_Date DESC;
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


@recruiter.route("/recruiter/candidate-profiles", methods=["GET"])
def get_candidate_profiles():
    try:
        query = """
            SELECT
                ja.ApplicationID,
                s.StudentID,
                CONCAT(u.FirstName, ' ', u.LastName) AS CandidateName,
                u.Email,
                inst.InstitutionName,
                m.MajorName,
                s.Year,
                s.GPA,
                p.Title AS PositionTitle,
                e.Name AS EmployerName,
                ja.Status,
                ja.Application_Date
            FROM Job_Application ja
            JOIN Student s
                ON ja.StudentID = s.StudentID
            JOIN User u
                ON s.UserID = u.UserID
            JOIN Institution inst
                ON u.InstitutionID = inst.InstitutionID
            LEFT JOIN Major m
                ON s.MajorID = m.MajorID
            JOIN Position p
                ON ja.PositionID = p.PositionID
            JOIN Employer e
                ON p.EmployerID = e.EmployerID
            ORDER BY ja.Application_Date DESC;
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


@recruiter.route("/recruiter/notes", methods=["GET"])
def get_recruiter_notes():
    try:
        query = """
            SELECT
                n.NoteID,
                n.ApplicationID,
                CONCAT(u.FirstName, ' ', u.LastName) AS CandidateName,
                e.Name AS EmployerName,
                p.Title AS PositionTitle,
                n.Note_Text,
                n.Created_At
            FROM Note n
            JOIN Job_Application ja
                ON n.ApplicationID = ja.ApplicationID
            JOIN Student s
                ON ja.StudentID = s.StudentID
            JOIN User u
                ON s.UserID = u.UserID
            JOIN Position p
                ON ja.PositionID = p.PositionID
            JOIN Employer e
                ON p.EmployerID = e.EmployerID
            ORDER BY n.Created_At DESC;
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