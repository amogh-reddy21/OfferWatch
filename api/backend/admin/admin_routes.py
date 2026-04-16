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
