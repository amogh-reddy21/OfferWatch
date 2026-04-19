from flask import Blueprint, jsonify
from backend.db_connection import get_db

offers = Blueprint("offers", __name__)


@offers.route("/offers", methods=["GET"])
def get_offers():
    try:
        query = """
            SELECT
                jo.OfferID,
                jo.ApplicationID,
                ja.StudentID,
                p.PositionID,
                p.Title AS PositionTitle,
                e.Name AS EmployerName,
                jo.Salary,
                jo.Location,
                jo.Deadline,
                jo.StartDate,
                jo.OfferAccepted
            FROM Job_Offer jo
            JOIN Job_Application ja
                ON jo.ApplicationID = ja.ApplicationID
            JOIN Position p
                ON ja.PositionID = p.PositionID
            JOIN Employer e
                ON p.EmployerID = e.EmployerID
            ORDER BY jo.Deadline ASC;
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


@offers.route("/offers/<int:offer_id>/accept", methods=["PATCH"])
def accept_offer(offer_id):
    try:
        conn = get_db()
        cursor = conn.cursor()

        query = """
            UPDATE Job_Offer
            SET OfferAccepted = TRUE
            WHERE OfferID = %s
        """

        cursor.execute(query, (offer_id,))
        conn.commit()
        cursor.close()

        return jsonify({"message": "Offer accepted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500