from flask import Blueprint, jsonify
from backend.db_connection import get_db

admin = Blueprint("admin", __name__)


@admin.route("/admin/logs", methods=["GET"])
def get_logs():
    try:
        query = """
            SELECT
                ErrorID,
                ComponentID,
                Error_Type,
                Occurred_At,
                Status,
                Severity,
                Message
            FROM Error_Log
            ORDER BY Occurred_At DESC;
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


@admin.route("/admin/metrics", methods=["GET"])
def get_metrics():
    try:
        query = """
            SELECT
                MetricID,
                ComponentID,
                Metric_Name,
                Metric_Value,
                Metric_Unit,
                Recorded_At
            FROM Health_Metric
            ORDER BY Recorded_At DESC;
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


@admin.route("/admin/users", methods=["GET"])
def get_users():
    try:
        query = """
            SELECT
                UserID,
                FirstName,
                LastName,
                Email,
                RoleID,
                InstitutionID,
                Created_At,
                Deactivated_At,
                Account_Status
            FROM User
            ORDER BY UserID;
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