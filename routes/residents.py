from flask import Blueprint, request, jsonify
from db import get_connection

residents_bp = Blueprint('residents', __name__)

@residents_bp.route('/residents', methods=['GET'])
def get_residents():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT resident_id, student_id, name FROM residents")
    residents = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(residents), 200

@residents_bp.route("/residents/<int:resident_id>", methods=["GET"])
def get_resident(resident_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM residents WHERE resident_id = %s", (resident_id,))
    result = cursor.fetchone()
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "Resident not found"}), 404

@residents_bp.route('/residents', methods=['POST'])
def add_resident():
    data = request.json
    student_id = data.get("student_id")
    name = data.get("name")

    if not student_id or not name:
        return jsonify({"error": "student_id and name required"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM residents WHERE student_id=%s", (student_id,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"error": "student_id must be unique"}), 409

    cursor.execute("INSERT INTO residents (student_id, name) VALUES (%s, %s)", (student_id, name))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True}), 201

@residents_bp.route('/residents/<int:resident_id>', methods=['PUT'])
def update_resident(resident_id):
    data = request.json
    student_id = data.get('student_id')
    name = data.get('name')

    if not student_id or not name:
        return jsonify({"error": "student_id and name required"}), 400

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT resident_id FROM residents WHERE resident_id = %s", (resident_id,))
            if not cursor.fetchone():
                return jsonify({"error": "Resident not found"}), 404

            cursor.execute(
                "SELECT resident_id FROM residents WHERE student_id = %s AND resident_id != %s",
                (student_id, resident_id)
            )
            if cursor.fetchone():
                return jsonify({"error": "student_id must be unique"}), 409

            cursor.execute(
                "UPDATE residents SET student_id = %s, name = %s WHERE resident_id = %s",
                (student_id, name, resident_id)
            )
            conn.commit()

    return jsonify({"success": True}), 200

@residents_bp.route("/residents/<int:resident_id>", methods=["DELETE"])
def delete_resident(resident_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        conn.start_transaction()

        cursor.execute("DELETE FROM bathroom_usage WHERE resident_id = %s", (resident_id,))
        cursor.execute("DELETE FROM residents WHERE resident_id = %s", (resident_id,))

        conn.commit()
        return jsonify({"message": "Resident deleted"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()