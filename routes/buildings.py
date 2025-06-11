from flask import Blueprint, request, jsonify
from db import get_connection

buildings_bp = Blueprint('buildings', __name__)

@buildings_bp.route('/building', methods=['POST'])
def insert_building():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    query = "INSERT INTO building (building_name, year_built, floors, material) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (
        data['building_name'],
        data['year_built'],
        data['floors'],
        data['material']
    ))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True}), 201

@buildings_bp.route("/building/<int:building_id>", methods=["GET"])
def get_building(building_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM building WHERE building_id = %s", (building_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            return jsonify(result), 200
        else:
            return jsonify({"error": "Building not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@buildings_bp.route('/building', methods=['GET'])
def get_all_buildings():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM building")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results), 200



@buildings_bp.route("/building/<int:building_id>", methods=["DELETE"])
def delete_building(building_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        conn.start_transaction()

        cursor.execute("""
            DELETE bu FROM bathroom_usage bu
            JOIN bathroom b ON bu.bathroom_id = b.bathroom_id
            JOIN floor f ON b.floor_id = f.floor_id
            WHERE f.building_id = %s
        """, (building_id,))

        cursor.execute("""
            DELETE b FROM bathroom b
            JOIN floor f ON b.floor_id = f.floor_id
            WHERE f.building_id = %s
        """, (building_id,))
        cursor.execute("DELETE FROM floor WHERE building_id = %s", (building_id,))
        cursor.execute("DELETE FROM building WHERE building_id = %s", (building_id,))

        conn.commit()
        return jsonify({"message": "Building deleted"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
