from flask import Blueprint, jsonify, request, current_app, redirect, url_for
from backend.db_connection import get_db
from mysql.connector import Error

admin = Blueprint("admin", __name__)

@admin.route("/health", methods=["GET"])
def get_health():
    cursor = get_db().cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT COUNT(*) AS ActiveUsers
            FROM `User`
            WHERE Account_Status = 'Active';
        """)
        active_users = cursor.fetchone()

        cursor.execute("""
            SELECT Metric_Value AS APIResponse
            FROM Health_Metric
            WHERE Metric_Name = 'Response Time'
            ORDER BY Recorded_At DESC LIMIT 1;
        """)
        api_response = cursor.fetchone()

        cursor.execute("""
            SELECT COUNT(*) AS ErrorsLast24h
            FROM Error_Log
            WHERE Occurred_At >= NOW() - INTERVAL 24 HOUR;
        """)
        errors = cursor.fetchone()

        cursor.execute("""
            SELECT Metric_Value AS Uptime
            FROM Health_Metric
            WHERE Metric_Name = 'Uptime'
            ORDER BY Recorded_At DESC 
            LIMIT 1;
        """)
        uptime = cursor.fetchone()

        cursor.execute("""
            SELECT Component_Name, Current_Status
            FROM Service_Component;
        """)
        components = cursor.fetchall()

        return jsonify({
            "active_users":  active_users["ActiveUsers"],
            "api_response":  api_response["APIResponse"],
            "errors_24h":    errors["ErrorsLast24h"],
            "uptime":        uptime["Uptime"] if uptime else None,
            "components":    components
        }), 200

    except Error as e:
        current_app.logger.error(f'get_health error happened: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@admin.route("/users", methods=["GET"])
def get_users():
    cursor = get_db().cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT u.UserID,
                   CONCAT(u.FirstName, ' ', u.LastName) AS FullName,
                   u.Email,
                   r.RoleName,
                   i.InstitutionName,
                   u.Account_Status
            FROM `User` u
                JOIN Role r ON u.RoleID = r.RoleID
                JOIN Institution i ON u.InstitutionID = i.InstitutionID
            ORDER BY u.Created_At DESC;
        """)

        results = cursor.fetchall()
        return jsonify(results), 200

    except Error as e:
        current_app.logger.error(f'get_users error happened: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@admin.route("/data-cleanup", methods=["GET"])
def get_errors():
    cursor = get_db().cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT el.ErrorID,
                   sc.Component_Name,
                   el.Error_Type,
                   el.Severity,
                   el.Status,
                   el.Occurred_At,
                   el.Message
            FROM Error_Log el
                JOIN Service_Component sc ON el.ComponentID = sc.ComponentID
            ORDER BY el.Occurred_At DESC;
        """)

        results = cursor.fetchall()
        return jsonify(results), 200

    except Error as e:
        current_app.logger.error(f'get_error happened: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


@admin.route("/data-cleanup", methods=["GET"])
def get_outdated_records():
    cursor = get_db().cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT ja.ApplicationID,
                   CONCAT(u.FirstName, ' ', u.LastName) AS StudentName,
                   p.Title AS PositionTitle,
                   e.Name AS EmployerName,
                   ja.Application_Date,
                   ja.Status,
                   ja.IsArchived
            FROM Job_Application ja
                JOIN Student s ON ja.StudentID = s.StudentID
                JOIN `User` u ON s.UserID = u.UserID
                JOIN `Position` p ON ja.PositionID = p.PositionID
                JOIN Employer e ON p.EmployerID = e.EmployerID
            WHERE ja.IsArchived = TRUE
            ORDER BY ja.Application_Date;
        """)

        results = cursor.fetchall()
        return jsonify(results), 200

    except Error as e:
        current_app.logger.error(f'get_outdated_records happened: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()